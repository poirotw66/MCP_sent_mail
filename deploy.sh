#!/bin/bash
# Google Cloud Run 部署腳本

set -e

# 設定變數
PROJECT_ID="itr-aimasteryhub-lab"
SERVICE_NAME="email-sender-mcp"
REGION="asia-east1"
IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"

echo "🚀 開始部署到 Google Cloud Run..."

# 讀取 .env 檔案
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ 已從 .env 讀取環境變數"
else
    echo "⚠️  找不到 .env 檔案"
    exit 1
fi

# 確認環境變數
if [ -z "$EMAIL_ACCOUNT" ] || [ -z "$EMAIL_PASSWORD" ]; then
    echo "❌ 錯誤：EMAIL_ACCOUNT 或 EMAIL_PASSWORD 未設定"
    exit 1
fi

echo "📧 使用郵件帳號: $EMAIL_ACCOUNT"

# 設定專案
echo "🔧 設定 GCP 專案..."
gcloud config set project $PROJECT_ID

# 啟用必要的 API
echo "🔧 啟用必要的 API..."
gcloud services enable \
    containerregistry.googleapis.com \
    run.googleapis.com \
    --project=$PROJECT_ID

# 配置 Docker 認證
echo "🔐 配置 Docker 認證..."
gcloud auth configure-docker --quiet

# 建置 Docker 映像
echo "🐳 建置 Docker 映像..."
docker build -t $IMAGE_NAME:latest .

# 推送映像到 Google Container Registry
echo "📤 推送映像到 GCR..."
docker push $IMAGE_NAME:latest

# 部署到 Cloud Run
echo "🚀 部署到 Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE_NAME:latest \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --set-env-vars="EMAIL_ACCOUNT=$EMAIL_ACCOUNT,EMAIL_PASSWORD=$EMAIL_PASSWORD" \
  --port=8080 \
  --memory=512Mi \
  --cpu=1 \
  --timeout=300 \
  --project=$PROJECT_ID

echo ""
echo "✅ 部署完成！"
echo ""
echo "📍 服務資訊："
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
echo "   URL: $SERVICE_URL"
echo ""
echo "📊 查看日誌："
echo "   gcloud run logs tail $SERVICE_NAME --region=$REGION --project=$PROJECT_ID"
echo ""
echo "🧪 測試 MCP Server:"
echo "   curl $SERVICE_URL/mcp  (use MCP client; or curl $SERVICE_URL/health for health check)"
