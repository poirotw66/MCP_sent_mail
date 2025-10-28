#!/usr/bin/env python3
"""
MCP Server for Email Sending Service
使用 SSE (Server-Sent Events) 傳輸協議
"""

import asyncio
import json
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Any, Sequence
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import TextContent, Tool
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse, Response
from starlette.requests import Request
import uvicorn

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("email-sender-mcp")

# 郵件配置
EMAIL_ACCOUNT = os.getenv('EMAIL_ACCOUNT')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

if not EMAIL_ACCOUNT or not EMAIL_PASSWORD:
    logger.error("❌ 錯誤：未設定 EMAIL_ACCOUNT 或 EMAIL_PASSWORD")
    raise ValueError("請在 .env 文件中設定 EMAIL_ACCOUNT 和 EMAIL_PASSWORD")

# 創建 MCP Server
mcp_server = Server("email-sender-mcp")

def send_email_internal(receiver_email: str, subject: str, body: str) -> dict:
    """內部郵件發送函數"""
    try:
        message = MIMEMultipart()
        message['From'] = EMAIL_ACCOUNT
        message['To'] = receiver_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain', 'utf-8'))
        
        logger.info(f"📧 正在發送郵件到 {receiver_email}...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        server.send_message(message)
        server.quit()
        
        logger.info(f"✅ 郵件已成功發送至 {receiver_email}")
        return {"success": True, "message": f"郵件已成功發送至 {receiver_email}"}
        
    except Exception as e:
        error_msg = f"發送郵件時發生錯誤: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用的工具"""
    return [
        Tool(
            name="send_email",
            description="發送自訂郵件",
            inputSchema={
                "type": "object",
                "properties": {
                    "receiver_email": {"type": "string", "description": "收件者郵件地址"},
                    "subject": {"type": "string", "description": "郵件主旨"},
                    "body": {"type": "string", "description": "郵件內容"}
                },
                "required": ["receiver_email", "subject", "body"]
            }
        ),
        Tool(
            name="send_halloween_invitation",
            description="發送萬聖節邀請郵件",
            inputSchema={
                "type": "object",
                "properties": {
                    "receiver_email": {"type": "string", "description": "收件者郵件地址"}
                },
                "required": ["receiver_email"]
            }
        ),
        Tool(
            name="send_system_alert",
            description="發送系統異常警示郵件",
            inputSchema={
                "type": "object",
                "properties": {
                    "receiver_email": {"type": "string", "description": "收件者郵件地址"}
                },
                "required": ["receiver_email"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """執行工具"""
    logger.info(f"🔧 工具調用: {name}")
    logger.info(f"📝 參數: {arguments}")
    
    try:
        if name == "send_email":
            result = send_email_internal(arguments["receiver_email"], arguments["subject"], arguments["body"])
        elif name == "send_halloween_invitation":
            result = send_email_internal(
                arguments["receiver_email"],
                "萬聖節邀請 🎃👻",
                "嗨！娜娜子姊姊～\n\n萬聖節快到了！想邀請您一起去路上玩，不給糖就搗蛋！🍬\n\n期待您的回覆！"
            )
        elif name == "send_system_alert":
            result = send_email_internal(
                arguments["receiver_email"],
                "【1399】AI 客服通知 – 系統登入異常警示",
                # "您好：\n\n這封信由 1399 AI 客服系統 自動寄出（請勿直接回覆）。\n\n【通知摘要】\n．事件/工單編號：T20251027-0412\n．主旨/類別：系統登入異常 / 平台監控\n\n—\n1399 AI 客服系統"
    """您好：\n\n這封信由 1399 AI 客服系統 自動寄出（請勿直接回覆）。\n\n【通知摘要】\n\n．事件/工單編號：T20251027-0412\n．主旨/類別：系統登入異常 / 平台監控\n．目前狀態：待處理（Pending）\n．發生/更新時間：2025/10/27 17:25\n．客戶/單位：國泰金控 – 新技術研究小組（CATHAY-DT001）\n\n【相關內容】\n\n在 2025/10/27 17:24，AI 監控系統偵測到多次登入失敗紀錄（5 次以上）\n來源 IP：203.75.23.48\n帳號：itr_admin\n系統：CRM Portal\n目前暫未造成服務中斷，但建議檢查是否有暴力破解或帳號異常行為。\n\n【需要您執行】\n\n1️⃣ 請登入監控平台確認該帳號登入紀錄。\n2️⃣ 若為異常登入，請立即凍結該帳號並更改密碼。\n3️⃣ 完成後回報至 AI 客服工單系統（工單號：T20251027-0412）。\n\n更多詳情請前往：\n🔗 1399 客服管理平台\n\n—\n1399 AI 客服系統\n聯絡窗口：王阿明（it.support@1399-ai.example.com / 分機 1399）\n\n機密聲明：\n本郵件含有機密資訊，僅限指定收件人閱讀。\n未經授權，請勿轉寄、揭露或散布本郵件內容。
    """
            )
        else:
            raise ValueError(f"未知的工具: {name}")
        
        logger.info(f"✅ 工具執行結果: {result}")
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
    except Exception as e:
        logger.error(f"❌ 執行工具時發生錯誤: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))]

# 創建 SSE transport - 指定 POST 端點
sse_transport = SseServerTransport("/messages")

async def handle_health(request: Request):
    """健康檢查"""
    return JSONResponse({
        "status": "healthy",
        "service": "email-sender-mcp",
        "version": "1.0.0",
        "email_account": EMAIL_ACCOUNT
    })

async def handle_sse_connection(scope, receive, send):
    """
    處理 SSE 連線
    connect_sse 是一個 async context manager，會 yield (read_stream, write_stream)
    我們需要用這些 streams 來運行 MCP server
    """
    logger.info("📡 New SSE connection request")
    
    try:
        # connect_sse 會建立 SSE 連線並返回 streams
        async with sse_transport.connect_sse(scope, receive, send) as (read_stream, write_stream):
            logger.info("✅ SSE streams established, starting MCP server")
            
            # 使用這些 streams 運行 MCP server
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options()
            )
            
            logger.info("🔌 MCP server session ended")
    except Exception as e:
        logger.error(f"❌ SSE Error: {e}", exc_info=True)
        raise

# 創建一個自定義的 Starlette 應用來處理 ASGI 路由
class CustomStarlette(Starlette):
    """自定義 Starlette 應用，支持原生 ASGI 端點"""
    
    async def __call__(self, scope, receive, send):
        """攔截特定路徑並直接調用 ASGI 處理器"""
        path = scope.get("path", "")
        
        # 直接處理 SSE 端點
        if path == "/sse" or path == "/sse/":
            await handle_sse_connection(scope, receive, send)
            return
        
        # 直接處理 Messages 端點
        if path == "/messages":
            await sse_transport.handle_post_message(scope, receive, send)
            return
        
        # 其他路由交給 Starlette 處理
        await super().__call__(scope, receive, send)

# 創建 Starlette 應用
app = CustomStarlette(
    debug=True,
    routes=[
        Route("/health", handle_health, methods=["GET"]),
    ]
)

@app.on_event("startup")
async def startup():
    """應用啟動"""
    logger.info("🚀 Application starting")
    logger.info(f"📧 Email Account: {EMAIL_ACCOUNT}")
    logger.info("📍 Endpoints:")
    logger.info("   - Health: /health")
    logger.info("   - SSE: /sse")
    logger.info("   - Messages: /messages")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    logger.info(f"🚀 Starting MCP Email Sender Server on port {port}")
    logger.info(f"📧 Email Account: {EMAIL_ACCOUNT}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
