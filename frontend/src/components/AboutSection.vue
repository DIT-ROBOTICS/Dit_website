<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

// About 區塊的團隊照片與文字資料。
const photoUrls = ref([])
const aboutData = ref({})
const activeDailyCardIndex = ref(null)
const usesTouchInteraction = ref(window.matchMedia('(hover: none), (pointer: coarse)').matches)
let touchMediaQuery

// 展開版面參數：漸層占圖片寬度的比例，以及文字在整個相簿中的起點。
const dailyLayout = {
    gradientShare: 0.4,
    // 文字從整個相簿左側多少百分比的位置開始（50 代表正中央）。
    textStart: 50,
    // 圖片載入前暫時使用 3:1。
    fallbackAspectRatio: 3,
}

const dailyPhotoRatios = ref({})

function saveDailyPhotoRatio(index, event) {
    const image = event.currentTarget
    if (!image.naturalWidth || !image.naturalHeight) return
    dailyPhotoRatios.value[index] = image.naturalWidth / image.naturalHeight
}

function getDailyCardStyle(index) {
    const aspectRatio = dailyPhotoRatios.value[index] || dailyLayout.fallbackAspectRatio
    const gradientFactor = aspectRatio * dailyLayout.gradientShare
    const purePhotoFactor = aspectRatio - gradientFactor

    return {
        '--Theme-Color': aboutData.value.themeColor,
        '--daily-expanded-image-width': `calc(var(--daily-gallery-height) * ${aspectRatio})`,
        '--daily-overlap-width': `calc(var(--daily-gallery-height) * ${gradientFactor})`,
        '--daily-pure-photo-width': `calc(var(--daily-gallery-height) * ${purePhotoFactor})`,
        '--daily-content-width': 'calc(100vw - var(--daily-pure-photo-width))',
        '--daily-text-offset': `max(22px, calc(${dailyLayout.textStart}vw - var(--daily-pure-photo-width)))`,
    }
}

// 從後端取得 About 區塊的標題與團隊簡介。
async function loadAboutData() {
    try {
        const response = await fetch('/api/aboutPage/data')

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
        }

        aboutData.value = await response.json()
        photoUrls.value = aboutData.value.aboutPhotos
    } catch (error) {
        console.error('團隊資料載入失敗：', error)
    }
}

// 元件掛載後同時載入照片與文字資料。
onMounted(() => {
    loadAboutData()

    touchMediaQuery = window.matchMedia('(hover: none), (pointer: coarse)')
    usesTouchInteraction.value = touchMediaQuery.matches
    touchMediaQuery.addEventListener('change', updateInteractionMode)
    document.addEventListener('pointerdown', closeDailyCardFromOutside)
})

onUnmounted(() => {
    touchMediaQuery?.removeEventListener('change', updateInteractionMode)
    document.removeEventListener('pointerdown', closeDailyCardFromOutside)
})

// 平板或觸控裝置點擊卡片後保持展開；再次點同一張不負責收合，方便未來加入跳轉。
function activateDailyCard(index) {
    if (!usesTouchInteraction.value) return
    activeDailyCardIndex.value = index
}

// 點擊卡片以外的空白區域時，才將目前展開的卡片復原。
function closeDailyCardFromOutside(event) {
    if (!usesTouchInteraction.value || activeDailyCardIndex.value === null) return
    if (event.target.closest('.daily-card')) return
    activeDailyCardIndex.value = null
}

function updateInteractionMode(event) {
    usesTouchInteraction.value = event.matches
    activeDailyCardIndex.value = null
}

// 根據照片數量計算水平位置、U 形高度與旋轉角度。
function getPhotoStyle(index, total) {
    if (total === 1) {
        return {
            left: '50%',
            top: '20px',
            transform: 'translateX(-50%) rotate(0deg)',
        }
    }

    // normalized 從 -1 到 1，代表由最左到最右。
    const normalized = (index / (total - 1)) * 2 - 1
    const rotation = normalized * 6
    const x = 50 + normalized * 32

    // 左右照片較高、中間照片較低，形成 U 形排列。
    const y = 30 + (1 - Math.abs(normalized)) * 50

    return {
        left: `${x}%`,
        top: `${y}px`,
        transform: `translateX(-50%) rotate(${rotation}deg)`,
    }
}
</script>

<template>
    <!-- DIT Robotics 團隊介紹區塊。 -->
    <section class="about-section">
        <!-- 團隊介紹標題。 -->
        <header class="about-heading">
            <!-- 團隊介紹小標。 -->
            <p class="about-heading-label">{{ aboutData.smallTitle }}</p>
            <!-- 團隊介紹主標題。 -->
            <h2 class="about-heading-title">{{ aboutData.mainTitle }}</h2>
        </header>

        <!-- 以 U 形堆疊排列的團隊照片。 -->
        <div class="photo-stack">
            <!-- 單張團隊照片。 -->
            <img v-for="(photoUrl, index) in photoUrls" :key="photoUrl" class="team-photo" :src="photoUrl"
                :style="getPhotoStyle(index, photoUrls.length)" :alt="`團隊活動照片 ${index + 1}`" />
        </div>

        <!-- 團隊簡介文字。 -->
        <div class="about-description">{{ aboutData.description }}</div>

        <!-- 團隊日常內容標題。 -->
        <h2 class="daily-title">{{ aboutData.dailyTitle }}</h2>

        <!-- 四張橫向鋪滿的日常照片；聚焦時展開該項目的介紹。 -->
        <div class="daily-gallery" :class="{ 'uses-touch': usesTouchInteraction }">
            <article v-for="(detail, index) in (aboutData.moreDetails || []).slice(0, 4)" :key="detail.title"
                class="daily-card" :class="{ 'is-touch-active': activeDailyCardIndex === index }" tabindex="0"
                :style="getDailyCardStyle(index)" @click="activateDailyCard(index)">
                <img v-if="photoUrls.length" class="daily-card-image" :src="photoUrls[index % photoUrls.length]"
                    :alt="detail.title" @load="saveDailyPhotoRatio(index, $event)" />
                <span class="daily-card-image-title">{{ detail.title }}</span>
                <div class="daily-card-content">
                    <h3 class="daily-card-title">{{ detail.title }}</h3>
                    <p class="daily-card-text">{{ detail.detail }}</p>
                </div>
            </article>
        </div>
    </section>
</template>

<style scoped>
.about-section {
    position: relative;
    padding: 120px 8vw 0;
    background: #fafafa;
    z-index: 1;
}

.about-heading {
    max-width: 90vw;
    margin: auto;
    text-align: center;
}

.about-heading-label {
    margin: 0 0 18px;
    letter-spacing: 0.2em;
    font-size: 2vw;
    color: #000000;
    font-weight: 500;
}

.about-heading-title {
    font-size: clamp(42px, 3vw, 72px);
    line-height: 1.15;
    font-weight: 700;
    letter-spacing: 0.2em;
    margin: 0;
}

/* 照片區域 */
.photo-stack {
    position: relative;
    width: min(1400px, 95%);
    height: 450px;
    margin: 50px auto 0;
}

.team-photo {
    position: absolute;
    /*
      不固定 height，
      保留照片原本比例
    */
    width: clamp(240px, 34vw, 480px);
    height: auto;
    display: block;
    border-radius: 28px;
    object-fit: contain;
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.08);
}

.about-description {
    max-width: 900px;
    margin: 70px auto;
    text-align: center;
    font-size: 25px;
    letter-spacing: 0.2em;
    line-height: 2;
    color: #555;
}

.daily-title {
    margin-top: 70px;
    margin-bottom: 80px;

    text-align: center;
    letter-spacing: 0.15em;
    font-size: clamp(26px, 2.5vw, 42px);
    font-weight: 900;
}

/* 團隊日常互動相簿 */
.daily-gallery {
    --daily-gallery-height: clamp(220px, 30vw, 600px);
    display: flex;
    width: calc(100% + 16vw);
    height: var(--daily-gallery-height);
    margin-inline: -8vw;
    margin-bottom: 150px;
    overflow: hidden;
    background: #171717;
}

.daily-card {
    position: relative;
    display: flex;
    flex: 1 1 25%;
    min-width: 0;
    overflow: hidden;
    color: #fff;
    background: var(--Theme-Color);
    outline: none;
    transition: flex-grow 650ms cubic-bezier(0.22, 1, 0.36, 1),
        flex-basis 650ms cubic-bezier(0.22, 1, 0.36, 1),
        border-width 300ms ease;
}

.daily-card + .daily-card {
    border-left: 1px solid rgba(255, 255, 255, 0.3);
}

/* 滑入其中一張時，該項目接管整個相簿，其餘項目同步收合。 */
@media (min-width: 901px) {
    .daily-gallery:not(.uses-touch):has(.daily-card:hover) .daily-card:not(:hover),
    .daily-gallery:has(.daily-card:focus-visible) .daily-card:not(:focus-visible) {
        flex: 0 1 0;
        border-width: 0;
    }

    .daily-gallery:has(.daily-card.is-touch-active) .daily-card:not(.is-touch-active) {
        flex: 0 1 0;
        border-width: 0;
    }

    /* 展開後照片與文字為 1:2。 */
    .daily-gallery:not(.uses-touch) .daily-card:hover .daily-card-image,
    .daily-card:focus-visible .daily-card-image {
        margin-left: 0;
    }

    .daily-card.is-touch-active {
        flex: 1 0 100%;
    }

    .daily-card.is-touch-active .daily-card-image {
        width: var(--daily-expanded-image-width);
        min-width: var(--daily-expanded-image-width);
        flex-basis: var(--daily-expanded-image-width);
        margin-left: 0;
        filter: brightness(1);
    }

    .daily-card.is-touch-active .daily-card-image-title {
        opacity: 0;
    }

    .daily-card.is-touch-active .daily-card-content {
        margin-left: calc(-1 * var(--daily-overlap-width));
        opacity: 1;
        transform: translateX(0);
    }
}

.daily-gallery:not(.uses-touch) .daily-card:hover,
.daily-card:focus-visible {
    flex: 1 0 100%;
}

.daily-card:focus-visible {
    box-shadow: inset 0 0 0 4px #fff;
}

.daily-card-image {
    width: 25vw;
    min-width: 25vw;
    flex: 0 0 25vw;
    height: 100%;
    display: block;
    object-fit: cover;
    filter: brightness(0.82);
    transition: width 650ms cubic-bezier(0.22, 1, 0.36, 1),
        min-width 650ms cubic-bezier(0.22, 1, 0.36, 1),
        flex-basis 650ms cubic-bezier(0.22, 1, 0.36, 1),
        margin-left 650ms cubic-bezier(0.22, 1, 0.36, 1),
        filter 450ms ease;
}

.daily-gallery:not(.uses-touch) .daily-card:hover .daily-card-image,
.daily-card:focus-visible .daily-card-image {
    width: var(--daily-expanded-image-width);
    min-width: var(--daily-expanded-image-width);
    flex-basis: var(--daily-expanded-image-width);
    filter: brightness(1);
}

.daily-card-image-title {
    position: absolute;
    z-index: 2;
    top: 50%;
    left: 0;
    width: 25vw;
    padding: 0 20px;
    color: #fff;
    font-size: clamp(20px, 2.5vw, 50px);
    font-weight: 800;
    letter-spacing: 0.2em;
    text-align: center;
    text-shadow: 0 3px 18px rgba(0, 0, 0, 0.7);
    box-sizing: border-box;
    opacity: 1;
    transform: translateY(-50%);
    pointer-events: none;
    transition: opacity 300ms ease;
}

.daily-gallery:not(.uses-touch) .daily-card:hover .daily-card-image-title,
.daily-card:focus-visible .daily-card-image-title {
    opacity: 0;
}

.daily-card-content {
    position: relative;
    display: flex;
    width: var(--daily-content-width);
    min-width: var(--daily-content-width);
    flex: 0 0 var(--daily-content-width);
    padding: clamp(22px, 3vw, 52px);
    padding-left: var(--daily-text-offset);
    padding-right: 15vw;
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box;
    background: transparent;
    opacity: 0;
    transform: translateX(28px);
    transition: opacity 300ms ease 120ms, transform 450ms ease 100ms,
        margin-left 650ms cubic-bezier(0.22, 1, 0.36, 1);
}

/* 讓照片在文字區左緣自然融入深色背景。 */
.daily-card-content::before,
.daily-card-content::after {
    content: '';
    position: absolute;
    z-index: 0;
    top: 0;
    bottom: 0;
    pointer-events: none;
}

.daily-card-content::before {
    left: 0;
    width: var(--daily-overlap-width);
    background: linear-gradient(to right, transparent, var(--Theme-Color) 100%);
}

.daily-card-content::after {
    right: 0;
    left: var(--daily-overlap-width);
    background: var(--Theme-Color);
}

.daily-gallery:not(.uses-touch) .daily-card:hover .daily-card-content,
.daily-card:focus-visible .daily-card-content {
    margin-left: calc(-1 * var(--daily-overlap-width));
    opacity: 1;
    transform: translateX(0);
}

.daily-card-title {
    position: relative;
    z-index: 1;
    margin: 18px 0 14px;
    font-size: clamp(24px, 2.4vw, 42px);
    line-height: 1.2;
    white-space: nowrap;
    letter-spacing: 0.2em;
}

.daily-card-text {
    position: relative;
    z-index: 1;
    margin: 0;
    color: rgba(255, 255, 255, 0.72);
    font-size: clamp(14px, 1.15vw, 18px);
    line-height: 1.8;
    letter-spacing: 0.1em;
}

/* About 上半部的手機排版；不改動照片堆疊邏輯與下方四張日常卡片。 */
@media (max-width: 600px) {
    .about-section {
        padding-top: 76px;
    }

    .about-heading {
        max-width: 100%;
    }

    .about-heading-label {
        margin: 0 0 14px;
        font-size: 13px;
        line-height: 1.5;
    }

    .about-heading-title {
        font-size: clamp(16px, 8vw, 46px);
        line-height: 1.25;
        letter-spacing: 0.12em;
    }

    .photo-stack {
        height: clamp(250px, 70vw, 340px);
        margin-top: 34px;
        margin-bottom: 0;
    }

    .about-description {
        margin: 24px auto 54px;
        font-size: clamp(15px, 4.2vw, 18px);
        line-height: 1.85;
        letter-spacing: 0.1em;
    }

    .daily-title {
        margin-top: 54px;
        margin-bottom: 52px;
        font-size: clamp(25px, 7vw, 34px);
        line-height: 1.35;
        letter-spacing: 0.1em;
    }
}

@media (max-width: 900px) {
    .daily-gallery {
        height: auto;
        flex-direction: column;
    }

    .daily-card,
    .daily-card:hover,
    .daily-card:focus-visible {
        height: 250px;
        min-height: 250px;
        flex: none;
    }

    .daily-card + .daily-card {
        border-top: 1px solid rgba(255, 255, 255, 0.3);
        border-left: 0;
    }

    .daily-card-image,
    .daily-card:hover .daily-card-image,
    .daily-card:focus-visible .daily-card-image {
        width: 50%;
        min-width: 50%;
        flex-basis: 50%;
        height: 100%;
    }

    .daily-card-content,
    .daily-card:hover .daily-card-content,
    .daily-card:focus-visible .daily-card-content {
        width: 50%;
        min-width: 50%;
        flex-basis: 50%;
        padding: 22px;
        margin-left: 0;
        background: var(--Theme-Color);
        opacity: 1;
        transform: none;
    }

    .daily-card-content::before,
    .daily-card-content::after {
        display: none;
    }

    .daily-card-image-title,
    .daily-card:hover .daily-card-image-title,
    .daily-card:focus-visible .daily-card-image-title {
        width: 50%;
        opacity: 1;
    }

    .daily-card-title {
        white-space: normal;
    }
}

/* 手機版固定為：純照片 1/3｜照片與背景漸層 1/3｜純色背景 1/3。 */
@media (max-width: 600px) {
    .daily-card-image,
    .daily-card:hover .daily-card-image,
    .daily-card:focus-visible .daily-card-image {
        width: 66.666%;
        min-width: 66.666%;
        flex-basis: 66.666%;
    }

    .daily-card-content,
    .daily-card:hover .daily-card-content,
    .daily-card:focus-visible .daily-card-content {
        position: absolute;
        inset: 0;
        width: 100%;
        min-width: 100%;
        padding: 20px 18px 20px 55%;
        background: transparent;
    }

    .daily-card-content::before {
        display: block;
        inset: 0;
        width: auto;
        background: linear-gradient(
            to right,
            transparent 33.333%,
            var(--Theme-Color) 66.666%,
            var(--Theme-Color) 100%
        );
    }

    .daily-card-image-title,
    .daily-card:hover .daily-card-image-title,
    .daily-card:focus-visible .daily-card-image-title {
        display: none;
    }

    .daily-card-title {
        margin: 0 0 10px;
        font-size: clamp(18px, 5.2vw, 23px);
        letter-spacing: 0.1em;
    }

    .daily-card-text {
        font-size: 12px;
        line-height: 1.6;
        letter-spacing: 0.05em;
    }
}

@media (prefers-reduced-motion: reduce) {
    .daily-card,
    .daily-card-image,
    .daily-card-image-title,
    .daily-card-content {
        transition: none;
    }
}
</style>
