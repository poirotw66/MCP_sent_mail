# Email Sender MCP Server

這是一個使用 Model Context Protocol (MCP) 的郵件發送服務，使用 **Streamable HTTP** 傳輸協議，部署在 Google Cloud Run 上。

## ✨ 功能特色

- ✉️ 發送自訂郵件
- 🎃 發送萬聖節邀請郵件（預設模板）
- 🚨 發送系統異常警示郵件（預設模板）
- 📎 支援附件
- 🌐 Streamable HTTP 傳輸協議（單一 `/mcp` 端點）
- ☁️ 部署在 Google Cloud Run

## 🚀 快速開始

### 已部署的服務

**服務 URL**: `https://email-sender-mcp-jt7pjdeeoa-de.a.run.app`

### 測試連線

```bash
# 健康檢查
curl https://email-sender-mcp-jt7pjdeeoa-de.a.run.app/health
```
MCP 端點為 `/mcp`（GET/POST），需使用支援 Streamable HTTP 的 MCP 客戶端連線。

## 📖 使用方式

### 在 Claude Desktop 中使用

1. **編輯 Claude Desktop 配置文件**

   macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   
   Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. **添加 MCP Server 配置**

   ```json
   {
     "mcpServers": {
       "email-sender": {
         "url": "https://email-sender-mcp-jt7pjdeeoa-de.a.run.app/mcp",
         "transport": "streamable-http"
       }
     }
   }
   ```

3. **重啟 Claude Desktop**

4. **開始使用**
   
   在 Claude Desktop 中，您可以直接說：
   - "幫我發送一封郵件給 example@gmail.com"
   - "發送萬聖節邀請給 friend@gmail.com"
   - "發送系統警示郵件給 admin@company.com"

### 在其他 MCP 客戶端中使用

任何支援 MCP over Streamable HTTP 的客戶端都可以連接：

```json
{
  "url": "https://email-sender-mcp-jt7pjdeeoa-de.a.run.app/mcp",
  "transport": "streamable-http"
}
```

### 使用 curl 測試

```bash
# 健康檢查
curl https://email-sender-mcp-jt7pjdeeoa-de.a.run.app/health
```
`/mcp` 為 MCP 協定端點，需以 MCP 客戶端（如 `test_send_email.py`）測試，不適合用 curl 直接呼叫。

## 🛠️ MCP Tools 說明

### 1. `send_email` - 發送自訂郵件

發送完全自訂的郵件，包括主旨、內容和附件。

**參數：**
- `receiver_email` (必要): 收件者郵件地址
- `subject` (必要): 郵件主旨
- `body` (必要): 郵件內容
- `attachment_path` (可選): 附件路徑

**範例使用（在 Claude 中）：**
```
幫我發送郵件給 john@example.com
主旨：會議通知
內容：明天下午 3 點開會，請準時參加。
```

### 2. `send_halloween_invitation` - 萬聖節邀請

使用預設的萬聖節邀請模板發送郵件。

**參數：**
- `receiver_email` (必要): 收件者郵件地址

**範例使用（在 Claude 中）：**
```
發送萬聖節邀請給 nanako@example.com
```

### 3. `send_system_alert` - 系統警示通知

使用預設的系統異常警示模板發送郵件（適用於 IT 運維場景）。

**參數：**
- `receiver_email` (必要): 收件者郵件地址

**範例使用（在 Claude 中）：**
```
發送系統警示給 admin@company.com
```

## 💻 本地開發

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

建立 `.env` 文件：

```env
EMAIL_ACCOUNT=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

> ⚠️ **重要**: Gmail 需使用「應用程式密碼」而非帳號密碼
> 
> 設定方式：
> 1. 前往 [Google 帳戶安全性設定](https://myaccount.google.com/security)
> 2. 啟用「兩步驟驗證」
> 3. 搜尋「應用程式密碼」
> 4. 選擇「郵件」和「其他」，生成密碼
> 5. 將生成的 16 位密碼填入 `EMAIL_PASSWORD`

### 3. 執行 MCP Server

```bash
python server.py
```

服務會在 `http://localhost:8080` 啟動。

### 4. 本地測試

```bash
# 健康檢查
curl http://localhost:8080/health

# MCP 端點（需用 MCP 客戶端測試）
# 本地: http://localhost:8080/mcp
```

## ☁️ 部署到 Google Cloud Run

### 前置需求

1. **安裝 gcloud CLI**
   ```bash
   # macOS
   brew install --cask google-cloud-sdk
   
   # 初始化
   gcloud init
   ```

2. **安裝 Docker Desktop**
   ```bash
   # macOS
   brew install --cask docker
   ```

### 部署步驟

1. **設定 `.env` 文件**（已完成）

2. **執行部署腳本**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

部署腳本會自動：
- ✅ 讀取 `.env` 環境變數
- ✅ 建置 Docker 映像
- ✅ 推送到 Google Container Registry
- ✅ 部署到 Cloud Run
- ✅ 顯示服務 URL

### 查看服務狀態

```bash
# 查看日誌
gcloud run logs tail email-sender-mcp \
  --region=asia-east1 \
  --project=itr-aimasteryhub-lab

# 查看服務資訊
gcloud run services describe email-sender-mcp \
  --region=asia-east1 \
  --project=itr-aimasteryhub-lab
```

### 更新部署

當您修改代碼後，只需再次執行：

```bash
./deploy.sh
```

## 🔐 安全性建議

### 1. 環境變數保護

- ✅ `.env` 文件已加入 `.gitignore`，不會提交到 Git
- ✅ 敏感資訊通過環境變數傳遞到 Cloud Run
- ⚠️ 不要在代碼中硬編碼密碼

### 2. 使用 Secret Manager（進階）

```bash
# 將密碼存到 Secret Manager
echo -n "your_password" | gcloud secrets create email-password \
  --data-file=- \
  --project=itr-aimasteryhub-lab

# 更新 Cloud Run 使用 Secret
gcloud run services update email-sender-mcp \
  --region=asia-east1 \
  --update-secrets=EMAIL_PASSWORD=email-password:latest \
  --project=itr-aimasteryhub-lab
```

### 3. 限制存取權限

預設部署允許未經驗證的存取。如需限制：

```bash
# 移除公開存取
gcloud run services remove-iam-policy-binding email-sender-mcp \
  --region=asia-east1 \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --project=itr-aimasteryhub-lab

# 授予特定使用者存取權限
gcloud run services add-iam-policy-binding email-sender-mcp \
  --region=asia-east1 \
  --member="user:example@gmail.com" \
  --role="roles/run.invoker" \
  --project=itr-aimasteryhub-lab
```

## 📊 監控與維護

### 查看即時日誌

```bash
gcloud run logs tail email-sender-mcp \
  --region=asia-east1 \
  --project=itr-aimasteryhub-lab
```

### 查看歷史日誌

```bash
gcloud run logs read email-sender-mcp \
  --region=asia-east1 \
  --project=itr-aimasteryhub-lab \
  --limit=50
```

### 更新環境變數

```bash
gcloud run services update email-sender-mcp \
  --region=asia-east1 \
  --set-env-vars="EMAIL_ACCOUNT=new_email@gmail.com,EMAIL_PASSWORD=new_password" \
  --project=itr-aimasteryhub-lab
```

## 💰 成本估算

Google Cloud Run 採用按使用量計費：

- **免費額度**: 每月 200 萬次請求
- **CPU**: $0.00002400/vCPU-秒
- **記憶體**: $0.00000250/GiB-秒
- **請求**: $0.40/百萬次
- **網路出站**: $0.12/GB

對於一般郵件服務使用量，**通常每月成本 < $1 USD**，甚至完全在免費額度內。

## 🐛 常見問題排除

### Q: 郵件發送失敗，顯示 "SMTP Authentication Error"

**A**: 請確認：
1. 使用的是 Gmail **應用程式密碼**，而非帳號密碼
2. 已啟用 Google 帳戶的兩步驟驗證
3. `.env` 文件中的 `EMAIL_PASSWORD` 沒有多餘的空格或引號

### Q: Cloud Run 部署失敗

**A**: 檢查：
1. Docker Desktop 是否正在運行
2. gcloud CLI 是否已登入：`gcloud auth list`
3. 專案 ID 是否正確
4. 必要的 API 是否已啟用

### Q: 如何測試 MCP Server 是否正常運行？

**A**: 
```bash
# 測試健康檢查端點
curl https://email-sender-mcp-jt7pjdeeoa-de.a.run.app/health

# 應該返回：{"status": "healthy"}
```

### Q: 如何在 Claude Desktop 中驗證 MCP Server 已連接？

**A**: 
1. 重啟 Claude Desktop
2. 在對話中嘗試說："列出可用的工具"
3. 應該可以看到 `send_email`、`send_halloween_invitation`、`send_system_alert` 三個工具

## 📚 技術棧

- **語言**: Python 3.11
- **框架**: Starlette + Uvicorn
- **協議**: Model Context Protocol (MCP) over Streamable HTTP
- **部署**: Google Cloud Run
- **容器**: Docker

## 🔧 專案優化說明

以下優化已套用於程式碼：

| 項目 | 說明 |
|------|------|
| **安全性** | `/health` 不再回傳 `email_account`，避免洩漏寄件者信箱。 |
| **安全性** | Docker 映像不再包含 `.env`，憑證僅由 Cloud Run 環境變數注入。 |
| **效能** | SMTP 發信改為在 thread pool 執行（`asyncio.to_thread`），避免阻塞事件迴圈。 |
| **正式環境** | Starlette `debug` 改為依環境變數 `DEBUG`（預設關閉）；需除錯時可設 `DEBUG=1`。 |

**可選的後續優化：**

- **依賴版本**：在 `requirements.txt` 中鎖定套件版本（如 `mcp==1.x.x`）以利重現建置。
- **單元測試**：使用 pytest 對 `send_email_internal`（mock SMTP）、`/health` 與 tool 列表撰寫測試。
- **附件支援**：若需 `send_email` 支援 `attachment_path`，需在 server 實作並更新 schema；或從 README 移除該參數說明。
- **sent_mail.py**：為符合專案規範，可為函式加上 type hints、將註解改為英文，並與 server 共用發信邏輯以減少重複。

本地以 Docker 執行時，請以環境變數傳入帳密，例如：

```bash
docker run -p 8080:8080 -e EMAIL_ACCOUNT=you@gmail.com -e EMAIL_PASSWORD=app_password your-image
```

## 📝 檔案結構

```
MCP_sent_mail/
├── server.py              # MCP Server 主程式（Streamable HTTP）
├── sent_mail.py          # 原始郵件發送腳本（獨立使用）
├── requirements.txt      # Python 依賴套件
├── Dockerfile           # Docker 建置配置
├── .dockerignore        # Docker 忽略檔案
├── deploy.sh            # 自動部署腳本
├── cloudbuild.yaml      # Cloud Build 配置
├── .env                 # 環境變數（不提交到 Git）
└── README.md            # 本文件
```

## 🔗 相關資源

- [Model Context Protocol 官方文檔](https://modelcontextprotocol.io/)
- [Google Cloud Run 文檔](https://cloud.google.com/run/docs)
- [Gmail API 設定指南](https://support.google.com/accounts/answer/185833)
- [Claude Desktop 配置](https://docs.anthropic.com/claude/docs)
