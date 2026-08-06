<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import logoUrl from '@/assets/dit_logo.png'
import robotImageUrl from '@/assets/dit_logo.png'

const emit = defineEmits(['finished'])

const progress = ref(0)
const phase = ref('loading')

let progressTimer = null
let launchTimer = null
let finishTimer = null

onMounted(() => {
  progressTimer = window.setInterval(() => {
    progress.value += 1

    if (progress.value >= 100) {
      progress.value = 100

      window.clearInterval(progressTimer)

      launchTimer = window.setTimeout(() => {
        phase.value = 'launching'
      }, 200)

      finishTimer = window.setTimeout(() => {
        emit('finished')
      }, 1800)
    }
  }, 20)
})

onUnmounted(() => {
  window.clearInterval(progressTimer)
  window.clearTimeout(launchTimer)
  window.clearTimeout(finishTimer)
})
</script>

<template>
  <div class="startup-screen">
    <div class="logo-wrapper" :class="{ launching: phase === 'launching' }">
      <div class="progress-ring" :style="{ '--progress': progress }">
        <svg viewBox="0 0 180 180">
          <circle class="track" cx="90" cy="90" r="80"/>
          <circle class="value" cx="90" cy="90" r="80" />
        </svg>

        <div class="logo-morph">
          <img
            class="startup-logo"
            :src="logoUrl"
            alt="DIT Logo"
          >
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.startup-logo,
.startup-robot {
  width: 120px;
  height: 120px;
  object-fit: contain;
  backface-visibility: visible;
  transition:
    opacity 0.45s ease,
    transform 0.45s ease;
}

.startup-robot {
  opacity: 0;
  transform: scale(0.65) rotate(-20deg);
}

.startup-screen {
  position: fixed;
  inset: 0;
  z-index: 9999;
  overflow: hidden;
  background: white;
}

.logo-wrapper {
  position: absolute;
  left: 50%;
  top: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  transform: translate(-50%, -50%);
  transform-style: preserve-3d;
}

.progress-ring {
  --radius: 80;
  --circumference: 502.65;

  position: relative;
  width: 180px;
  height: 180px;
  display: grid;
  place-items: center;
  transform-style: preserve-3d;
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

.track {
  stroke: #e7e7e7;
}

.value {
  stroke: #111;
  stroke-linecap: round;
  stroke-dasharray: var(--circumference);
  stroke-dashoffset:
    calc(
      var(--circumference) -
      var(--circumference) * var(--progress) / 100
    );
  transition: stroke-dashoffset 0.05s linear;
}

.logo {
  width: 120px;
  height: 120px;
  object-fit: contain;
  backface-visibility: visible;
}

.loading-info {
  width: 180px;
  margin-top: 22px;
  display: flex;
  justify-content: space-between;
  color: #777;
  font-size: 14px;
}

.loading-info strong {
  color: #111;
}

.logo-wrapper.launching {
  animation:
    logo-flight 1.8s cubic-bezier(0.25, 0.75, 0.25, 1)
    forwards;
}

.logo-wrapper.launching .progress-ring {
  animation:
    logo-spin 1.8s cubic-bezier(0.25, 0.75, 0.25, 1)
    forwards;
}

.logo-wrapper.launching svg {
  animation: ring-hide 0.25s forwards;
}

@keyframes logo-flight {
  0% {
    left: 50%;
    top: 50%;
    transform:
      translate(-50%, -50%)
      scale(1);
  }

  100% {
    top: calc(100% - clamp(18px, 4vw, 52px));
    left: calc(100% - clamp(18px, 4vw, 45px));
    transform:
      translate(-100%, -100%)
      scale(0.66)
      rotateY(1080deg);
  }
}

@keyframes logo-spin {
  from {
    transform: rotateY(0deg);
  }

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