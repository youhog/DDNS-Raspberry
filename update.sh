#!/bin/bash

# Cloudflare DDNS 自動更新腳本
# 適用於 Docker 或 Systemd 部署環境

# 取得腳本所在的目錄
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "--- 開始更新 Cloudflare DDNS ---"

# 1. 從 Git 拉取最新代碼
if [ -d ".git" ]; then
    echo "[1/3] 正在從 Git 拉取最新代碼..."
    git pull
else
    echo "[!] 警告: 目前目錄不是 Git 儲存庫，跳過 git pull。"
fi

# 2. 判斷部署方式並執行更新
if [ -f "docker-compose.yml" ] && command -v docker >/dev/null 2>&1 && docker compose ps >/dev/null 2>&1; then
    # Docker 部署方式
    echo "[2/3] 檢測到 Docker 部署，正在更新鏡像與重啟容器..."
    docker compose pull
    docker compose up -d
    echo "[3/3] Docker 容器已重啟。"
else
    # 虛擬環境 + Systemd 方式
    echo "[2/3] 檢測到手動部署，正在更新 Python 依賴..."
    
    if [ -d "venv" ]; then
        ./venv/bin/pip install --upgrade pip
        ./venv/bin/pip install -r requirements.txt
    else
        echo "[!] 找不到 venv 目錄，請確保你已手動建立虛擬環境。"
    fi

    # 檢查並重啟 Systemd 服務
    if systemctl is-active --quiet ddns.service; then
        echo "[3/3] 正在重啟 ddns.service..."
        sudo systemctl restart ddns.service
    else
        echo "[3/3] ddns.service 未執行或未安裝，跳過重啟。"
    fi
fi

echo "--- 更新完成！ ---"
echo "你可以執行 'tail -f ddns.log' 或 'docker compose logs -f' 查看日誌。"
