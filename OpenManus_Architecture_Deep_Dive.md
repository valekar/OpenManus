# OpenManus Architecture Deep Dive

## Table of Contents

- [OpenManus Architecture Deep Dive](#openmanus-architecture-deep-dive)
  - [Table of Contents](#table-of-contents)
  - [1. Introduction](#1-introduction)
  - [2. Project Structure Overview](#2-project-structure-overview)
    - [Key Files and Their Roles](#key-files-and-their-roles)
    - [Dependency Structure](#dependency-structure)
  - [3. Core Components](#3-core-components)
    - [3.1 Agent System](#31-agent-system)
      - [3.1.1 Agent Hierarchy](#311-agent-hierarchy)
      - [3.1.2 Agent State and Memory](#312-agent-state-and-memory)
      - [3.1.3 Agent Execution Flow](#313-agent-execution-flow)
      - [3.1.4 Key Methods and Their Roles](#314-key-methods-and-their-roles)
      - [3.1.5 Agent Configuration](#315-agent-configuration)
    - [3.2 Tool System](#32-tool-system)
      - [3.2.1 Tool Architecture](#321-tool-architecture)
      - [3.2.2 Tool Implementation Pattern](#322-tool-implementation-pattern)
      - [3.2.3 Available Tools](#323-available-tools)
      - [3.2.4 Tool Registration and Discovery](#324-tool-registration-and-discovery)
      - [3.2.5 Tool Execution Flow](#325-tool-execution-flow)
      - [3.2.6 Tool Parameters and JSON Schema](#326-tool-parameters-and-json-schema)
    - [3.3 LLM Integration](#33-llm-integration)
      - [3.3.1 LLM Architecture](#331-llm-architecture)
      - [3.3.2 Key Methods and Their Roles](#332-key-methods-and-their-roles)
      - [3.3.3 Error Handling and Retries](#333-error-handling-and-retries)
      - [3.3.4 Message Formatting](#334-message-formatting)
      - [3.3.5 Tool Calling](#335-tool-calling)
    - [3.4 Flow System](#34-flow-system)
      - [3.4.1 Flow Architecture](#341-flow-architecture)
      - [3.4.2 Flow Execution Process](#342-flow-execution-process)
      - [3.4.3 Planning Flow](#343-planning-flow)
      - [3.4.4 Flow Configuration](#344-flow-configuration)
    - [3.5 Configuration System](#35-configuration-system)
      - [3.5.1 Configuration Architecture](#351-configuration-architecture)
      - [3.5.2 Configuration Structure](#352-configuration-structure)
      - [3.5.3 Configuration Access](#353-configuration-access)
  - [4. Execution Flow](#4-execution-flow)
    - [4.1 Main Execution Flow](#41-main-execution-flow)
    - [4.2 Agent Execution Cycle](#42-agent-execution-cycle)
    - [4.3 Tool Execution Flow](#43-tool-execution-flow)
    - [4.4 LLM Interaction Flow](#44-llm-interaction-flow)
  - [5. Function Call Chains](#5-function-call-chains)
    - [5.1 Prompt Processing Chain](#51-prompt-processing-chain)
    - [5.2 Tool Execution Chain](#52-tool-execution-chain)
    - [5.3 LLM Interaction Chain](#53-llm-interaction-chain)
  - [6. Extension Guidelines](#6-extension-guidelines)
    - [6.1 Adding New Tools](#61-adding-new-tools)
      - [6.1.1 Tool Implementation](#611-tool-implementation)
      - [6.1.2 Tool Registration](#612-tool-registration)
      - [6.1.3 Tool Configuration](#613-tool-configuration)
      - [6.1.4 Testing the Tool](#614-testing-the-tool)
    - [6.2 Modifying Prompts](#62-modifying-prompts)
      - [6.2.1 Prompt Structure](#621-prompt-structure)
      - [6.2.2 Prompt Modification](#622-prompt-modification)
      - [6.2.3 Adding New Prompts](#623-adding-new-prompts)
    - [6.3 Adding New Agent Capabilities](#63-adding-new-agent-capabilities)
      - [6.3.1 Understanding the Agent Hierarchy](#631-understanding-the-agent-hierarchy)
      - [6.3.2 Creating a Custom Agent](#632-creating-a-custom-agent)
      - [6.3.3 Extending Existing Agents](#633-extending-existing-agents)
    - [6.4 Extending the Flow System](#64-extending-the-flow-system)
      - [6.4.1 Understanding the Flow System](#641-understanding-the-flow-system)
      - [6.4.2 Creating a Custom Flow](#642-creating-a-custom-flow)
      - [6.4.3 Using the Custom Flow](#643-using-the-custom-flow)
  - [7. Conclusion](#7-conclusion)

## 1. Introduction

OpenManus is an open-source framework for building general AI agents. It's designed to be a flexible, extensible system that allows developers to create AI agents capable of using various tools to accomplish tasks. The project is inspired by systems like Manus but aims to be fully open-source and accessible without requiring invite codes.

The architecture of OpenManus follows a modular design with several key components that work together to process user prompts, make decisions, and execute actions. This document provides a comprehensive analysis of the OpenManus architecture, focusing on how the components interact, the flow of execution, and the guidelines for extending the system.

The core functionality of OpenManus revolves around:

- Processing user prompts through LLM-powered agents
- Using a tool-based architecture to perform actions
- Executing complex workflows through planning and execution
- Saving outputs and results for later reference

This deep dive will explore each component in detail, explaining how they work together and the design principles behind the architecture.

## 2. Project Structure Overview

The OpenManus project follows a well-organized directory structure that separates concerns and makes the codebase maintainable. Here's a breakdown of the main directories and their purposes:

```
OpenManus/
├── app/                    # Core application code
│   ├── agent/              # Agent implementations
│   ├── flow/               # Execution flow implementations
│   ├── prompt/             # Prompt templates
│   ├── tool/               # Tool implementations
│   ├── config.py           # Configuration handling
│   ├── exceptions.py       # Custom exceptions
│   ├── llm.py              # LLM integration
│   ├── logger.py           # Logging utilities
│   └── schema.py           # Data models and schemas
├── config/                 # Configuration files
├── examples/               # Example use cases
├── logs/                   # Log output directory
├── output/                 # Tool output directory
├── main.py                 # Main entry point
├── run_flow.py             # Alternative entry point
├── requirements.txt        # Dependencies
└── setup.py                # Package setup
```

### Key Files and Their Roles

1. **Entry Points**:

   - `main.py`: The primary entry point for the application. It initializes the Manus agent and processes user prompts.
   - `run_flow.py`: An alternative entry point that provides more flexibility for running different flows.

2. **Core Modules**:

   - `app/config.py`: Handles loading and accessing configuration settings from TOML files.
   - `app/llm.py`: Provides integration with language models (primarily OpenAI) with error handling and retries.
   - `app/schema.py`: Defines data models and schemas used throughout the application.
   - `app/logger.py`: Sets up logging for the application.

3. **Agent System**:

   - `app/agent/base.py`: Defines the base agent interface.
   - `app/agent/react.py`: Implements the ReAct (Reasoning and Acting) pattern.
   - `app/agent/toolcall.py`: Adds tool calling capabilities to agents.
   - `app/agent/manus.py`: The main Manus agent implementation.

4. **Tool System**:

   - `app/tool/base.py`: Defines the base tool interface.
   - `app/tool/tool_collection.py`: Manages collections of tools.
   - Various tool implementations in `app/tool/`.

5. **Flow System**:

   - `app/flow/base.py`: Defines the base flow interface.
   - `app/flow/planning.py`: Implements planning-based execution flows.
   - `app/flow/flow_factory.py`: Factory for creating flows.

6. **Prompt System**:

   - `app/prompt/manus.py`: Defines prompts for the Manus agent.
   - `app/prompt/toolcall.py`: Defines prompts for tool calling.

7. **Configuration**:
   - `config/config.example.toml`: Example configuration file.
   - `config/config.toml`: User-specific configuration file.

### Dependency Structure

The project follows a hierarchical dependency structure:

1. **Entry Points** depend on **Agents**
2. **Agents** depend on **Tools**, **LLM**, and **Prompts**
3. **Tools** depend on **Base Tool** and may depend on external libraries
4. **Flows** depend on **Agents** and orchestrate their execution
5. All components may depend on **Configuration**, **Schema**, and **Logger**

This structure ensures separation of concerns and makes the codebase modular and extensible.

## 3. Core Components

### 3.1 Agent System

The agent system is the heart of OpenManus, responsible for processing user prompts, making decisions, and executing actions. It follows a hierarchical design with several layers of abstraction:

#### 3.1.1 Agent Hierarchy

```
BaseAgent
   ↑
ReActAgent
   ↑
ToolCallAgent
   ↑
Manus
```

1. **BaseAgent** (`app/agent/base.py`):

   - The foundation of the agent system
   - Defines the basic interface and common functionality
   - Key methods: `run()`, `reset()`, `_initialize()`
   - Manages agent state and memory

2. **ReActAgent** (`app/agent/react.py`):

   - Implements the ReAct (Reasoning and Acting) pattern
   - Extends BaseAgent with thinking and acting capabilities
   - Key methods: `think()`, `act()`, `step()`
   - Manages the reasoning and action cycle

3. **ToolCallAgent** (`app/agent/toolcall.py`):

   - Adds tool/function calling capabilities
   - Extends ReActAgent with tool execution
   - Key methods: `execute_tool()`, `_fix_malformed_json()`
   - Handles tool calls and their results

4. **Manus** (`app/agent/manus.py`):
   - The main agent implementation
   - Configures available tools and settings
   - Extends ToolCallAgent with specific capabilities
   - Customizes the agent for general-purpose use

#### 3.1.2 Agent State and Memory

The agent system uses a state management approach to track its progress and store information:

1. **AgentState** (defined in `app/schema.py`):

   - Enum with states: `IDLE`, `RUNNING`, `FINISHED`, `ERROR`
   - Used to track the current state of the agent

2. **Memory** (defined in `app/schema.py`):

   - Stores the conversation history
   - Methods: `add_message()`, `add_messages()`, `clear()`, `get_recent_messages()`
   - Used to maintain context for the LLM

3. **Message** (defined in `app/schema.py`):
   - Represents a message in the conversation
   - Types: `system`, `user`, `assistant`, `tool`
   - Used to structure the conversation for the LLM

#### 3.1.3 Agent Execution Flow

The agent follows a specific execution flow:

1. **Initialization**:

   ```
   main.py → Manus.__init__() → ToolCallAgent.__init__() → ReActAgent.__init__() → BaseAgent.__init__()
   ```

2. **Run Cycle**:

   ```
   main.py → Manus.run() → BaseAgent.run() → BaseAgent._run_loop() → step() → think() → act()
   ```

3. **Tool Execution**:
   ```
   act() → execute_tool() → ToolCollection.execute() → Tool.execute()
   ```

#### 3.1.4 Key Methods and Their Roles

1. **BaseAgent.run(request)**:

   - Entry point for agent execution
   - Initializes the agent and starts the execution loop
   - Parameters: `request` (the user prompt)
   - Returns: A summary of the execution

2. **BaseAgent.\_run_loop()**:

   - Manages the execution loop
   - Calls `step()` repeatedly until completion
   - Handles maximum steps and termination

3. **ReActAgent.step()**:

   - Executes a single step in the reasoning and action cycle
   - Calls `think()` to generate a plan
   - Calls `act()` to execute the plan
   - Returns: Whether to continue execution

4. **ReActAgent.think()**:

   - Processes the current state and decides on actions
   - Interacts with the LLM to generate a response
   - Returns: Whether to proceed with actions

5. **ReActAgent.act()**:

   - Executes the actions decided in the thinking phase
   - May involve tool execution
   - Returns: The result of the actions

6. **ToolCallAgent.execute_tool(command)**:
   - Executes a specific tool call
   - Handles tool arguments and error cases
   - Returns: The result of the tool execution

#### 3.1.5 Agent Configuration

The Manus agent is configured with:

1. **System Prompt**:

   - Defined in `app/prompt/manus.py`
   - Sets the overall behavior and capabilities

2. **Next Step Prompt**:

   - Defined in `app/prompt/manus.py`
   - Guides the agent in taking the next step

3. **Available Tools**:

   - Defined in `app/agent/manus.py`
   - Specifies which tools the agent can use

4. **Max Steps**:
   - Limits the number of steps to prevent infinite loops
   - Default: 20 steps

### 3.2 Tool System

The tool system is a critical component of OpenManus, providing the agent with capabilities to interact with the world. It follows a modular design that makes it easy to add new tools and extend functionality.

#### 3.2.1 Tool Architecture

The tool system is built around several key components:

```
BaseTool
   ↓
Specific Tool Implementations
   ↓
ToolCollection
```

1. **BaseTool** (`app/tool/base.py`):

   - Abstract base class for all tools
   - Defines the interface that all tools must implement
   - Key methods: `execute()`, `to_param()`, `__call__()`
   - Includes metadata like name, description, and parameters

2. **ToolResult** (`app/tool/base.py`):

   - Represents the result of a tool execution
   - Fields: `output`, `error`, `system`
   - Methods for combining and formatting results

3. **ToolCollection** (`app/tool/tool_collection.py`):
   - Manages a collection of tools
   - Provides methods for executing tools by name
   - Key methods: `execute()`, `to_params()`, `add_tool()`
   - Used by agents to access and manage tools

#### 3.2.2 Tool Implementation Pattern

Each tool in OpenManus follows a consistent implementation pattern:

```python
class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "Description of what the tool does"
    parameters: dict = {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Description of parameter 1",
            },
            # More parameters...
        },
        "required": ["param1"],  # List of required parameters
    }

    async def execute(self, param1: str, **kwargs) -> ToolResult:
        """
        Execute the tool with the given parameters.

        Args:
            param1: Description of parameter 1
            **kwargs: Additional parameters

        Returns:
            ToolResult with the output or error
        """
        try:
            # Tool implementation logic
            result = "Result of tool execution"
            return ToolResult(output=result)
        except Exception as e:
            return ToolResult(error=f"Error executing tool: {str(e)}")
```

This pattern ensures consistency across tools and makes it easy to add new ones.

#### 3.2.3 Available Tools

OpenManus comes with several built-in tools:

1. **FileSaver** (`app/tool/file_saver.py`):

   - Saves content to files
   - Parameters: `content`, `file_path`, `mode`, `output_dir`
   - Used for saving outputs and results

2. **GoogleSearch** (`app/tool/google_search.py`):

   - Performs web searches using Google
   - Parameters: `query`, `num_results`
   - Used for retrieving information from the web

3. **BrowserUseTool** (`app/tool/browser_use_tool.py`):

   - Interacts with web browsers
   - Parameters: `action`, `url`, `index`, etc.
   - Used for web browsing and interaction

4. **PythonExecute** (`app/tool/python_execute.py`):

   - Executes Python code
   - Parameters: `code`
   - Used for running Python scripts

5. **Terminate** (`app/tool/terminate.py`):
   - Ends the agent's execution
   - Parameters: `reason`
   - Used to signal completion or failure

#### 3.2.4 Tool Registration and Discovery

Tools are registered with the agent through the `available_tools` field in the agent class:

```python
# In app/agent/manus.py
available_tools: ToolCollection = Field(
    default_factory=lambda: ToolCollection(
        PythonExecute(), GoogleSearch(), BrowserUseTool(), FileSaver(), Terminate()
    )
)
```

This approach allows for easy addition and removal of tools.

#### 3.2.5 Tool Execution Flow

The tool execution flow follows these steps:

1. **Tool Call Generation**:

   ```
   ReActAgent.think() → LLM.ask_tool() → LLM response with tool calls
   ```

2. **Tool Call Processing**:

   ```
   ToolCallAgent.act() → ToolCallAgent.execute_tool() → Parse arguments
   ```

3. **Tool Execution**:

   ```
   Tool.execute() → ToolResult → Add to memory → Continue execution
   ```

#### 3.2.6 Tool Parameters and JSON Schema

Tools use JSON Schema to define their parameters, which serves several purposes:

1. **Parameter Validation**: Ensures that required parameters are provided and have the correct types
2. **Documentation**: Provides clear documentation of what parameters a tool accepts
3. **LLM Guidance**: Helps the LLM understand how to use the tool correctly

The schema follows this structure:

```json
{
  "type": "object",
  "properties": {
    "param1": {
      "type": "string",
      "description": "Description of parameter 1"
    },
    "param2": {
      "type": "integer",
      "description": "Description of parameter 2"
    }
  },
  "required": ["param1"]
}
```

This schema is converted to a format that the LLM can understand using the `to_param()` method.

### 3.3 LLM Integration

The LLM (Large Language Model) integration is a core component of OpenManus, providing the intelligence and reasoning capabilities for the agent. It's implemented in `app/llm.py` and provides a clean interface for interacting with language models.

#### 3.3.1 LLM Architecture

The LLM integration follows a singleton pattern to ensure efficient use of resources:

```
LLM (Singleton)
   ↓
OpenAI/Azure API Client
```

1. **LLM Class** (`app/llm.py`):

   - Singleton class for LLM interactions
   - Manages API connections and retries
   - Key methods: `ask()`, `ask_tool()`, `format_messages()`
   - Supports both OpenAI and Azure OpenAI endpoints

2. **Configuration**:
   - Defined in `config/config.toml`
   - Specifies model, API keys, and other settings
   - Supports different configurations for different use cases

#### 3.3.2 Key Methods and Their Roles

1. **LLM.\_\_new\_\_(config_name, llm_config)**:

   - Implements the singleton pattern
   - Creates a new instance if one doesn't exist for the given config name
   - Returns an existing instance if one exists

2. **LLM.\_\_init\_\_(config_name, llm_config)**:

   - Initializes the LLM with configuration
   - Sets up the API client (OpenAI or Azure)
   - Configures model, tokens, temperature, etc.

3. **LLM.format_messages(messages)**:

   - Formats messages for the LLM API
   - Converts Message objects to dictionaries
   - Validates message structure

4. **LLM.ask(messages, system_msgs)**:

   - Sends a request to the LLM without tool calling
   - Handles retries and errors
   - Returns the LLM's response

5. **LLM.ask_tool(messages, system_msgs, tools, tool_choice)**:
   - Sends a request to the LLM with tool calling
   - Configures tools and tool choice
   - Returns the LLM's response with tool calls

#### 3.3.3 Error Handling and Retries

The LLM integration includes robust error handling and retry logic:

1. **Retry Mechanism**:

   - Uses the `tenacity` library for retries
   - Exponential backoff with jitter
   - Configurable maximum attempts

2. **Error Types**:

   - `AuthenticationError`: API key issues
   - `RateLimitError`: API rate limiting
   - `APIError`: General API errors
   - Other exceptions

3. **Logging**:
   - Logs errors and retries
   - Provides detailed information for debugging

#### 3.3.4 Message Formatting

Messages are formatted according to the OpenAI API requirements:

```python
[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm doing well, thank you for asking!"},
    {"role": "user", "content": "What can you help me with?"}
]
```

The `format_messages()` method ensures that messages are properly formatted and contain the required fields.

#### 3.3.5 Tool Calling

Tool calling is implemented using the OpenAI function calling API:

1. **Tool Definition**:

   - Tools are defined using JSON Schema
   - Each tool has a name, description, and parameters

2. **Tool Choice**:

   - `"none"`: No tools are used
   - `"auto"`: The LLM decides whether to use tools
   - `"required"`: The LLM must use a tool

3. **Tool Response Parsing**:
   - Parses the LLM's response for tool calls
   - Extracts tool name, arguments, and ID
   - Passes tool calls to the agent for execution

### 3.4 Flow System

The flow system orchestrates the execution of agents and tools to accomplish complex tasks. It's implemented in the `app/flow/` directory and provides a framework for defining and executing workflows.

#### 3.4.1 Flow Architecture

The flow system follows a hierarchical design:

```
BaseFlow
   ↓
Specific Flow Implementations (e.g., PlanningFlow)
```

1. **BaseFlow** (`app/flow/base.py`):

   - Abstract base class for all flows
   - Defines the basic interface and common functionality
   - Key methods: `execute()`
   - Manages agents and their execution

2. **PlanningFlow** (`app/flow/planning.py`):

   - Implements a planning-based execution flow
   - Breaks down complex tasks into steps
   - Manages step execution and dependencies
   - Handles success and failure conditions

3. **FlowFactory** (`app/flow/flow_factory.py`):
   - Factory for creating flows
   - Provides a centralized way to instantiate flows
   - Supports different flow types

#### 3.4.2 Flow Execution Process

The flow execution process follows these steps:

1. **Flow Initialization**:

   ```
   FlowFactory.create_flow() → Flow.__init__() → Configure agents and tools
   ```

2. **Flow Execution**:

   ```
   Flow.execute() → Process input → Execute steps → Return result
   ```

3. **Agent Interaction**:
   ```
   Flow.execute() → Agent.run() → Agent processes request → Flow processes result
   ```

#### 3.4.3 Planning Flow

The planning flow is a key implementation that breaks down complex tasks into manageable steps:

1. **Plan Generation**:

   - Uses an LLM to generate a plan
   - Breaks down the task into steps
   - Defines dependencies between steps

2. **Step Execution**:

   - Executes steps in order, respecting dependencies
   - Handles success and failure conditions
   - Updates the plan based on execution results

3. **Plan Adaptation**:
   - Adapts the plan based on execution results
   - Adds, removes, or modifies steps as needed
   - Ensures the goal is achieved

#### 3.4.4 Flow Configuration

Flows are configured through the configuration system:

1. **Flow Type**:

   - Defined in `config/config.toml`
   - Specifies which flow implementation to use

2. **Flow Parameters**:

   - Configures flow-specific parameters
   - Sets execution options and limits

3. **Agent Configuration**:
   - Specifies which agents to use
   - Configures agent-specific parameters

### 3.5 Configuration System

The configuration system provides a centralized way to manage settings and options for the OpenManus system. It's implemented in `app/config.py` and uses TOML files for configuration.

#### 3.5.1 Configuration Architecture

The configuration system follows a hierarchical design:

```
Config (Singleton)
   ↓
Configuration Files (TOML)
```

1. **Config Class** (`app/config.py`):

   - Singleton class for configuration
   - Loads and parses configuration files
   - Provides access to configuration values
   - Supports default values and validation

2. **Configuration Files**:
   - `config/config.example.toml`: Example configuration
   - `config/config.toml`: User-specific configuration
   - TOML format for readability and structure

#### 3.5.2 Configuration Structure

The configuration is structured into sections:

1. **LLM Configuration**:

   ```toml
   [llm]
   model = "gpt-4o"
   base_url = "https://api.openai.com/v1"
   api_key = "sk-..."
   max_tokens = 4096
   temperature = 0.0
   ```

2. **Tool Configuration**:

   ```toml
   [tools.google_search]
   enabled = true
   api_key = "..."
   ```

3. **Flow Configuration**:
   ```toml
   [flow]
   type = "planning"
   max_steps = 20
   ```

#### 3.5.3 Configuration Access

Configuration values are accessed through the `config` singleton:

```python
from app.config import config

# Access configuration values
model = config.llm["model"]
api_key = config.llm["api_key"]
```

This provides a consistent way to access configuration values throughout the codebase.

## 4. Execution Flow

### 4.1 Main Execution Flow

The main execution flow of OpenManus involves several key steps that work together to process user prompts and generate responses. Here's a detailed breakdown of the flow:

```
User Prompt
    ↓
main.py
    ↓
Manus Agent Initialization
    ↓
Agent Run Cycle
    ↓
Tool Execution
    ↓
Output Generation
```

1. **User Prompt Input**:

   - The user provides a prompt through the command line or a file
   - The prompt is read in `main.py`
   - The prompt is validated and preprocessed

2. **Manus Agent Initialization**:

   - The Manus agent is initialized in `main.py`
   - Configuration is loaded from `config/config.toml`
   - Tools are registered with the agent
   - Memory and state are initialized

3. **Agent Run Cycle**:

   - The agent's `run()` method is called with the user prompt
   - The agent enters a loop of thinking and acting
   - The loop continues until completion or max steps

4. **Tool Execution**:

   - The agent executes tools based on the LLM's decisions
   - Tool results are added to the agent's memory
   - The agent continues the cycle with the new information

5. **Output Generation**:
   - Results are saved to the output directory
   - A summary is returned to the user
   - The agent's state is reset for the next prompt

### 4.2 Agent Execution Cycle

The agent execution cycle is the core of the OpenManus system, responsible for processing prompts and generating responses. Here's a detailed breakdown of the cycle:

```
Agent.run(prompt)
    ↓
_initialize(prompt)
    ↓
_run_loop()
    ↓
step() → think() → act()
    ↓
Return Result
```

1. **Initialization Phase**:

   - `Agent.run(prompt)`: Entry point for agent execution
   - `_initialize(prompt)`: Sets up the agent for execution
   - Adds the prompt to memory
   - Sets the agent state to `RUNNING`

2. **Execution Loop**:

   - `_run_loop()`: Manages the execution loop
   - Calls `step()` repeatedly until completion
   - Handles maximum steps and termination
   - Tracks the number of steps taken

3. **Step Execution**:

   - `step()`: Executes a single step in the cycle
   - Calls `think()` to generate a plan
   - Calls `act()` to execute the plan
   - Returns whether to continue execution

4. **Thinking Phase**:

   - `think()`: Processes the current state and decides on actions
   - Interacts with the LLM to generate a response
   - Analyzes the response for tool calls
   - Returns whether to proceed with actions

5. **Acting Phase**:

   - `act()`: Executes the actions decided in the thinking phase
   - Executes tool calls if present
   - Processes the results of tool execution
   - Returns the result of the actions

6. **Result Generation**:
   - The final result is compiled from the agent's memory
   - The agent state is set to `FINISHED`
   - The result is returned to the caller

### 4.3 Tool Execution Flow

The tool execution flow is responsible for executing tools and processing their results. Here's a detailed breakdown of the flow:

```
ToolCallAgent.act()
    ↓
execute_tool(command)
    ↓
ToolCollection.execute(name, tool_input)
    ↓
Tool.execute(**kwargs)
    ↓
ToolResult
    ↓
Add to Memory
```

1. **Tool Call Identification**:

   - `ToolCallAgent.act()`: Identifies tool calls from the LLM response
   - Extracts tool name, arguments, and ID
   - Prepares for tool execution

2. **Tool Execution Preparation**:

   - `execute_tool(command)`: Prepares to execute a specific tool
   - Parses and validates arguments
   - Handles special cases and error conditions

3. **Tool Collection Lookup**:

   - `ToolCollection.execute(name, tool_input)`: Looks up the tool by name
   - Validates that the tool exists
   - Passes arguments to the tool

4. **Tool Execution**:

   - `Tool.execute(**kwargs)`: Executes the tool with the given arguments
   - Performs the tool's specific functionality
   - Handles errors and exceptions
   - Returns a `ToolResult`

5. **Result Processing**:
   - The `ToolResult` is processed by the agent
   - The result is added to the agent's memory
   - The agent continues execution with the new information

### 4.4 LLM Interaction Flow

The LLM interaction flow is responsible for communicating with the language model and processing its responses. Here's a detailed breakdown of the flow:

```
ReActAgent.think()
    ↓
LLM.ask_tool(messages, system_msgs, tools, tool_choice)
    ↓
OpenAI API Request
    ↓
Response Processing
    ↓
Tool Call Extraction
```

1. **Request Preparation**:

   - `ReActAgent.think()`: Prepares to interact with the LLM
   - Formats messages from memory
   - Adds system messages and prompts

2. **LLM Request**:

   - `LLM.ask_tool()`: Sends a request to the LLM
   - Configures tools and tool choice
   - Handles retries and errors

3. **API Interaction**:

   - The request is sent to the OpenAI API
   - The API processes the request
   - The API returns a response

4. **Response Processing**:

   - The response is parsed and validated
   - Content and tool calls are extracted
   - The response is formatted for the agent

5. **Tool Call Extraction**:
   - Tool calls are extracted from the response
   - Tool name, arguments, and ID are parsed
   - Tool calls are prepared for execution

## 5. Function Call Chains

### 5.1 Prompt Processing Chain

The prompt processing chain is responsible for processing user prompts and preparing them for the agent. Here's a detailed breakdown of the chain:

```
main.py:main()
    ↓
Manus.run(prompt)
    ↓
BaseAgent.run(prompt)
    ↓
BaseAgent._initialize(prompt)
    ↓
Memory.add_message(Message.user_message(prompt))
```

1. **Entry Point**:

   - `main.py:main()`: The entry point for the application
   - Reads the user prompt from the command line or a file
   - Initializes the Manus agent

2. **Agent Run**:

   - `Manus.run(prompt)`: Starts the agent execution
   - Resets the FileSaver session
   - Calls the parent class's `run()` method

3. **Base Agent Run**:

   - `BaseAgent.run(prompt)`: The base implementation of `run()`
   - Initializes the agent
   - Starts the execution loop

4. **Initialization**:

   - `BaseAgent._initialize(prompt)`: Initializes the agent for execution
   - Resets the agent's state
   - Prepares memory and tools

5. **Memory Update**:
   - `Memory.add_message(Message.user_message(prompt))`: Adds the prompt to memory
   - Creates a user message from the prompt
   - Adds the message to the agent's memory

### 5.2 Tool Execution Chain

The tool execution chain is responsible for executing tools and processing their results. Here's a detailed breakdown of the chain:

```
ToolCallAgent.act()
    ↓
ToolCallAgent.execute_tool(command)
    ↓
ToolCollection.execute(name, tool_input)
    ↓
BaseTool.__call__(**kwargs)
    ↓
BaseTool.execute(**kwargs)
    ↓
SpecificTool.execute(**kwargs)
```

1. **Action Phase**:

   - `ToolCallAgent.act()`: Executes actions based on the LLM's decisions
   - Identifies tool calls from the LLM response
   - Iterates through tool calls for execution

2. **Tool Execution Preparation**:

   - `ToolCallAgent.execute_tool(command)`: Prepares to execute a specific tool
   - Parses and validates arguments
   - Handles special cases and error conditions

3. **Tool Collection Lookup**:

   - `ToolCollection.execute(name, tool_input)`: Looks up the tool by name
   - Validates that the tool exists
   - Passes arguments to the tool

4. **Tool Call**:

   - `BaseTool.__call__(**kwargs)`: Calls the tool with the given arguments
   - Delegates to the `execute()` method
   - Handles common functionality

5. **Base Execution**:

   - `BaseTool.execute(**kwargs)`: The base implementation of `execute()`
   - May be overridden by specific tools
   - Provides common functionality

6. **Specific Execution**:
   - `SpecificTool.execute(**kwargs)`: The specific implementation of `execute()`
   - Performs the tool's specific functionality
   - Returns a `ToolResult`

### 5.3 LLM Interaction Chain

The LLM interaction chain is responsible for communicating with the language model and processing its responses. Here's a detailed breakdown of the chain:

```
ReActAgent.think()
    ↓
LLM.ask_tool(messages, system_msgs, tools, tool_choice)
    ↓
LLM.format_messages(messages)
    ↓
OpenAI API Request
    ↓
Response Processing
    ↓
Message.from_tool_calls(content, tool_calls)
```

1. **Thinking Phase**:

   - `ReActAgent.think()`: Processes the current state and decides on actions
   - Formats messages from memory
   - Adds system messages and prompts

2. **LLM Request**:

   - `LLM.ask_tool()`: Sends a request to the LLM
   - Configures tools and tool choice
   - Handles retries and errors

3. **Message Formatting**:

   - `LLM.format_messages(messages)`: Formats messages for the LLM API
   - Converts Message objects to dictionaries
   - Validates message structure

4. **API Interaction**:

   - The request is sent to the OpenAI API
   - The API processes the request
   - The API returns a response

5. **Response Processing**:

   - The response is parsed and validated
   - Content and tool calls are extracted
   - The response is formatted for the agent

6. **Message Creation**:
   - `Message.from_tool_calls(content, tool_calls)`: Creates a message from tool calls
   - Formats tool calls for the agent
   - Adds the message to the agent's memory

## 6. Extension Guidelines

### 6.1 Adding New Tools

Adding new tools to OpenManus is a common way to extend its functionality. Here's a detailed guide on how to add a new tool:

#### 6.1.1 Tool Implementation

1. **Create a New Tool Class**:

   - Create a new file in the `app/tool/` directory (e.g., `app/tool/my_tool.py`)
   - Define a class that inherits from `BaseTool`
   - Implement the required methods and properties

   ```python
   from app.tool.base import BaseTool, ToolResult

   class MyTool(BaseTool):
       name: str = "my_tool"
       description: str = "Description of what the tool does"
       parameters: dict = {
           "type": "object",
           "properties": {
               "param1": {
                   "type": "string",
                   "description": "Description of parameter 1",
               },
               # More parameters...
           },
           "required": ["param1"],  # List of required parameters
       }

       async def execute(self, param1: str, **kwargs) -> ToolResult:
           """
           Execute the tool with the given parameters.

           Args:
               param1: Description of parameter 1
               **kwargs: Additional parameters

           Returns:
               ToolResult with the output or error
           """
           try:
               # Tool implementation logic
               result = "Result of tool execution"
               return ToolResult(output=result)
           except Exception as e:
               return ToolResult(error=f"Error executing tool: {str(e)}")
   ```

2. **Define Tool Parameters**:

   - Use JSON Schema to define parameters
   - Include clear descriptions for each parameter
   - Specify required parameters
   - Use appropriate types (string, integer, boolean, etc.)

3. **Implement the Execute Method**:

   - Make the method `async` to support asynchronous execution
   - Include proper type hints for parameters and return value
   - Handle errors and exceptions
   - Return a `ToolResult` with output or error

4. **Add Documentation**:
   - Include a clear description of the tool
   - Document parameters and their purpose
   - Provide examples of usage
   - Explain any special considerations or limitations

#### 6.1.2 Tool Registration

1. **Import the Tool**:

   - Import the tool in `app/agent/manus.py`
   - Add it to the imports at the top of the file

   ```python
   from app.tool.my_tool import MyTool
   ```

2. **Add to Available Tools**:

   - Add the tool to the `available_tools` field in the `Manus` class
   - Include it in the `ToolCollection` constructor

   ```python
   available_tools: ToolCollection = Field(
       default_factory=lambda: ToolCollection(
           PythonExecute(), GoogleSearch(), BrowserUseTool(), FileSaver(), MyTool(), Terminate()
       )
   )
   ```

3. **Update Dependencies**:
   - Add any new dependencies to `requirements.txt`
   - Document the dependencies in the tool's documentation

#### 6.1.3 Tool Configuration

1. **Add Configuration Settings**:

   - Add configuration settings to `config/config.example.toml`
   - Document the configuration options
   - Provide default values where appropriate

   ```toml
   [tools.my_tool]
   enabled = true
   option1 = "value1"
   option2 = "value2"
   ```

2. **Access Configuration in the Tool**:

   - Import the configuration in the tool
   - Access configuration values as needed

   ```python
   from app.config import config

   # In the execute method
   tool_config = config.get("tools", {}).get("my_tool", {})
   option1 = tool_config.get("option1", "default_value")
   ```

#### 6.1.4 Testing the Tool

1. **Manual Testing**:

   - Run the agent with a prompt that should use the tool
   - Verify that the tool is called correctly
   - Check that the tool's output is as expected

2. **Automated Testing**:
   - Add tests for the tool in the appropriate test directory
   - Test both success and error cases
   - Test with various parameter values

### 6.2 Modifying Prompts

Modifying prompts is another way to extend OpenManus's functionality. Here's a detailed guide on how to modify prompts:

#### 6.2.1 Prompt Structure

1. **Understand the Prompt Structure**:

   - Prompts are defined in the `app/prompt/` directory
   - Each prompt has a specific purpose and context
   - Prompts are used to guide the LLM's behavior

2. **Identify the Prompt to Modify**:
   - `app/prompt/manus.py`: Prompts for the Manus agent
   - `app/prompt/toolcall.py`: Prompts for tool calling
   - Other prompt files for specific purposes

#### 6.2.2 Prompt Modification

1. **Edit the Prompt**:

   - Open the appropriate prompt file
   - Modify the prompt text as needed
   - Ensure the prompt maintains its purpose and context

   ```python
   # In app/prompt/manus.py
   SYSTEM_PROMPT = """
   You are Manus, a versatile AI assistant that can help with various tasks.
   You have access to several tools that you can use to assist the user.
   ...
   """
   ```

2. **Test the Modified Prompt**:
   - Run the agent with the modified prompt
   - Verify that the agent's behavior is as expected
   - Adjust the prompt as needed based on testing

#### 6.2.3 Adding New Prompts

1. **Create a New Prompt File**:

   - Create a new file in the `app/prompt/` directory
   - Define the prompts as constants
   - Include documentation for each prompt

   ```python
   # In app/prompt/my_prompts.py
   MY_SYSTEM_PROMPT = """
   System prompt for a specific purpose.
   ...
   """

   MY_NEXT_STEP_PROMPT = """
   Next step prompt for a specific purpose.
   ...
   """
   ```

2. **Use the New Prompts**:

   - Import the prompts in the appropriate agent or flow
   - Assign the prompts to the appropriate fields
   - Test the agent with the new prompts

   ```python
   # In a custom agent
   from app.prompt.my_prompts import MY_SYSTEM_PROMPT, MY_NEXT_STEP_PROMPT

   class MyAgent(ToolCallAgent):
       system_prompt: str = MY_SYSTEM_PROMPT
       next_step_prompt: str = MY_NEXT_STEP_PROMPT
       # ...
   ```

### 6.3 Adding New Agent Capabilities

Adding new agent capabilities allows you to extend the functionality of OpenManus in more significant ways. Here's a detailed guide on how to add new agent capabilities:

#### 6.3.1 Understanding the Agent Hierarchy

1. **Review the Agent Hierarchy**:

   - `BaseAgent`: The foundation of the agent system
   - `ReActAgent`: Adds reasoning and acting capabilities
   - `ToolCallAgent`: Adds tool calling capabilities
   - `Manus`: The main agent implementation

2. **Identify the Extension Point**:
   - Extend an existing agent class
   - Override methods to add new capabilities
   - Add new methods for specific functionality

#### 6.3.2 Creating a Custom Agent

1. **Create a New Agent Class**:

   - Create a new file in the `app/agent/` directory
   - Define a class that inherits from an appropriate base class
   - Implement the required methods and properties

   ```python
   # In app/agent/my_agent.py
   from app.agent.toolcall import ToolCallAgent
   from app.prompt.my_prompts import MY_SYSTEM_PROMPT, MY_NEXT_STEP_PROMPT
   from app.tool import ToolCollection
   from pydantic import Field

   class MyAgent(ToolCallAgent):
       name: str = "my_agent"
       description: str = "A custom agent with specific capabilities"

       system_prompt: str = MY_SYSTEM_PROMPT
       next_step_prompt: str = MY_NEXT_STEP_PROMPT

       available_tools: ToolCollection = Field(
           default_factory=lambda: ToolCollection(
               # Tools for this agent
           )
       )

       # Override methods as needed
       async def think(self) -> bool:
           # Custom thinking logic
           return await super().think()

       async def act(self) -> str:
           # Custom acting logic
           return await super().act()

       # Add new methods for specific functionality
       async def custom_method(self) -> str:
           # Custom functionality
           return "Result of custom method"
   ```

2. **Register the Agent**:

   - Import the agent in the appropriate entry point
   - Initialize the agent as needed
   - Use the agent in the application

   ```python
   # In a custom entry point
   from app.agent.my_agent import MyAgent

   async def main():
       agent = MyAgent()
       # Use the agent
   ```

#### 6.3.3 Extending Existing Agents

1. **Extend the Manus Agent**:

   - Create a new class that inherits from `Manus`
   - Override methods to add new capabilities
   - Add new methods for specific functionality

   ```python
   # In app/agent/extended_manus.py
   from app.agent.manus import Manus
   from app.tool import ToolCollection
   from pydantic import Field

   class ExtendedManus(Manus):
       name: str = "extended_manus"
       description: str = "An extended version of the Manus agent"

       # Override or extend available tools
       available_tools: ToolCollection = Field(
           default_factory=lambda: ToolCollection(
               # Tools for this agent
           )
       )

       # Override methods as needed
       async def run(self, request: Optional[str] = None) -> str:
           # Custom run logic
           return await super().run(request)
   ```

2. **Use the Extended Agent**:
   - Import the extended agent in the appropriate entry point
   - Initialize the agent as needed
   - Use the agent in the application

### 6.4 Extending the Flow System

Extending the flow system allows you to create custom execution flows for specific use cases. Here's a detailed guide on how to extend the flow system:

#### 6.4.1 Understanding the Flow System

1. **Review the Flow Hierarchy**:

   - `BaseFlow`: The foundation of the flow system
   - `PlanningFlow`: Implements planning-based execution
   - Other flow implementations for specific purposes

2. **Identify the Extension Point**:
   - Extend an existing flow class
   - Override methods to add new capabilities
   - Add new methods for specific functionality

#### 6.4.2 Creating a Custom Flow

1. **Create a New Flow Class**:

   - Create a new file in the `app/flow/` directory
   - Define a class that inherits from an appropriate base class
   - Implement the required methods and properties

   ```python
   # In app/flow/my_flow.py
   from app.flow.base import BaseFlow
   from app.agent.base import BaseAgent
   from typing import Dict, Union, List

   class MyFlow(BaseFlow):
       """A custom flow implementation for specific use cases."""

       async def execute(self, input_text: str) -> str:
           """
           Execute the flow with the given input.

           Args:
               input_text: The input text to process

           Returns:
               The result of the flow execution
           """
           # Custom flow execution logic
           agent = self.primary_agent
           result = await agent.run(input_text)
           # Process the result as needed
           return result
   ```

2. **Register the Flow**:

   - Add the flow to the `FlowFactory`
   - Import the flow in the appropriate entry point
   - Initialize the flow as needed

   ```python
   # In app/flow/flow_factory.py
   from app.flow.my_flow import MyFlow

   def create_flow(flow_type: str, agents, **kwargs) -> BaseFlow:
       if flow_type == "my_flow":
           return MyFlow(agents, **kwargs)
       # Other flow types...
   ```

#### 6.4.3 Using the Custom Flow

1. **Configure the Flow**:

   - Add configuration settings to `config/config.toml`
   - Specify the flow type and parameters
   - Document the configuration options

   ```toml
   [flow]
   type = "my_flow"
   # Flow-specific parameters
   ```

2. **Use the Flow**:

   - Import the flow factory in the appropriate entry point
   - Create the flow using the factory
   - Execute the flow with the input text

   ```python
   # In a custom entry point
   from app.flow.flow_factory import create_flow
   from app.agent.manus import Manus

   async def main():
       agent = Manus()
       flow = create_flow("my_flow", agent)
       result = await flow.execute("Input text")
       # Process the result as needed
   ```

## 7. Conclusion

OpenManus is a powerful framework for building general AI agents. Its modular design allows developers to easily extend and customize the system to meet their specific needs. By understanding the architecture and following the guidelines for extending the system, developers can create AI agents that are capable of using various tools to accomplish tasks.

The key components of OpenManus—the agent system, tool system, LLM integration, and flow system—work together to provide a flexible and extensible framework for AI agent development. The clear separation of concerns and well-defined interfaces make it easy to add new capabilities and customize the system.

By following the extension guidelines provided in this document, developers can:

1. **Add New Tools**: Extend the agent's capabilities by adding new tools for specific tasks.
2. **Modify Prompts**: Customize the agent's behavior by modifying the prompts used to guide the LLM.
3. **Add New Agent Capabilities**: Create custom agents with specific capabilities for particular use cases.
4. **Extend the Flow System**: Define custom execution flows for complex tasks and workflows.

These extension points provide a wide range of possibilities for customizing and extending OpenManus to meet the needs of various applications and use cases. Whether you're building a simple chatbot or a complex AI assistant, OpenManus provides the foundation and flexibility to make it happen.
