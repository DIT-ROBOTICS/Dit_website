<script setup>
import {
  computed,
  onMounted,
  onUnmounted,
  ref,
} from 'vue'

import teamPhoto from '@/assets/Hero_Image.png'

const aboutContainer = ref(null)
const progress = ref(0)

let animationFrameId = null

function clamp(value, min = 0, max = 1) {
  return Math.min(Math.max(value, min), max)
}

/*
 * 把總 progress 的某一段重新換算成 0～1。
 *
 * 例如：
 * segmentProgress(0.2, 0.5)
 * 表示總進度從 20% 到 50% 時，
 * 回傳值會從 0 漸變到 1。
 */
function segmentProgress(start, end) {
  return computed(() => {
    return clamp(
      (progress.value - start) / (end - start),
    )
  })
}

const titleProgress = segmentProgress(0, 0.28)
const imageProgress = segmentProgress(0.15, 0.58)
const contentProgress = segmentProgress(0.52, 0.82)

const styleVariables = computed(() => ({
  '--about-progress': String(progress.value),
  '--title-progress': String(titleProgress.value),
  '--image-progress': String(imageProgress.value),
  '--content-progress': String(contentProgress.value),
}))

function updateProgress() {
  const element = aboutContainer.value

  if (!element) {
    return
  }

  const rect = element.getBoundingClientRect()

  const scrollDistance =
    element.offsetHeight - window.innerHeight

  if (scrollDistance <= 0) {
    progress.value = 0
    return
  }

  progress.value = clamp(
    -rect.top / scrollDistance * 2,
  )
}

function requestProgressUpdate() {
  if (animationFrameId !== null) {
    return
  }

  animationFrameId = requestAnimationFrame(() => {
    updateProgress()
    animationFrameId = null
  })
}

onMounted(() => {
  updateProgress()

  window.addEventListener(
    'scroll',
    requestProgressUpdate,
    { passive: true },
  )

  window.addEventListener(
    'resize',
    requestProgressUpdate,
  )
})

onUnmounted(() => {
  window.removeEventListener(
    'scroll',
    requestProgressUpdate,
  )

  window.removeEventListener(
    'resize',
    requestProgressUpdate,
  )

  if (animationFrameId !== null) {
    cancelAnimationFrame(animationFrameId)
  }
})
</script>

<template>
  <section
    ref="aboutContainer"
    class="about-scroll-space"
    :style="styleVariables"
  >
    <div class="about-sticky">
      <div class="about-title">
        <p>WHO WE ARE</p>

        <h2>
          我們打造的不只是機器人，
          <br>
          更是一群能一起完成夢想的人。
        </h2>
      </div>

      <div class="photo-stage">
        <img
          :src="teamPhoto"
          alt="DIT Robotics 團隊合照"
        >

        <div class="photo-overlay"></div>
      </div>

      <div class="about-content">
        <p class="content-eyebrow">
          ABOUT DIT
        </p>

        <h3>
          從一個想法，
          <br>
          到一台真正能上場的機器人。
        </h3>

        <p class="content-description">
          DIT Robotics 成立於 2012 年，持續投入 Eurobot
          國際機器人競賽。團隊涵蓋機構、電控、軟體與策略，
          每一位隊員都能實際參與設計、製造、測試與競賽。
        </p>

        <div class="content-stats">
          <div>
            <strong>2012</strong>
            <span>團隊成立</span>
          </div>

          <div>
            <strong>4</strong>
            <span>核心領域</span>
          </div>

          <div>
            <strong>∞</strong>
            <span>持續嘗試</span>
          </div>
        </div>

        <a href="#team">
          認識我們的團隊
        </a>
      </div>

      <div class="scroll-hint">
        <span>SCROLL TO EXPLORE</span>
        <i></i>
      </div>
    </div>
  </section>
</template>

<style scoped>
.about-scroll-space {
  position: relative;

  /*
   * 數字越大，整段動畫越慢。
   * 280vh～340vh 都可以嘗試。
   */
  height: 320vh;

  color: white;
  background: #090b0f;
}

.about-sticky {
  position: sticky;
  top: 0;

  width: 100%;
  height: 100vh;

  overflow: hidden;
  background: #fafafa;
}

/* -------------------------
   一開始出現的標題
------------------------- */

.about-title {
  position: absolute;
  top: 11vh;
  left: 50%;
  z-index: 5;

  width: min(1100px, 84vw);

  color: #111;
  text-align: center;

  opacity:
    calc(1 - var(--title-progress));

  transform:
    translate(
      -50%,
      calc(var(--title-progress) * -120px)
    );

  will-change: transform, opacity;
}

.about-title p {
  margin: 0 0 18px;

  color: #777;
  font-size: 13px;
  letter-spacing: 0.3em;
}

.about-title h2 {
  margin: 0;

  font-size: clamp(38px, 5vw, 72px);
  font-weight: 700;
  line-height: 1.15;
  letter-spacing: -0.04em;
}

/* -------------------------
   照片從卡片擴張成滿版
------------------------- */

.photo-stage {
  position: absolute;

  /*
   * imageProgress = 0：
   * 上下左右都有空間，像一張大卡片。
   *
   * imageProgress = 1：
   * inset 全部變成 0，填滿整個螢幕。
   */
  top:
    calc(
      (1 - var(--image-progress)) * 36vh
    );

  right:
    calc(
      (1 - var(--image-progress)) * 7vw
    );

  bottom:
    calc(
      (1 - var(--image-progress)) * 8vh
    );

  left:
    calc(
      (1 - var(--image-progress)) * 7vw
    );

  z-index: 2;

  overflow: hidden;

  border-radius:
    calc(
      (1 - var(--image-progress)) * 30px
    );

  box-shadow:
    0
    calc((1 - var(--image-progress)) * 35px)
    calc((1 - var(--image-progress)) * 80px)
    rgba(0, 0, 0, 0.18);

  will-change:
    top,
    right,
    bottom,
    left,
    border-radius;
}

.photo-stage img {
  width: 100%;
  height: 100%;

  display: block;
  object-fit: cover;
  object-position: center 55%;

  transform:
    scale(
      calc(
        1.04 + var(--image-progress) * 0.08
      )
    );

  will-change: transform;
}

.photo-overlay {
  position: absolute;
  inset: 0;

  background:
    linear-gradient(
      90deg,
      rgba(4, 7, 12, 0.08) 0%,
      rgba(4, 7, 12, 0.2) 40%,
      rgba(4, 7, 12, 0.78) 100%
    );

  opacity:
    calc(
      var(--content-progress) * 0.95
    );
}

/* -------------------------
   右側介紹內容滑入
------------------------- */

.about-content {
  position: absolute;
  top: 50%;
  right: clamp(24px, 8vw, 130px);
  z-index: 4;

  width: min(520px, 42vw);

  opacity: var(--content-progress);

  transform:
    translateY(
      calc(
        -50%
        + (1 - var(--content-progress)) * 150px
      )
    );

  pointer-events:
    none;

  will-change: transform, opacity;
}

.content-eyebrow {
  margin: 0 0 22px;

  color: rgba(255, 255, 255, 0.58);
  font-size: 12px;
  letter-spacing: 0.3em;
}

.about-content h3 {
  margin: 0;

  font-size: clamp(34px, 4vw, 64px);
  line-height: 1.12;
  letter-spacing: -0.045em;
}

.content-description {
  margin: 28px 0 0;

  color: rgba(255, 255, 255, 0.74);
  font-size: clamp(15px, 1.25vw, 19px);
  line-height: 1.9;
}

.content-stats {
  margin-top: 34px;

  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 22px;
}

.content-stats div {
  padding-top: 18px;

  display: flex;
  flex-direction: column;
  gap: 7px;

  border-top: 1px solid rgba(255, 255, 255, 0.24);
}

.content-stats strong {
  font-size: 26px;
}

.content-stats span {
  color: rgba(255, 255, 255, 0.58);
  font-size: 12px;
}

.about-content > a {
  margin-top: 36px;
  padding: 13px 22px;

  display: inline-block;

  border: 1px solid rgba(255, 255, 255, 0.45);
  border-radius: 999px;

  color: white;
  text-decoration: none;

  pointer-events: auto;

  transition:
    color 0.25s ease,
    background 0.25s ease;
}

.about-content > a:hover {
  color: #111;
  background: white;
}

/* -------------------------
   下方滾動提示
------------------------- */

.scroll-hint {
  position: absolute;
  left: 50%;
  bottom: 30px;
  z-index: 6;

  display: flex;
  align-items: center;
  gap: 14px;

  color: rgba(255, 255, 255, 0.58);

  font-size: 9px;
  letter-spacing: 0.22em;

  opacity:
    calc(
      1 - var(--about-progress) * 4
    );

  transform: translateX(-50%);
}

.scroll-hint i {
  width: 45px;
  height: 1px;
  background: currentColor;
}

@media (max-width: 800px) {
  .about-scroll-space {
    height: 300vh;
  }

  .about-title {
    top: 10vh;
    width: calc(100% - 40px);
  }

  .about-title h2 {
    font-size: clamp(34px, 9vw, 52px);
  }

  .photo-stage {
    top:
      calc(
        (1 - var(--image-progress)) * 34vh
      );

    right:
      calc(
        (1 - var(--image-progress)) * 20px
      );

    bottom:
      calc(
        (1 - var(--image-progress)) * 8vh
      );

    left:
      calc(
        (1 - var(--image-progress)) * 20px
      );
  }

  .photo-overlay {
    background:
      linear-gradient(
        0deg,
        rgba(4, 7, 12, 0.88) 0%,
        rgba(4, 7, 12, 0.35) 65%,
        rgba(4, 7, 12, 0.08) 100%
      );
  }

  .about-content {
    top: auto;
    right: 24px;
    bottom: 55px;
    left: 24px;

    width: auto;

    transform:
      translateY(
        calc(
          (1 - var(--content-progress)) * 120px
        )
      );
  }

  .about-content h3 {
    font-size: clamp(32px, 9vw, 46px);
  }

  .content-description {
    line-height: 1.7;
  }
}
</style>