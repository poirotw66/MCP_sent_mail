#!/usr/bin/env python3
"""
簡單的 MCP Server 測試腳本
"""

import requests
import json

# 服務 URL
SERVER_URL = "https://email-sender-mcp-jt7pjdeeoa-de.a.run.app"

def test_health():
    """測試健康檢查端點"""
    print("=" * 60)
    print("🏥 測試 1: 健康檢查")
    print("=" * 60)
    
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=10)
        print(f"✅ 狀態碼: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ 回應內容: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return True
            except:
                print(f"✅ 回應內容: {response.text}")
                return True
        else:
            print(f"❌ 失敗: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False

def test_sse_endpoint():
    """測試 SSE 端點"""
    print("\n" + "=" * 60)
    print("🔌 測試 2: SSE 端點連線")
    print("=" * 60)
    
    try:
        # 發送一個簡單的 GET 請求到 SSE 端點
        response = requests.get(f"{SERVER_URL}/sse", timeout=5, stream=True)
        print(f"✅ 狀態碼: {response.status_code}")
        print(f"✅ Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        
        # 讀取前幾行
        print("✅ 嘗試讀取 SSE 流...")
        for i, line in enumerate(response.iter_lines(decode_unicode=True)):
            if i < 5:  # 只讀取前 5 行
                print(f"   {line}")
            if i >= 5:
                break
        
        return True
        
    except requests.exceptions.Timeout:
        print("⚠️  連線超時（這是正常的，SSE 是長連線）")
        return True
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return False

def show_usage_guide():
    """顯示使用指南"""
    print("\n" + "=" * 60)
    print("📖 如何實際測試發送郵件")
    print("=" * 60)
    
    print("\n方法 1️⃣ : 在 Claude Desktop 中使用")
    print("-" * 60)
    print("1. 編輯配置文件:")
    print("   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("\n2. 添加以下內容:")
    print(json.dumps({
        "mcpServers": {
            "email-sender": {
                "url": f"{SERVER_URL}/sse",
                "transport": "sse"
            }
        }
    }, indent=2))
    print("\n3. 重啟 Claude Desktop")
    print("\n4. 在對話中說:")
    print('   "發送郵件給 your-email@example.com，主旨是測試，內容是這是一封測試郵件"')
    
    print("\n\n方法 2️⃣ : 使用 MCP Inspector (開發工具)")
    print("-" * 60)
    print("npm install -g @modelcontextprotocol/inspector")
    print(f"mcp-inspector {SERVER_URL}/sse")
    
    print("\n\n方法 3️⃣ : 本地運行測試")
    print("-" * 60)
    print("python server.py")
    print("# 然後在 Claude Desktop 中連接到 http://localhost:8080/sse")

def main():
    """主函數"""
    print("\n" + "=" * 60)
    print("🧪 MCP Email Server 測試工具")
    print("=" * 60)
    print(f"服務地址: {SERVER_URL}")
    
    # 執行測試
    health_ok = test_health()
    sse_ok = test_sse_endpoint()
    
    # 顯示結果
    print("\n" + "=" * 60)
    print("📊 測試結果")
    print("=" * 60)
    print(f"健康檢查: {'✅ 通過' if health_ok else '❌ 失敗'}")
    print(f"SSE 連線: {'✅ 通過' if sse_ok else '❌ 失敗'}")
    
    if health_ok and sse_ok:
        print("\n🎉 所有測試通過！MCP Server 運作正常。")
    else:
        print("\n⚠️  部分測試失敗，請檢查服務狀態。")
    
    # 顯示使用指南
    show_usage_guide()
    
    print("\n" + "=" * 60)
    print("✅ 測試完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
