# 使用 Python 3.11 作為基礎映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY server.py .
COPY .env .

# 設定環境變數
ENV PYTHONUNBUFFERED=1

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# 暴露端口
EXPOSE 8080

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# 啟動應用程式
CMD ["python", "server.py"]
