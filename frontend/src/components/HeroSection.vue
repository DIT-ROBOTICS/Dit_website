<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import heroImageUrl from '@/assets/Hero_Image.png'
import heroVideoUrl from '@/assets/hero背景影片.m4v'
import logoUrl from '@/assets/dit_logo.png'

const heroContainer = ref(null)
const progress = defineModel('progress', { type: Number, default: 0 })

function updateHeroProgress() {
    const element = heroContainer.value

    if (!element) return

    const rect = element.getBoundingClientRect()
    const animationDistance = element.offsetHeight - window.innerHeight

    if (animationDistance <= 0) {
        progress.value = 0
        return
    }

    const rawProgress = -rect.top / animationDistance
    progress.value = Math.min(Math.max(rawProgress, 0), 1)
}

onMounted(() => {
    updateHeroProgress()

    window.addEventListener('scroll', updateHeroProgress, { passive: true })
    window.addEventListener('resize', updateHeroProgress)
})

onUnmounted(() => {
    window.removeEventListener('scroll', updateHeroProgress)
    window.removeEventListener('resize', updateHeroProgress)
})
</script>

<template>
    <!-- 提供捲動動畫所需的垂直空間。 -->
    <section ref="heroContainer" class="hero-scroll-space">
        <!-- 會隨捲動進度收合的首頁封面。 -->
        <div class="hero" :style="{ '--progress': progress }">
            <!-- 封面背景圖。 -->
            <!-- <img class="hero-background" :src="heroImageUrl" alt="DIT 團隊封面照片" /> -->
            <video class="hero-background" :src="heroVideoUrl" autoplay muted loop playsinline preload="auto"></video>

            <!-- 深色漸層遮罩，提高文字可讀性。 -->
            <div class="hero-overlay"></div>

            <!-- 封面主文字區。 -->
            <div class="hero-content">
                <!-- 團隊精神標語。 -->
                <p class="hero-eyebrow">Do, Improve, and Try</p>

                <!-- 網站主標題。 -->
                <h1 class="hero-title">We are <span class="hero-title-highlight">DIT Robotics</span></h1>

                <!-- 團隊簡介。 -->
                <p class="hero-description">
                    我們來自清華大學，一群勇於追逐夢想，實現理想的大學生<br />
                    邀請你看看我們的故事吧～
                </p>

                <!-- 前往團隊介紹的主要按鈕。 -->
                <a class="hero-cta" href="#aboutSection">認識團隊</a>
            </div>
        </div>

        <!-- 將頂部導覽掛載到 body，避免受封面容器裁切。 -->
        <Teleport to="body">
            <!-- 隨封面收合而淡入的頂部導覽。 -->
            <header class="title-bar" :style="{ '--progress': progress }">
                <!-- 回到首頁的品牌連結。 -->
                <a href="#hero" class="title-brand">
                    <!-- DIT 品牌 Logo。 -->
                    <img class="title-brand-logo" :src="logoUrl" alt="DIT Logo" />
                    <!-- DIT 品牌名稱。 -->
                    <strong class="title-brand-name">DIT Robotics</strong>
                </a>

                <!-- 網站主要區塊導覽。 -->
                <nav class="title-navigation" aria-label="主要導覽">
                    <a class="title-navigation-link" href="#aboutSection">團隊</a>
                    <a class="title-navigation-link" href="#EurobotSection">Eurobot</a>
                    <a class="title-navigation-link" href="#robotArchive">歷年機器人</a>
                    <a class="title-navigation-link" href="#competitions">其他競賽</a>
                    <a class="title-navigation-link" href="#advisors">指導教授</a>
                    <a class="title-navigation-link" href="#sponsors">贊助商</a>
                    <a class="title-navigation-link" href="#contact">聯絡</a>
                </nav>
            </header>
        </Teleport>
    </section>
</template>

<style scoped>
.hero-scroll-space {
    position: relative;
    height: calc(160vh - 76px);
}

.hero-scroll-space,
.hero {
    min-height: 76px;
}

.hero {
    position: sticky;
    top: 0;
    z-index: 20;
    height: calc(100vh - var(--progress) * (100vh - 76px));
    overflow: hidden;
    color: white;
    background: #111;
    box-shadow: 0 calc(var(--progress) * 8px) calc(var(--progress) * 30px) rgba(0, 0, 0, 0.18);
}

.hero-background,
.hero-overlay {
    position: absolute;
    inset: 0;
}

.hero-background {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: left 70%;

    opacity: calc(1 - var(--progress) * 0.82);

    transform: scale(calc(1 + var(--progress) * 0.08));

    filter: blur(calc(var(--progress) * 5px));
}

.hero-overlay {
    background: linear-gradient(90deg, rgba(5, 8, 14, 0.7), rgba(5, 8, 14, 0.25));

    opacity: calc(1 - var(--progress) * 0.5);
}

.hero-content {
    position: absolute;
    left: 8vw;
    bottom: 9vh;
    z-index: 2;

    max-width: 70vw;

    opacity: calc(1 - var(--progress) * 1.5);

    transform: translateY(calc(var(--progress) * -60px));
}

.hero-eyebrow,
.hero-title,
.hero-title-highlight {
    font-family: 'Orbitron', sans-serif;
}

.hero-eyebrow,
.hero-title,
.hero-description {
    margin: 0;
}

.hero-eyebrow {
    margin-bottom: 18px;
    font-size: 2.6vw;
    font-weight: 900;
    word-spacing: 0.2em;
    letter-spacing: 0.1em;
}

.hero-title {
    font-size: 4vw;
    line-height: 1;
    letter-spacing: 0.1em;
}

.hero-title-highlight {
    font-size: 5vw;
    letter-spacing: 0.07em;
    font-weight: 900;
    color: #8594c9;
    -webkit-text-stroke: 3px currentColor;
    text-shadow: 0 3px 5px #000;
}

.hero-description {
    white-space: nowrap;
    max-width: 600px;
    margin-top: 26px;
    color: rgba(255, 255, 255, 0.72);
    line-height: 1.9;
    font-size: 1.3vw;
    letter-spacing: 0.1em;
}

.hero-cta {
    display: inline-block;
    margin-top: 30px;
    padding: 13px 22px;
    border-radius: 15px;
    background: white;
    color: #111;
}

.title-bar,
.title-brand,
.title-navigation {
    display: flex;
    align-items: center;
}

.title-bar,
.title-brand {
    gap: 14px;
}

.hero-cta,
.title-brand,
.title-navigation-link {
    text-decoration: none;
}

.title-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 54;
    box-sizing: border-box;
    height: 76px;
    padding-inline: 5vw;
    opacity: var(--progress);
    color: white;
    transform: translateY(calc((1 - var(--progress)) * -24px));
    background: rgba(10, 12, 17, 1);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
}

.title-brand {
    margin-right: auto;
    color: white;
    cursor: pointer;
}

.title-brand-logo {
    width: 42px;
    height: 42px;
    object-fit: contain;
    border-radius: 10px;
}

.title-brand-name {
    font-size: 16px;
}

.title-navigation {
    gap: 2.4vw;
}

.title-navigation-link {
    color: rgba(255, 255, 255, 0.72);
    font-size: 13px;
    transition:
        color 0.2s ease,
        transform 0.2s ease;
}

.title-navigation-link:hover {
    color: white;
    transform: translateY(-1px);
}

@media (max-width: 760px) {
    .title-bar {
        gap: 10px;
        padding-inline: 16px;
    }

    .title-brand {
        flex-shrink: 0;
    }

    .title-brand-name {
        display: none;
    }

    .title-navigation {
        min-width: 0;
        flex: 1;
        gap: 18px;
        overflow-x: auto;
        overscroll-behavior-x: contain;
        scrollbar-width: none;
    }

    .title-navigation::-webkit-scrollbar {
        display: none;
    }

    .title-navigation-link {
        flex-shrink: 0;
        white-space: nowrap;
    }

    .hero-content {
        left: 24px;
        right: 24px;
        bottom: 80px;
    }
}

/* 小螢幕保留導覽列兩側的最小留白。 */
@media (max-width: 400px) {
    .title-bar {
        padding-inline: 12px;
    }
}

/* 大螢幕限制導覽列留白與連結間距，維持原本版面上限。 */
@media (min-width: 1333.34px) {
    .title-navigation {
        gap: 32px;
    }
}

@media (min-width: 1440px) {
    .title-bar {
        padding-inline: 72px;
    }
}
</style>
