<script setup>
import { computed, ref } from 'vue'
import { RouterView, useRoute } from 'vue-router'

import StartupAnimation from '@/components/StartupAnimation.vue'
import FloatingRobot from '@/components/FloatingRobot.vue'
import TitleBar from '@/components/TitleBar.vue'

const startupFinished = ref(false)
const route = useRoute()
const isHomeRoute = computed(() => route.path === '/')

function finishStartup() {
  startupFinished.value = true
  sessionStorage.setItem('startupFinished', true)
  window.dispatchEvent(new CustomEvent('startup-animation-finished'))
}

const startup = sessionStorage.getItem('startupFinished')
if(startup){
  startupFinished.value = true
}
</script>

<template>
  <StartupAnimation v-if="!startupFinished" :track-hero-video="isHomeRoute" @finished="finishStartup" />

  <div class="website" :class="{ visible: startupFinished }" >
    <RouterView />
  </div>

  <!-- 全路由共用，不受個別分頁的堆疊與裁切影響。 -->
  <FloatingRobot v-if="startupFinished" />

  <!-- 首頁由 Hero 控制動畫；其他分頁固定顯示同一條導覽列。 -->
  <TitleBar v-if="startupFinished && !isHomeRoute" :progress="1" />
</template>

<style>
html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  overflow-x: hidden;
  background: #f5f5f5;
  font-family:
    Inter,
    "Noto Sans TC",
    "PingFang TC",
    sans-serif;
}

* {
  box-sizing: border-box;
  user-select: none;
  -webkit-user-select: none;
}

input,
textarea,
[contenteditable="true"] {
  user-select: text;
  -webkit-user-select: text;
}

.website {
  opacity: 0;
  transition: opacity 0.8s ease;
}

.website.visible {
  opacity: 1;
}
</style>
