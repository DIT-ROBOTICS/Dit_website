<!--
網頁小助手：
看有沒有機會加入ai來帶領訪客導覽整個網頁和介紹我們團隊
-->


<script setup>
import { ref } from 'vue'
import robotImageUrl from '@/assets/dit_logo.png'

const menuOpen = ref(false)
const messageOpen = ref(true)

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

function toggleMenu() {
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
</script>

<template>
  <aside class="robot-assistant">
    <transition name="bubble">
      <div v-if="messageOpen" class="speech-bubble" >
        嗨！需要我帶你認識 DIT 嗎？

        <button
          type="button"
          aria-label="關閉提示"
          @click="messageOpen = false"
        >
          ×
        </button>
      </div>
    </transition>

    <transition name="menu">
      <div
        v-if="menuOpen"
        class="robot-menu"
      >
        <p>前往哪個區域？</p>

        <button
          v-for="item in navigationItems"
          :key="item.target"
          type="button"
          @click="goToSection(item.target)"
        >
          {{ item.label }}
        </button>
      </div>
    </transition>

    <button
      class="robot-button"
      type="button"
      :aria-expanded="menuOpen"
      aria-label="開啟網站導覽機器人"
      @click="toggleMenu"
    >
      <img :src="robotImageUrl" alt="" ><!--為啥這個圖片沒有圓角-->
    </button>
  </aside>
</template>

<style scoped>
.robot-assistant {
  position: fixed;
  right: clamp(18px, 4vw, 52px);
  bottom: clamp(18px, 4vw, 45px);
  transform: translate(-50%,-50%);
  z-index: 500;
}

.robot-button {
  width: 88px;
  height: 88px;
  padding: 0;

  border: none;
  border-radius: 50%;
  overflow: hidden;

  background:
    radial-gradient(
      circle at 35% 25%,
      #ffffff,
      #d9e7ff 42%,
      #829ddb
    );

  box-shadow:
    0 16px 40px rgba(17, 32, 67, 0.28);

  cursor: pointer;

  animation:
    robot-floating 3.2s ease-in-out infinite;
}

.robot-button img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.robot-button:hover {
  animation-play-state: paused;
  transform: translateY(-4px) scale(1.04);
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
  box-shadow:
    0 22px 60px rgba(18, 29, 52, 0.2);

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

  box-shadow:
    0 18px 50px rgba(20, 30, 52, 0.17);

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
  0%,
  100% {
    transform:
      translateY(0)
      rotate(-2deg);
  }

  50% {
    transform:
      translateY(-12px)
      rotate(2deg);
  }
}

.menu-enter-active,
.menu-leave-active,
.bubble-enter-active,
.bubble-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
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