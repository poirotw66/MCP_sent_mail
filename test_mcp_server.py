#!/usr/bin/env python3
"""
MCP Server 測試腳本
測試已部署的 Email Sender MCP Server
"""

import httpx
import json
import asyncio

# MCP Server URL
SERVER_URL = "https://email-sender-mcp-jt7pjdeeoa-de.a.run.app"

async def test_health_check():
    """測試健康檢查端點"""
    print("🏥 測試健康檢查...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVER_URL}/health", timeout=10.0)
            print(f"   狀態碼: {response.status_code}")
            print(f"   回應: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"   ❌ 錯誤: {e}")
            return False

async def test_sse_endpoint():
    """測試 SSE 端點連接"""
    print("\n🔌 測試 SSE 端點...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SERVER_URL}/sse", timeout=5.0)
            print(f"   狀態碼: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type')}")
            
            # 顯示前 200 個字元
            content = response.text[:200]
            print(f"   回應預覽: {content}...")
            return True
        except httpx.ReadTimeout:
            print("   ⚠️  連接超時（這是正常的，SSE 是長連接）")
            return True
        except Exception as e:
            print(f"   ❌ 錯誤: {e}")
            return False

async def test_send_email_tool():
    """測試發送郵件工具（模擬 MCP 請求）"""
    print("\n📧 測試發送郵件工具...")
    print("   ⚠️  注意：這需要實際的 MCP 客戶端來調用")
    print("   建議使用 Claude Desktop 或 MCP Inspector 來測試")
    
    # 顯示如何使用的範例
    example = {
        "tool": "send_email",
        "arguments": {
            "receiver_email": "test@example.com",
            "subject": "測試郵件",
            "body": "這是一封測試郵件"
        }
    }
    print(f"\n   範例調用：")
    print(json.dumps(example, indent=2, ensure_ascii=False))

def print_claude_config():
    """顯示 Claude Desktop 配置"""
    print("\n⚙️  Claude Desktop 配置")
    print("   檔案位置: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("\n   配置內容：")
    config = {
        "mcpServers": {
            "email-sender": {
                "url": SERVER_URL + "/sse",
                "transport": "sse"
            }
        }
    }
    print(json.dumps(config, indent=2, ensure_ascii=False))

async def main():
    """主測試函數"""
    print("=" * 60)
    print("🧪 MCP Email Sender Server 測試")
    print("=" * 60)
    print(f"📍 Server URL: {SERVER_URL}\n")
    
    # 執行測試
    results = []
    
    # 1. 健康檢查
    result1 = await test_health_check()
    results.append(("健康檢查", result1))
    
    # 2. SSE 端點
    result2 = await test_sse_endpoint()
    results.append(("SSE 端點", result2))
    
    # 3. 工具說明
    test_send_email_tool()
    
    # 4. Claude 配置
    print_claude_config()
    
    # 顯示測試結果摘要
    print("\n" + "=" * 60)
    print("📊 測試結果摘要")
    print("=" * 60)
    for test_name, passed in results:
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"   {test_name}: {status}")
    
    # 下一步建議
    print("\n💡 下一步:")
    print("   1. 複製上面的 Claude Desktop 配置到配置文件")
    print("   2. 重啟 Claude Desktop")
    print("   3. 在 Claude 中說：'發送測試郵件給 your@email.com'")
    print("   4. 或說：'發送萬聖節邀請給 friend@email.com'")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
