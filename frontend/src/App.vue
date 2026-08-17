<script setup>
import { ref } from 'vue'

import StartupAnimation from '@/components/StartupAnimation.vue'
import FloatingRobot from '@/components/FloatingRobot.vue'
import HomeView from '@/views/HomeView.vue'

const startupFinished = ref(false)

function finishStartup() {
  startupFinished.value = true
  sessionStorage.setItem('startupFinished', true)
}

const startup = sessionStorage.getItem('startupFinished')
if(startup){
  startupFinished.value = true
}
</script>

<template>
  <StartupAnimation v-if="!startupFinished" @finished="finishStartup" />

  <div class="website" :class="{ visible: startupFinished }" >
    <HomeView />
    <!-- <FloatingRobot v-if="startupFinished" /> -->
  </div>
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
}

.website {
  opacity: 0;
  transition: opacity 0.8s ease;
}

.website.visible {
  opacity: 1;
}
</style>