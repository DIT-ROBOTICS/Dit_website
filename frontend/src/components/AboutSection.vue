<script setup>
import { onMounted, ref } from 'vue'

// About 區塊的團隊照片與文字資料。
const photoUrls = ref([])
const aboutData = ref({})

// 從後端取得團隊照片清單。
async function loadImages() {
    try {
        const response = await fetch('/api/aboutPageImages')

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
        }

        photoUrls.value = await response.json()
    } catch (error) {
        console.error('圖片載入失敗：', error)
    }
}

// 從後端取得 About 區塊的標題與團隊簡介。
async function loadAboutData() {
    try {
        const response = await fetch('/api/jsonData/AboutData')

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
        }

        aboutData.value = await response.json()
    } catch (error) {
        console.error('團隊資料載入失敗：', error)
    }
}

// 元件掛載後同時載入照片與文字資料。
onMounted(loadImages)
onMounted(loadAboutData)

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
            <p class="about-heading-label">{{ aboutData.SmallTitle }}</p>
            <!-- 團隊介紹主標題。 -->
            <h2 class="about-heading-title">{{ aboutData.MainTitle }}</h2>
        </header>

        <!-- 以 U 形堆疊排列的團隊照片。 -->
        <div class="photo-stack">
            <!-- 單張團隊照片。 -->
            <img v-for="(photoUrl, index) in photoUrls" :key="photoUrl" class="team-photo" :src="photoUrl"
                :style="getPhotoStyle(index, photoUrls.length)" :alt="`團隊活動照片 ${index + 1}`" />
        </div>

        <!-- 團隊簡介文字。 -->
        <div class="about-description">
            <p class="about-description-text">{{ aboutData.description }}</p>
        </div>

        <!-- 團隊日常內容標題。 -->
        <h2 class="daily-title">{{ aboutData.daily_title }}</h2>

        <!-- 四張橫向鋪滿的日常照片；聚焦時展開該項目的介紹。 -->
        <div class="daily-gallery">
            <article v-for="(detail, index) in (aboutData.MoreDetail || []).slice(0, 4)" :key="detail.title"
                class="daily-card" tabindex="0">
                <img v-if="photoUrls.length" class="daily-card-image" :src="photoUrls[index % photoUrls.length]"
                    :alt="detail.title" />
                <div class="daily-card-content">
                    <span class="daily-card-icon" aria-hidden="true">{{ detail.icon }}</span>
                    <h3 class="daily-card-title">{{ detail.title }}</h3>
                    <p class="daily-card-text">DIT 團隊日常，從每一次合作與實作中累積經驗。</p>
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
    letter-spacing: 0.2em;
    font-size: 2vw;
    color: #000000;
    margin-bottom: 18px;
    font-weight: 500;
}

.about-heading-title {
    font-size: clamp(42px, 3vw, 72px);
    line-height: 1.15;
    font-weight: 700;
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
    display: flex;
    width: calc(100% + 16vw);
    height: clamp(220px, 18vw, 340px);
    margin-inline: -8vw;
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
    background: #171717;
    outline: none;
    transition: flex-grow 650ms cubic-bezier(0.22, 1, 0.36, 1),
        flex-basis 650ms cubic-bezier(0.22, 1, 0.36, 1),
        border-width 300ms ease;
}

.daily-card + .daily-card {
    border-left: 1px solid rgba(255, 255, 255, 0.3);
}

/* 滑入其中一張時，該項目接管整個相簿，其餘項目同步收合。 */
@media (min-width: 801px) {
    .daily-gallery:has(.daily-card:hover) .daily-card:not(:hover),
    .daily-gallery:has(.daily-card:focus-visible) .daily-card:not(:focus-visible) {
        flex: 0 1 0;
        border-width: 0;
    }

    /* 固定為初始四等分的寬度，避免展開途中圖片先放大再縮回。 */
    .daily-card-image,
    .daily-card:hover .daily-card-image,
    .daily-card:focus-visible .daily-card-image {
        width: 25vw;
        /* min-width: 25vw; */
    }

    /* 展開後照片中心位於畫面左起 25%，左側留白沿用卡片背景色。 */
    .daily-card:hover .daily-card-image,
    .daily-card:focus-visible .daily-card-image {
        margin-left: 12.5vw;
    }
}

.daily-card:hover,
.daily-card:focus-visible {
    flex: 1 0 100%;
}

.daily-card:focus-visible {
    box-shadow: inset 0 0 0 4px #fff;
}

.daily-card-image {
    width: 25vw;
    /* height: 100%; */
    display: block;
    object-fit: cover;
    filter: brightness(0.82);
    transition: width 650ms cubic-bezier(0.22, 1, 0.36, 1),
        margin-left 650ms cubic-bezier(0.22, 1, 0.36, 1),
        filter 450ms ease;
}

.daily-card:hover .daily-card-image,
.daily-card:focus-visible .daily-card-image {
    width: 25vw;
    filter: brightness(1);
}

.daily-card-content {
    display: flex;
    width: 75vw;
    padding: clamp(22px, 3vw, 52px);
    flex-direction: column;
    justify-content: center;
    box-sizing: border-box;
    opacity: 0;
    transform: translateX(28px);
    transition: opacity 300ms ease 120ms, transform 450ms ease 100ms;
}

.daily-card:hover .daily-card-content,
.daily-card:focus-visible .daily-card-content {
    opacity: 1;
    transform: translateX(0);
}

.daily-card-icon {
    font-size: clamp(28px, 3vw, 48px);
}

.daily-card-title {
    margin: 18px 0 14px;
    font-size: clamp(24px, 2.4vw, 42px);
    line-height: 1.2;
    white-space: nowrap;
}

.daily-card-text {
    margin: 0;
    color: rgba(255, 255, 255, 0.72);
    font-size: clamp(14px, 1.15vw, 18px);
    line-height: 1.8;
}

@media (max-width: 800px) {
    .daily-gallery {
        height: auto;
        flex-direction: column;
    }

    .daily-card,
    .daily-card:hover,
    .daily-card:focus-visible {
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
        width: 55%;
        min-width: 55%;
    }

    .daily-card-content {
        width: 45%;
        min-width: 45%;
        padding: 22px;
        opacity: 1;
        transform: none;
    }

    .daily-card-title {
        white-space: normal;
    }
}

@media (prefers-reduced-motion: reduce) {
    .daily-card,
    .daily-card-image,
    .daily-card-content {
        transition: none;
    }
}
</style>
