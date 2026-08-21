# Database 資料夾規範

本資料夾存放網站的內容資料與媒體資源。前端不應直接讀取此資料夾，而是透過 FastAPI 的 `/api/...` 端點取得內容。

## 目錄結構

```text
database/
├── AboutSection/
│   ├── AboutSectionData.json
│   └── 活動照片
├── AdvisorSection/
│   ├── Advisors.json
│   └── 顧問照片
├── CompetitionSection/
│   ├── background.png
│   └── <year>/<competition>/
├── ContactSection/
│   └── Linktree.json
├── Eurobot/
│   ├── EurobotIntroduction.txt
│   ├── ArchiveBackground/
│   └── <year>/
│       ├── main_data.json
│       ├── 圖片
│       └── 3D 模型
├── HeroVideo/
│   ├── VideoInfo.json
│   └── 首頁背景影片
├── MemberSection/
│   ├── Leadership.json
│   └── members/<generation>_members.json
├── SponsorSection/
│   ├── SponsorsData.json
│   └── icon/
└── assets/
    ├── item_name.json
    └── PDF 等共用附件
```

## 命名規則

### 資料夾

- 網站區塊使用 `PascalCase`，並以 `Section` 結尾，例如 `AboutSection`、`SponsorSection`。
- 一般用途資料夾使用清楚的英文名稱，例如 `assets`、`members`、`icon`。
- 年度資料夾只使用四位數西元年，例如 `2026`。
- 競賽名稱使用正式英文縮寫或名稱，例如 `ASME`、`TDK`。
- 資料夾名稱不可包含前後空白。

### JSON 檔案

- 區塊主要資料使用 `PascalCase`，例如 `SponsorsData.json`、`Advisors.json`。
- 每年度 Eurobot 的固定入口必須命名為 `main_data.json`，因為後端會依此名稱讀取。
- 成員資料使用 `<generation>_members.json`，例如 `13th_members.json`。
- 副檔名固定使用小寫 `.json`。
- 不要只靠檔名大小寫區分兩個檔案，以免 macOS 與 Linux 行為不同。

### JSON key

所有 JSON key 統一使用 `camelCase`：

```json
{
  "smallTitle": "...",
  "backgroundImage": "background.webp",
  "aboutPhotos": [],
  "moreDetails": []
}
```

規則如下：

- 第一個單字小寫，後續單字首字大寫，例如 `themeColor`。
- 不使用 `snake_case`、`PascalCase` 或帶連字號的 key。
- 布林值優先使用 `is`、`has`、`show`、`enable` 開頭，例如 `isActive`、`showHistoryButton`。
- 陣列使用複數名詞，例如 `robots`、`components`、`aboutPhotos`。
- 單一物件或字串使用單數名詞，例如 `background`、`venueImage`。
- URL 使用 `url`，檔案路徑使用 `path`，例如 `websiteUrl`、`glbPath`。
- 顏色使用 CSS 可辨識的字串，例如 `#100d40`。
- ID key 統一命名為 `id`，同一陣列內不得重複。

禁止的例子：

```json
{
  "ThemeColor": "#fff",
  "Robot_Data": [],
  "daily-title": "...",
  "Componets": []
}
```

正確寫法：

```json
{
  "themeColor": "#fff",
  "robots": [],
  "dailyTitle": "...",
  "components": []
}
```

### 圖片、影片、模型與附件

新媒體檔案建議使用 ASCII `kebab-case`：

```text
team-photo-01.webp
eurobot-2026-white-robot.glb
eurobot-2026-venue.png
sponsorship-guide.pdf
```

- 使用具有內容意義的名稱，不使用 `IMG_1234`、`final-final-2`。
- 同一組連號檔案補零，例如 `photo-01`、`photo-02`。
- 副檔名統一小寫，例如 `.jpg`，不要混用 `.JPG` 與 `.jpg`。
- JSON 中的檔名必須與實際檔案完全一致，包括大小寫。
- 檔名盡量不要包含空白；使用 `-` 分隔單字。
- 圖片優先使用 WebP；需要透明背景時可使用 PNG 或 SVG。
- Logo 優先使用 SVG。
- 3D 模型使用 `.glb`。
- 文件附件使用 `.pdf`。
- 已被 JSON 或 API 引用的舊檔案不可直接改名；必須同步修改所有引用。

目前資料庫仍有部分中文、空白及大寫副檔名的既有檔案。這些屬於相容性保留，新檔案應遵循上述規則；若要整理舊檔，必須以一次完整 migration 同步修改 JSON 和程式引用。

## JSON 格式規則

- 使用 UTF-8 編碼。
- 使用雙引號，不使用單引號。
- 縮排使用 2 個空白。
- 檔案最後保留一個換行。
- 不允許 trailing comma。
- 不在 JSON 中加入註解。
- 同類物件保持相同欄位與型別。
- 未設定的陣列使用 `[]`，不要使用空字串。
- 未設定的選填文字可使用 `""`；需要明確表示不存在時才使用 `null`。
- 年份、尺寸與座標使用 number，不要存成數字字串。

## Eurobot 年度資料

每個年度都必須提供：

```text
Eurobot/<year>/main_data.json
```

建議基本結構：

```json
{
  "background": "eurobot-2026-background.webp",
  "bigTitle": "THIS YEAR\nWE MADE IT",
  "awards": [],
  "awardsColor": "#c75b5b",
  "description": "",
  "venueRules": [],
  "venueImage": "eurobot-2026-venue.png",
  "robots": [
    {
      "id": 1,
      "name": "白機",
      "displayName": "NTHU DIT",
      "themeColor": "#ffac70",
      "glbPath": "eurobot-2026-white-robot.glb",
      "imagePath": "eurobot-2026-white-robot.webp",
      "viewerBackground": "eurobot-2026-white-viewer.webp",
      "moreDetailsPath": "",
      "components": []
    }
  ]
}
```

注意事項：

- `year` 不寫在 JSON；後端會從年度資料夾名稱／路由參數取得並加入 API 回傳。
- 3D Viewer 的初始左右視角由前端依 `robots` 陣列位置自動計算，不寫入 JSON。
- `robots` 和 `components` 即使沒有資料也要保留空陣列。
- JSON 只儲存同年度資料夾內的檔名，不直接寫本機絕對路徑。
- 後端會將媒體檔名轉成 `/api/Eurobot/<year>/file/<filename>`。
- 最新年度由 `/api/Eurobot` 提供；歷史年度由 `/api/Eurobot/History` 提供。

## 路徑與安全規則

JSON 中禁止寫入本機絕對路徑：

```text
/Users/name/project/database/...
C:\Users\name\project\database\...
```

應只保存檔名或相對資料：

```json
{
  "image": "advisor-name.webp"
}
```

由 FastAPI router 和 `ResourceService` 組合公開 API URL。這樣資料可以在本機、伺服器及容器環境共用。

## 新增或修改資料檢查清單

提交前確認：

- [ ] 資料放在正確的 Section 或年度資料夾。
- [ ] JSON 可以正常解析。
- [ ] 所有 key 都是 camelCase。
- [ ] 陣列欄位使用複數名稱。
- [ ] `id` 在同一陣列內沒有重複。
- [ ] JSON 檔名與實際媒體檔名大小寫完全一致。
- [ ] 沒有本機絕對路徑。
- [ ] 圖片方向已正規化，不依賴錯誤的 EXIF Orientation。
- [ ] 新媒體檔名使用 kebab-case 與小寫副檔名。
- [ ] 對應 FastAPI API 可以正常回傳資料與媒體。
- [ ] 前端 loading、error、empty 和正常內容狀態皆正常。
