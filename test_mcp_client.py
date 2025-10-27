#!/usr/bin/env python3
"""
MCP Server 測試客戶端
直接測試部署在 Cloud Run 上的 MCP Server
"""

import httpx
import json
import asyncio


class MCPClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def test_health(self):
        """測試健康檢查端點"""
        print("\n🏥 測試健康檢查...")
        try:
            response = await self.client.get(f"{self.base_url}/health")
            print(f"✅ 狀態碼: {response.status_code}")
            print(f"✅ 回應: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ 錯誤: {e}")
            return False
    
    async def test_sse_connection(self):
        """測試 SSE 連線"""
        print("\n🔌 測試 SSE 連線...")
        try:
            async with self.client.stream('GET', f"{self.base_url}/sse") as response:
                print(f"✅ 連線成功，狀態碼: {response.status_code}")
                print(f"✅ Content-Type: {response.headers.get('content-type')}")
                
                # 讀取前幾行來確認連線
                lines_read = 0
                async for line in response.aiter_lines():
                    if line:
                        print(f"   📨 收到: {line[:100]}...")
                        lines_read += 1
                        if lines_read >= 3:  # 只讀取前幾行
                            break
                
                print("✅ SSE 連線測試成功")
                return True
        except Exception as e:
            print(f"❌ 錯誤: {e}")
            return False
    
    async def send_test_email(self, receiver_email):
        """
        發送測試郵件
        注意：這需要 MCP 協議的完整實現
        這裡只是示範如何構建請求
        """
        print(f"\n📧 準備發送測試郵件到 {receiver_email}...")
        
        # MCP 請求格式
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "send_email",
                "arguments": {
                    "receiver_email": receiver_email,
                    "subject": "MCP Server 測試郵件",
                    "body": "這是一封來自 MCP Server 的測試郵件。\n\n如果您收到這封郵件，代表 MCP Server 運作正常！"
                }
            }
        }
        
        print(f"📤 請求內容: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
        print("\n⚠️  注意：直接 HTTP POST 需要完整的 MCP 協議實現")
        print("   建議使用 MCP 客戶端（如 Claude Desktop）來測試工具調用")
        
        return request_data
    
    async def close(self):
        """關閉客戶端"""
        await self.client.aclose()


async def main():
    print("=" * 60)
    print("🧪 MCP Email Server 測試")
    print("=" * 60)
    
    # Cloud Run 上的服務 URL
    server_url = "https://email-sender-mcp-jt7pjdeeoa-de.a.run.app"
    
    print(f"\n🌐 目標服務: {server_url}")
    
    client = MCPClient(server_url)
    
    try:
        # 測試 1: 健康檢查
        health_ok = await client.test_health()
        
        # 測試 2: SSE 連線
        if health_ok:
            sse_ok = await client.test_sse_connection()
        
        # 測試 3: 顯示如何發送郵件（需要 MCP 客戶端）
        print("\n" + "=" * 60)
        print("📬 如何發送測試郵件")
        print("=" * 60)
        
        test_email = input("\n請輸入測試郵件地址（或按 Enter 跳過）: ").strip()
        
        if test_email:
            request_data = await client.send_test_email(test_email)
            
            print("\n💡 要真正發送郵件，請使用以下方式之一：")
            print("\n1️⃣  使用 Claude Desktop:")
            print("   - 在 claude_desktop_config.json 中添加此 MCP Server")
            print("   - 重啟 Claude Desktop")
            print(f"   - 說：「發送郵件給 {test_email}，主旨是測試，內容是這是測試郵件」")
            
            print("\n2️⃣  使用 MCP Inspector:")
            print("   npm install -g @modelcontextprotocol/inspector")
            print(f"   mcp-inspector {server_url}/sse")
            
            print("\n3️⃣  使用本地 server.py:")
            print("   python server.py")
            print("   # 然後連接到 http://localhost:8080/sse")
        
        print("\n" + "=" * 60)
        print("✅ 測試完成！")
        print("=" * 60)
        
        print("\n📊 測試結果摘要：")
        print(f"   健康檢查: {'✅ 通過' if health_ok else '❌ 失敗'}")
        print(f"   SSE 連線: {'✅ 通過' if sse_ok else '❌ 失敗'}")
        
        if health_ok and sse_ok:
            print("\n🎉 MCP Server 運行正常！")
            print("\n🔗 在 Claude Desktop 中使用此 Server:")
            print("   編輯 ~/Library/Application Support/Claude/claude_desktop_config.json")
            print("   添加:")
            print('   {')
            print('     "mcpServers": {')
            print('       "email-sender": {')
            print(f'         "url": "{server_url}/sse",')
            print('         "transport": "sse"')
            print('       }')
            print('     }')
            print('   }')
        
    except KeyboardInterrupt:
        print("\n\n⚠️  測試被中斷")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
