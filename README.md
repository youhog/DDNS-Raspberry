# Cloudflare Python DDNS 腳本

這是一個輕量級的 Python 腳本，專為樹梅派 (Raspberry Pi) 或 Linux 伺服器設計，用於自動更新 Cloudflare 上的 DNS A 紀錄。

## 功能
- **日誌記錄**：使用 Python `logging` 模組，支援日誌輪替 (Rotating logs)，防止磁碟空間被佔滿。
- **單次執行**：執行一次即結束，適合配合 `cron` 定時執行。
- **環境變數**：安全地使用 `.env` 檔案管理 API 金鑰。

## 安裝步驟

1. **複製專案到樹梅派**：
   ```bash
   git clone https://github.com/youhog/DDNS-Raspberry
   cd DDNS-Raspberry
   ```

2. **建立虛擬環境並安裝相依套件**：
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **設定認證資訊**：
   - 複製範本檔案：`cp .env.example .env`
   - 編輯 `.env` 並填入您的 Cloudflare 資訊：
     - `CF_API_TOKEN`: 具備 DNS 編輯權限的 API Token。
     - `ZONE_ID`: 網域的 Zone ID。
     - `RECORD_NAME`: 您要更新的完整域名 (例如 `pi.yourdomain.com`)。

## 定時執行 (Cron Job)

建議設定每 5 或 10 分鐘執行一次腳本。`cron` 服務在系統開機後會自動啟動，因此腳本會按照排程自動執行。

1. 打開 cron 編輯器：
   ```bash
   crontab -e
   ```

2. 在檔案末尾添加以下內容：
   ```bash
   # 每 5 分鐘執行一次
   */5 * * * * /home/pi/DDNS-Raspberry/venv/bin/python /home/pi/DDNS-Raspberry/cloudflare_ddns.py >> /dev/null 2>&1
   
   # 如果希望開機時立即執行一次，可加入這行：
   @reboot /home/pi/DDNS-Raspberry/venv/bin/python /home/pi/DDNS-Raspberry/cloudflare_ddns.py >> /dev/null 2>&1
   ```

## 使用 Docker 部署 (推薦)

這也是最簡單的方式，您可以直接拉取打包好的映像檔。

1. **準備 `docker-compose.yml`**：
   ```yaml
   version: '3.8'
   services:
     ddns:
       image: ghcr.io/${{ github.repository }}:main
       container_name: cloudflare-ddns
       restart: always
       env_file: .env
       volumes:
         - ./logs:/app/logs
   ```

2. **建立 `.env` 檔案** 並填入資訊：
   ```env
   CF_API_TOKEN=您的_TOKEN
   ZONE_ID=您的_ZONE_ID
   RECORD_NAME=您的_域名
   CHECK_INTERVAL=300
   DOCKER_MODE=true
   ```

3. **啟動**：
   ```bash
   docker compose up -d
   ```

## 查看日誌
您可以隨時檢查 `ddns.log` 來確認運作狀態：
```bash
tail -f ddns.log
```
