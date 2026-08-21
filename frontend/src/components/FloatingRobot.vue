<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import robotImageUrl from '@/assets/dit_logo.png'

const router = useRouter()
const menuOpen = ref(false)
const messageOpen = ref(true)
const assistantRef = ref(null)
const position = ref({
  x: window.innerWidth,
  y: window.innerHeight,
})

// Robot 中心距離右下角在此半徑內時，視窗縮放後會繼續貼齊右下角。
const BOTTOM_RIGHT_SNAP_RADIUS_VW = 30
const VIEWPORT_MARGIN = 10

let dragging = false
let hasDragged = false
let pointerId = null
let offsetX = 0
let offsetY = 0
let startX = 0
let startY = 0
let followsBottomRight = true
let resizeEndTimer = null

const navigationItems = [
  {
    label: '團隊',
    target: '/#aboutSection',
  },
  {
    label: 'Eurobot',
    target: '/Eurobot',
  },
  {
    label: '歷年機器人',
    target: '/Eurobot#RobotArchive',
  },
  {
    label: '其他競賽',
    target: '/Competition',
  },
  {
    label: '指導教授',
    target: '/#advisors',
  },
  {
    label: '贊助商',
    target: '/#sponsors',
  },
  {
    label: '聯絡我們',
    target: '/#contact',
  },
]

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max)
}

function toggleMenu() {
  if (hasDragged) {
    hasDragged = false
    return
  }

  menuOpen.value = !menuOpen.value
  messageOpen.value = false
}

async function goToSection(target) {
  const destination = router.resolve(target)
  const isCurrentLocation = router.currentRoute.value.fullPath === destination.fullPath
  menuOpen.value = false

  await router.push(target)

  // 已經位於完全相同的網址時 Router 不會再次觸發 scrollBehavior，手動補上捲動。
  if (isCurrentLocation && destination.hash) {
    document.querySelector(destination.hash)?.scrollIntoView({
      behavior: 'smooth',
      block: 'start',
    })
  }
}

function startDrag(event) {
  if (event.button !== undefined && event.button !== 0) {
    return
  }

  dragging = true
  hasDragged = false
  pointerId = event.pointerId

  startX = event.clientX
  startY = event.clientY

  const rect = assistantRef.value.getBoundingClientRect()

  offsetX = event.clientX - rect.left
  offsetY = event.clientY - rect.top

  event.currentTarget.setPointerCapture(event.pointerId)
}

function drag(event) {
  if (!dragging || event.pointerId !== pointerId) {
    return
  }

  const moveDistance = Math.hypot(
    event.clientX - startX,
    event.clientY - startY
  )

  if (moveDistance > 4) {
    hasDragged = true
  }

  const assistant = assistantRef.value

  if (!assistant) {
    return
  }

  const width = assistant.offsetWidth
  const height = assistant.offsetHeight

  position.value.x = clamp(
    event.clientX - offsetX,
    VIEWPORT_MARGIN,
    window.innerWidth - width - VIEWPORT_MARGIN
  )

  position.value.y = clamp(
    event.clientY - offsetY,
    VIEWPORT_MARGIN,
    window.innerHeight - height - VIEWPORT_MARGIN
  )
}

function endDrag(event) {
  if (!dragging || event.pointerId !== pointerId) {
    return
  }

  const releasedPointerId = pointerId
  dragging = false
  pointerId = null

  updateBottomRightAffinity()

  if (event.currentTarget.hasPointerCapture(releasedPointerId)) {
    event.currentTarget.releasePointerCapture(releasedPointerId)
  }
}

function keepInsideViewport() {
  const assistant = assistantRef.value

  if (!assistant) {
    return
  }

  position.value.x = clamp(
    position.value.x,
    VIEWPORT_MARGIN,
    window.innerWidth - assistant.offsetWidth - VIEWPORT_MARGIN
  )

  position.value.y = clamp(
    position.value.y,
    VIEWPORT_MARGIN,
    window.innerHeight - assistant.offsetHeight - VIEWPORT_MARGIN
  )
}

// 判斷 Robot 中心是否位於右下角 20vw 半徑內，供下一次 resize 使用。
function updateBottomRightAffinity() {
  const assistant = assistantRef.value
  if (!assistant) return

  const robotCenterX = position.value.x + assistant.offsetWidth / 2
  const robotCenterY = position.value.y + assistant.offsetHeight / 2
  const distanceToBottomRight = Math.hypot(
    window.innerWidth - robotCenterX,
    window.innerHeight - robotCenterY
  )
  const snapRadius = window.innerWidth * BOTTOM_RIGHT_SNAP_RADIUS_VW / 100

  followsBottomRight = distanceToBottomRight <= snapRadius
}

function moveToBottomRight() {
  const assistant = assistantRef.value
  if (!assistant) return

  position.value.x = window.innerWidth - assistant.offsetWidth - VIEWPORT_MARGIN
  position.value.y = window.innerHeight - assistant.offsetHeight - VIEWPORT_MARGIN
}

function handleViewportResize() {
  if (followsBottomRight) {
    moveToBottomRight()
  } else {
    keepInsideViewport()
  }

  // resize 結束後重新判斷目前位置，供下一次螢幕尺寸改變時使用。
  clearTimeout(resizeEndTimer)
  resizeEndTimer = setTimeout(updateBottomRightAffinity, 150)
}

onMounted(() => {
  keepInsideViewport()
  updateBottomRightAffinity()
  window.addEventListener('resize', handleViewportResize)
})

onBeforeUnmount(() => {
  clearTimeout(resizeEndTimer)
  window.removeEventListener('resize', handleViewportResize)
})
</script>

<template>
  <aside ref="assistantRef" class="robot-assistant" :style="{ left: `${position.x}px`, top: `${position.y}px` }">
    <transition name="menu">
      <div v-if="menuOpen" class="robot-menu">
        <p>前往哪個區域？</p>
        <button v-for="item in navigationItems" :key="item.target" type="button" @click="goToSection(item.target)">{{ item.label }}</button>
      </div>
    </transition>
    <button class="robot-button" type="button" :aria-expanded="menuOpen" aria-label="開啟網站導覽機器人" @pointerdown="startDrag" @pointermove="drag" @pointerup="endDrag" @pointercancel="endDrag" @click="toggleMenu">
      <img :src="robotImageUrl" alt="">
    </button>
  </aside>
</template>

<style scoped>
.robot-assistant {
  position: fixed;
  z-index: 500;
  user-select: none;
  touch-action: none;
}
.robot-button {
  width: 70px;
  height: 70px;
  padding: 0;
  border: none;
  border-radius: 50%;
  overflow: hidden;
  background: radial-gradient(circle at 35% 25%, #ffffff, #d9e7ff 42%, #829ddb);
  box-shadow: 0 16px 40px rgba(17, 32, 67, 0.28);
  cursor: grab;
  animation: robot-floating 3.2s ease-in-out infinite;
  touch-action: none;
}
.robot-button:active {
  cursor: grabbing;
}
.robot-button img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  pointer-events: none;
}
.robot-button:hover {
  animation-play-state: paused;
}
.robot-menu {
  position: absolute;
  right: 0;
  bottom: 106px;
  width: 230px;
  padding: 17px;
  border: 1px solid rgba(255, 255, 255, 0.6);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.92);
  box-shadow: 0 22px 60px rgba(18, 29, 52, 0.2);
  backdrop-filter: blur(20px);
}
.robot-menu p {
  margin: 0 0 12px;
  color: #6b7280;
  font-size: 13px;
}
.robot-menu button {
  width: 100%;
  padding: 10px 12px;
  border: none;
  border-radius: 11px;
  background: transparent;
  color: #15171b;
  text-align: left;
  font: inherit;
  cursor: pointer;
}
.robot-menu button:hover {
  background: #edf2ff;
}
.speech-bubble {
  position: absolute;
  right: 14px;
  bottom: 108px;
  width: 230px;
  padding: 14px 38px 14px 16px;
  border-radius: 18px 18px 4px 18px;
  background: white;
  color: #25272d;
  box-shadow: 0 18px 50px rgba(20, 30, 52, 0.17);
  font-size: 14px;
  line-height: 1.6;
}
.speech-bubble button {
  position: absolute;
  top: 7px;
  right: 9px;
  border: none;
  background: none;
  color: #777;
  font-size: 19px;
  cursor: pointer;
}
@keyframes robot-floating {
  0%, 100% {
    transform: translateY(0) rotate(-2deg);
  }
  50% {
    transform: translateY(-12px) rotate(2deg);
  }
}
.menu-enter-active,
.menu-leave-active,
.bubble-enter-active,
.bubble-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.menu-enter-from,
.menu-leave-to,
.bubble-enter-from,
.bubble-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.96);
}
@media (max-width: 600px) {
  .robot-button {
    width: 68px;
    height: 68px;
  }
  .robot-menu,
  .speech-bubble {
    bottom: 84px;
  }
}
</style>
