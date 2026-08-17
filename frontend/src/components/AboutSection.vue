<!--
團隊的介紹：

-->
<script setup>
import { onMounted, ref } from 'vue'

const images = ref([])
const loadData = ref({})
const MoreDetail = ref([])
const ThemeColor = ref("")

async function loadImages() {
    try {
        const response = await fetch('/api/aboutPageImages')

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
        }

        images.value = await response.json()

        console.log(images.value)
    } catch (error) {
        console.error('圖片載入失敗：', error)
    }
}

async function loadAboutData() {
    try {
        const response = await fetch('/api/jsonData/AboutData')

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
        }

        const jsonfile = await response.json()
        loadData.value = jsonfile
        MoreDetail.value = jsonfile.MoreDetail
        ThemeColor.value = jsonfile.ThemeColor
    } catch (error) {
        console.error(error)
        // errorMessage.value = '資料載入失敗'
    } finally {
        // loading.value = false
    }
}

onMounted(loadImages)
onMounted(loadAboutData)

function goToLink(item) {
    if (item.link) {
        window.open(item.link, '_blank')
    } else if (item.html) {
        window.open(item.html, '_blank')
    }
}

function getPhotoStyle(index, total) {
    if (total === 1) {
        return {
            left: '50%',
            top: '20px',
            transform: 'translateX(-50%) rotate(0deg)',
            zIndex: 1
        }
    }

    // -1 ~ 1
    const normalized = (index / (total - 1)) * 2 - 1

    // 左 → 負角度
    // 右 → 正角度
    const rotation = normalized * 6

    // 水平方向散開
    //
    // 最左約 18%
    // 中間約 50%
    // 最右約 82%
    const x = 50 + normalized * 32

    /*
      做成 U 型：
  
      左右照片比較高
      中間照片比較低
  
      normalized:
      -1      0      1
       ↑      ↓      ↑
    */
    const y = 30 + (1 - Math.abs(normalized)) * 50

    return {
        left: `${x}%`,
        top: `${y}px`,
        transform: `
      translateX(-50%)
      rotate(${rotation}deg)
    `,
        index
    }
}
</script>

<template>
    <section class="about-section">

        <div class="title">

            <p>{{ loadData.SmallTitle }}</p>

            <h2>{{ loadData.MainTitle }}</h2>

        </div>

        <div class="photo-stack">
            <img v-for="(image, index) in images" :src="image" :style="getPhotoStyle(index, images.length)"
                class="photo" alt="">
        </div>

        <div class="description">
            <p>{{ loadData.description }}</p>
        </div>
        <h2 class="daily-title">{{ loadData.daily_title }}</h2>

        <div class="department-grid" :style="{'--button-color':ThemeColor}">
            <div v-for="item in MoreDetail" :key="item.title" class="department-card" @click="goToLink(item)">
                <svg class="card-border" viewBox="0 0 600 180" preserveAspectRatio="none">
                    <rect x="3" y="3" width="594" height="174" rx="19" ry="19" />
                </svg>

                <div class="department-content">
                    <span class="icon">
                        {{ item.icon }}
                    </span>

                    <h3>
                        {{ item.title }}
                    </h3>
                </div>
            </div>
        </div>
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
    content: "";

    position: absolute;

    left: 0;
    bottom: -124px;

    width: 100%;
    height: 125px;

    background: linear-gradient(
        to bottom,
        #fafafa 0%,
        #fafafa 10%,
        rgba(250, 250, 250, 0.8) 40%,
        rgba(250, 250, 250, 0.4) 70%,
        rgba(250, 250, 250, 0) 100%
    );

    pointer-events: none;

    z-index: 10;
}

.title {
    max-width: 90vw;
    margin: auto;
    text-align: center;
}

.title p {
    letter-spacing: .2em;
    font-size: 2vw;
    color: #000000;
    margin-bottom: 18px;
    font-weight: 500;
}

.title h2 {
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

.photo {
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

    box-shadow:
        0 18px 45px rgba(0, 0, 0, 0.08);

    transition:
        transform 0.35s ease,
        filter 0.35s ease;
}

.description {
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
    letter-spacing: .15em;
    font-size: clamp(26px, 2.5vw, 42px);
    font-weight: 900;
}


/* 2 × 2 */
.department-grid {
    width: min(1300px, 90%);
    margin: 0 auto;

    display: grid;
    grid-template-columns: repeat(4, 1fr);

    column-gap: 5vw;
    row-gap: 100px;
}


/* 卡片 */
.department-card {
    position: relative;

    aspect-ratio: 2.8/1;

    display: flex;
    align-items: center;
    justify-content: center;

    background: #fafafa;

    border-radius: 19px;

    cursor: pointer;

    isolation: isolate;
    transform: scale(1);
    transition: transform .25s ease;
}


/* 右下藍色底 */
.department-card::after {
    content: "";

    position: absolute;

    top: 18px;
    left: 18px;

    width: 100%;
    height: 100%;

    border-radius: 19px;

    background: var(--button-color);

    z-index: -2;

    transition: .25s;
}


/* 白色本體，把藍色底遮住 */
.department-card::before {
    content: "";

    position: absolute;
    inset: 0;

    border-radius: 38px;

    background: #fafafa;

    z-index: -1;
}


/* SVG 虛線邊框 */
.card-border {
    position: absolute;
    inset: 0;

    width: 100%;
    height: 100%;

    overflow: visible;

    pointer-events: none;
}

.card-border rect {
    fill: none;

    stroke: var(--button-color);
    stroke-width: 7px;

    /*
        50px 藍線
        8px 空白
    */
    stroke-dasharray: 42 7;

    stroke-linecap: butt;
}


/* 中央內容 */
.department-content {
    display: flex;
    align-items: center;
    justify-content: center;

    gap: 18px;

    white-space: nowrap;
}

.department-content .icon {
    font-size: 42px;
    margin: 0;
}

.department-content h3 {
    margin: 0;

    font-size: clamp(28px, 2.5vw, 46px);
    font-weight: 900;

    letter-spacing: .12em;

    color: #111;
}


/* hover */
.department-card:hover {
    transform: scale(1.05);
    transition: transform .25s ease;
}


/* @media(max-width:900px) {
    .department-grid {
        grid-template-columns:
            repeat(2, 1fr);
    }
} */
</style>