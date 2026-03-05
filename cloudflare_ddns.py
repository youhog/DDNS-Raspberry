import requests
import os
import time
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# 獲取腳本所在目錄
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- 設定區 ---
CF_API_TOKEN = os.getenv("CF_API_TOKEN")
ZONE_ID = os.getenv("ZONE_ID")
RECORD_NAME = os.getenv("RECORD_NAME")
LOG_FILE = os.path.join(BASE_DIR, "ddns.log")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))
DOCKER_MODE = os.getenv("DOCKER_MODE", "false").lower() == "true"

# --- 日誌設定 ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_public_ip():
    """獲取目前的公網 IP"""
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        return response.json()['ip']
    except Exception as e:
        logger.error(f"無法獲取公網 IP: {e}")
        return None

def get_dns_record():
    """從 Cloudflare 獲取目前的 DNS 紀錄資訊"""
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    params = {"name": RECORD_NAME}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        result = response.json()
        if result['success'] and result['result']:
            return result['result'][0]
        else:
            logger.error(f"找不到網域紀錄: {RECORD_NAME}")
            return None
    except Exception as e:
        logger.error(f"查詢 Cloudflare 失敗: {e}")
        return None

def update_dns_record(record_id, ip):
    """更新 Cloudflare 的 DNS 紀錄"""
    url = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records/{record_id}"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "type": "A",
        "name": RECORD_NAME,
        "content": ip,
        "ttl": 1,
        "proxied": False
    }
    
    try:
        response = requests.put(url, headers=headers, json=data, timeout=10)
        if response.json()['success']:
            logger.info(f"成功更新 IP 為: {ip}")
        else:
            logger.error(f"更新失敗: {response.json()['errors']}")
    except Exception as e:
        logger.error(f"發送更新請求失敗: {e}")

def run_once():
    logger.info(f"--- 開始檢查 {RECORD_NAME} ---")
    
    if not all([CF_API_TOKEN, ZONE_ID, RECORD_NAME]):
        logger.error("設定不完整，請檢查 .env 檔案內容。")
        return

    current_ip = get_public_ip()
    if not current_ip:
        return

    record = get_dns_record()
    if not record:
        return

    if record['content'] != current_ip:
        logger.info(f"偵測到 IP 變動: {record['content']} -> {current_ip}")
        update_dns_record(record['id'], current_ip)
    else:
        logger.info("IP 未變動，無需更新。")

def main():
    if DOCKER_MODE:
        logger.info("以 Docker 循環模式啟動...")
        while True:
            run_once()
            time.sleep(CHECK_INTERVAL)
    else:
        run_once()

if __name__ == "__main__":
    main()
