<!--
網站最上面的封面：
帥就對了
-->

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import heroImageUrl from '@/assets/Hero_Image.png'
import logoUrl from '@/assets/dit_logo.png'


const heroContainer = ref(null)
// const progress = ref(0)
const progress = defineModel('progress', { type: Number, default: 0, })

function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max)
}

function updateHeroProgress() {
    const element = heroContainer.value

    if (!element) {
        return
    }

    const rect = element.getBoundingClientRect()

    const animationDistance = element.offsetHeight - window.innerHeight

    if (animationDistance <= 0) {
        progress.value = 0
        return
    }

    progress.value = clamp(-rect.top / animationDistance, 0, 1)
}

onMounted(() => {
    updateHeroProgress()

    window.addEventListener(
        'scroll',
        updateHeroProgress,
        { passive: true },
    )

    window.addEventListener(
        'resize',
        updateHeroProgress,
    )
})

onUnmounted(() => {
    window.removeEventListener(
        'scroll',
        updateHeroProgress,
    )

    window.removeEventListener(
        'resize',
        updateHeroProgress,
    )
})
</script>

<template>
    <section ref="heroContainer" class="hero-scroll-space">
        <div class="hero" :style="{ '--progress': progress }">
            <img class="hero-background" :src="heroImageUrl" alt="DIT 團隊封面照片">

            <div class="hero-overlay"></div>

            <div class="hero-content">
                <p class="hero-eyebrow">
                    We Do Improve and Try
                </p>

                <h1>We are <span>DIT Robotics</span>
                </h1>

                <div class="hero-description">
                    我們來自清華大學，一群勇於追逐夢想，實現理想的大學生<br>
                    邀請你看看我們的故事吧～
                    <!-- <img src="@/assets/image/Canva_Arrow.png" alt="arrow" style="width: 5vw; height: 10px;"> -->
                </div>

                <a href="#team">
                    認識團隊
                </a>
            </div>

        </div>
        <Teleport to="body">
            <div class="title-bar" :style="{ '--progress': progress }">
                <a href="#hero" class="title-brand">
                    <img :src="logoUrl" alt="DIT Logo">
                    <strong>DIT Robotics</strong>
                </a>
                <nav>
                    <a href="#team">團隊</a>
                    <a href="#EurobotSection">Eurobot</a>
                    <a href="#robotArchive">歷年機器人</a>
                    <a href="#competitions">其他競賽</a>
                    <a href="#advisors">指導教授</a>
                    <a href="#sponsors">贊助商</a>
                    <a href="#contact">聯絡</a>
                </nav>
            </div>
        </Teleport>
    </section>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=League+Spartan:wght@400;500;600;700;800&display=swap');

.hero-scroll-space {
    position: relative;
    height: calc(160vh - 76px);
    /*calc( 100vh - var(--progress) * (100vh - 76px) );*/

    min-height: 76px;
}

.hero {
    position: sticky;
    top: 0;
    z-index: 20;

    height: calc(100vh - var(--progress) * (100vh - 76px));

    min-height: 76px;

    overflow: hidden;
    color: white;
    background: #111;
    box-shadow:
        0 calc(var(--progress) * 8px) calc(var(--progress) * 30px) rgba(0, 0, 0, 0.18);
}

.hero-background {
    position: absolute;
    inset: 0;

    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: left 70%;

    opacity:
        calc(1 - var(--progress) * 0.82);

    transform:
        scale(calc(1 + var(--progress) * 0.08));

    filter:
        blur(calc(var(--progress) * 5px));
}

.hero-overlay {
    position: absolute;
    inset: 0;

    background:
        linear-gradient(90deg,
            rgba(5, 8, 14, 0.7),
            rgba(5, 8, 14, 0.25));

    opacity:
        calc(1 - var(--progress) * 0.5);
}

.hero-content {
    position: absolute;
    left: 8vw;
    bottom: 9vh;
    z-index: 2;

    max-width: 70vw;

    opacity:
        calc(1 - var(--progress) * 1.5);

    transform:
        translateY(calc(var(--progress) * -60px));

    pointer-events:
        calc(1 - var(--progress));
}

.hero-eyebrow {
    margin: 0 0 18px;
    font-size: 2.6vw;
    font-weight: 900;
    word-spacing: 0.2em;
    letter-spacing: 0.1em;
    /* font-family: 'League Spartan', sans-serif; */
    font-family:'Orbitron',sans-serif;
}

.hero-content h1 {
    margin: 0;
    font-size: 4vw;
    line-height: 1;
    letter-spacing: 0.1em;
    /* font-family: 'League Spartan', sans-serif; */
    font-family:'Orbitron',sans-serif;
}

.hero-content h1 span {
    font-family:'Orbitron',sans-serif;
    font-size: 5vw;
    letter-spacing: 0.07em;
    font-weight: 900;
    color: #8594c9;
    -webkit-text-stroke:3px currentColor;
    text-shadow:0px 3px 5px #000000;
}

.hero-description {
    white-space: nowrap;
    max-width: 600px;
    margin: 26px 0 0;
    color: rgba(255, 255, 255, 0.72);
    line-height: 1.9;
    font-size: 1.3vw;
    letter-spacing: 0.1em;
}

.hero-content>a {
    display: inline-block;
    margin-top: 30px;
    padding: 13px 22px;
    border-radius: 15px;
    background: white;
    color: #111;
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
    padding: 0 clamp(20px, 5vw, 72px);
    display: flex;
    align-items: center;
    gap: 14px;
    opacity: var(--progress);
    color: white;
    transform: translateY(calc((1 - var(--progress)) * -24px));
    background: rgba(10, 12, 17, 1);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
}

.title-brand{
    display:flex;
    align-items:center;
    gap:14px;
    margin-right:auto;
    color:white;
    text-decoration:none;
    cursor:pointer;
}

.title-brand img{
    width:42px;
    height:42px;
    object-fit:contain;
    border-radius: 10px;
}

.title-brand strong{
    font-size:16px;
}

.title-bar nav {
    display: flex;
    align-items: center;
    gap: clamp(14px, 2.4vw, 32px);
}

.title-bar nav a {
    color: rgba(255, 255, 255, 0.72);
    font-size: 13px;
    text-decoration: none;
    transition:
        color 0.2s ease,
        transform 0.2s ease;
}

.title-bar nav a:hover {
    color: white;
    transform: translateY(-1px);
}

.scroll-indicator {
    position: absolute;
    right: 45px;
    bottom: 45px;
    z-index: 3;

    display: flex;
    align-items: center;
    gap: 13px;

    opacity:
        calc(1 - var(--progress) * 2);

    font-size: 10px;
    letter-spacing: 0.2em;
}

.scroll-indicator i {
    width: 52px;
    height: 1px;
    background: rgba(255, 255, 255, 0.5);
}

.fixed-title-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 100;

    height: 76px;
    padding: 0 clamp(20px, 5vw, 72px);

    display: flex;
    align-items: center;
    gap: 14px;

    color: white;
    background: rgba(10, 12, 17, 0.88);
    backdrop-filter: blur(18px);

    opacity: 0;
    visibility: hidden;
    transform: translateY(-100%);

    transition:
        opacity 0.25s ease,
        visibility 0.25s ease,
        transform 0.25s ease;
}

.fixed-title-bar.visible {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.page-content {
    position: relative;
    z-index: 1;

    min-height: 100vh;
    background: #f5f5f3;
}

.team-section {
    scroll-margin-top: 76px;

    padding:
        clamp(110px, 12vw, 180px) clamp(24px, 8vw, 120px);
}

.arrow-line {
    position: relative;
    width: 140px;
    height: 2px;
    background: white;

    transform: rotate(-2deg);
}

.arrow-line::after {
    content: "";
    position: absolute;
    right: 0;
    top: 50%;

    width: 18px;
    height: 18px;

    border-top: 2px solid white;
    border-right: 2px solid white;

    transform: translateY(-50%) rotate(45deg);
}

@media (max-width: 760px) {
    .title-bar nav {
        display: none;
    }

    .hero-content {
        left: 24px;
        right: 24px;
        bottom: 80px;
    }

    .scroll-indicator {
        display: none;
    }
}
</style>