# DIT Official Website 正式部署指南

本文件位於 `docs/`，不會取代儲存庫根目錄的 `README.md`，因此不會作為 GitHub 專案首頁說明顯示。

以下流程以 Ubuntu Server、Nginx、systemd 與 Let's Encrypt HTTPS 為例。正式環境架構為：

```text
瀏覽器
  └─ HTTPS / Nginx
       ├─ /       → frontend/dist（Vue 靜態網站）
       └─ /api/*  → 127.0.0.1:8000（FastAPI / Uvicorn）
```

## 1. 部署前準備

準備以下項目：

- 一台 Ubuntu 22.04 或 24.04 伺服器
- 指向伺服器公開 IP 的網域，例如 `www.example.com`
- SSH 與 sudo 權限
- Node.js `22.18.0` 以上，或 `24.12.0` 以上
- Python 3.10 以上
- 專案完整資料與未提交至 Git 的大型檔案

請先將下列範例中的 `<DOMAIN>`、`<REPOSITORY_URL>` 和 `<DEPLOY_USER>` 換成正式值。

### Git 不會包含的檔案

專案 `.gitignore` 會忽略：

```text
*.glb
*.pem
```

因此只執行 `git clone` 不會取得 Eurobot 3D 模型。部署前必須另外將 `.glb` 上傳至對應年度目錄，例如：

```text
backend/data/Eurobot/2024/*.glb
backend/data/Eurobot/2025/*.glb
backend/data/Eurobot/2026/*.glb
```

正式環境由 Nginx 負責 HTTPS，不需要把開發用的 `cert.pem` 或 `key.pem` 上傳到專案目錄，也不可將私鑰提交到 Git。

## 2. 安裝系統套件

```sh
sudo apt update
sudo apt install -y git nginx python3 python3-venv python3-pip curl
```

依照 Node.js 官方方式安裝符合 `frontend/package.json` engines 要求的 Node.js，完成後確認：

```sh
node --version
npm --version
python3 --version
nginx -v
```

## 3. 取得專案

以下範例將專案放在 `/srv/dit-website`：

```sh
sudo mkdir -p /srv/dit-website
sudo chown <DEPLOY_USER>:<DEPLOY_USER> /srv/dit-website
git clone <REPOSITORY_URL> /srv/dit-website
cd /srv/dit-website
```

接著用 `rsync`、`scp` 或其他安全方式上傳被 Git 忽略的 `.glb`。上傳後確認 FastAPI 執行帳號具備讀取權限：

```sh
find backend/data/Eurobot -name '*.glb' -type f -exec chmod 640 {} \;
```

不要將伺服器上的資料目錄開放成所有人可寫入。

## 4. 安裝並測試後端

建立獨立 Python 虛擬環境：

```sh
cd /srv/dit-website/backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install fastapi 'uvicorn[standard]' pillow
```

正式環境不要直接執行 `python main.py`，因為目前 `main.py` 的直接啟動模式包含：

- `reload=True`
- 開發用的 `key.pem` 與 `cert.pem`
- 對外監聽 `0.0.0.0`

正式環境應由 Nginx 終止 HTTPS，Uvicorn 只監聽本機：

```sh
cd /srv/dit-website/backend
./.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
```

另開終端測試 API：

```sh
curl -fsS http://127.0.0.1:8000/api/Eurobot
```

確認成功後按 `Ctrl+C` 停止測試程序。

## 5. 建置前端

```sh
cd /srv/dit-website/frontend
npm ci
npm run build
```

建置結果位於：

```text
/srv/dit-website/frontend/dist
```

部署前至少確認一次：

```sh
npm run build
```

不要使用 `npm run preview` 作為正式網站伺服器。

## 6. 建立 systemd 後端服務

建立 `/etc/systemd/system/dit-website-api.service`：

```ini
[Unit]
Description=DIT Official Website FastAPI
After=network.target

[Service]
Type=simple
User=<DEPLOY_USER>
Group=<DEPLOY_USER>
WorkingDirectory=/srv/dit-website/backend
ExecStart=/srv/dit-website/backend/.venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --workers 2 --proxy-headers --forwarded-allow-ips=127.0.0.1
Restart=on-failure
RestartSec=5
Environment=PYTHONUNBUFFERED=1

# 基本安全限制
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true

[Install]
WantedBy=multi-user.target
```

如果資料檔需要在網站執行期間修改，應另行規劃可寫入目錄；目前網站資料以唯讀方式提供時，以上限制即可使用。

載入並啟動服務：

```sh
sudo systemctl daemon-reload
sudo systemctl enable --now dit-website-api
sudo systemctl status dit-website-api
```

查看後端日誌：

```sh
sudo journalctl -u dit-website-api -f
```

## 7. 設定 Nginx

建立 `/etc/nginx/sites-available/dit-website`：

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name <DOMAIN>;

    root /srv/dit-website/frontend/dist;
    index index.html;

    # Vue Router history mode：直接開啟 /Eurobot 時仍回傳 index.html。
    location / {
        try_files $uri $uri/ /index.html;
    }

    # FastAPI。proxy_pass 不加結尾斜線，保留完整 /api 路徑。
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 大型 GLB/PDF 回應直接串流，讓前端能持續收到載入進度。
        proxy_buffering off;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    # Vite 產生含 hash 的靜態資源可以長期快取。
    location /assets/ {
        try_files $uri =404;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # index.html 不長期快取，避免部署後仍載入舊版入口。
    location = /index.html {
        add_header Cache-Control "no-cache";
    }
}
```

啟用設定並檢查：

```sh
sudo ln -s /etc/nginx/sites-available/dit-website /etc/nginx/sites-enabled/dit-website
sudo nginx -t
sudo systemctl reload nginx
```

若預設站台造成衝突，可移除預設連結：

```sh
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## 8. 啟用 HTTPS

安裝 Certbot：

```sh
sudo apt install -y certbot python3-certbot-nginx
```

申請憑證並讓 Certbot 更新 Nginx：

```sh
sudo certbot --nginx -d <DOMAIN>
```

測試自動續期：

```sh
sudo certbot renew --dry-run
```

正式站只需開放 SSH、HTTP 和 HTTPS，不要將 Uvicorn 的 8000 port 公開到網際網路：

```sh
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
sudo ufw status
```

## 9. 正式上線檢查

逐項確認：

- `https://<DOMAIN>/` 首頁正常顯示
- 直接開啟 `https://<DOMAIN>/Eurobot` 不會出現 Nginx 404
- `https://<DOMAIN>/api/Eurobot` 回傳 JSON
- About、Advisors、Sponsors 與 Contact API 資料正常
- 圖片、影片、PDF、GLB 都能載入
- 3D 模型能顯示真實載入百分比
- 手機、平板與桌面斷點正常
- FloatingRobot 與 TitleBar 跨頁跳轉正常
- See more PDF 預覽正常
- 瀏覽器 DevTools Console 沒有持續錯誤
- HTTP 會自動導向 HTTPS

可使用下列指令快速檢查：

```sh
curl -I https://<DOMAIN>/
curl -I https://<DOMAIN>/Eurobot
curl -fsS https://<DOMAIN>/api/Eurobot
```

## 10. 後續更新部署

每次更新建議依序執行：

```sh
cd /srv/dit-website
git pull --ff-only

cd frontend
npm ci
npm run build

cd ../backend
source .venv/bin/activate
pip install fastapi 'uvicorn[standard]' pillow

sudo systemctl restart dit-website-api
sudo nginx -t
sudo systemctl reload nginx
```

更新後再次檢查：

```sh
sudo systemctl status dit-website-api
sudo journalctl -u dit-website-api --since '10 minutes ago'
curl -I https://<DOMAIN>/
curl -fsS https://<DOMAIN>/api/Eurobot
```

## 11. 備份與回復

至少備份以下內容：

```text
backend/data/
backend/static/
backend/assets/
所有未提交至 Git 的 .glb
Nginx 與 systemd 設定
```

部署前記錄目前 Git commit：

```sh
git rev-parse HEAD
```

若新版發生問題，切回上一個已驗證 commit、重新建置前端並重啟後端：

```sh
git checkout <KNOWN_GOOD_COMMIT>
cd frontend
npm ci
npm run build
sudo systemctl restart dit-website-api
sudo systemctl reload nginx
```

不要使用 `git reset --hard` 處理伺服器上尚未備份的資料或模型檔。

## 12. 常見問題

### API 顯示 502 Bad Gateway

```sh
sudo systemctl status dit-website-api
sudo journalctl -u dit-website-api -n 100
curl http://127.0.0.1:8000/api/Eurobot
```

### 重新整理 `/Eurobot` 顯示 404

確認 Nginx 的根路由包含：

```nginx
try_files $uri $uri/ /index.html;
```

### 3D 模型顯示不存在

確認 `.glb` 已另外上傳、檔名大小寫與 `main_data.json` 完全相同，且 systemd 的執行帳號有讀取權限。

### 前端 API 請求連到錯誤位置

正式前端使用 `/api/...` 相對路徑。請確認 Nginx 有設定 `/api/` 反向代理；正式環境不會使用 Vite `server.proxy`。

### 影片或模型首次載入較慢

目前 Hero 影片與 GLB 檔案較大。正式部署前應另外準備壓縮版本，並確認 Nginx 支援 Range request 與正確的 `Content-Length`，以改善下載和進度顯示。
