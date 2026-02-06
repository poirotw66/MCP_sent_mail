#!/usr/bin/env python3
"""
Connect to MCP Server via Streamable HTTP and send system alert email.
"""
import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def send_system_alert():
    """Connect to MCP Server and send system alert email."""
    # server_url = "http://localhost:8080/mcp"
    server_url = "https://email-sender-mcp-jt7pjdeeoa-de.a.run.app/mcp"

    print(f"Connecting to MCP Server: {server_url}")

    try:
        async with streamable_http_client(server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("Connected to MCP Server")

                tools_result = await session.list_tools()
                print("\nAvailable tools:")
                for tool in tools_result.tools:
                    print(f"   - {tool.name}: {tool.description}")

                print("\nSending system alert email to poirotw66@gmail.com...")
                
                result = await session.call_tool(
                    "send_system_alert",
                    arguments={
                        "receiver_email": "poirotw66@gmail.com"
                    }
                )
                
                print("\nResult:")
                for content in result.content:
                    if hasattr(content, "text"):
                        response = json.loads(content.text)
                        print(json.dumps(response, indent=2, ensure_ascii=False))
                        if response.get("success"):
                            print("\nEmail sent successfully.")
                        else:
                            print(f"\nSend failed: {response.get('error')}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 70)
    print("MCP Client test - send system alert email (Streamable HTTP)")
    print("=" * 70)
    asyncio.run(send_system_alert())
    print("=" * 70)
