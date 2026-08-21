# DIT Official Website

DIT 官方網站完整專案，包含 Vue 前端、FastAPI 後端與檔案式內容資料庫。文字、圖片、影片、PDF 與 Eurobot 年度資料由後端讀取 `database/`，再透過 `/api/...` 提供給前端。

瀏覽網站：[DIT Official Website](https://jasonwu314159.github.io/Dit_Web_Link/)

若公開網站無法正常顯示，請聯絡專案負責人。

## 專案結構

```text
Dit_Official_Website/
├── frontend/               # Vue、Vue Router、Vite 前端
│   ├── src/
│   │   ├── components/     # 共用與全站 layout 元件
│   │   ├── composables/    # API、互動模式、捲動鎖定
│   │   ├── features/       # About、Eurobot、Sponsors 等功能
│   │   ├── router/         # 路由與捲動行為
│   │   └── views/          # 路由頁面組裝
│   └── vite.config.js
├── backend/                # FastAPI 與媒體檔案服務
│   ├── main.py
│   ├── routers/            # 各功能的 APIRouter
│   └── PyAPI/              # JSON、圖片與 Eurobot 處理服務
├── database/               # JSON 與網站媒體內容
└── README.md
```

詳細文件：

- [Frontend README](frontend/README.md)：前端分層、元件溝通、API 使用與新增功能流程。
- [Backend README](backend/README.md)：環境設定、API、APIRouter、ResourceService 與除錯。
- [Database README](database/README.md)：資料夾結構、JSON 格式、命名規則與維護清單。

## 技術架構

| 區域 | 技術 | 用途 |
| --- | --- | --- |
| Frontend | Vue、Vue Router、Vite | 畫面、路由、動畫與 API 狀態 |
| 3D | Three.js | Eurobot GLB 模型預覽 |
| 文件 | PDF.js | PDF 附件預覽 |
| Backend | Python、FastAPI、Uvicorn | JSON API 與媒體回傳 |
| Image | Pillow | 圖片縮放及 WebP 轉換 |
| Content | JSON、圖片、影片、GLB、PDF | 網站實際內容 |

```text
database files
      ↓
FastAPI routers + ResourceService
      ↓ /api/...
Vite development proxy
      ↓
Vue feature components
```

前端不直接讀取 `database/`。JSON 中的媒體檔名由後端轉換成公開 API URL。

## 環境需求

- Node.js `22.18.0` 以上，或 `24.12.0` 以上
- npm
- Python 3.10 以上
- FastAPI、Uvicorn、Pillow
- `backend/cert.pem` 與 `backend/key.pem`
- 選用：Cloudflared，用於分享本機預覽

## 第一次安裝

### 後端

macOS / Linux：

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install fastapi "uvicorn[standard]" pillow
```

Windows PowerShell：

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install fastapi "uvicorn[standard]" pillow
```

### 前端

```sh
cd frontend
npm install
```

## 啟動完整開發環境

完整網站需要後端與前端同時執行。

### 終端一：後端

macOS / Linux：

```sh
cd backend
source .venv/bin/activate
python3 main.py
```

Windows PowerShell：

```powershell
cd backend
.venv\Scripts\Activate.ps1
python main.py
```

後端預設網址為 `https://127.0.0.1:8000`。後端使用本機 HTTPS 憑證，直接由瀏覽器開啟時可能出現開發憑證警告。

### 終端二：前端

```sh
cd frontend
npm run dev
```

前端預設網址為 `http://localhost:5173`。Vite 會將 `/api` 代理到 `https://127.0.0.1:8000`，且已允許開發用自簽憑證。

## 確認環境正常

1. 開啟 `https://127.0.0.1:8000/docs`，確認 Swagger UI 可以顯示。
2. 開啟 `https://127.0.0.1:8000/api/aboutPage/data`，確認後端能讀取 database。
3. 開啟 `http://localhost:5173`，確認首頁資料與圖片正常載入。
4. 前端修改後執行 `npm run build`，確認 Vue template 與 imports 可正式打包。

## 常用指令

### Frontend

```sh
cd frontend
npm run dev       # 開發伺服器
npm run build     # 正式建置
npm run preview   # 預覽建置結果
npm run format    # 格式化 src
```

正式版輸出至 `frontend/dist/`。

### Backend

```sh
cd backend
source .venv/bin/activate
python3 main.py
```

API 文件：

- Swagger UI：`https://127.0.0.1:8000/docs`
- ReDoc：`https://127.0.0.1:8000/redoc`
- OpenAPI JSON：`https://127.0.0.1:8000/openapi.json`

## 主要功能與 API

| 功能 | 前端位置 | 主要 API |
| --- | --- | --- |
| 首頁 Hero | `features/hero/` | `/api/heroVideo/{platform}` |
| About | `features/about/` | `/api/aboutPage/data` |
| Advisors | `features/advisors/` | `/api/Advisor/data` |
| Eurobot 當年度 | `features/eurobot/` | `/api/Eurobot` |
| Eurobot 歷史資料 | `features/eurobot/` | `/api/Eurobot/History` |
| Sponsors | `features/sponsors/` | `/api/Sponsors` |
| Contact | `features/contact/` | `/api/jsonData/Links` |
| 附件預覽 | `components/common/` | `/api/PopUpItem/{file}` |

完整端點與回傳內容請參考 [Backend README](backend/README.md)。

## 修改網站內容

網站內容放在 `database/`，而不是寫死於 Vue 元件。

1. 找到對應 Section 或 Eurobot 年度資料夾。
2. 依 [Database README](database/README.md) 修改 JSON 或媒體。
3. 確認 JSON key 使用 `camelCase`，檔名大小寫與實際檔案相同。
4. 直接測試對應後端 API。
5. 確認前端 loading、error、empty 與正常資料狀態。

已被 JSON 引用的檔案不可只改檔名而不更新 JSON。Eurobot 年份由年度資料夾名稱產生，不需要寫入 `main_data.json`。

## 修改或新增前端功能

- 路由頁面放在 `src/views/`，只負責組裝區塊。
- About、Eurobot、Sponsors 等功能放在 `src/features/`。
- 功能 API URL 放在同 feature 的 `*Api.js`。
- 跨功能 UI 放在 `src/components/common/`。
- 全站外框元件放在 `src/components/layout/`。
- 共用狀態與瀏覽器行為放在 `src/composables/`。

避免讓元件依賴其他元件建立特殊 DOM id。排列需求優先使用 props、emits 與 slots；只有 modal 或全螢幕 overlay 適合 Teleport 到 `body`。

詳細規則與範例請參考 [Frontend README](frontend/README.md)。

## 新增後端 API

網站功能 API 應使用 APIRouter：

1. 在 `backend/routers/` 建立 router。
2. 使用 `ResourceService` 讀取 JSON 或回傳媒體。
3. 從 `backend/routers/__init__.py` 匯出 router。
4. 在 `backend/main.py` 使用 `app.include_router()` 註冊。
5. 在 Swagger UI 與前端分別測試。

不要把本機絕對路徑寫進 JSON 或 API。資料根目錄統一由 `ResourceService.BASE_DIR` 管理。

## 分享本機預覽

確認前後端皆已啟動後，開啟第三個終端：

```sh
cloudflared tunnel --url http://localhost:5173
```

Cloudflared 會提供臨時 `https://*.trycloudflare.com` 網址。前端、後端與 tunnel 都必須持續執行；重新啟動後網址通常會改變。此方式適合測試，不適合正式部署。

## 常見問題

### 前端空白或顯示目前沒有資料

1. 確認後端仍在 port `8000` 執行。
2. 直接測試對應的 `https://127.0.0.1:8000/api/...`。
3. 確認前端由 Vite 啟動，不是直接開啟 HTML。
4. 查看瀏覽器 Network 是否有 `/api` 的 404、500 或 proxy 錯誤。
5. 查看後端是否印出對應 `[REQUEST]` 與 `[RESPONSE]`。

### API 能開啟，但前端沒有 request

確認元件已被目前 view import 並實際 render，也要確認 endpoint 來自該 feature 的 `*Api.js`。非同步畫面應使用 `useApiData` 與 `ApiState` 管理載入、錯誤、空資料及 reload。

### 圖片方向錯誤

來源圖片可能依賴 EXIF Orientation。上傳前應將方向實際套用到像素並重新輸出，避免瀏覽器或 Pillow 轉檔後方向不同。

### HTTPS 憑證錯誤

Vite proxy 已設定 `secure: false`。若直接在瀏覽器測試後端，仍可能需要先接受開發憑證警告。正式私密金鑰不可提交或公開分享。

## 提交前檢查

- [ ] 前端通過 `npm run build`。
- [ ] 修改過的 API 可從 Swagger 或瀏覽器正常存取。
- [ ] JSON 可以解析，媒體檔名大小寫正確。
- [ ] 非同步畫面有 loading、error、empty 與 reload。
- [ ] 沒有加入本機絕對路徑、虛擬環境、建置輸出或私密金鑰。
- [ ] 目錄或資料格式變更已同步更新對應 README。
