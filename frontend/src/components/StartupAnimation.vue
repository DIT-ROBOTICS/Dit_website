<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import logoUrl from '@/assets/dit_logo.png'

const emit = defineEmits(['finished'])
const platform=window.innerWidth<=600?'mobile':'desktop'
const heroVideoUrl=`/api/heroVideo/${platform}`
const props = defineProps({
  trackHeroVideo: {
    type: Boolean,
    default: false,
  },
})

const PROGRESS_UPDATE_INTERVAL_MS = 20
const LAUNCH_DELAY_MS = 200
const SCREEN_DISMISS_DELAY_MS = 1800
const HERO_VIDEO_VALIDATION_TIMEOUT_MS = 8000
const HERO_VIDEO_READY_EVENT = 'hero-video-download-ready'
const HERO_VIDEO_PLAYABLE_EVENT = 'hero-video-playable'
const HERO_VIDEO_FAILED_EVENT = 'hero-video-failed'

const loadingProgress = ref(0)
const isLaunching = ref(false)

// 載入過半後顯示歡迎文字，起飛時立即隱藏。
const shouldShowWelcome = computed(
  () => loadingProgress.value >= 50 && !isLaunching.value,
)

let progressIntervalId
let launchTimeoutId
let finishTimeoutId
let videoValidationTimeoutId
let launchStarted = false
let videoDownloadController
let defaultAnimationStarted = false

function startLaunchSequence() {
  if (launchStarted) return
  launchStarted = true
  window.clearInterval(progressIntervalId)

  // 短暫停留在 100%，再開始 Logo 起飛動畫。
  launchTimeoutId = window.setTimeout(() => {
    isLaunching.value = true
  }, LAUNCH_DELAY_MS)

  // 通知父元件移除啟動畫畫面。
  finishTimeoutId = window.setTimeout(() => {
    emit('finished')
  }, LAUNCH_DELAY_MS + SCREEN_DISMISS_DELAY_MS)
}

function handleHeroVideoPlayable() {
  if (defaultAnimationStarted) return
  window.clearTimeout(videoValidationTimeoutId)
  loadingProgress.value = 100
  startLaunchSequence()
}

// 影片取得失敗或 Hero 無法解碼時，不再等待影片事件，改播一般啟動動畫。
function startDefaultAnimation() {
  if (defaultAnimationStarted || launchStarted) return

  defaultAnimationStarted = true
  videoDownloadController?.abort()
  window.clearTimeout(videoValidationTimeoutId)
  window.removeEventListener(HERO_VIDEO_PLAYABLE_EVENT, handleHeroVideoPlayable)
  loadingProgress.value = 0
  startLoadingProgress()
}

function handleHeroVideoFailed() {
  startDefaultAnimation()
}

// 完整下載影片並建立 Blob URL，確保 Hero 不需要再次發出影片請求。
async function downloadHeroVideo() {
  videoDownloadController = new AbortController()

  try {
    const response = await fetch(heroVideoUrl, {
      signal: videoDownloadController.signal,
    })

    if (!response.ok) throw new Error(`Hero video HTTP ${response.status}`)
    if (!response.body) throw new Error('瀏覽器不支援串流下載影片')

    const totalBytes = Number(response.headers.get('content-length'))
    const contentType = response.headers.get('content-type') || 'video/mp4'
    const reader = response.body.getReader()
    const chunks = []
    let loadedBytes = 0

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      chunks.push(value)
      loadedBytes += value.byteLength

      if (totalBytes > 0) {
        // 保留最後 1%，直到 Blob 已建立且 video 元素確認 canplay。
        loadingProgress.value = Math.min((loadedBytes / totalBytes) * 99, 99)
      } else {
        const estimateBase = 20 * 1024 * 1024
        loadingProgress.value = Math.min(95 * (1 - Math.exp(-loadedBytes / estimateBase)), 95)
      }
    }

    if (loadedBytes === 0) throw new Error('Hero video file is empty')

    loadingProgress.value = 99
    const videoBlob = new Blob(chunks, { type: contentType })
    const videoObjectUrl = URL.createObjectURL(videoBlob)

    window.dispatchEvent(new CustomEvent(HERO_VIDEO_READY_EVENT, {
      detail: { url: videoObjectUrl },
    }))

    // 某些損毀檔案不會立即觸發 video error，以逾時避免進度永遠停在 99%。
    videoValidationTimeoutId = window.setTimeout(() => {
      window.dispatchEvent(new CustomEvent(HERO_VIDEO_FAILED_EVENT))
      startDefaultAnimation()
    }, HERO_VIDEO_VALIDATION_TIMEOUT_MS)
  } catch (error) {
    if (error?.name === 'AbortError') return

    console.error('Hero 影片下載失敗：', error)
    window.dispatchEvent(new CustomEvent(HERO_VIDEO_FAILED_EVENT))
    startDefaultAnimation()
  }
}

function startLoadingProgress() {
  progressIntervalId = window.setInterval(() => {
    loadingProgress.value += 1

    if (loadingProgress.value >= 100) {
      loadingProgress.value = 100
      startLaunchSequence()
    }
  }, PROGRESS_UPDATE_INTERVAL_MS)
}

function clearAnimationTimers() {
  window.clearInterval(progressIntervalId)
  window.clearTimeout(launchTimeoutId)
  window.clearTimeout(finishTimeoutId)
  window.clearTimeout(videoValidationTimeoutId)
  videoDownloadController?.abort()
}

onMounted(() => {
  if (!props.trackHeroVideo) {
    startLoadingProgress()
    return
  }

  window.addEventListener(HERO_VIDEO_PLAYABLE_EVENT, handleHeroVideoPlayable)
  window.addEventListener(HERO_VIDEO_FAILED_EVENT, handleHeroVideoFailed)
  downloadHeroVideo()
})

onUnmounted(() => {
  clearAnimationTimers()
  window.removeEventListener(HERO_VIDEO_PLAYABLE_EVENT, handleHeroVideoPlayable)
  window.removeEventListener(HERO_VIDEO_FAILED_EVENT, handleHeroVideoFailed)
})
</script>

<template>
  <div class="startup-screen">
    <div class="logo-wrapper" :class="{ launching: isLaunching }">
      <div class="progress-ring" :style="{ '--progress': loadingProgress }">
        <svg viewBox="0 0 180 180">
          <circle class="progress-track" cx="90" cy="90" r="80" />
          <circle class="progress-value" cx="90" cy="90" r="80" />
        </svg>
        <img class="startup-logo" :src="logoUrl" alt="DIT Logo" />
      </div>

      <Transition name="welcome">
        <p v-if="shouldShowWelcome" class="welcome-text">
          WELCOME TO DIT ROBOTICS
        </p>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
.startup-screen {
  --launch-animation: 1.8s cubic-bezier(0.25, 0.75, 0.25, 1) forwards;

  position: fixed;
  inset: 0;
  z-index: 9999;
  overflow: hidden;
  background: white;
}

.logo-wrapper {
  position: absolute;
  top: 50%;
  left: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  transform: translate(-50%, -50%);
}

.logo-wrapper,
.progress-ring {
  transform-style: preserve-3d;
}

/* 圓環周長 = 2 × π × 80，dashoffset 會依載入進度逐漸減少。 */
.progress-ring {
  --circumference: 502.65;

  position: relative;
  width: 180px;
  height: 180px;
  display: grid;
  place-items: center;
}

.startup-logo {
  width: 120px;
  height: 120px;
  object-fit: contain;
}

.progress-ring svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.progress-ring circle {
  fill: none;
  stroke-width: 4;
}

.progress-track {
  stroke: #e7e7e7;
}

.progress-value {
  stroke: #111;
  stroke-linecap: round;
  stroke-dasharray: var(--circumference);
  stroke-dashoffset: calc(
    var(--circumference) - var(--circumference) * var(--progress) / 100
  );
  transition: stroke-dashoffset 0.05s linear;
}

.welcome-text {
  position: absolute;
  top: calc(100% + 24px);
  left: 50%;
  margin: 0;
  transform: translateX(-50%);
  white-space: nowrap;
  color: #111;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.22em;
  text-transform: uppercase;
}

/* Vue Transition：歡迎文字淡入與淡出。 */
.welcome-enter-active {
  transition:
    opacity 0.8s ease,
    transform 0.8s ease;
}

.welcome-enter-from {
  opacity: 0;
  transform: translateX(-50%) translateY(10px);
}

.welcome-leave-active {
  transition: opacity 0.2s ease;
}

.welcome-leave-to {
  opacity: 0;
}

/* 進度完成後，Logo 飛往畫面右下角。 */
.logo-wrapper.launching {
  animation: logo-flight var(--launch-animation);
}

.logo-wrapper.launching .progress-ring {
  animation: logo-spin var(--launch-animation);
}

.logo-wrapper.launching svg {
  animation: ring-hide 0.25s forwards;
}

@keyframes logo-flight {
  0% {
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%) scale(1);
  }

  100% {
    /* 修改 top 與 left 可調整 Logo 的最終位置。 */
    top: calc(100% - 60px);
    left: calc(100% - 60px);
    transform:
      translate(-50%, -50%)
      scale(0.66)
      rotateY(1080deg);
  }
}

@keyframes logo-spin {
  to {
    transform: rotateY(1080deg);
  }
}

@keyframes ring-hide {
  to {
    opacity: 0;
  }
}
</style>
