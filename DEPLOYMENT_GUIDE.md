# 📧 MCP Email Sender - 部署指南

本文檔詳細說明如何將 MCP Email Sender Server 部署到 Google Cloud Run，以及如何連接和使用這個服務。

---

## 📋 目錄

1. [環境準備](#環境準備)
2. [本地測試](#本地測試)
3. [部署到 Google Cloud Run](#部署到-google-cloud-run)
4. [MCP 客戶端連線方式](#mcp-客戶端連線方式)
5. [故障排除](#故障排除)

---

## 🛠 環境準備

### 1. 安裝必要工具

```bash
# 安裝 Google Cloud SDK
# macOS
brew install google-cloud-sdk

# 或訪問: https://cloud.google.com/sdk/docs/install
```

### 2. 設定 GCP 專案

```bash
# 登入 Google Cloud
gcloud auth login

# 設定專案 ID
gcloud config set project itr-aimasteryhub-lab

# 啟用必要的 API
gcloud services enable containerregistry.googleapis.com
gcloud services enable run.googleapis.com
```

### 3. 設定 Gmail 應用程式密碼

1. 前往 [Google Account Settings](https://myaccount.google.com/)
2. 選擇「安全性」→「兩步驟驗證」→「應用程式密碼」
3. 選擇「郵件」和「其他（自訂名稱）」
4. 生成密碼（格式：`xxxx xxxx xxxx xxxx`，**實際使用時需移除空格**）

### 4. 建立 `.env` 檔案

在專案根目錄建立 `.env` 檔案：

```bash
# .env
EMAIL_ACCOUNT=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-without-spaces
```

**重要**：
- ✅ 正確：`EMAIL_PASSWORD="dyzb fvnu iaar tzca"`（有空格）

---

## 🧪 本地測試

### 1. 安裝 Python 依賴

```bash
pip install -r requirements.txt
```

### 2. 啟動本地伺服器

```bash
python server.py
```

輸出應該顯示：
```
Starting MCP Email Sender Server on port 8080 (Streamable HTTP)
Email account: your-email@gmail.com
Endpoints: /health, /mcp (GET/POST)
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### 3. 測試健康檢查

```bash
curl http://localhost:8080/health
```

預期回應：
```json
{
  "status": "healthy",
  "service": "email-sender-mcp",
  "version": "1.0.0",
  "email_account": "your-email@gmail.com"
}
```

### 4. 測試 MCP 連線和郵件發送

```bash
python test_send_email.py
```

預期輸出：
```
Connected to MCP Server

Available tools:
   - send_email: ...
   - send_halloween_invitation: ...
   - send_system_alert: ...

Sending system alert email to poirotw66@gmail.com...

Result:
{ "success": true, "message": "Email sent to ..." }
Email sent successfully.
```

---

## 🚀 部署到 Google Cloud Run

### 方法一：使用自動化部署腳本（推薦）

```bash
# 確保 .env 檔案存在且格式正確
cat .env

# 執行部署腳本
chmod +x deploy.sh
./deploy.sh
```

部署腳本會自動執行以下步驟：
1. ✅ 讀取 `.env` 檔案並驗證環境變數
2. ✅ 建置 Docker 映像
3. ✅ 推送映像到 Google Container Registry
4. ✅ 部署到 Cloud Run 並設定環境變數
5. ✅ 顯示服務 URL

### 方法二：手動部署步驟

#### 步驟 1: 建置 Docker 映像

```bash
# 設定變數
PROJECT_ID="itr-aimasteryhub-lab"
SERVICE_NAME="email-sender-mcp"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

# 建置映像
docker build -t $IMAGE_NAME:latest .
```

#### 步驟 2: 推送到 GCR

```bash
# 配置 Docker 認證
gcloud auth configure-docker

# 推送映像
docker push $IMAGE_NAME:latest
```

#### 步驟 3: 部署到 Cloud Run

```bash
# 讀取環境變數（確保密碼沒有空格）
EMAIL_ACCOUNT="itr.notify.2025@gmail.com"
EMAIL_PASSWORD="dyzbfvnuiaartzca"  # 移除所有空格

# 部署服務
gcloud run deploy email-sender-mcp \
  --image=$IMAGE_NAME:latest \
  --platform=managed \
  --region=asia-east1 \
  --allow-unauthenticated \
  --set-env-vars="EMAIL_ACCOUNT=$EMAIL_ACCOUNT,EMAIL_PASSWORD=$EMAIL_PASSWORD" \
  --port=8080 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --project=$PROJECT_ID
```

#### 步驟 4: 獲取服務 URL

```bash
gcloud run services describe email-sender-mcp \
  --region=asia-east1 \
  --project=$PROJECT_ID \
  --format='value(status.url)'
```

輸出範例：
```
https://email-sender-mcp-jt7pjdeeoa-de.a.run.app
```

### 更新環境變數（部署後）

如果需要更新環境變數而不重新部署映像：

```bash
gcloud run services update email-sender-mcp \
  --region=asia-east1 \
  --project=itr-aimasteryhub-lab \
  --set-env-vars="EMAIL_ACCOUNT=itr.notify.2025@gmail.com,EMAIL_PASSWORD=dyzbfvnuiaartzca"
```

---

## 🔌 MCP 客戶端連線方式

### Python 客戶端範例

#### 1. 安裝 MCP SDK

```bash
pip install mcp
```

#### 2. 基本連線程式碼

```python
#!/usr/bin/env python3
import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

async def connect_and_send_email():
    # Cloud Run 服務 URL（Streamable HTTP 端點為 /mcp）
    server_url = "https://email-sender-mcp-jt7pjdeeoa-de.a.run.app/mcp"

    async with streamable_http_client(server_url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected to MCP Server")
            
            # 列出可用工具
            tools = await session.list_tools()
            print("\n📋 可用工具:")
            for tool in tools.tools:
                print(f"   - {tool.name}: {tool.description}")
            
            # 調用工具：發送系統警示郵件
            result = await session.call_tool(
                "send_system_alert",
                arguments={"receiver_email": "poirotw66@gmail.com"}
            )
            
            # 解析結果
            for content in result.content:
                if hasattr(content, 'text'):
                    response = json.loads(content.text)
                    print("\n✅ 結果:", json.dumps(response, indent=2, ensure_ascii=False))

# 執行
asyncio.run(connect_and_send_email())
```

#### 3. 發送自訂郵件

```python
result = await session.call_tool(
    "send_email",
    arguments={
        "receiver_email": "recipient@example.com",
        "subject": "測試郵件",
        "body": "這是一封測試郵件的內容。"
    }
)
```

#### 4. 發送萬聖節邀請

```python
result = await session.call_tool(
    "send_halloween_invitation",
    arguments={
        "receiver_email": "friend@example.com"
    }
)
```

### 測試連線

使用專案中的測試腳本：

```bash
# 修改 test_send_email.py 中的 server_url
server_url = "https://your-service-url.a.run.app/mcp"

# 執行測試
python test_send_email.py
```

### cURL 測試（僅健康檢查）

```bash
# 測試健康檢查端點
curl https://email-sender-mcp-jt7pjdeeoa-de.a.run.app/health

# 預期回應
{
  "status": "healthy",
  "service": "email-sender-mcp",
  "version": "1.0.0",
  "email_account": "itr.notify.2025@gmail.com"
}
```

**注意**：`/mcp` 端點為 MCP 協定，不適合用 cURL 測試，請使用 MCP 客戶端（如 `test_send_email.py`）。

---

## 🔍 故障排除

### 問題 1: 認證失敗 (535 錯誤)

**錯誤訊息**：
```
5.7.8 Username and Password not accepted. BadCredentials
```

**解決方案**：

1. **檢查密碼格式**（最常見）：
   ```bash
   # ❌ 錯誤：密碼中有空格
   EMAIL_PASSWORD="dyzb fvnu iaar tzca"
   
   # ✅ 正確：移除所有空格
   EMAIL_PASSWORD="dyzbfvnuiaartzca"
   ```

2. **重新生成應用程式密碼**：
   - Gmail → 安全性 → 兩步驟驗證 → 應用程式密碼
   - 刪除舊密碼，生成新密碼

3. **更新 Cloud Run 環境變數**：
   ```bash
   gcloud run services update email-sender-mcp \
     --region=asia-east1 \
     --set-env-vars="EMAIL_PASSWORD=新密碼無空格"
   ```

4. **驗證環境變數**：
   ```bash
   gcloud run services describe email-sender-mcp \
     --region=asia-east1 \
     --format="value(spec.template.spec.containers[0].env)"
   ```

### 問題 2: 連線逾時

**症狀**：客戶端無法連接到 `/mcp` 端點

**解決方案**：

1. 確認服務 URL 正確：
   ```bash
   gcloud run services describe email-sender-mcp \
     --region=asia-east1 \
     --format='value(status.url)'
   ```

2. 檢查服務狀態：
   ```bash
   gcloud run services list --project=itr-aimasteryhub-lab
   ```

3. 查看日誌：
   ```bash
   gcloud run logs tail email-sender-mcp \
     --region=asia-east1 \
     --project=itr-aimasteryhub-lab
   ```

### 問題 3: Docker 建置失敗

**症狀**：`docker build` 執行失敗

**解決方案**：

1. 確認 Dockerfile 存在且格式正確
2. 確認 `.env` 檔案存在（如果 Dockerfile 中有 `COPY .env .`）
3. 清理 Docker 快取：
   ```bash
   docker system prune -a
   ```

### 問題 4: 工具調用沒有回應

**症狀**：客戶端卡在等待回應

**解決方案**：

1. 檢查伺服器日誌：
   ```bash
   gcloud run logs tail email-sender-mcp --region=asia-east1
   ```

2. 確認工具名稱正確：
   - `send_email`
   - `send_halloween_invitation`
   - `send_system_alert`

3. 確認參數格式正確：
   ```python
   # 正確的參數格式
   arguments={
       "receiver_email": "test@example.com"
   }
   ```

### 問題 5: 本地測試成功但雲端失敗

**可能原因**：環境變數未正確設定到 Cloud Run

**解決方案**：

1. 驗證本地 `.env` 檔案：
   ```bash
   cat .env
   ```

2. 手動設定環境變數到 Cloud Run：
   ```bash
   # 讀取本地 .env（確保密碼無空格）
   source .env
   
   # 更新 Cloud Run
   gcloud run services update email-sender-mcp \
     --region=asia-east1 \
     --update-env-vars EMAIL_ACCOUNT=$EMAIL_ACCOUNT,EMAIL_PASSWORD=$EMAIL_PASSWORD
   ```

---

## 📊 監控和日誌

### 即時日誌

```bash
# 追蹤即時日誌
gcloud run logs tail email-sender-mcp \
  --region=asia-east1 \
  --project=itr-aimasteryhub-lab

# 查看最近的日誌
gcloud run logs read email-sender-mcp \
  --region=asia-east1 \
  --limit=50
```

### 查看服務指標

```bash
# 在 GCP Console 中查看
https://console.cloud.google.com/run/detail/asia-east1/email-sender-mcp/metrics
```

### 測試端點

```bash
# 健康檢查
curl https://your-service-url.a.run.app/health

# 預期回應: {"status": "healthy", ...}
```

---

## 🔐 安全性建議

1. **不要提交 `.env` 到版本控制**：
   ```bash
   # 確保 .gitignore 包含
   echo ".env" >> .gitignore
   ```

2. **定期輪換密碼**：
   - 每 3-6 個月更新 Gmail 應用程式密碼

3. **限制服務存取**（可選）：
   ```bash
   # 移除 --allow-unauthenticated
   # 改用 IAM 認證
   gcloud run services update email-sender-mcp \
     --region=asia-east1 \
     --no-allow-unauthenticated
   ```

4. **使用 Secret Manager**（進階）：
   ```bash
   # 將密碼存儲到 Secret Manager
   echo -n "your-password" | gcloud secrets create email-password \
     --data-file=-
   
   # 在 Cloud Run 中使用
   gcloud run services update email-sender-mcp \
     --region=asia-east1 \
     --update-secrets=EMAIL_PASSWORD=email-password:latest
   ```

---

## 📚 相關資源

- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)

---

## 🎯 快速參考

### 常用命令

```bash
# 部署服務
./deploy.sh

# 查看日誌
gcloud run logs tail email-sender-mcp --region=asia-east1

# 更新環境變數
gcloud run services update email-sender-mcp \
  --region=asia-east1 \
  --set-env-vars="KEY=VALUE"

# 查看服務資訊
gcloud run services describe email-sender-mcp --region=asia-east1

# 刪除服務
gcloud run services delete email-sender-mcp --region=asia-east1
```

### 服務資訊

- **專案 ID**: `itr-aimasteryhub-lab`
- **服務名稱**: `email-sender-mcp`
- **區域**: `asia-east1`
- **端口**: `8080`
- **記憶體**: `512Mi`
- **CPU**: `1`
- **逾時**: `300s`

---

**最後更新**: 2025年10月28日
**版本**: 1.0.0
