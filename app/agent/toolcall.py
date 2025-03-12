import json
import os
import re
from typing import Any, Dict, List, Literal

from pydantic import Field

from app.agent.react import ReActAgent
from app.logger import logger
from app.prompt.toolcall import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.schema import AgentState, Message, ToolCall
from app.tool import CreateChatCompletion, Terminate, ToolCollection


TOOL_CALL_REQUIRED = "Tool calls required but none provided"
OUTPUT_DIR = "output"


class ToolCallAgent(ReActAgent):
    """Base agent class for handling tool/function calls with enhanced abstraction"""

    name: str = "toolcall"
    description: str = "an agent that can execute tool calls."

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    available_tools: ToolCollection = ToolCollection(
        CreateChatCompletion(), Terminate()
    )
    tool_choices: Literal["none", "auto", "required"] = "auto"
    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])

    tool_calls: List[ToolCall] = Field(default_factory=list)
    output_directory: str = OUTPUT_DIR

    max_steps: int = 30

    async def think(self) -> bool:
        """Process current state and decide next actions using tools"""
        if self.next_step_prompt:
            user_msg = Message.user_message(self.next_step_prompt)
            self.messages += [user_msg]

        # Add information about output directory
        enhanced_system_prompt = self.system_prompt
        if not enhanced_system_prompt.endswith('\n'):
            enhanced_system_prompt += '\n'
        enhanced_system_prompt += f"\nOutput Directory: Files will be saved in the '{self.output_directory}' directory by default. " \
                                 f"You can access previous task outputs from this directory."

        # Get response with tool options
        response = await self.llm.ask_tool(
            messages=self.messages,
            system_msgs=[Message.system_message(enhanced_system_prompt)]
            if self.system_prompt
            else None,
            tools=self.available_tools.to_params(),
            tool_choice=self.tool_choices,
        )
        self.tool_calls = response.tool_calls

        # Log response info
        logger.info(f"✨ {self.name}'s thoughts: {response.content}")
        logger.info(
            f"🛠️ {self.name} selected {len(response.tool_calls) if response.tool_calls else 0} tools to use"
        )
        if response.tool_calls:
            logger.info(
                f"🧰 Tools being prepared: {[call.function.name for call in response.tool_calls]}"
            )

        try:
            # Handle different tool_choices modes
            if self.tool_choices == "none":
                if response.tool_calls:
                    logger.warning(
                        f"🤔 Hmm, {self.name} tried to use tools when they weren't available!"
                    )
                if response.content:
                    self.memory.add_message(Message.assistant_message(response.content))
                    return True
                return False

            # Create and add assistant message
            assistant_msg = (
                Message.from_tool_calls(
                    content=response.content, tool_calls=self.tool_calls
                )
                if self.tool_calls
                else Message.assistant_message(response.content)
            )
            self.memory.add_message(assistant_msg)

            if self.tool_choices == "required" and not self.tool_calls:
                return True  # Will be handled in act()

            # For 'auto' mode, continue with content if no commands but content exists
            if self.tool_choices == "auto" and not self.tool_calls:
                return bool(response.content)

            return bool(self.tool_calls)
        except Exception as e:
            logger.error(f"🚨 Oops! The {self.name}'s thinking process hit a snag: {e}")
            self.memory.add_message(
                Message.assistant_message(
                    f"Error encountered while processing: {str(e)}"
                )
            )
            return False

    async def act(self) -> str:
        """Execute tool calls and handle their results"""
        if not self.tool_calls:
            if self.tool_choices == "required":
                raise ValueError(TOOL_CALL_REQUIRED)

            # Return last message content if no tool calls
            return self.messages[-1].content or "No content or commands to execute"

        results = []
        for command in self.tool_calls:
            result = await self.execute_tool(command)
            logger.info(
                f"🎯 Tool '{command.function.name}' completed its mission! Result: {result}"
            )

            # Add tool response to memory
            tool_msg = Message.tool_message(
                content=result, tool_call_id=command.id, name=command.function.name
            )
            self.memory.add_message(tool_msg)
            results.append(result)

        return "\n\n".join(results)

    def _fix_malformed_json(self, raw_args: str) -> Dict:
        """Helper method to fix malformed JSON for tools"""
        # Add closing brace if missing
        if "{" in raw_args and "}" not in raw_args:
            raw_args = raw_args + "}"
            
        # Try to extract key-value pairs using regex
        args = {}
        # Extract file_path
        file_path_match = re.search(r'"file_path"\s*:\s*"([^"]+)"', raw_args)
        if file_path_match:
            args["file_path"] = file_path_match.group(1)
        
        # Extract content if it exists
        content_match = re.search(r'"content"\s*:\s*"([^"]*)"', raw_args)
        if content_match:
            args["content"] = content_match.group(1)
            
        # Extract mode if it exists
        mode_match = re.search(r'"mode"\s*:\s*"([^"]*)"', raw_args)
        if mode_match:
            args["mode"] = mode_match.group(1)
            
        # Extract output_dir if it exists
        output_dir_match = re.search(r'"output_dir"\s*:\s*"([^"]*)"', raw_args)
        if output_dir_match:
            args["output_dir"] = output_dir_match.group(1)
            
        return args
    
    def _generate_default_content(self, file_path: str) -> str:
        """Generate default content based on file extension"""
        from app.tool.file_saver import FileSaver
        return FileSaver.generate_default_content(file_path)

    async def execute_tool(self, command: ToolCall) -> str:
        """Execute a single tool call with robust error handling"""
        if not command or not command.function or not command.function.name:
            return "Error: Invalid command format"

        name = command.function.name
        if name not in self.available_tools.tool_map:
            return f"Error: Unknown tool '{name}'"

        try:
            # Parse arguments
            args = json.loads(command.function.arguments or "{}")
            
            # Special handling for file_saver tool
            if name == "file_saver":
                if "content" not in args:
                    error_msg = f"Error: Missing required 'content' parameter for file_saver tool"
                    logger.error(f"📝 {error_msg}, received arguments: {command.function.arguments}")
                    return f"Error: {error_msg}"
                if "file_path" not in args:
                    error_msg = f"Error: Missing required 'file_path' parameter for file_saver tool"
                    logger.error(f"📝 {error_msg}, received arguments: {command.function.arguments}")
                    return f"Error: {error_msg}"
                
                # Use the agent's output directory if output_dir is not specified
                if "output_dir" not in args:
                    args["output_dir"] = self.output_directory
                    logger.info(f"📁 Using default output directory: {self.output_directory}")

            # Execute the tool
            logger.info(f"🔧 Activating tool: '{name}'...")
            result = await self.available_tools.execute(name=name, tool_input=args)

            # Format result for display
            observation = (
                f"Observed output of cmd `{name}` executed:\n{str(result)}"
                if result
                else f"Cmd `{name}` completed with no output"
            )

            # Handle special tools like `finish`
            await self._handle_special_tool(name=name, result=result)

            return observation
        except json.JSONDecodeError:
            # Try to fix common JSON formatting issues
            if name == "file_saver":
                try:
                    # Get the raw arguments string
                    raw_args = command.function.arguments or ""
                    logger.warning(f"Attempting to fix malformed JSON for file_saver: {raw_args}")
                    
                    # Try to extract arguments using regex pattern matching
                    args = self._fix_malformed_json(raw_args)
                    logger.info(f"Extracted args from malformed JSON: {args}")
                    
                    # If we have file_path but no content, generate default content
                    if "file_path" in args and "content" not in args:
                        file_path = args["file_path"]
                        error_msg = f"Error: JSON is malformed. Missing 'content' parameter for file_saver tool."
                        logger.error(f"📝 {error_msg}, attempting to fix...")
                        
                        # Generate default content based on file type
                        default_content = self._generate_default_content(file_path)
                        
                        if default_content:
                            # Create a corrected JSON object
                            corrected_args = {
                                "file_path": file_path,
                                "content": default_content,
                                "output_dir": self.output_directory
                            }
                            
                            # Add mode if it was in the original arguments
                            if "mode" in args:
                                corrected_args["mode"] = args["mode"]
                                
                            # Add output_dir if it was in the original arguments
                            if "output_dir" in args:
                                corrected_args["output_dir"] = args["output_dir"]
                            
                            logger.warning(f"Created default content for {file_path}")
                            logger.info(f"Fixed arguments: {corrected_args}")
                            
                            # Execute the tool with fixed arguments
                            result = await self.available_tools.execute(name=name, tool_input=corrected_args)
                            
                            return f"Observed output of cmd `{name}` executed (with auto-fixed arguments):\n{str(result)}\n\nNote: Default content was generated because the original request had missing content."
                    
                    # If we extracted both file_path and content, try to execute with those
                    if "file_path" in args and "content" in args:
                        corrected_args = {
                            "file_path": args["file_path"],
                            "content": args["content"],
                            "output_dir": self.output_directory
                        }
                        
                        # Add mode if it was in the original arguments
                        if "mode" in args:
                            corrected_args["mode"] = args["mode"]
                            
                        # Add output_dir if it was in the original arguments
                        if "output_dir" in args:
                            corrected_args["output_dir"] = args["output_dir"]
                        
                        logger.warning(f"Fixed malformed JSON and extracted parameters")
                        logger.info(f"Fixed arguments: {corrected_args}")
                        
                        # Execute the tool with fixed arguments
                        result = await self.available_tools.execute(name=name, tool_input=corrected_args)
                        
                        return f"Observed output of cmd `{name}` executed (with fixed JSON):\n{str(result)}"
                    
                    return f"Error: Invalid JSON format for file_saver tool. To save a file, you need both 'file_path' and 'content' parameters in valid JSON format."
                except Exception as e:
                    logger.error(f"Error while trying to fix JSON: {str(e)}")
            
            error_msg = f"Error parsing arguments for {name}: Invalid JSON format"
            logger.error(
                f"📝 Oops! The arguments for '{name}' don't make sense - invalid JSON, arguments:{command.function.arguments}"
            )
            return f"Error: {error_msg}"
        except Exception as e:
            error_msg = f"⚠️ Tool '{name}' encountered a problem: {str(e)}"
            logger.error(error_msg)
            return f"Error: {error_msg}"

    async def _handle_special_tool(self, name: str, result: Any, **kwargs):
        """Handle special tool execution and state changes"""
        if not self._is_special_tool(name):
            return

        if self._should_finish_execution(name=name, result=result, **kwargs):
            # Set agent state to finished
            logger.info(f"🏁 Special tool '{name}' has completed the task!")
            self.state = AgentState.FINISHED

    @staticmethod
    def _should_finish_execution(**kwargs) -> bool:
        """Determine if tool execution should finish the agent"""
        return True

    def _is_special_tool(self, name: str) -> bool:
        """Check if tool name is in special tools list"""
        return name.lower() in [n.lower() for n in self.special_tool_names]
