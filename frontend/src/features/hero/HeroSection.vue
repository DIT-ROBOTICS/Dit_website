<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import heroImageUrl from '@/assets/Hero_Image.png'
import TitleBar from '@/components/layout/TitleBar.vue'
import { heroApi } from '@/features/hero/heroApi'

const platform=window.innerWidth<=600?'mobile':'desktop'
const heroVideoUrl = heroApi.video(platform)
const heroContainer = ref(null)
const heroVideo = ref(null)
const progress = defineModel('progress', { type: Number, default: 0 })

const HERO_VIDEO_READY_EVENT = 'hero-video-download-ready'
const HERO_VIDEO_PLAYABLE_EVENT = 'hero-video-playable'
const HERO_VIDEO_FAILED_EVENT = 'hero-video-failed'
const STARTUP_FINISHED_EVENT = 'startup-animation-finished'
const startupAlreadyFinished = Boolean(sessionStorage.getItem('startupFinished'))
const heroVideoFailed = ref(false)
let downloadedVideoUrl = ''
let heroVideoPlayableReported = false
let heroAudioEnabled = false

// Hero 收合進度 0~1 對應音量 1~0；尚未有使用者操作前維持靜音。
function syncHeroVideoVolume() {
    const video = heroVideo.value
    if (!video) return

    const volume = Math.min(Math.max(1 - progress.value, 0), 1)
    video.volume = volume
    video.muted = !heroAudioEnabled || volume <= 0.01

    if (video.muted) {
        video.setAttribute('muted', '')
    } else {
        video.removeAttribute('muted')
    }
}

// Safari 對動態換入的影片來源較嚴格：必須先設定靜音屬性，再設定 src。
function prepareHeroVideo(source) {
    const video = heroVideo.value
    if (!video || !source) return

    video.muted = true
    video.defaultMuted = true
    video.volume = 0
    video.setAttribute('muted', '')
    video.setAttribute('playsinline', '')
    video.src = source
    video.load()

    // 在啟動畫面還在時就申請靜音自動播放，不延遲到進入 Hero 才申請。
    video.play().catch(() => {
        // Safari 低耗電模式或使用者禁止自動播放時，改由第一次觸控恢復。
    })
}

// StartupAnimation 完整下載影片後，將 Blob URL 交給真正的 video 元素解析。
async function receiveDownloadedHeroVideo(event) {
    downloadedVideoUrl = event.detail?.url || ''

    // 10 秒逾時時可能正顯示圖片；下載完成後先重建 video，再交付 Blob URL。
    heroVideoFailed.value = false
    await nextTick()
    prepareHeroVideo(downloadedVideoUrl)
}

// Blob 已完整下載，且 video 確認可播放後，才允許啟動畫面進入起飛階段。
function notifyHeroVideoPlayable() {
    if (!startupAlreadyFinished && downloadedVideoUrl && !heroVideoPlayableReported) {
        heroVideoPlayableReported = true
        window.dispatchEvent(new CustomEvent(HERO_VIDEO_PLAYABLE_EVENT))
    }
}

// 下載成功不代表影片可解碼；video error 時改用預設封面並解除啟動畫面等待。
function handleHeroVideoFailed() {
    heroVideoFailed.value = true

    if (downloadedVideoUrl.startsWith('blob:')) {
        URL.revokeObjectURL(downloadedVideoUrl)
    }

    downloadedVideoUrl = ''
}

function notifyHeroVideoError() {
    window.dispatchEvent(new CustomEvent(HERO_VIDEO_FAILED_EVENT))
}

function playHeroVideo() {
    const video = heroVideo.value
    if (!video) return

    syncHeroVideoVolume()
    if (video.paused) video.play().catch(() => {})
}

// 每次點擊都在有聲與靜音之間切換；第一次點擊同時滿足瀏覽器的有聲播放限制。
function toggleHeroAudio() {
    const video = heroVideo.value
    if (!video?.src) return

    heroAudioEnabled = !heroAudioEnabled
    syncHeroVideoVolume()

    if (heroAudioEnabled) playHeroVideo()
}

// 啟動畫面結束後才從頭播放，避免動畫期間消耗剛緩衝好的內容。
function startHeroVideoPlayback() {
    const video = heroVideo.value
    if (!video) return

    video.currentTime = 0

    // 影片已在啟動畫面後方靜音自動播放，通常不需要再呼叫 play()。
    // 僅在瀏覽器曾意外暫停時嘗試恢復，避免 Safari 拒絕延遲的自動播放請求。
    playHeroVideo()
}

function updateHeroProgress() {
    const element = heroContainer.value

    if (!element) return

    const rect = element.getBoundingClientRect()
    const animationDistance = element.offsetHeight - window.innerHeight

    if (animationDistance <= 0) {
        progress.value = 0
        syncHeroVideoVolume()
        return
    }

    const rawProgress = -rect.top / animationDistance
    progress.value = Math.min(Math.max(rawProgress, 0), 1)
    syncHeroVideoVolume()
}

onMounted(() => {
    updateHeroProgress()

    if (startupAlreadyFinished) prepareHeroVideo(heroVideoUrl)

    window.addEventListener(HERO_VIDEO_READY_EVENT, receiveDownloadedHeroVideo)
    window.addEventListener(HERO_VIDEO_FAILED_EVENT, handleHeroVideoFailed)
    window.addEventListener(STARTUP_FINISHED_EVENT, startHeroVideoPlayback)

    window.addEventListener('scroll', updateHeroProgress, { passive: true })
    window.addEventListener('resize', updateHeroProgress)
})

onUnmounted(() => {
    window.removeEventListener(HERO_VIDEO_READY_EVENT, receiveDownloadedHeroVideo)
    window.removeEventListener(HERO_VIDEO_FAILED_EVENT, handleHeroVideoFailed)
    window.removeEventListener(STARTUP_FINISHED_EVENT, startHeroVideoPlayback)
    window.removeEventListener('scroll', updateHeroProgress)
    window.removeEventListener('resize', updateHeroProgress)

    if (downloadedVideoUrl.startsWith('blob:')) URL.revokeObjectURL(downloadedVideoUrl)
})
</script>

<template>
    <!-- 提供捲動動畫所需的垂直空間。 -->
    <section ref="heroContainer" class="hero-scroll-space">
        <!-- 會隨捲動進度收合的首頁封面。 -->
        <div class="hero" :style="{ '--progress': progress }" @click="toggleHeroAudio">
            <!-- 影片超過 10 秒或解碼失敗時，在預設啟動畫後方載入圖片封面。 -->
            <img v-if="heroVideoFailed" class="hero-background" :src="heroImageUrl" alt="DIT 團隊封面照片" />

            <!-- 自動播放、靜音並循環的封面背景影片。 -->
            <video v-else ref="heroVideo" class="hero-background"
                autoplay muted loop playsinline preload="auto"
                @canplay="notifyHeroVideoPlayable" @error="notifyHeroVideoError"></video>

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
