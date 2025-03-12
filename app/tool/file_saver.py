import os
import datetime

import aiofiles

from app.tool.base import BaseTool
from app.logger import logger


class FileSaver(BaseTool):
    name: str = "file_saver"
    description: str = """Save content to a local file at a specified path.
Use this tool when you need to save text, code, or generated content to a file on the local filesystem.
The tool accepts content and a file path, and saves the content to that location.
By default, files are saved to the 'output' directory unless specified otherwise.

To use this tool properly, always provide both the 'content' and 'file_path' parameters.
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "(required) The content to save to the file.",
            },
            "file_path": {
                "type": "string",
                "description": "(required) The path where the file should be saved, including filename and extension. If not absolute, it will be saved in the output directory.",
            },
            "mode": {
                "type": "string",
                "description": "(optional) The file opening mode. Default is 'w' for write. Use 'a' for append.",
                "enum": ["w", "a"],
                "default": "w",
            },
            "output_dir": {
                "type": "string",
                "description": "(optional) The directory where to save the file. Default is 'output'.",
                "default": "output",
            },
        },
        "required": ["content", "file_path"],
    }
    
    # Class variable to store the timestamp for the current prompt execution
    # This ensures all files from the same prompt execution go to the same folder
    _current_session_timestamp = None
    
    @classmethod
    def reset_session(cls):
        """Reset the session timestamp to create a new output folder for a new prompt execution"""
        cls._current_session_timestamp = None
    
    @classmethod
    def get_session_folder(cls, output_dir="output"):
        """Get or create a session folder based on the current timestamp"""
        if cls._current_session_timestamp is None:
            # Only create a new timestamp when needed, once per prompt execution
            cls._current_session_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Create the output directory with timestamp
        timestamped_output_dir = os.path.join(output_dir, f"result_{cls._current_session_timestamp}")
        
        # Ensure the timestamped output directory exists
        if not os.path.exists(timestamped_output_dir):
            os.makedirs(timestamped_output_dir)
            
        return timestamped_output_dir

    @staticmethod
    def generate_default_content(file_path: str) -> str:
        """Generate default content based on file extension"""
        filename = os.path.basename(file_path)
        extension = os.path.splitext(filename)[1].lower()
        
        if extension == '.md':
            return f"# {filename}\n\nDefault content for {filename}\n"
        elif extension == '.txt':
            return f"Default content for {filename}\n"
        elif extension == '.json':
            return "{}"
        elif extension == '.html':
            return f"""<!DOCTYPE html>
<html>
<head>
    <title>{filename}</title>
</head>
<body>
    <h1>Generated Content</h1>
    <p>This is auto-generated content for {filename}.</p>
</body>
</html>"""
        elif extension == '.py':
            return f"""# {filename}
# Auto-generated Python script

def main():
    print("Hello from {filename}!")

if __name__ == "__main__":
    main()
"""
        elif extension == '.css':
            return """/* Auto-generated CSS */
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
}
"""
        elif extension == '.js':
            return """// Auto-generated JavaScript
console.log('Script loaded!');

function greet(name) {
    return `Hello, ${name}!`;
}
"""
        else:
            return f"Default content for {filename}"

    async def execute(self, content=None, file_path=None, mode="w", output_dir="output") -> str:
        """
        Save content to a file at the specified path.

        Args:
            content (str): The content to save to the file.
            file_path (str): The path where the file should be saved.
            mode (str, optional): The file opening mode. Default is 'w' for write. Use 'a' for append.
            output_dir (str, optional): The output directory to save to. Default is 'output'.

        Returns:
            str: A message indicating the result of the operation.
        """
        # Print debugging information
        logger.info(f"FileSaver received: content={type(content)}, file_path={file_path}, mode={mode}")
        
        # Additional validation to ensure required parameters are provided and valid
        if content is None or content == "":
            # Try to generate default content based on file extension
            if file_path:
                logger.warning(f"No content provided for {file_path}, generating default content")
                content = self.generate_default_content(file_path)
                return f"Warning: No content provided. Using auto-generated content for {file_path}.\n" + await self.execute(content, file_path, mode, output_dir)
            else:
                return "Error: Missing or invalid 'content' parameter. Content must be a string."
            
        if not isinstance(content, str):
            logger.error(f"Invalid content type: {type(content)}")
            try:
                # Attempt to convert content to string
                content = str(content)
                logger.warning(f"Converted non-string content to string")
            except:
                return "Error: Invalid 'content' parameter. Content must be convertible to a string."
            
        if file_path is None or not isinstance(file_path, str) or not file_path.strip():
            return "Error: Missing or invalid 'file_path' parameter. File path must be a non-empty string."
            
        if mode not in ["w", "a"]:
            return f"Error: Invalid mode '{mode}'. Mode must be 'w' (write) or 'a' (append)."

        try:
            # Get the session folder (creates it only once per prompt execution)
            timestamped_output_dir = self.get_session_folder(output_dir)
            
            # Check if the path is absolute
            if os.path.isabs(file_path):
                # For absolute paths, extract just the filename or respect relative structure
                # This prevents writing to paths outside the output directory
                if "/" in file_path or "\\" in file_path:
                    # Get the path relative to the root
                    relative_path = os.path.basename(file_path)
                    logger.warning(f"Absolute path detected: {file_path}. Converting to {relative_path} to prevent modifying files outside output directory.")
                    file_path = relative_path
                else:
                    # Already just a filename
                    pass
            else:
                # Remove any existing output directory prefix from the file_path to avoid nesting
                # For example, if file_path is "output/file.md", we want to extract just "file.md"
                if file_path.startswith(f"{output_dir}/"):
                    file_path = file_path[len(f"{output_dir}/"):]
            
            # Preserve the structure specified by the LLM within the file_path
            # But ensure it's all contained within the timestamped output directory
            final_path = os.path.join(timestamped_output_dir, file_path)
            
            # Ensure the directory structure exists
            directory = os.path.dirname(final_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            # Write directly to the file
            async with aiofiles.open(final_path, mode, encoding="utf-8") as file:
                await file.write(content)

            return f"Content successfully saved to {final_path}"
        except Exception as e:
            logger.error(f"Error in FileSaver: {str(e)}")
            return f"Error saving file: {str(e)}"
