"""
MCP Server for Slack Notifications
Handles sending messages to Slack channels
"""
import os
from mcp.server import Server
from mcp.types import Tool, TextContent
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

# Initialize Slack client
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL_ID")
SLACK_ENABLED = os.getenv("SLACK_ENABLED", "false").lower() == "true"

slack_client = WebClient(token=SLACK_TOKEN) if SLACK_TOKEN else None

# Create MCP server
server = Server("slack-notifications-server")

@server.list_tools()
async def list_tools():
    """List available Slack tools"""
    return [
        Tool(
            name="send_slack_message",
            description="Send a message to the configured Slack channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message text to send"
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional title/header for the message"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="send_slack_summary",
            description="Send a formatted summary to Slack with sections",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the summary"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Main summary content"
                    },
                    "sections": {
                        "type": "array",
                        "description": "Array of section objects with title and content",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "content": {"type": "string"}
                            }
                        }
                    }
                },
                "required": ["title", "summary"]
            }
        ),
        Tool(
            name="send_slack_blocks",
            description="Send a rich formatted message using Slack blocks",
            inputSchema={
                "type": "object",
                "properties": {
                    "blocks": {
                        "type": "array",
                        "description": "Array of Slack block objects"
                    }
                },
                "required": ["blocks"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls"""
    
    if not SLACK_ENABLED:
        return [TextContent(type="text", text="Slack notifications are disabled. Set SLACK_ENABLED=true in .env")]
    
    if not slack_client:
        return [TextContent(type="text", text="Slack client not initialized. Check SLACK_BOT_TOKEN in .env")]
    
    try:
        if name == "send_slack_message":
            message = arguments["message"]
            title = arguments.get("title")
            
            # Simple text message
            full_message = f"*{title}*\n\n{message}" if title else message
            
            response = slack_client.chat_postMessage(
                channel=SLACK_CHANNEL,
                text=full_message
            )
            
            return [TextContent(type="text", text=f"Message sent successfully to Slack (ts: {response['ts']})")]
        
        elif name == "send_slack_summary":
            title = arguments["title"]
            summary = arguments["summary"]
            sections = arguments.get("sections", [])
            
            # Build blocks for rich formatting
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": title
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": summary
                    }
                },
                {"type": "divider"}
            ]
            
            # Add sections
            for section in sections:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{section['title']}*\n{section['content']}"
                    }
                })
            
            response = slack_client.chat_postMessage(
                channel=SLACK_CHANNEL,
                blocks=blocks,
                text=title  # Fallback text
            )
            
            return [TextContent(type="text", text=f"Summary sent successfully to Slack (ts: {response['ts']})")]
        
        elif name == "send_slack_blocks":
            blocks = arguments["blocks"]
            
            response = slack_client.chat_postMessage(
                channel=SLACK_CHANNEL,
                blocks=blocks,
                text="New notification from Agile Sprint Assistant"
            )
            
            return [TextContent(type="text", text=f"Blocks sent successfully to Slack (ts: {response['ts']})")]
        
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except SlackApiError as e:
        error_msg = f"Slack API Error: {e.response['error']}"
        return [TextContent(type="text", text=error_msg)]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    asyncio.run(main())