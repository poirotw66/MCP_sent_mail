#!/usr/bin/env python3
"""
通過 HTTP/SSE 連接到 MCP Server 並發送系統警示郵件
"""
import asyncio
import json
import httpx
from mcp import ClientSession
from mcp.client.sse import sse_client

async def send_system_alert():
    """連接到 MCP Server 並發送系統警示郵件"""
    
    server_url = "http://localhost:8080/sse"
    
    print(f"🔌 正在連接到 MCP Server: {server_url}")
    
    try:
        # 使用 SSE 客戶端連接
        async with sse_client(server_url) as (read, write):
            async with ClientSession(read, write) as session:
                # 初始化連接
                await session.initialize()
                print("✅ 已成功連接到 MCP Server")
                
                # 列出可用工具
                tools_result = await session.list_tools()
                print(f"\n📋 可用工具:")
                for tool in tools_result.tools:
                    print(f"   - {tool.name}: {tool.description}")
                
                # 發送系統警示郵件
                print(f"\n📧 正在發送系統警示郵件到 poirotw66@gmail.com...")
                
                result = await session.call_tool(
                    "send_system_alert",
                    arguments={
                        "receiver_email": "poirotw66@gmail.com"
                    }
                )
                
                # 顯示結果
                print("\n✅ 發送結果:")
                for content in result.content:
                    if hasattr(content, 'text'):
                        response = json.loads(content.text)
                        print(json.dumps(response, indent=2, ensure_ascii=False))
                        
                        if response.get("success"):
                            print("\n🎉 郵件發送成功！")
                        else:
                            print(f"\n❌ 郵件發送失敗: {response.get('error')}")
    
    except Exception as e:
        print(f"\n❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 70)
    print("🧪 MCP Client 測試 - 發送系統警示郵件")
    print("=" * 70)
    asyncio.run(send_system_alert())
    print("=" * 70)
