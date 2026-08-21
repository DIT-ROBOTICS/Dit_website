# DIT Official Website Backend

本目錄是 DIT 官方網站的 FastAPI 後端，負責讀取 `database/` 中的 JSON、圖片、影片、3D 模型與 PDF，並透過 `/api/...` 提供給 Vue 前端。

> 維護提醒：非必要請勿直接修改後端行為。若要更動 API 路徑、JSON 結構、資料夾結構或部署設定，請先與吳佳昇確認，並同步檢查前端引用。

## 主要功能

- 提供 About、Advisor、Sponsors、Eurobot 與 Contact 資料。
- 將 JSON 中的媒體檔名轉成前端可請求的 API URL。
- 回傳圖片、影片、GLB、PDF、TXT 與 JSON。
- 圖片可縮放至最大 `1600 × 1600` 並即時轉成 WebP。
- 依 Eurobot 年度資料夾找出最新年度與歷史年度。
- 計算 GLB 檔案大小並加入 Eurobot API 回傳。
- 記錄 request 來源 IP、路徑與 response status。
- 開發環境使用 HTTPS，供 Vite `/api` proxy 存取。

## 目錄結構

```text
backend/
├── main.py
├── README.md
├── cert.pem
├── key.pem
├── routers/
│   ├── __init__.py
│   ├── about.py
│   ├── advisor.py
│   ├── eurobot.py
│   └── sponsors.py
└── PyAPI/
    ├── EurobotAPI.py
    └── ResourceService.py
```

| 檔案 | 職責 |
| --- | --- |
| `main.py` | 建立 FastAPI、CORS、request log middleware、註冊 routers、提供共用端點並啟動 Uvicorn。 |
| `routers/about.py` | About JSON 與圖片 API。 |
| `routers/advisor.py` | Advisor JSON 與圖片 API。 |
| `routers/eurobot.py` | 最新年度、指定年度、歷史資料、介紹文字與年度檔案 API。 |
| `routers/sponsors.py` | Sponsors JSON 與 Logo API。 |
| `PyAPI/EurobotAPI.py` | Eurobot 年度搜尋、資料載入、年份注入、GLB 大小與媒體 URL 處理。 |
| `PyAPI/ResourceService.py` | 共用 JSON、檔案、圖片轉換與附件查詢工具。 |
| `cert.pem` | 開發 HTTPS 憑證。 |
| `key.pem` | HTTPS 私密金鑰，不應公開分享。 |

後端內容位於專案根目錄的 `database/`。命名與 JSON 規範請參考 [`database/README.md`](../database/README.md)。

## 安裝環境

建議使用 Python 3.10 以上。必要套件：FastAPI、Uvicorn、Pillow。

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

目前沒有獨立的 `requirements.txt`；若依賴有變動，需同步更新本文件或建立 requirements。

## 啟動後端

必須從 `backend/` 目錄啟動，因為 `main.py` 以相對檔名讀取 `key.pem` 與 `cert.pem`：

```sh
cd backend
source .venv/bin/activate
python3 main.py
```

預設設定：

```text
Protocol: HTTPS
Host:     0.0.0.0
Port:     8000
Reload:   enabled
```

本機 API 根網址為 `https://127.0.0.1:8000`。開發憑證可能觸發瀏覽器安全警告；Vite proxy 已使用 `secure: false`。

FastAPI 自動文件：

- Swagger UI：`https://127.0.0.1:8000/docs`
- ReDoc：`https://127.0.0.1:8000/redoc`
- OpenAPI JSON：`https://127.0.0.1:8000/openapi.json`

## 同時啟動前端

另開一個終端：

```sh
cd frontend
npm install
npm run dev
```

前端使用 `/api/...` 相對路徑，Vite 會代理到 `https://127.0.0.1:8000`。開發網站預設為 `http://localhost:5173`。

## API 端點

### About

| Method | Path | 回傳內容 |
| --- | --- | --- |
| GET | `/api/aboutPage/data` | About 標題、介紹、照片與詳細內容。 |
| GET | `/api/aboutPage/Image/{name}` | 縮圖並轉為 WebP 的 About 圖片。 |

`aboutPhotos` 與 `moreDetails.image` 會轉成 `/api/aboutPage/Image/...`。

### Advisor

| Method | Path | 回傳內容 |
| --- | --- | --- |
| GET | `/api/Advisor/data` | Advisor 陣列。 |
| GET | `/api/Advisor/Image/{name}` | 縮圖並轉為 WebP 的 Advisor 圖片。 |

`image` 會轉成 `/api/Advisor/Image/...`。

### Sponsors

| Method | Path | 回傳內容 |
| --- | --- | --- |
| GET | `/api/Sponsors` | Sponsors 標題與贊助商陣列。 |
| GET | `/api/Sponsors/Image/{filename}` | `SponsorSection/icon/` 中的原始 Logo。 |

`sponsors.logo` 會轉成 `/api/Sponsors/Image/...`。

### Eurobot

| Method | Path | 回傳內容 |
| --- | --- | --- |
| GET | `/api/Eurobot` | 數字年度資料夾中最新一年的完整資料。 |
| GET | `/api/Eurobot/{year}` | 指定年度資料。 |
| GET | `/api/Eurobot/History` | 除最新年度外的完整歷史年度資料陣列。 |
| GET | `/api/Eurobot/Introduction` | `EurobotIntroduction.txt`。 |
| GET | `/api/Eurobot/History/Background` | `ArchiveBackground/` 中找到的第一個檔案。 |
| GET | `/api/Eurobot/{year}/file/{filename}` | 指定年度資料夾內的原始媒體檔案。 |

年度資料來源：

```text
database/Eurobot/<year>/main_data.json
```

年份不寫在 JSON。後端從資料夾／路由取得並加入：

```python
data["year"] = year
```

這些欄位會轉成年度檔案 API URL：

```text
background
venueImage
robots.glbPath
robots.imagePath
robots.viewerBackground
robots.moreDetailsPath
```

每個 robot 會額外得到 `glbSize`；GLB 不存在時為 `0`。

### 其他端點

| Method | Path | 回傳內容 |
| --- | --- | --- |
| GET | `/api/jsonData/Links` | Contact `Linktree.json`。 |
| GET | `/api/jsonData/AboutData` | About JSON 原始檔。 |
| GET | `/api/PopUpItem/{file}` | 依 `assets/item_name.json` 的 key 回傳附件。 |
| GET | `/api/heroVideo/mobile` | 手機版 Hero 影片。 |
| GET | `/api/heroVideo/desktop` | 桌面版 Hero 影片。 |

例如：

```text
/api/PopUpItem/sponsorshipMethods
```

其中 `sponsorshipMethods` 是設定 key，不是實際 PDF 檔名。

## ResourceService

### 回傳原始檔案

```python
return GIAPI.get_file(file_path)
```

檔案不存在時回傳 HTTP 404。

### 讀取 JSON

```python
data = GIAPI.build_api_data_from_json(json_path, {})
```

### 轉換媒體 URL

```python
return GIAPI.build_api_data_from_json(
    json_path,
    {
        "background": "/api/example/Image",
        "items.image": "/api/example/Image",
    },
)
```

輸入：

```json
{
  "background": "background.jpg",
  "items": [{ "image": "item.png" }]
}
```

輸出：

```json
{
  "background": "/api/example/Image/background.jpg",
  "items": [{ "image": "/api/example/Image/item.png" }]
}
```

點號可穿越巢狀物件與陣列。`build_api_data()` 會直接修改傳入物件，同一份資料不要重複處理。

### 回傳網頁版圖片

```python
return GIAPI.create_image_response(image_path, full=False)
```

流程：

1. Pillow 開啟圖片。
2. 保持比例縮放至最大 `1600 × 1600`。
3. 以品質 `80` 轉為 WebP。
4. 使用 `StreamingResponse` 回傳。

回傳原始圖片：

```python
return GIAPI.create_image_response(image_path, full=True)
```

## 新增 APIRouter

以 Competition 為例，新建 `routers/competition.py`：

```python
from fastapi import APIRouter

import PyAPI.ResourceService as GIAPI


router = APIRouter(prefix="/api/Competition", tags=["Competition"])
COMPETITION_DIR = GIAPI.BASE_DIR / "CompetitionSection"


@router.get("/data")
async def get_competition_data():
    return GIAPI.build_api_data_from_json(
        COMPETITION_DIR / "CompetitionData.json",
        {"image": "/api/Competition/Image"},
    )
```

接著在 `routers/__init__.py` 匯出：

```python
from .competition import router as competition_router
```

加入 `__all__`，再於 `main.py` 註冊：

```python
app.include_router(competition_router)
```

最後到 `/docs` 確認端點已出現。

## Request log

middleware 會輸出：

```text
[REQUEST] 127.0.0.1 -> GET /api/Sponsors
[RESPONSE] 127.0.0.1 <- 200 /api/Sponsors
```

IP 判斷順序：

1. `cf-connecting-ip`
2. `x-forwarded-for` 第一個 IP
3. `request.client.host`
4. `unknown`

## CORS

目前只允許：

```text
http://localhost:5173
```

其他網域直接呼叫 API 時，需在 `main.py` 的 `allow_origins` 加入完整 origin。經 Vite `/api` proxy 的同源請求通常不受此限制。

## BASE_DIR

目前 `database` 的絕對路徑分別寫在：

```text
backend/main.py
backend/PyAPI/ResourceService.py
```

移動專案或換電腦後，兩處都可能需要修改。目前格式為：

```python
BASE_DIR = Path("/Users/.../Dit_Official_Website/database")
```

未來建議統一成一個由檔案位置推算的設定來源，例如：

```python
BASE_DIR = Path(__file__).resolve().parents[2] / "database"
```

實際 `parents[index]` 必須依該檔案層級確認。

## 手動測試

開發憑證未被系統信任時，curl 使用 `-k`：

```sh
curl -k https://127.0.0.1:8000/api/Sponsors
curl -k https://127.0.0.1:8000/api/Advisor/data
curl -k https://127.0.0.1:8000/api/aboutPage/data
curl -k https://127.0.0.1:8000/api/Eurobot
curl -k https://127.0.0.1:8000/api/Eurobot/History
curl -k https://127.0.0.1:8000/api/jsonData/Links
```

只檢查 status：

```sh
curl -k -o /dev/null -w "%{http_code}\n" https://127.0.0.1:8000/api/Sponsors
```

語法檢查：

```sh
cd backend
python3 -m compileall main.py routers PyAPI
```

## 常見問題

### 前端顯示「目前沒有資料」

1. 確認 FastAPI 正在 `8000` port 執行。
2. 查看後端是否出現對應 `[REQUEST]`。
3. 直接開啟 `https://127.0.0.1:8000/api/...`。
4. 確認前端由 `npm run dev` 啟動，讓 Vite proxy 生效。
5. 檢查 JSON key 是否與前端一致。
6. 修改 Python 後重新啟動後端。

### 憑證錯誤

先開啟 `https://127.0.0.1:8000/docs` 確認瀏覽器警告，或透過 Vite 已設定 `secure: false` 的 proxy 存取。

### 404

- 確認檔案存在。
- 確認 JSON 檔名與實際檔案大小寫完全一致。
- Linux 會區分 `.JPG` 與 `.jpg`。
- 確認年度資料夾與 `main_data.json` 存在。
- 確認 URL 大小寫符合 router。

### 422

通常表示 path/query parameter 不符合型別。例如 Hero platform 只接受 `mobile` 或 `desktop`。

### 圖片 API 回傳 500

- 確認 Pillow 已安裝。
- 確認檔案是 Pillow 支援的圖片。
- 確認圖片未損毀且路徑不是資料夾。

### 修改 JSON 後仍顯示舊資料

- 重新整理瀏覽器。
- 確認 request 有到 FastAPI。
- 若修改 Python 回傳格式，重新啟動後端。
- 檢查前端是否仍有舊 key 相容轉換。

## 安全與部署

- `key.pem` 是私密金鑰，不可公開分享。
- 開發憑證不可直接用於正式環境。
- 正式環境建議由 Nginx、Caddy 或 Cloudflare 處理 TLS，再反向代理 Uvicorn。
- 不要在 JSON 中保存本機絕對路徑。
- 正式部署要限制 CORS origins。
- 對外提供檔案路由時，必須避免路徑跳出預期資料夾。
- `.venv/`、私密金鑰、系統暫存與快取不應提交版本控制。

## 修改後檢查清單

- [ ] 已先確認修改範圍與 API 相容性。
- [ ] Router 已在 `routers/__init__.py` 匯出。
- [ ] Router 已在 `main.py` 使用 `include_router()` 註冊。
- [ ] JSON key 使用 camelCase。
- [ ] JSON 與媒體檔案大小寫完全一致。
- [ ] 媒體欄位已轉成 `/api/...` URL。
- [ ] 404、空資料與錯誤情況有合理回應。
- [ ] Swagger UI 可看到端點。
- [ ] 前端 fetch URL 與資料 key 已同步。
- [ ] Python 語法檢查通過。
- [ ] 前端正式建置通過。
