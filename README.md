# DIT Official Website 前端

這是 DIT 官方網站的 Vue 3 前端專案，使用 Vite 進行開發與建置。

## 開發環境

- Node.js `22.18.0` 以上，或 `24.12.0` 以上
- npm
- 如需顯示完整網站資料，需同時啟動本專案的 FastAPI 後端
- 選用：Cloudflared，用於將本機開發網站分享給其他人預覽

## 安裝前端

進入 `frontend` 目錄後安裝套件：

```sh
cd frontend
npm install
```

## 啟動完整開發環境

前端會向 `/api` 取得網站內容、圖片、PDF 與 Eurobot 資料。Vite 會將這些請求代理到 `https://127.0.0.1:8000`，因此開發時需同時啟動後端與前端。

### 1. 啟動後端

在專案根目錄開啟第一個終端：

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]"
python3 main.py
```

Windows PowerShell 啟用虛擬環境的指令為：

```powershell
.venv\Scripts\Activate.ps1
```

後端會使用 `backend/cert.pem` 與 `backend/key.pem` 啟動在 `https://127.0.0.1:8000`。這兩個檔案必須存在，且私密金鑰不應公開分享。

### 2. 啟動前端

在專案根目錄開啟第二個終端：

```sh
cd frontend
npm install
npm run dev
```

啟動後開啟 Vite 顯示的網址，預設為 `http://localhost:5173`。

## 分享本機預覽網站

請先確認前端與後端都已啟動，再開啟第三個終端：

```sh
cloudflared tunnel --url http://localhost:5173
```

Cloudflared 會產生一個臨時的 `https://*.trycloudflare.com` 網址，將這個網址分享給其他人即可預覽。

注意：

- 前端、後端和 Cloudflared 的終端都必須保持運作。
- 重新啟動 Cloudflared 後，臨時網址通常會改變。
- 這個方式適合測試與臨時預覽，不適合正式上線。

## 只修改前端

主要的頁面元件位於 `frontend/src/components/`，全域樣式位於 `frontend/src/styles/`。

若對方只取得 `frontend` 目錄，仍可修改介面與執行 `npm run dev`，但是下列由 API 提供的內容無法完整顯示：

- About 圖片與文字資料
- Advisor 資料
- Sponsors 資料與 Logo
- Eurobot 資料、歷年紀錄與檔案
- 聯絡連結與贊助 PDF

若要在不提供後端原始碼的情況下進行完整前端開發，需由維護者另外提供可存取的測試 API，或在前端建立 mock data。

## 格式化程式碼

```sh
cd frontend
npm run format
```

## 建置與預覽正式版本

```sh
cd frontend
npm run build
npm run preview
```

建置結果會輸出到 `frontend/dist/`。`npm run preview` 只用於在本機檢查建置結果，不是正式網站伺服器。
