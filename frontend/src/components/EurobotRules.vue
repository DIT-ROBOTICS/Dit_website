<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'

// API 載入狀態：介紹文字來自 txt，年度與場地資料來自當年 main_data.json。
const introduction = ref('')
const eurobotData = ref({})
const loading = ref(true)
const loadError = ref('')

// 場地圖片尚未載入時先假設為 3:2；載入後會替換成圖片的真實寬高比。
const venueImageAspect = ref(1.5)

// 場地標註版面設定；calloutSpacing 是相鄰文字中心相差的舞台高度百分比。
const venueLayout = {
    calloutSpacing: 40,
}

// 將 JSON 的 point 值安全轉為數字。
// 不做 clamp，讓小於 0 或超過 3、2 的座標仍能依相同比例向外延伸。
function numericPoint(value, fallback) {
    const number = Number(value)
    return Number.isFinite(number) ? number : fallback
}

// 圖片載入完成後讀取原始尺寸，以便找出圖片正中央最大的 3:2 區域。
function saveVenueImageAspect(event) {
    const image = event.currentTarget
    if (!image.naturalWidth || !image.naturalHeight) return
    venueImageAspect.value = image.naturalWidth / image.naturalHeight
    notifyLayoutReady()
}

// 通知 Router：非同步規則與圖片已撐開版面，可以安全計算 hash 目標位置。
async function notifyLayoutReady() {
    await nextTick()
    window.dispatchEvent(new CustomEvent('eurobot-rules-ready'))
}

/*
 * 將 main_data.json 的 VenueRules 轉成畫面所需的標註資訊。
 *
 * 座標轉換分成四步：
 * 1. 在原圖中央找出最大的 3:2 矩形。
 * 2. 將使用者的 (pointX, pointY) 從「左下為原點」轉成 DOM 的「左上為原點」。
 * 3. 將圖片內座標換算成 venue-stage 三欄版面的百分比座標。
 * 4. 依 point 左右位置分組，再按 calloutSpacing 排列說明文字。
 */
const annotations = computed(() => {
    const imageAspect = venueImageAspect.value
    const targetAspect = 3 / 2

    /*
     * 取照片正中央最大的 3:2 區域，以下數值皆為相對於整張照片的 0～1 比例。
     *
     * 寬圖（原圖比例 >= 3:2）：保留完整高度，左右平均裁掉多餘寬度。
     * 高圖（原圖比例 < 3:2）：保留完整寬度，上下平均裁掉多餘高度。
     */
    const cropWidth = imageAspect >= targetAspect ? targetAspect / imageAspect : 1
    const cropHeight = imageAspect >= targetAspect ? 1 : imageAspect / targetAspect
    const cropLeft = (1 - cropWidth) / 2
    const cropTop = (1 - cropHeight) / 2

    // 先依 id 由小到大排序；非數字 id 則使用文字排序。
    const sortedRules = [...(eurobotData.value.VenueRules || [])].sort((a, b) => {
        const numberA = Number(a.id)
        const numberB = Number(b.id)

        if (Number.isFinite(numberA) && Number.isFinite(numberB)) return numberA - numberB
        return String(a.id ?? '').localeCompare(String(b.id ?? ''), 'zh-Hant', { numeric: true })
    })

    // pointX 預設置中於 0～3，pointY 預設置中於 0～2。
    const rules = sortedRules.map((rule, index) => ({
        ...rule,
        index,
        x: numericPoint(rule.pointX, 1.5),
        y: numericPoint(rule.pointY, 1),
    }))

    const positionedRules = rules.map((rule) => ({
        ...rule,
        /*
         * X：pointX / 3 得到它在中央矩形內的水平比例，再加上矩形的左側偏移。
         * Y：資料以左下為原點，但網頁以左上為原點，所以使用 1 - pointY / 2 反轉方向。
         * 不限制輸入範圍，因此 pointX=4 或 pointY=3 會自然落在中央矩形之外。
         */
        imageX: cropLeft + (rule.x / 3) * cropWidth,
        imageY: cropTop + (1 - rule.y / 2) * cropHeight,
    }))

    // 依 point 在整張圖片的左半或右半決定說明文字放置側，並由上到下排序。
    const sides = {
        left: positionedRules.filter((rule) => rule.imageX < 0.5).sort((a, b) => a.imageY - b.imageY),
        right: positionedRules.filter((rule) => rule.imageX >= 0.5).sort((a, b) => a.imageY - b.imageY),
    }

    return positionedRules.map((rule) => {
        const side = rule.imageX < 0.5 ? 'left' : 'right'
        const group = sides[side]
        const rank = group.findIndex((item) => item.index === rule.index)

        /*
         * 手機版數字由圖片中心朝外偏移，避免一律往上而遮住場地中央。
         * 若 point 剛好位於中心，則預設往上；角落 point 會沿斜線方向外移。
         */
        const directionX = rule.imageX - 0.5
        const directionY = rule.imageY - 0.5
        const directionLength = Math.hypot(directionX, directionY) || 1
        const unitX = directionLength === 1 && directionX === 0 && directionY === 0 ? 0 : directionX / directionLength
        const unitY = directionLength === 1 && directionX === 0 && directionY === 0 ? -1 : directionY / directionLength
        const mobileOffset = 30
        const lineAngle = Math.atan2(-unitY, -unitX) * 180 / Math.PI

        /*
         * 以舞台垂直中心 50% 為基準，向上、向下平均展開。
         * 例如同側 3 筆且 calloutSpacing=15，位置會是 35%、50%、65%。
         */
        const centeredRank = rank - (group.length - 1) / 2
        const labelY = 0.5 + (centeredRank * venueLayout.calloutSpacing) / 100

        return {
            ...rule,
            side,
            labelY,
            /*
             * venue-stage 為「左說明 22%｜圖片 56%｜右說明 22%」。
             * 所以圖片 point 的全舞台 X = 22 + 圖內比例 × 56。
             * Y 方向圖片占滿舞台高度，直接乘以 100 即可。
             */
            targetX: 22 + rule.imageX * 56,
            targetY: rule.imageY * 100,

            // 箭頭起點位於左右文字欄靠近圖片的邊緣。
            anchorX: side === 'left' ? 20 : 80,
            anchorY: labelY * 100,
            mobileOffsetX: unitX * mobileOffset,
            mobileOffsetY: unitY * mobileOffset,
            mobileLineAngle: lineAngle,
        }
    })
})

// 同時載入共用介紹文字與最新年度資料，兩者皆完成後才呈現場地區塊。
async function loadRules() {
    loading.value = true
    loadError.value = ''

    try {
        const [introductionResponse, dataResponse] = await Promise.all([
            fetch('/api/Eurobot/Introduction'),
            fetch('/api/Eurobot'),
        ])

        if (!introductionResponse.ok) throw new Error(`Introduction HTTP ${introductionResponse.status}`)
        if (!dataResponse.ok) throw new Error(`Eurobot HTTP ${dataResponse.status}`)

        introduction.value = await introductionResponse.text()
        eurobotData.value = await dataResponse.json()
    } catch (error) {
        console.error('Eurobot 規則載入失敗：', error)
        loadError.value = '規則資料暫時無法載入'
    } finally {
        loading.value = false
        if (!eurobotData.value.VenueImage) notifyLayoutReady()
    }
}

onMounted(loadRules)
</script>

<template>
    <!-- 等 EurobotSection 建立 #Eurobot_rules 後，將整個規則內容傳送至該位置。 -->
    <Teleport defer to="#Eurobot_rules">
        <article class="eurobot-rules">
            <div class="eurobot-rules-content">
                <!-- Eurobot 共用介紹。 -->
                <p class="eurobot-rules-label">EUROBOT INTRODUCTION</p>
                <h2 class="eurobot-rules-title">關於 Eurobot</h2>

                <p v-if="loading" class="eurobot-rules-state">內容載入中⋯</p>
                <p v-else-if="loadError" class="eurobot-rules-state">{{ loadError }}</p>
                <p v-else class="eurobot-rules-description">{{ introduction }}</p>

                <!-- 最新年度的場地圖片與規則標註。 -->
                <section v-if="!loading && !loadError" class="venue-section">
                    <header class="venue-heading">
                        <h3 class="venue-heading-title">{{ eurobotData.Year }}EUROBOT規則介紹</h3>
                        <p class="venue-heading-description">Eurobot是一場100秒的計時比賽，兩邊隊伍分數高者勝利</p>
                    </header>

                    <!-- 三欄舞台：左側說明、中央圖片、右側說明。 -->
                    <div v-if="eurobotData.VenueImage" class="venue-stage">
                        <!-- 圖片定位容器讓手機版 point 能使用純圖片座標，不受桌面左右欄影響。 -->
                        <div class="venue-image-area">
                            <!-- 載入事件會取得圖片真實比例，並觸發 annotations 重新計算。 -->
                            <img class="venue-image" :src="eurobotData.VenueImage"
                                :alt="`Eurobot ${eurobotData.Year} 場地`" @load="saveVenueImageAspect" />

                            <!-- 手機版：讓規則 id 徽章中心直接對齊圖片目標點。 -->
                            <span v-for="rule in annotations" :key="`mobile-point-${rule.index}`"
                                class="venue-mobile-point"
                                :style="{
                                    left: `${rule.imageX * 100}%`,
                                    top: `${rule.imageY * 100}%`,
                                    '--offset-x': `${rule.mobileOffsetX}px`,
                                    '--offset-y': `${rule.mobileOffsetY}px`,
                                    '--line-angle': `${rule.mobileLineAngle}deg`,
                                }">
                                {{ rule.id }}
                            </span>
                        </div>

                        <!-- SVG 疊在整個舞台上，從文字欄 anchor 畫線至圖片 point。 -->
                        <svg class="venue-lines" aria-hidden="true">
                            <defs class="venue-arrow-definitions">
                                <marker id="venue-arrow" class="venue-arrow-marker" viewBox="0 0 10 10" refX="9" refY="5"
                                    markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                                    <path class="venue-arrow-head" d="M 0 0 L 10 5 L 0 10 z" />
                                </marker>
                            </defs>
                            <line v-for="rule in annotations" :key="`line-${rule.index}`"
                                class="venue-connector-line"
                                :x1="`${rule.anchorX}%`" :y1="`${rule.anchorY}%`"
                                :x2="`${rule.targetX}%`" :y2="`${rule.targetY}%`"
                                marker-end="url(#venue-arrow)" />
                        </svg>

                        <!-- 圖片上的 point 圓點。 -->
                        <span v-for="rule in annotations" :key="`point-${rule.index}`" class="venue-point"
                            :style="{ left: `${rule.targetX}%`, top: `${rule.targetY}%` }"
                            aria-hidden="true"></span>

                        <!-- 自動分配到左右兩側及不同高度的規則文字。 -->
                        <div v-for="rule in annotations" :key="`label-${rule.index}`"
                            class="venue-callout" :class="`is-${rule.side}`"
                            :style="{ top: `${rule.labelY * 100}%` }">
                            <span class="venue-callout-id">{{ rule.id }}</span>
                            <p class="venue-callout-content">
                                {{ rule.content || '請在 main_data.json 填入此標註的規則內容。' }}
                            </p>
                        </div>
                    </div>

                    <!-- VenueImage 尚未設定時保留清楚的資料提示。 -->
                    <p v-else class="venue-empty">
                        請在當年度的 <code class="venue-empty-code">main_data.json</code>
                        填入 <code class="venue-empty-code">VenueImage</code> 圖片檔名。
                    </p>
                </section>
            </div>
        </article>
    </Teleport>
</template>

<style scoped>
/* ===== 規則區塊外框與提亮背景 ===== */
.eurobot-rules {
    position: relative;
    width: 100%;
    padding: clamp(80px, 10vw, 150px) clamp(24px, 6vw, 90px);
    overflow: hidden;
    color: #fff;
    background: rgba(255, 255, 255, 0.14);
    backdrop-filter: brightness(1.22) saturate(0.88);
    -webkit-backdrop-filter: brightness(1.22) saturate(0.88);
}

.eurobot-rules::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(115deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.04));
    pointer-events: none;
}

.eurobot-rules-content {
    position: relative;
    z-index: 1;
    max-width: 1500px;
    margin: 0 auto;
}

/* ===== Eurobot 介紹文字 ===== */
.eurobot-rules-label,
.venue-heading-description {
    margin: 0 0 18px;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 0.22em;
}

.eurobot-rules-title {
    margin: 0;
    font-size: clamp(42px, 6vw, 88px);
    line-height: 1;
}

.eurobot-rules-description,
.eurobot-rules-state {
    max-width: 980px;
    margin: 36px 0 0;
    font-size: clamp(16px, 1.45vw, 21px);
    line-height: 2;
    white-space: pre-line;
}

/* ===== 場地區塊標題 ===== */
.venue-section {
    margin-top: clamp(90px, 12vw, 170px);
}

.venue-heading {
    margin-bottom: 48px;
    text-align: center;
}

.venue-heading-title {
    margin: 0;
    font-size: clamp(34px, 4vw, 62px);
}

/* ===== 三欄場地舞台：左說明 22%｜圖片 56%｜右說明 22% ===== */
.venue-stage {
    position: relative;
    display: grid;
    grid-template-columns: 22% 56% 22%;
    width: 100%;
}

.venue-image-area {
    grid-column: 2;
    position: relative;
    align-self: center;
}

.venue-image {
    width: 100%;
    height: auto;
    display: block;
    filter: drop-shadow(0 24px 45px rgba(0, 0, 0, 0.28));
}

/* 手機數字點預設隱藏，只在手機斷點啟用。 */
.venue-mobile-point {
    display: none;
}

.venue-lines {
    position: absolute;
    z-index: 2;
    inset: 0;
    width: 100%;
    height: 100%;
    overflow: visible;
    pointer-events: none;
}

.venue-connector-line {
    stroke: rgba(255, 255, 255, 0.86);
    stroke-width: 1.5;
    vector-effect: non-scaling-stroke;
}

.venue-arrow-head {
    fill: #fff;
}

/* ===== 桌面版目標點與左右規則文字 ===== */
.venue-point {
    position: absolute;
    z-index: 3;
    width: 12px;
    height: 12px;
    border: 2px solid #fff;
    border-radius: 50%;
    background: #171717;
    box-shadow: 0 0 0 5px rgba(255, 255, 255, 0.2);
    transform: translate(-50%, -50%);
}

.venue-callout {
    position: absolute;
    z-index: 4;
    width: 19%;
    display: flex;
    gap: 5px;
    align-items: flex-start;
    transform: translateY(-50%);
}

.venue-callout.is-left {
    left: 0;
}

.venue-callout.is-right {
    right: 0;
}

.venue-callout-id {
    flex: none;
    color: rgba(255, 255, 255, 0.55);
    font-size: 12px;
    letter-spacing: 0.12em;
}

.venue-callout-content {
    margin: 0;
    font-size: clamp(13px, 2vw, 20px);
    line-height: 1.65;
    white-space: pre-wrap;
}

.venue-empty {
    margin: 0;
    padding: 54px 24px;
    border: 1px dashed rgba(255, 255, 255, 0.45);
    text-align: center;
    color: rgba(255, 255, 255, 0.72);
}

.venue-empty-code {
    color: #fff;
}

/* ===== 手機版：圖片上顯示編號，規則文字改為圖片下方列表 ===== */
@media (max-width: 800px) {
    .venue-stage {
        display: block;
    }

    .venue-lines {
        display: none;
    }

    .venue-point {
        display: none;
    }

    .venue-mobile-point {
        position: absolute;
        z-index: 4;
        width: 28px;
        height: 28px;
        display: grid;
        place-items: center;
        border: 2px solid #fff;
        border-radius: 50%;
        background: #171717;
        color: #fff;
        box-shadow: 0 0 0 5px rgba(255, 255, 255, 0.2);
        font-size: 12px;
        font-weight: 800;
        transform: translate(calc(-50% + var(--offset-x)), calc(-50% + var(--offset-y)));
    }

    .venue-mobile-point::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 16px;
        height: 2px;
        background: #fff;
        transform: rotate(var(--line-angle)) translateX(14px);
        transform-origin: left center;
    }

    .venue-callout,
    .venue-callout.is-left,
    .venue-callout.is-right {
        position: relative;
        top: auto !important;
        right: auto;
        left: auto;
        width: 100%;
        margin-top: 22px;
        padding: 18px;
        background: rgba(10, 12, 17, 0.3);
        transform: none;
    }
}
</style>
