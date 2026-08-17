<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import robotImageUrl from '@/assets/dit_logo.png'

const menuOpen = ref(false)
const messageOpen = ref(true)
const assistantRef = ref(null)
const position = ref({
  x: window.innerWidth,
  y: window.innerHeight,
})

let dragging = false
let hasDragged = false
let pointerId = null
let offsetX = 0
let offsetY = 0
let startX = 0
let startY = 0

const navigationItems = [
  {
    label: '認識團隊',
    target: '#team',
  },
  {
    label: '年度機器人',
    target: '#featured-robot',
  },
  {
    label: '歷年作品',
    target: '#robots',
  },
  {
    label: '指導教授',
    target: '#advisors',
  },
  {
    label: '贊助商',
    target: '#sponsors',
  },
  {
    label: '聯絡我們',
    target: '#contact',
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

function goToSection(target) {
  const element = document.querySelector(target)

  if (!element) {
    return
  }

  element.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })

  menuOpen.value = false
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
  const margin = 10

  position.value.x = clamp(
    event.clientX - offsetX,
    margin,
    window.innerWidth - width - margin
  )

  position.value.y = clamp(
    event.clientY - offsetY,
    margin,
    window.innerHeight - height - margin
  )
}

function endDrag(event) {
  if (!dragging || event.pointerId !== pointerId) {
    return
  }

  dragging = false
  pointerId = null

  if (event.currentTarget.hasPointerCapture(event.pointerId)) {
    event.currentTarget.releasePointerCapture(event.pointerId)
  }
}

function keepInsideViewport() {
  const assistant = assistantRef.value

  if (!assistant) {
    return
  }

  const margin = 10

  position.value.x = clamp(
    position.value.x,
    margin,
    window.innerWidth - assistant.offsetWidth - margin
  )

  position.value.y = clamp(
    position.value.y,
    margin,
    window.innerHeight - assistant.offsetHeight - margin
  )
}

onMounted(() => {
  keepInsideViewport()
  window.addEventListener('resize', keepInsideViewport)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', keepInsideViewport)
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
  width: 88px;
  height: 88px;
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