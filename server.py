#!/usr/bin/env python3
"""
MCP Server for Email Sending Service
Uses Streamable HTTP transport (single /mcp endpoint for GET/POST).
"""

import contextlib
import json
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Sequence
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import TextContent, Tool
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
from starlette.requests import Request
import uvicorn

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email-sender-mcp")

EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

if not EMAIL_ACCOUNT or not EMAIL_PASSWORD:
    logger.error("Missing EMAIL_ACCOUNT or EMAIL_PASSWORD")
    raise ValueError("Set EMAIL_ACCOUNT and EMAIL_PASSWORD in .env")

mcp_server = Server("email-sender-mcp")


def send_email_internal(receiver_email: str, subject: str, body: str) -> dict:
    """Internal email send helper."""
    try:
        message = MIMEMultipart()
        message["From"] = EMAIL_ACCOUNT
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain", "utf-8"))

        logger.info("Sending email to %s...", receiver_email)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        server.send_message(message)
        server.quit()

        logger.info("Email sent to %s", receiver_email)
        return {"success": True, "message": f"Email sent to {receiver_email}"}

    except Exception as e:
        error_msg = f"Send failed: {str(e)}"
        logger.error("%s", error_msg)
        return {"success": False, "error": error_msg}


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="send_email",
            description="Send custom email",
            inputSchema={
                "type": "object",
                "properties": {
                    "receiver_email": {"type": "string", "description": "Recipient email"},
                    "subject": {"type": "string", "description": "Subject"},
                    "body": {"type": "string", "description": "Body"},
                },
                "required": ["receiver_email", "subject", "body"],
            },
        ),
        Tool(
            name="send_halloween_invitation",
            description="Send Halloween invitation email",
            inputSchema={
                "type": "object",
                "properties": {
                    "receiver_email": {"type": "string", "description": "Recipient email"},
                },
                "required": ["receiver_email"],
            },
        ),
        Tool(
            name="send_system_alert",
            description="Send system alert email",
            inputSchema={
                "type": "object",
                "properties": {
                    "receiver_email": {"type": "string", "description": "Recipient email"},
                },
                "required": ["receiver_email"],
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """Execute tool by name."""
    logger.info("Tool call: %s", name)
    logger.info("Arguments: %s", arguments)

    try:
        if name == "send_email":
            result = send_email_internal(
                arguments["receiver_email"],
                arguments["subject"],
                arguments["body"],
            )
        elif name == "send_halloween_invitation":
            result = send_email_internal(
                arguments["receiver_email"],
                "Halloween Invitation",
                "Hi! You are invited to our Halloween party.",
            )
        elif name == "send_system_alert":
            result = send_email_internal(
                arguments["receiver_email"],
                "System login alert",
                "This is an automated system alert.",
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

        logger.info("Tool result: %s", result)
        return [
            TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2),
            )
        ]

    except Exception as e:
        logger.error("Tool error: %s", e)
        return [
            TextContent(
                type="text",
                text=json.dumps(
                    {"success": False, "error": str(e)},
                    ensure_ascii=False,
                ),
            )
        ]


# Streamable HTTP: stateless mode (one transport per request, suitable for Cloud Run)
session_manager = StreamableHTTPSessionManager(
    mcp_server,
    stateless=True,
    json_response=False,
)


async def streamable_asgi_app(scope, receive, send):
    """ASGI app that forwards to Streamable HTTP session manager (no StreamableHTTPASGIApp in mcp 1.26)."""
    await session_manager.handle_request(scope, receive, send)


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    """Run session manager for the app lifetime."""
    async with session_manager.run():
        logger.info("StreamableHTTP session manager started")
        yield
        logger.info("StreamableHTTP session manager stopped")


async def handle_health(request: Request):
    """Health check."""
    return JSONResponse(
        {
            "status": "healthy",
            "service": "email-sender-mcp",
            "version": "1.0.0",
            "transport": "streamable-http",
            "email_account": EMAIL_ACCOUNT,
        }
    )


app = Starlette(
    debug=True,
    routes=[
        Route("/health", handle_health, methods=["GET"]),
        Mount("/mcp", streamable_asgi_app),
    ],
    lifespan=lifespan,
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    logger.info("Starting MCP Email Sender Server on port %s (Streamable HTTP)", port)
    logger.info("Email account: %s", EMAIL_ACCOUNT)
    logger.info("Endpoints: /health, /mcp (GET/POST)")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
