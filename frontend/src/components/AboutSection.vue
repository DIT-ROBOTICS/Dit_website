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
    </section>
</template>

<style scoped>
.about-section {
    position: relative;

    padding: 120px 8vw;

    background: #fafafa;

    z-index: 1;
}

.about-section::after {
    content: '';

    position: absolute;

    left: 0;
    bottom: -124px;

    width: 100%;
    height: 125px;

    background: linear-gradient(to bottom,
            #fafafa 0%,
            #fafafa 10%,
            rgba(250, 250, 250, 0.8) 40%,
            rgba(250, 250, 250, 0.4) 70%,
            rgba(250, 250, 250, 0) 100%);

    pointer-events: none;

    z-index: 10;
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
</style>
