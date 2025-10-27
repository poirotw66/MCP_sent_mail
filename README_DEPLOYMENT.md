# MCP Email Sender - 部署指南

## 📋 前置需求

1. **Google Cloud Platform 帳號**
2. **安裝 gcloud CLI**
   ```bash
   # macOS
   brew install --cask google-cloud-sdk
   
   # 或從官網下載
   # https://cloud.google.com/sdk/docs/install
   ```

3. **Docker** (本地測試用)

## 🔐 環境變數設定

在 `.env` 文件中設定：
```env
EMAIL_ACCOUNT=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

## 🏗️ 本地測試

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 測試 MCP Server
```bash
python server.py
```

### 3. Docker 本地測試
```bash
# 建置映像
docker build -t email-sender-mcp .

# 執行容器
docker run -p 8080:8080 --env-file .env email-sender-mcp
```

## ☁️ 部署到 Google Cloud Run

### 方法 1: 使用部署腳本

1. **修改 `deploy.sh`**
   ```bash
   # 編輯 deploy.sh，替換：
   PROJECT_ID="your-project-id"
   ```

2. **設定環境變數**
   ```bash
   export EMAIL_ACCOUNT="your-email@gmail.com"
   export EMAIL_PASSWORD="your-app-password"
   ```

3. **執行部署**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

### 方法 2: 手動部署

1. **登入 GCP**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **部署到 Cloud Run**
   ```bash
   gcloud run deploy email-sender-mcp \
     --source . \
     --platform managed \
     --region asia-east1 \
     --allow-unauthenticated \
     --set-env-vars EMAIL_ACCOUNT=your-email@gmail.com,EMAIL_PASSWORD=your-password \
     --port 8080
   ```

### 方法 3: 使用 Cloud Build

```bash
gcloud builds submit --config cloudbuild.yaml
```

## 🧪 測試部署的服務

部署完成後，您會獲得一個 URL，例如：
```
https://email-sender-mcp-xxxxx-xx.a.run.app
```

## 📊 MCP Server 工具

此 MCP Server 提供以下工具：

1. **send_email** - 發送自訂郵件
2. **send_halloween_invitation** - 發送萬聖節邀請（預設模板）
3. **send_system_alert** - 發送系統警示郵件（預設模板）

## 🔒 安全性建議

1. **不要將 `.env` 提交到 Git**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **使用 Secret Manager**（建議用於生產環境）
   ```bash
   # 創建 secret
   echo -n "your-password" | gcloud secrets create email-password --data-file=-
   
   # 在 Cloud Run 中使用
   gcloud run deploy email-sender-mcp \
     --set-secrets=EMAIL_PASSWORD=email-password:latest
   ```

3. **限制訪問權限**
   - 考慮設定 `--no-allow-unauthenticated` 並使用 IAM 控制訪問

## 📝 監控與日誌

查看服務日誌：
```bash
gcloud run services logs read email-sender-mcp --region asia-east1
```

查看服務狀態：
```bash
gcloud run services describe email-sender-mcp --region asia-east1
```

## 🛠️ 故障排除

### 問題：SMTP 認證失敗
- 確認使用的是 Gmail 應用程式密碼，而非帳號密碼
- 檢查環境變數是否正確設定

### 問題：容器啟動失敗
- 檢查 Cloud Run 日誌
- 確認 Dockerfile 中的指令正確

### 問題：連線超時
- 調整 Cloud Run 的超時設定（預設 300 秒）
- 檢查 SMTP 連線是否被防火牆阻擋

## 🔄 更新部署

```bash
# 重新部署最新程式碼
gcloud run deploy email-sender-mcp --source . --region asia-east1
```

## 💰 費用估算

Google Cloud Run 提供：
- 每月 2 百萬次請求免費
- 每月 360,000 GB-秒的記憶體免費
- 每月 180,000 vCPU-秒的 CPU 免費

一般小型應用完全在免費額度內。

## 📞 支援

如有問題，請查看：
- [Google Cloud Run 文檔](https://cloud.google.com/run/docs)
- [MCP 文檔](https://modelcontextprotocol.io/)
