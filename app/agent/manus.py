from pydantic import Field

from app.agent.toolcall import ToolCallAgent
from app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool import Terminate, ToolCollection
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.file_saver import FileSaver
from app.tool.google_search import GoogleSearch
from app.tool.python_execute import PythonExecute
from typing import Optional


class Manus(ToolCallAgent):
    """
    A versatile general-purpose agent that uses planning to solve various tasks.

    This agent extends PlanningAgent with a comprehensive set of tools and capabilities,
    including Python execution, web browsing, file operations, and information retrieval
    to handle a wide range of user requests.
    """

    name: str = "Manus"
    description: str = (
        "A versatile agent that can solve various tasks using multiple tools"
    )

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    # Add general-purpose tools to the tool collection
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(), GoogleSearch(), BrowserUseTool(), FileSaver(), Terminate()
        )
    )

    max_steps: int = 20
    
    async def run(self, request: Optional[str] = None) -> str:
        """
        Execute the agent's main loop with a reset of FileSaver session.
        
        This ensures each prompt creates a single timestamped output folder.
        
        Args:
            request: Optional initial user request to process.
            
        Returns:
            A string summarizing the execution results.
        """
        # Reset the FileSaver session to create a new timestamp for this prompt
        FileSaver.reset_session()
        
        # Call the parent class run method to handle the execution
        return await super().run(request)
