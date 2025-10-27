#!/usr/bin/env python3
"""
MCP Server for Email Sending Service
使用 SSE (Server-Sent Events) 傳輸協議 via HTTP
"""

import asyncio
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Any
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
import uvicorn

# 載入環境變數
from dotenv import load_dotenv
load_dotenv()

# 建立 MCP server 實例
mcp_server = Server("email-sender")


def send_email_internal(receiver_email: str, subject: str, body: str, attachment_path: str = None) -> dict:
    """
    內部郵件發送函數
    
    Args:
        receiver_email: 收件者郵件地址
        subject: 郵件主旨
        body: 郵件內容
        attachment_path: 附件路徑（可選）
    
    Returns:
        dict: 包含 success 和 message 的結果
    """
    sender_email = os.getenv('EMAIL_ACCOUNT')
    sender_password = os.getenv('EMAIL_PASSWORD')
    
    if not sender_email or not sender_password:
        return {
            "success": False,
            "message": "郵件帳號或密碼未在環境變數中設定"
        }
    
    try:
        # 建立郵件物件
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        
        # 加入郵件內容
        message.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 如果有附件，加入附件
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            filename = os.path.basename(attachment_path)
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            message.attach(part)
        
        # 連接到 Gmail SMTP 伺服器
        server_smtp = smtplib.SMTP('smtp.gmail.com', 587)
        server_smtp.starttls()
        
        # 登入
        server_smtp.login(sender_email, sender_password)
        
        # 發送郵件
        server_smtp.send_message(message)
        
        # 關閉連接
        server_smtp.quit()
        
        return {
            "success": True,
            "message": f"郵件已成功發送至 {receiver_email}"
        }
        
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": "SMTP 認證失敗，請檢查郵件地址和密碼"
        }
    except smtplib.SMTPException as e:
        return {
            "success": False,
            "message": f"發送郵件時發生 SMTP 錯誤: {str(e)}"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "message": "找不到指定的附件檔案"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"發生未預期的錯誤: {str(e)}"
        }


@mcp_server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    列出可用的工具
    """
    return [
        types.Tool(
            name="send_email",
            description="發送電子郵件給指定收件者。支援自訂主旨、內容和附件。",
            inputSchema={
                "type": "object",
                "properties": {
                    "receiver_email": {
                        "type": "string",
                        "description": "收件者的郵件地址"
                    },
                    "subject": {
                        "type": "string",
                        "description": "郵件主旨"
                    },
                    "body": {
                        "type": "string",
                        "description": "郵件內容"
                    },
                    "attachment_path": {
                        "type": "string",
                        "description": "附件檔案路徑（可選）"
                    }
                },
                "required": ["receiver_email", "subject", "body"]
            }
        ),
        types.Tool(
            name="send_halloween_invitation",
            description="發送萬聖節邀請郵件給娜娜子姊姊（使用預設模板）",
            inputSchema={
                "type": "object",
                "properties": {
                    "receiver_email": {
                        "type": "string",
                        "description": "收件者的郵件地址"
                    }
                },
                "required": ["receiver_email"]
            }
        ),
        types.Tool(
            name="send_system_alert",
            description="發送系統異常警示郵件（使用預設的 AI 客服通知模板）",
            inputSchema={
                "type": "object",
                "properties": {
                    "receiver_email": {
                        "type": "string",
                        "description": "收件者的郵件地址"
                    }
                },
                "required": ["receiver_email"]
            }
        )
    ]


@mcp_server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    處理工具調用
    """
    if not arguments:
        raise ValueError("缺少必要參數")
    
    if name == "send_email":
        receiver_email = arguments.get("receiver_email")
        subject = arguments.get("subject")
        body = arguments.get("body")
        attachment_path = arguments.get("attachment_path")
        
        if not all([receiver_email, subject, body]):
            raise ValueError("receiver_email、subject 和 body 是必要參數")
        
        result = send_email_internal(receiver_email, subject, body, attachment_path)
        
        return [
            types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )
        ]
    
    elif name == "send_halloween_invitation":
        receiver_email = arguments.get("receiver_email")
        
        if not receiver_email:
            raise ValueError("receiver_email 是必要參數")
        
        subject = "萬聖節邀請 🎃👻"
        body = """親愛的娜娜子姊姊：

您好！

萬聖節快到了，我想邀請您一起去路上玩，體驗萬聖節的歡樂氣氛！
不知道您有沒有興趣一起參加呢？

期待您的回覆！

祝好
"""
        
        result = send_email_internal(receiver_email, subject, body)
        
        return [
            types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )
        ]
    
    elif name == "send_system_alert":
        receiver_email = arguments.get("receiver_email")
        
        if not receiver_email:
            raise ValueError("receiver_email 是必要參數")
        
        subject = "【1399】AI 客服通知 – 系統登入異常警示"
        body = """您好：

這封信由 1399 AI 客服系統 自動寄出（請勿直接回覆）。

【通知摘要】

．事件/工單編號：T20251027-0412
．主旨/類別：系統登入異常 / 平台監控
．目前狀態：待處理（Pending）
．發生/更新時間：2025/10/27 17:25
．客戶/單位：國泰金控 – 新技術研究小組（CATHAY-DT001）

【相關內容】

在 2025/10/27 17:24，AI 監控系統偵測到多次登入失敗紀錄（5 次以上）
來源 IP：203.75.23.48
帳號：itr_admin
系統：CRM Portal
目前暫未造成服務中斷，但建議檢查是否有暴力破解或帳號異常行為。

【需要您執行】

1️⃣ 請登入監控平台確認該帳號登入紀錄。
2️⃣ 若為異常登入，請立即凍結該帳號並更改密碼。
3️⃣ 完成後回報至 AI 客服工單系統（工單號：T20251027-0412）。

更多詳情請前往：
🔗 1399 客服管理平台

—
1399 AI 客服系統
聯絡窗口：王阿明（it.support@1399-ai.example.com / 分機 1399）

機密聲明：
本郵件含有機密資訊，僅限指定收件人閱讀。
未經授權，請勿轉寄、揭露或散布本郵件內容。
"""
        
        result = send_email_internal(receiver_email, subject, body)
        
        return [
            types.TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )
        ]
    
    else:
        raise ValueError(f"未知的工具: {name}")


async def handle_sse(request):
    """
    處理 SSE 連接
    """
    async with SseServerTransport("/messages") as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="email-sender",
                server_version="1.0.0",
                capabilities=mcp_server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
    return Response()


async def handle_messages(request):
    """
    處理 MCP 消息端點
    """
    return Response()


# 建立 Starlette 應用
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
        Route("/", endpoint=lambda request: Response("MCP Email Sender Server is running!", media_type="text/plain")),
        Route("/health", endpoint=lambda request: Response("OK", media_type="text/plain")),
    ],
)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
