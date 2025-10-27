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
    subject = "萬聖節邀請 🎃👻"
    body = """親愛的娜娜子姊姊：

您好！

萬聖節快到了，我想邀請您一起去路上玩，體驗萬聖節的歡樂氣氛！
不知道您有沒有興趣一起參加呢？

期待您的回覆！

祝好
"""
    
    # 詢問是否要附加檔案
    attach_file = input("是否要附加檔案？(y/n): ").lower()
    file_path = None
    if attach_file == 'y':
        file_path = input("請輸入檔案路徑: ")
    
    try:
        # 建立郵件物件
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = receiver_email
        message['Subject'] = subject
        
        # 加入郵件內容
        message.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # 如果有附件，加入附件
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            filename = os.path.basename(file_path)
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            message.attach(part)
        
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
