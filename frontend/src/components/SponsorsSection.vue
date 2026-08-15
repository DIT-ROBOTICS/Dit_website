<!--
展示贊助商：
形式預計會像張浩翔在機器上放的那個相同
但是滑鼠移動到每個贊助商上面的時候可以跳出贊助商公司的官網
和一些其他資訊之類的
-->

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const sponsors = ref([])
const angle = ref(0)
const activeIndex = ref(0)
const previousIndex = ref(null)
const hoveredIndex = ref(null)
const paused = ref(false)

let animationId = null
let lastTime = 0
let activeTimer = null

async function loadSponsorsData() {
    try {
        const response = await fetch('/api/Sponsors')
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        sponsors.value = await response.json()
    } catch (error) {
        console.error(error)
    }
}
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

        const rx = 22 + ringIndex * 17
        const ry = 16 + ringIndex * 13

        rings.push({
            rx,
            ry,
            itemCount
        })

        remaining -= itemCount
        ringIndex++
    }

    return rings
})
const sponsorPositions = computed(() => {
    const rings = ringConfig.value
    if (rings.length === 0) return []

    const result = []
    let sponsorIndex = 0

    rings.forEach((ring, ringIndex) => {
        const countInRing = ring.itemCount
        const step = Math.PI * 2 / countInRing
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
                tooltipSide: x > 50 ? 'left' : 'right'
            })

            sponsorIndex++
        }
    })

    return result
})
function animate(time) {
    if (!lastTime) lastTime = time
    const delta = time - lastTime
    lastTime = time

    if (!paused.value) {
        angle.value += delta * 0.00008
    }

    animationId = requestAnimationFrame(animate)
}
function startActiveTimer() {
    activeTimer = setInterval(() => {
        if (paused.value || sponsors.value.length === 0) return

        previousIndex.value = activeIndex.value
        activeIndex.value = (activeIndex.value + 1) % sponsors.value.length

        setTimeout(() => {
            previousIndex.value = null
        }, 1000)
    }, 1000)
}

function isActive(index) {
    if (hoveredIndex.value !== null) return hoveredIndex.value === index
    return activeIndex.value === index
}

function isLeaving(index) {
    if (hoveredIndex.value !== null) return false
    return previousIndex.value === index
}

function handleEnter(index) {
    paused.value = true
    hoveredIndex.value = index
}

function handleLeave() {
    paused.value = false
    hoveredIndex.value = null
}


onMounted(() => {
    loadSponsorsData()
    animationId = requestAnimationFrame(animate)
    startActiveTimer()
})

onUnmounted(() => {
    cancelAnimationFrame(animationId)
    clearInterval(activeTimer)
})
</script>

<template>
    <section class="sponsors-section">
        <div class="heading">
            <p>OUR PARTNERS</p>
            <h2>與我們一起<br>讓想法成為現實。</h2>
        </div>

        <div class="orbit-area">
            <div v-for="(ring, index) in ringConfig" :key="index" class="orbit" :style="{
                width: `${ring.rx * 2}%`, height: `${ring.ry * 2}%` }"></div>

            <div class="center">
                <span>DIT</span>
                <strong>PARTNERS</strong>
            </div>

            <div v-for="(sponsor, index) in sponsorPositions" :key="sponsor.id" class="sponsor-wrapper"
                :class="{ focused: isActive(index) }" :style="{ left: `${sponsor.x}%`, top: `${sponsor.y}%` }"
                @mouseenter="handleEnter(index)" @mouseleave="handleLeave">
                <a class="sponsor" :class="{ active: isActive(index), leaving: isLeaving(index) }" :href="sponsor.url"
                    target="_blank" rel="noopener noreferrer">
                    <img :src="sponsor.logo" :alt="sponsor.name">
                </a>

                <Transition name="tooltip">
                    <div v-if="hoveredIndex === index" class="tooltip" :class="sponsor.tooltipSide">
                        <p class="tooltip-label">PARTNER</p>
                        <h3>{{ sponsor.name }}</h3>
                        <p>{{ sponsor.description }}</p>
                        <span>前往網站 ↗</span>
                    </div>
                </Transition>
            </div>
        </div>
    </section>
</template>

<style scoped>
.sponsors-section {
    min-height: 100vh;
    padding: 100px 7vw;
    background: #f9f9f9;
    display: grid;
    grid-template-columns: .7fr 1.3fr;
    align-items: center;
    overflow: hidden;
}

.heading {
    position: relative;
    z-index: 5;
}

.heading>p {
    font-size: 13px;
    letter-spacing: .22em;
    font-weight: 700;
    margin-bottom: 20px;
}

.heading h2 {
    font-size: clamp(38px, 4vw, 72px);
    line-height: 1.05;
    margin: 0;
}

.orbit-area {
    position: relative;
    width: 100%;
    height: min(78vh, 760px);
}

.orbit {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    /* border: 1px solid rgba(0, 0, 0, .12); */
    border-radius: 50%;
    pointer-events: none;
}

.center {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    z-index: 1;
    pointer-events: none;
}

.center span {
    font-size: clamp(35px, 5vw, 80px);
    font-weight: 900;
    line-height: .9;
}

.center strong {
    font-size: 11px;
    letter-spacing: .3em;
    margin-top: 10px;
}

.sponsor-wrapper {
    position: absolute;
    transform: translate(-50%, -50%);
    z-index: 3;
}

.sponsor-wrapper.focused {
    z-index: 100;
}

.sponsor {
    width: 150px;
    height: 110px;
    padding: 12px;
    border-radius: 18px;
    background: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    box-sizing: border-box;
    /* box-shadow: 0 8px 30px rgba(0, 0, 0, .07); */
    transition: transform .3s cubic-bezier(.2, .8, .2, 1), box-shadow .3s;
    text-decoration: none;
}

.sponsor img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: contain;
    pointer-events: none;
    filter: brightness(0);
}

@keyframes sponsorEnter {
    0% {
        transform: scale(1);
    }

    70% {
        transform: scale(1.3);
    }

    100% {
        transform: scale(1.4);
    }
}

@keyframes sponsorLeave {
    0% {
        transform: scale(1.4);
    }

    30% {
        transform: scale(1.3);
    }

    100% {
        transform: scale(1);
    }
}

.sponsor-wrapper:hover .sponsor {
    transform: scale(1.3);
    /* box-shadow: 0 18px 45px rgba(0, 0, 0, .16); */
    animation: none;
}

.tooltip {
    position: absolute;
    left: 135px;
    top: 50%;
    transform: translateY(-50%);
    width: 220px;
    padding: 20px;
    background: #111;
    color: white;
    border-radius: 14px;
    pointer-events: none;
    box-shadow: 0 18px 45px rgba(0, 0, 0, .2);
    z-index: 200;
}

.tooltip.left {
    left: auto;
    right: 135px;
}

.tooltip::before {
    content: '';
    position: absolute;
    left: -7px;
    top: 50%;
    width: 14px;
    height: 14px;
    background: #111;
    transform: translateY(-50%)rotate(45deg);
}

.tooltip.left::before {
    left: auto;
    right: -7px;
}

.tooltip-label {
    font-size: 9px;
    letter-spacing: .2em;
    opacity: .5;
    margin: 0 0 8px;
}

.tooltip h3 {
    font-size: 18px;
    margin: 0 0 8px;
}

.tooltip>p:not(.tooltip-label) {
    font-size: 12px;
    line-height: 1.6;
    opacity: .7;
    margin: 0 0 14px;
}

.tooltip span {
    font-size: 11px;
    font-weight: 700;
}

.tooltip-enter-active,
.tooltip-leave-active {
    transition: .2s ease;
}

.tooltip-enter-from,
.tooltip-leave-to {
    opacity: 0;
}

.tooltip-enter-from.right,
.tooltip-leave-to.right {
    transform: translateY(-50%)translateX(-10px);
}

.tooltip-enter-from.left,
.tooltip-leave-to.left {
    transform: translateY(-50%)translateX(10px);
}

@media(max-width:1100px) {
    .sponsors-section {
        grid-template-columns: .6fr 1.4fr;
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

@media(max-width:900px) {
    .sponsors-section {
        grid-template-columns: 1fr;
        padding: 80px 25px;
    }

    .heading {
        margin-bottom: 30px;
    }

    .orbit-area {
        height: 600px;
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