<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import heroImageUrl from '@/assets/Hero_Image.png'
import heroVideoUrl from '@/assets/hero背景影片.m4v'
import TitleBar from '@/components/TitleBar.vue'

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
            <!-- 測試靜態圖片時，取消下一行註解並註解掉 video。 -->
            <!-- <img class="hero-background" :src="heroImageUrl" alt="DIT 團隊封面照片" /> -->

            <!-- 自動播放、靜音並循環的封面背景影片。 -->
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

        <!-- 隨封面收合而淡入的獨立頂部導覽。 -->
        <TitleBar :progress="progress" />
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

.hero-cta {
    text-decoration: none;
}

@media (max-width: 900px) {
    .hero-scroll-space {
        height: calc(155svh - 76px);
    }

    .hero {
        height: calc(100svh - var(--progress) * (100svh - 76px));
    }

    .hero-background {
        object-position: 38% center;
        filter: none;
        transform: none;
    }

    .hero-overlay {
        background:
            linear-gradient(180deg, rgba(5, 8, 14, 0.18) 20%, rgba(5, 8, 14, 0.82) 100%),
            linear-gradient(90deg, rgba(5, 8, 14, 0.5), rgba(5, 8, 14, 0.08));
    }

    .hero-content {
        left: clamp(18px, 6vw, 28px);
        right: clamp(18px, 6vw, 28px);
        bottom: clamp(54px, 9svh, 84px);
        max-width: none;
    }

    .hero-eyebrow {
        margin-bottom: 14px;
        font-size: clamp(14px, 4vw, 18px);
        line-height: 1.4;
        word-spacing: 0.12em;
        letter-spacing: 0.08em;
    }

    .hero-title {
        max-width: 100%;
        font-size: clamp(27px, 7.5vw, 38px);
        line-height: 1.15;
        letter-spacing: 0.06em;
    }

    .hero-title-highlight {
        display: block;
        margin-top: 6px;
        font-size: clamp(34px, 9.5vw, 48px);
        line-height: 1.08;
        letter-spacing: 0.035em;
        -webkit-text-stroke-width: 2px;
    }

    .hero-description {
        max-width: 100%;
        margin-top: 20px;
        white-space: normal;
        font-size: clamp(13px, 3.6vw, 16px);
        line-height: 1.75;
        letter-spacing: 0.04em;
    }

    .hero-cta {
        margin-top: 24px;
        padding: 12px 20px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 0.08em;
    }
}

@media (max-width: 380px) {
    .hero-title {
        font-size: 25px;
    }

    .hero-title-highlight {
        font-size: 32px;
    }

    .hero-description {
        font-size: 13px;
    }
}
</style>
