<script setup>
import { computed, ref } from 'vue'
import { RouterView, useRoute } from 'vue-router'

import StartupAnimation from '@/components/layout/StartupAnimation.vue'
import FloatingRobot from '@/components/layout/FloatingRobot.vue'
import TitleBar from '@/components/layout/TitleBar.vue'

const startupFinished = ref(false)
const route = useRoute()
const isHomeRoute = computed(() => route.path === '/')

function finishStartup() {
  startupFinished.value = true
  sessionStorage.setItem('startupFinished', true)
  window.dispatchEvent(new CustomEvent('startup-animation-finished'))
}

const startup = sessionStorage.getItem('startupFinished')
if (startup) {
  startupFinished.value = true
}
</script>

<template>
  <StartupAnimation v-if="!startupFinished" :track-hero-video="isHomeRoute" @finished="finishStartup" />

  <div
    class="website"
    :class="{
      visible: startupFinished,
      'with-title-bar': startupFinished && !isHomeRoute,
    }"
  >
    <RouterView />
  </div>

  <!-- 全路由共用，不受個別分頁的堆疊與裁切影響。 -->
  <FloatingRobot v-if="startupFinished" />

  <!-- 首頁由 Hero 連續收合成 TitleBar；其他分頁直接使用固定 TitleBar。 -->
  <TitleBar v-if="startupFinished && !isHomeRoute" :progress="1" />
</template>

<style>
:root {
  --title-bar-height: 76px;
  --page-content-height: calc(100vh - var(--title-bar-height));
}

html {
  scroll-behavior: smooth;
  scroll-padding-top: var(--title-bar-height);
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

.website.with-title-bar {
  min-height: 100vh;
  padding-top: var(--title-bar-height);
}

.website.visible {
  opacity: 1;
}

/* 一般 hash link 也會讓 section top 對齊 TitleBar bottom。 */
section[id] {
  scroll-margin-top: var(--title-bar-height);
}
</style>
