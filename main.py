import asyncio
import sys

from app.agent.manus import Manus
from app.logger import logger
from app.tool.file_saver import FileSaver


async def main():
    agent = Manus()
    try:
        # Check if input is being piped from a file or redirected
        if not sys.stdin.isatty():
            # Read from stdin (piped input)
            prompt = sys.stdin.read().strip()
        else:
            # Interactive input from terminal
            prompt = input("Enter your prompt: ")
            
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        # Reset the FileSaver session to create a new timestamped folder for this prompt
        FileSaver.reset_session()
        
        logger.warning("Processing your request...")
        await agent.run(prompt)
        logger.info("Request processing completed.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")


if __name__ == "__main__":
    asyncio.run(main())
