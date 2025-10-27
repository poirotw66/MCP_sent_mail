import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv

# 載入 .env 文件
load_dotenv()

def send_email():
    """
    寄送郵件的主程式
    """
    # 取得寄件者資訊（優先從 .env 讀取）
    sender_email = os.getenv('EMAIL_ACCOUNT')
    sender_password = os.getenv('EMAIL_PASSWORD')
    
    # 如果 .env 中沒有設定，則詢問使用者
    if not sender_email:
        sender_email = input("請輸入您的郵件地址: ")
    else:
        print(f"使用郵件帳號: {sender_email}")
    
    if not sender_password:
        sender_password = input("請輸入您的郵件密碼或應用程式密碼: ")
    else:
        print("使用 .env 中的郵件密碼")
    
    # 取得收件者資訊
    receiver_email = input("請輸入收件者郵件地址: ")
    
    # 郵件內容（預設值）
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
聯絡窗口：王阿明（it.support@1399-ai.example.com
 / 分機 1399）

機密聲明：
本郵件含有機密資訊，僅限指定收件人閱讀。
未經授權，請勿轉寄、揭露或散布本郵件內容。
"""
    
    # 詢問是否要附加檔案
 
    try:
        # 建立郵件物件
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        
        # 加入郵件內容
        message.attach(MIMEText(body, 'plain', 'utf-8'))
        # 連接到 Gmail SMTP 伺服器
        print("\n正在連接到郵件伺服器...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # 啟用 TLS 加密
        
        # 登入
        print("正在登入...")
        server.login(sender_email, sender_password)
        
        # 發送郵件
        print("正在發送郵件...")
        server.send_message(message)
        
        # 關閉連接
        server.quit()
        
        print(f"\n✓ 郵件已成功發送至 {receiver_email}！")
        
    except smtplib.SMTPAuthenticationError:
        print("\n✗ 登入失敗！請檢查郵件地址和密碼。")
        print("提示：如果使用 Gmail，可能需要使用「應用程式密碼」而非帳號密碼。")
    except smtplib.SMTPException as e:
        print(f"\n✗ 發送郵件時發生錯誤: {e}")
    except FileNotFoundError:
        print("\n✗ 找不到指定的附件檔案！")
    except Exception as e:
        print(f"\n✗ 發生未預期的錯誤: {e}")

if __name__ == "__main__":
    print("=== Python 郵件發送程式 ===\n")
    send_email()
