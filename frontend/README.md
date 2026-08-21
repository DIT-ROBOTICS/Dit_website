# DIT Official Website Frontend

本目錄是以 Vue、Vue Router 與 Vite 建立的網站前端。前端依照「頁面組裝、功能模組、跨功能共用元件」分層，讓 API、畫面與共用行為各自有明確位置。

## 開發指令

請先進入 `frontend`：

```bash
npm install
npm run dev
```

其他常用指令：

```bash
npm run build    # 建立正式版並檢查 Vue 模板與 import
npm run preview  # 在本機預覽正式版
npm run format   # 使用 Prettier 格式化 src
```

開發時前端 API 路徑皆使用 `/api/...`。本機環境由 Vite proxy 轉送至後端；正式環境則由部署設定決定 API 來源。

## 目錄結構

```text
frontend/
├── public/                 # 不經打包處理、以原始路徑提供的靜態檔案
├── src/
│   ├── assets/             # 由 Vue 元件 import 的圖片與其他資源
│   ├── components/
│   │   ├── common/         # 跨功能、無業務領域的共用元件
│   │   ├── layout/         # 全站導覽列、啟動動畫、浮動元件
│   │   └── icons/          # SVG / icon 元件
│   ├── composables/        # 跨元件共用的狀態與瀏覽器行為
│   ├── features/           # 依網站功能切分的獨立模組
│   │   ├── about/
│   │   ├── advisors/
│   │   ├── competition/
│   │   ├── contact/
│   │   ├── eurobot/
│   │   ├── hero/
│   │   └── sponsors/
│   ├── router/             # 路由表與頁面捲動行為
│   ├── styles/             # 全站樣式
│   ├── views/              # 路由頁面，只負責組裝 feature
│   ├── App.vue             # 全站外框與跨路由元件
│   └── main.js             # Vue 啟動入口
└── vite.config.js
```

## 分層原則

### `views`

一個 view 對應一條路由，主要工作是排列功能區塊，不應直接處理資料格式或塞入大量區塊樣式。例如 `EurobotView.vue` 使用具名 slot，把 `EurobotRules` 放入 `EurobotSection` 的指定位置；子元件不需要自行尋找或傳送到外部 DOM。

### `features`

每個功能擁有自己的畫面與 API 路徑：

```text
features/sponsors/
├── SponsorsSection.vue
└── sponsorsApi.js
```

只有單一元件時可直接放在功能根目錄。像 Eurobot 有多個相關元件，則放進 `features/eurobot/components/`，同功能專用的計算程式放在 Eurobot 根目錄。

新增功能時，請優先建立新的 feature；不要把具有 About、Eurobot、Sponsors 等領域意義的元件放進 `components/common`。

### `components/common`

只放能被不同 feature 使用，而且本身不理解任何業務資料的元件：

- `ApiState.vue`：統一 loading、error、empty 與重試畫面。
- `FilePreviewModal.vue`：通用檔案預覽視窗。

### `components/layout`

放置控制全站外框或跨路由顯示的元件，例如 `TitleBar`、`FloatingRobot` 與 `StartupAnimation`。這些元件通常由 `App.vue` 使用。

### `composables`

- `useApiData`：統一請求、取消、錯誤、loading 與 reload；完整範例寫在檔案註解中。
- `useBodyScrollLock`：modal 開啟時鎖定 body，並支援多個視窗同時要求鎖定。
- `useInteractionMode`：統一判斷觸控／滑鼠操作模式與監聽媒體查詢。

## API 使用規則

每個 feature 將端點集中在自己的 `*Api.js`：

```js
export const sponsorsApi = Object.freeze({
  data: '/api/Sponsors',
})
```

元件透過 `useApiData` 載入，並用 `ApiState` 顯示狀態：

```js
const { data, loading, error, load, reload } = useApiData([])
load(sponsorsApi.data)
```

這項規則可避免 URL 散落在 template 與多個函式中。API 改名時，只需要更新該 feature 的 API 檔案。

## 元件溝通規則

元件之間依序優先使用：

1. Props 傳入資料或設定。
2. Emits 回報使用者操作或狀態變化。
3. Slots 讓父層決定內容與排列位置。
4. Composable 共用瀏覽器行為或可重用狀態流程。

只有 modal、全螢幕 overlay 這類確實需要脫離父層 stacking context 的內容才使用 `Teleport to="body"`。一般區塊不要依賴另一個元件提供特定 DOM id，否則單獨使用、改變載入順序或 API 失敗時容易整區消失。

## 新增一個功能區塊

以 `news` 為例：

1. 建立 `src/features/news/NewsSection.vue`。
2. 建立 `src/features/news/newsApi.js` 管理端點。
3. 在元件內使用 `useApiData` 與 `ApiState`。
4. 在需要顯示它的 view 中 import 並排列。
5. 執行 `npm run build`，確認模板、import 與正式打包皆成功。

如果一段程式只服務 News，留在 feature 內；只有確定至少兩個不同 feature 都能合理使用時，才提升到 `components/common` 或 `composables`。

## 維護檢查清單

- API 路徑是否集中在對應 feature 的 API 檔案。
- 非同步畫面是否提供 loading、error、empty 與 reload。
- `matchMedia`、event listener、timer 是否在卸載時清除。
- modal 是否使用共用 body scroll lock。
- 元件是否能在不依賴隱藏 DOM id 的情況下使用。
- 修改完成後是否通過 `npm run build`。
