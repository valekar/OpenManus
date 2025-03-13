# OpenManus Architecture Analysis and Tool Integration Guide

## Table of Contents

- [OpenManus Architecture Analysis and Tool Integration Guide](#openmanus-architecture-analysis-and-tool-integration-guide)
  - [Table of Contents](#table-of-contents)
  - [1. Project Overview](#1-project-overview)
  - [2. Architecture Overview](#2-architecture-overview)
  - [3. Core Components](#3-core-components)
    - [3.1 Agent System](#31-agent-system)
    - [3.2 Tool System](#32-tool-system)
    - [3.3 LLM Integration](#33-llm-integration)
    - [3.4 Flow System](#34-flow-system)
  - [4. End-to-End Flow](#4-end-to-end-flow)
  - [5. Adding New Messaging Tools](#5-adding-new-messaging-tools)
    - [5.1 WhatsApp Integration](#51-whatsapp-integration)
    - [5.2 Telegram Integration](#52-telegram-integration)
    - [5.3 Email Integration](#53-email-integration)
  - [6. Best Practices](#6-best-practices)
  - [7. Conclusion](#7-conclusion)

## 1. Project Overview

OpenManus is an open-source framework for building general AI agents. It's designed to be a flexible, extensible system that allows developers to create AI agents capable of using various tools to accomplish tasks. The project is inspired by systems like Manus but aims to be fully open-source and accessible without requiring invite codes.

The core functionality of OpenManus revolves around:

- Processing user prompts through LLM-powered agents
- Using a tool-based architecture to perform actions
- Executing complex workflows through planning and execution
- Saving outputs and results for later reference

## 2. Architecture Overview

OpenManus follows a modular architecture with several key components:

1. **Agent System**: Handles the reasoning and decision-making process
2. **Tool System**: Provides capabilities for the agent to interact with the world
3. **LLM Integration**: Connects to language models for generating responses
4. **Flow System**: Manages the execution flow and coordination between components
5. **Configuration System**: Handles settings and API keys
6. **Logging System**: Records the execution process and results

The architecture is designed to be extensible, allowing new tools and capabilities to be added with minimal changes to the core system.

## 3. Core Components

### 3.1 Agent System

The agent system is built around a hierarchy of agent classes:

- `BaseAgent`: The foundation class that defines the basic agent interface
- `ReActAgent`: Extends the base agent with reasoning and acting capabilities
- `ToolCallAgent`: Adds tool/function calling capabilities to the agent
- `Manus`: The main agent implementation that combines all capabilities

The agent system follows a "think-act" cycle:

1. The agent receives a prompt or request
2. It "thinks" by processing the request through an LLM
3. It "acts" by executing tools based on the LLM's output
4. It observes the results and continues the cycle until completion

Key files:

- `app/agent/base.py`: Base agent implementation
- `app/agent/react.py`: ReAct agent implementation
- `app/agent/toolcall.py`: Tool-calling agent implementation
- `app/agent/manus.py`: Main Manus agent implementation

### 3.2 Tool System

The tool system is the core of OpenManus's capabilities. Each tool is a class that inherits from `BaseTool` and implements an `execute` method. Tools are organized in a `ToolCollection` that manages their registration and execution.

Current tools include:

- `FileSaver`: Saves content to files
- `GoogleSearch`: Performs web searches
- `BrowserUseTool`: Interacts with web browsers
- `PythonExecute`: Executes Python code
- `Terminate`: Ends the agent's execution

Each tool defines:

- A name and description
- Parameters it accepts
- An execute method that performs the actual functionality

Key files:

- `app/tool/base.py`: Base tool implementation
- `app/tool/tool_collection.py`: Tool collection management
- `app/tool/__init__.py`: Tool registration
- Various tool implementations in the `app/tool/` directory

### 3.3 LLM Integration

OpenManus integrates with language models (primarily OpenAI's models) through a dedicated LLM class. This class handles:

- API communication
- Message formatting
- Error handling and retries
- Tool/function calling

The LLM integration supports both OpenAI and Azure OpenAI endpoints and can be configured through the configuration system.

Key files:

- `app/llm.py`: LLM integration implementation
- `app/config.py`: LLM configuration

### 3.4 Flow System

The flow system manages the execution flow of the agent. It defines how the agent processes requests and coordinates multiple agents if needed. The main flow implementation is the planning flow, which breaks down complex tasks into steps.

Key files:

- `app/flow/base.py`: Base flow implementation
- `app/flow/planning.py`: Planning flow implementation
- `app/flow/flow_factory.py`: Factory for creating flows

## 4. End-to-End Flow

The end-to-end flow of OpenManus works as follows:

1. **Input Processing**:

   - User provides a prompt through the command line or a file
   - The main script (`main.py`) initializes the Manus agent
   - The prompt is passed to the agent's `run` method

2. **Agent Initialization**:

   - The agent loads its configuration and available tools
   - It initializes the LLM connection
   - It prepares the memory and state

3. **Execution Loop**:

   - The agent enters a loop of thinking and acting
   - In the "think" phase, it sends the current state to the LLM
   - The LLM generates a response with tool calls
   - In the "act" phase, it executes the tool calls
   - Results are added to the agent's memory
   - The loop continues until completion or max steps

4. **Output Handling**:
   - Results are saved to the output directory
   - The agent provides a summary of the execution

## 5. Adding New Messaging Tools

To add new messaging tools like WhatsApp, Telegram, and email, you'll need to create new tool implementations that integrate with these services. Here's how to implement each one:

### 5.1 WhatsApp Integration

Create a new file `app/tool/whatsapp_messenger.py`:

```python
import os
from typing import Optional

from app.tool.base import BaseTool, ToolResult

class WhatsAppMessenger(BaseTool):
    name: str = "whatsapp_messenger"
    description: str = """Send messages via WhatsApp.
Use this tool when you need to send WhatsApp messages to a specified phone number.
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "phone_number": {
                "type": "string",
                "description": "(required) The phone number to send the message to, including country code (e.g., +1234567890).",
            },
            "message": {
                "type": "string",
                "description": "(required) The message content to send.",
            },
            "media_url": {
                "type": "string",
                "description": "(optional) URL to media file to attach to the message.",
            },
        },
        "required": ["phone_number", "message"],
    }

    async def execute(
        self,
        phone_number: str,
        message: str,
        media_url: Optional[str] = None
    ) -> ToolResult:
        """
        Send a WhatsApp message to the specified phone number.

        Args:
            phone_number: The recipient's phone number with country code
            message: The message content to send
            media_url: Optional URL to media file to attach

        Returns:
            ToolResult with the result of the operation
        """
        try:
            # Here you would implement the actual WhatsApp API integration
            # For example, using the WhatsApp Business API or a third-party service like Twilio

            # Example using Twilio (you would need to install the twilio package)
            # from twilio.rest import Client
            # account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
            # auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
            # client = Client(account_sid, auth_token)
            #
            # message_params = {
            #     'from_': f'whatsapp:{os.environ.get("TWILIO_WHATSAPP_NUMBER")}',
            #     'body': message,
            #     'to': f'whatsapp:{phone_number}'
            # }
            #
            # if media_url:
            #     message_params['media_url'] = [media_url]
            #
            # message = client.messages.create(**message_params)
            # return ToolResult(output=f"WhatsApp message sent successfully. SID: {message.sid}")

            # For demonstration purposes, we'll just return a success message
            return ToolResult(output=f"WhatsApp message would be sent to {phone_number}: {message}")

        except Exception as e:
            return ToolResult(error=f"Failed to send WhatsApp message: {str(e)}")
```

### 5.2 Telegram Integration

Create a new file `app/tool/telegram_messenger.py`:

```python
import os
from typing import Optional

from app.tool.base import BaseTool, ToolResult

class TelegramMessenger(BaseTool):
    name: str = "telegram_messenger"
    description: str = """Send messages via Telegram.
Use this tool when you need to send Telegram messages to a specified chat ID or username.
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "chat_id": {
                "type": "string",
                "description": "(required) The Telegram chat ID or username to send the message to.",
            },
            "message": {
                "type": "string",
                "description": "(required) The message content to send.",
            },
            "parse_mode": {
                "type": "string",
                "description": "(optional) The parsing mode for the message (HTML, Markdown, MarkdownV2).",
                "enum": ["HTML", "Markdown", "MarkdownV2"],
            },
        },
        "required": ["chat_id", "message"],
    }

    async def execute(
        self,
        chat_id: str,
        message: str,
        parse_mode: Optional[str] = None
    ) -> ToolResult:
        """
        Send a Telegram message to the specified chat ID or username.

        Args:
            chat_id: The Telegram chat ID or username
            message: The message content to send
            parse_mode: Optional parsing mode for the message

        Returns:
            ToolResult with the result of the operation
        """
        try:
            # Here you would implement the actual Telegram API integration
            # For example, using the python-telegram-bot library

            # Example using python-telegram-bot (you would need to install this package)
            # import telegram
            # bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
            # bot = telegram.Bot(token=bot_token)
            #
            # send_params = {
            #     'chat_id': chat_id,
            #     'text': message,
            # }
            #
            # if parse_mode:
            #     send_params['parse_mode'] = parse_mode
            #
            # message = await bot.send_message(**send_params)
            # return ToolResult(output=f"Telegram message sent successfully. Message ID: {message.message_id}")

            # For demonstration purposes, we'll just return a success message
            return ToolResult(output=f"Telegram message would be sent to {chat_id}: {message}")

        except Exception as e:
            return ToolResult(error=f"Failed to send Telegram message: {str(e)}")
```

### 5.3 Email Integration

Create a new file `app/tool/email_sender.py`:

```python
import os
from typing import List, Optional

from app.tool.base import BaseTool, ToolResult

class EmailSender(BaseTool):
    name: str = "email_sender"
    description: str = """Send emails to specified recipients.
Use this tool when you need to send email messages to one or more email addresses.
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "to": {
                "type": "array",
                "items": {"type": "string"},
                "description": "(required) List of email addresses to send the email to.",
            },
            "subject": {
                "type": "string",
                "description": "(required) The subject line of the email.",
            },
            "body": {
                "type": "string",
                "description": "(required) The body content of the email.",
            },
            "cc": {
                "type": "array",
                "items": {"type": "string"},
                "description": "(optional) List of email addresses to CC.",
            },
            "bcc": {
                "type": "array",
                "items": {"type": "string"},
                "description": "(optional) List of email addresses to BCC.",
            },
            "is_html": {
                "type": "boolean",
                "description": "(optional) Whether the email body is HTML. Default is false.",
                "default": False,
            },
        },
        "required": ["to", "subject", "body"],
    }

    async def execute(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        is_html: bool = False
    ) -> ToolResult:
        """
        Send an email to the specified recipients.

        Args:
            to: List of recipient email addresses
            subject: Email subject line
            body: Email body content
            cc: Optional list of CC recipients
            bcc: Optional list of BCC recipients
            is_html: Whether the email body is HTML

        Returns:
            ToolResult with the result of the operation
        """
        try:
            # Here you would implement the actual email sending functionality
            # For example, using the smtplib library or a service like SendGrid

            # Example using smtplib
            # import smtplib
            # from email.mime.text import MIMEText
            # from email.mime.multipart import MIMEMultipart
            #
            # smtp_server = os.environ.get('SMTP_SERVER')
            # smtp_port = int(os.environ.get('SMTP_PORT', 587))
            # smtp_username = os.environ.get('SMTP_USERNAME')
            # smtp_password = os.environ.get('SMTP_PASSWORD')
            # from_email = os.environ.get('FROM_EMAIL')
            #
            # msg = MIMEMultipart()
            # msg['From'] = from_email
            # msg['To'] = ', '.join(to)
            # msg['Subject'] = subject
            #
            # if cc:
            #     msg['Cc'] = ', '.join(cc)
            # if bcc:
            #     msg['Bcc'] = ', '.join(bcc)
            #
            # msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            #
            # with smtplib.SMTP(smtp_server, smtp_port) as server:
            #     server.starttls()
            #     server.login(smtp_username, smtp_password)
            #     all_recipients = to + (cc or []) + (bcc or [])
            #     server.sendmail(from_email, all_recipients, msg.as_string())
            #
            # return ToolResult(output=f"Email sent successfully to {', '.join(to)}")

            # For demonstration purposes, we'll just return a success message
            return ToolResult(output=f"Email would be sent to {', '.join(to)} with subject: {subject}")

        except Exception as e:
            return ToolResult(error=f"Failed to send email: {str(e)}")
```

## 6. Best Practices

When adding new tools to OpenManus, follow these best practices:

1. **Consistent Structure**: Follow the existing tool structure with clear name, description, and parameters.

2. **Error Handling**: Implement robust error handling to prevent crashes.

3. **Async Implementation**: Use async/await for all tool implementations to maintain compatibility.

4. **Documentation**: Provide clear documentation in the tool description and code comments.

5. **Configuration**: Store sensitive information like API keys in the configuration system.

6. **Testing**: Test your tools thoroughly before integration.

7. **Dependency Management**: Clearly document any new dependencies required by your tools.

## 7. Conclusion

OpenManus provides a flexible framework for building AI agents with tool-based capabilities. By adding new messaging tools like WhatsApp, Telegram, and email, you can extend the agent's ability to communicate through various channels.

To integrate these new tools into the Manus agent, you'll need to:

1. Create the tool implementations as shown above
2. Register the tools in the Manus agent by adding them to the `available_tools` field in `app/agent/manus.py`
3. Update the configuration to include any necessary API keys or settings
4. Test the integration to ensure it works as expected

With these additions, your OpenManus agent will be able to send messages through multiple channels, making it more versatile and useful for a wider range of applications.
