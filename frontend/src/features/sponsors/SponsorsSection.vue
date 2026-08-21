<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import ditLogoUrl from '@/assets/dit_logo_text.png'
import ApiState from '@/components/common/ApiState.vue'
import { useApiData } from '@/composables/useApiData'
import { useInteractionMode } from '@/composables/useInteractionMode'
import { sponsorsApi } from '@/features/sponsors/sponsorsApi'

// 贊助商資料與環繞動畫狀態。
const {
    data: sponsorData,
    loading,
    error,
    load: loadSponsorsData,
    reload,
} = useApiData({ sponsors: [], title: '' })
const sponsors = computed(() => sponsorData.value.sponsors || [])
const title = computed(() => sponsorData.value.title || '')

// 資料不依賴 DOM，setup 時立即請求，避免等待 mounted 才進入 loading 狀態。
loadSponsorsData(sponsorsApi.data)

const angle = ref(0)
const activeIndex = ref(0)
const hoveredIndex = ref(null)
const paused = ref(false)
const { usesTouchInteraction } = useInteractionMode({ onChange: resetSponsorSelection })

// 將 JS 的橢圓半徑單位換算成容器尺寸。
const ORBIT_WIDTH_PER_RADIUS_UNIT = 30
const ORBIT_HEIGHT_PER_RADIUS_UNIT = 20

// requestAnimationFrame 與自動聚焦計時器的 ID。
let animationId = null
let lastTime = 0
let activeTimer = null

// 依贊助商數量分配各圈容量與橢圓半徑。
const ringConfig = computed(() => {
    const count = sponsors.value.length
    if (count === 0) return []

    const capacities = [8, 12, 17, 23, 30]
    const rings = []
    let remaining = count
    let ringIndex = 0

    while (remaining > 0) {
        const capacity = capacities[ringIndex] ?? 14
        const itemCount = Math.min(capacity, remaining)

        const rx = 22 + ringIndex * 11
        const ry = 16 + ringIndex * 11

        rings.push({
            rx,
            ry,
            itemCount,
        })

        remaining -= itemCount
        ringIndex++
    }

    return rings
})

// 容器尺寸由最外圈橢圓半徑決定，讓 div 隨圈數自動縮放。
const orbitAreaStyle = computed(() => {
    const outerRing = ringConfig.value.at(-1)

    if (!outerRing) {
        return {
            '--orbit-width': '660px',
            '--orbit-height': '320px',
        }
    }

    return {
        '--orbit-width': `${outerRing.rx * ORBIT_WIDTH_PER_RADIUS_UNIT}px`,
        '--orbit-height': `${outerRing.ry * ORBIT_HEIGHT_PER_RADIUS_UNIT}px`,
    }
})

// 將每間贊助商換算成環繞區內的百分比座標。
const sponsorPositions = computed(() => {
    const rings = ringConfig.value
    if (rings.length === 0) return []

    const result = []
    let sponsorIndex = 0

    rings.forEach((ring, ringIndex) => {
        const countInRing = ring.itemCount
        const step = (Math.PI * 2) / countInRing
        const offset = ringIndex % 2 === 0 ? 0 : step / 2

        for (let i = 0; i < countInRing; i++) {
            const sponsor = sponsors.value[sponsorIndex]
            if (!sponsor) break

            const currentAngle = angle.value + step * i + offset
            const x = 50 + Math.cos(currentAngle) * ring.rx
            const y = 50 + Math.sin(currentAngle) * ring.ry

            result.push({
                ...sponsor,
                x,
                y,
                tooltipSide: x > 50 ? 'left' : 'right',
            })

            sponsorIndex++
        }
    })

    return result
})

// 根據每幀經過的時間持續旋轉，滑鼠懸停時暫停。
function animate(time) {
    if (!lastTime) lastTime = time
    const delta = time - lastTime
    lastTime = time

    if (!paused.value) {
        angle.value += delta * 0.00008
    }

    animationId = requestAnimationFrame(animate)
}

// 每秒自動將視覺焦點切換到下一間贊助商。
function startActiveTimer() {
    activeTimer = setInterval(() => {
        if (paused.value || sponsors.value.length === 0) return
        activeIndex.value = (activeIndex.value + 1) % sponsors.value.length
    }, 1000)
}

// 懸停項目優先，否則使用自動切換的項目。
function isActive(index) {
    if (hoveredIndex.value !== null) return hoveredIndex.value === index
    return activeIndex.value === index
}

// 懸停時停止旋轉與自動切換，並顯示詳細資訊。
function handleEnter(index) {
    if (usesTouchInteraction.value) return
    paused.value = true
    hoveredIndex.value = index
}

// 離開後恢復環繞動畫。
function handleLeave() {
    if (usesTouchInteraction.value) return
    resetSponsorSelection()
}

function resetSponsorSelection() {
    paused.value = false
    hoveredIndex.value = null
}

/*
 * 無滑鼠設備採用兩階段操作：
 * 第一次點擊只顯示資訊卡並暫停旋轉；第二次點同一 Logo 才讓 <a> 正常跳轉。
 */
function handleSponsorClick(event, index) {
    if (!usesTouchInteraction.value) return
    if (hoveredIndex.value === index) return

    event.preventDefault()
    paused.value = true
    hoveredIndex.value = index
    activeIndex.value = index
}

// 點擊 Logo 與資訊卡以外的空白處，關閉資訊並恢復環繞動畫。
function closeSponsorFromOutside(event) {
    if (!usesTouchInteraction.value || hoveredIndex.value === null) return
    if (event.target.closest('.sponsor-wrapper')) return
    resetSponsorSelection()
}

// 元件掛載後載入資料並啟動兩種動畫。
onMounted(() => {
    animationId = requestAnimationFrame(animate)
    startActiveTimer()

    document.addEventListener('pointerdown', closeSponsorFromOutside)
})

// 離開頁面時清除動畫與計時器，避免持續佔用資源。
onUnmounted(() => {
    cancelAnimationFrame(animationId)
    clearInterval(activeTimer)
    document.removeEventListener('pointerdown', closeSponsorFromOutside)
})
</script>

<template>
    <!-- 贊助商展示區塊。 -->
    <section class="sponsors-section" :class="{ 'uses-touch': usesTouchInteraction }">
        <ApiState :loading="loading" :error="error" :empty="sponsors.length === 0" @retry="reload">
        <!-- 區塊標題。 -->
        <div class="heading">
            <!-- 英文小標。 -->
            <p class="heading-label">SPONSORS</p>
            <!-- 區塊主標題。 -->
            <h2 class="heading-title">{{ title }}</h2>
        </div>

        <!-- Logo 環繞動畫的展示區。 -->
        <div class="orbit-area" :style="orbitAreaStyle">
            <!-- 環繞中心的 DIT Logo。 -->
            <div class="center">
                <img class="center-logo" :src="ditLogoUrl" alt="DIT Robotics" />
            </div>

            <!-- 單一贊助商的定位容器。 -->
            <div v-for="(sponsor, index) in sponsorPositions" :key="sponsor.id" class="sponsor-wrapper"
                :class="{ focused: isActive(index) }" :style="{ left: `${sponsor.x}%`, top: `${sponsor.y}%` }"
                @mouseenter="handleEnter(index)" @mouseleave="handleLeave">
                <!-- 連結至贊助商官網的 Logo 卡片。 -->
                <a class="sponsor" :class="{ active: isActive(index) }" :href="sponsor.url" target="_blank"
                    rel="noopener noreferrer" @click="handleSponsorClick($event, index)">
                    <img class="sponsor-logo" :src="sponsor.logo" :alt="sponsor.name" />
                </a>

                <!-- 懸停時顯示的贊助商資訊卡。 -->
                <Transition name="tooltip">
                    <div v-if="hoveredIndex === index" class="tooltip" :class="sponsor.tooltipSide">
                        <!-- 合作關係標籤。 -->
                        <p class="tooltip-label">PARTNER</p>
                        <!-- 贊助商名稱。 -->
                        <h3 class="tooltip-title">{{ sponsor.name }}</h3>
                        <!-- 贊助商簡介。 -->
                        <p class="tooltip-description">{{ sponsor.description }}</p>
                        <!-- 官網連結提示。 -->
                        <span class="tooltip-link-label">前往網站 ↗</span>
                    </div>
                </Transition>
            </div>
        </div>
        </ApiState>
    </section>
</template>

<style scoped>
.sponsors-section {
    --Width: 130px;

    min-height: 100vh;
    width: 100%;
    padding: 50px 7vw;
    background: #f9f9f9;
    overflow: hidden;
}

.heading {
    align-self: center;
    width: fit-content;
    position: relative;
    z-index: 5;
}

.heading-label {
    font-size: 13px;
    letter-spacing: 0.22em;
    font-weight: 700;
    margin-bottom: 20px;
}

.heading-title {
    font-size: clamp(38px, 4vw, 72px);
    line-height: 1.05;
    letter-spacing: 0.11em;
    margin: 0;
}

.orbit-area {
    position: relative;
    width: min(100%, var(--orbit-width));
    height: min(78vh, var(--orbit-height));
    margin-inline: auto;
}

.center,
.sponsor-wrapper {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
}

.center {
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 1;
    pointer-events: none;
}

.center-logo {
    width: var(--Width);
    aspect-ratio: 1;
}

.sponsor-wrapper {
    z-index: 3;
}

.sponsor-wrapper.focused {
    z-index: 100;
}

.sponsor {
    width: var(--Width);
    height: 110px;
    padding: 12px;
    border-radius: 18px;
    background: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    box-sizing: border-box;
    transform: scale(1);
    transition: transform 1s cubic-bezier(0.2, 0.8, 0.2, 1);
    text-decoration: none;
}

.sponsor-logo {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: contain;
    pointer-events: none;
    filter: brightness(0);
}

.sponsor.active,
.sponsors-section:not(.uses-touch) .sponsor-wrapper:hover .sponsor {
    transform: scale(1.4);
}

.sponsors-section:not(.uses-touch) .sponsor-wrapper:hover .sponsor {
    transition: transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.tooltip {
    position: absolute;
    left: calc(var(--Width) * 1.1);
    top: 50%;
    transform: translateY(-50%);
    width: 220px;
    padding: 20px;
    background: #111;
    color: white;
    border-radius: 14px;
    pointer-events: none;
    box-shadow: 0 18px 45px rgba(0, 0, 0, 0.2);
    z-index: 200;
}

.tooltip.left {
    left: auto;
    right: calc(var(--Width) * 1.1);
}

.tooltip::before {
    content: '';
    position: absolute;
    left: -7px;
    top: 50%;
    width: 14px;
    height: 14px;
    background: #111;
    transform: translateY(-50%) rotate(45deg);
}

.tooltip.left::before {
    left: auto;
    right: -7px;
}

.tooltip-label {
    font-size: 9px;
    letter-spacing: 0.2em;
    opacity: 0.5;
}

.tooltip-title {
    font-size: 18px;
}

.tooltip-label,
.tooltip-title {
    margin: 0 0 8px;
}

.tooltip-description {
    font-size: 12px;
    line-height: 1.6;
    opacity: 0.7;
    margin: 0 0 14px;
}

.tooltip-link-label {
    font-size: 11px;
    font-weight: 700;
}

.tooltip-enter-active,
.tooltip-leave-active {
    transition: 0.2s ease;
}

.tooltip-enter-from,
.tooltip-leave-to {
    opacity: 0;
}

.tooltip-enter-from.right,
.tooltip-leave-to.right {
    transform: translateY(-50%) translateX(-10px);
}

.tooltip-enter-from.left,
.tooltip-leave-to.left {
    transform: translateY(-50%) translateX(10px);
}

@media (max-width: 1100px) {
    .sponsors-section {
        padding: 80px 4vw;
    }

    .sponsor {
        width: 90px;
        height: 68px;
    }

    .tooltip {
        left: 110px;
        width: 190px;
    }

    .tooltip.left {
        left: auto;
        right: 110px;
    }
}

@media (max-width: 900px) {
    .sponsors-section {
        padding: 80px 25px;
    }

    .heading {
        margin-bottom: 30px;
    }

    .orbit-area {
        height: min(600px, var(--orbit-height));
    }

    .sponsor {
        width: 72px;
        height: 56px;
        padding: 8px;
        border-radius: 12px;
    }

    .tooltip {
        left: 90px;
        width: 170px;
    }

    .tooltip.left {
        left: auto;
        right: 90px;
    }
}
</style>
