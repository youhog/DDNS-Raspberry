# 使用輕量級的 Python 映像檔
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製需求檔案並安裝套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製腳本與 .env
COPY cloudflare_ddns.py .

# 執行腳本
CMD ["python", "cloudflare_ddns.py"]
