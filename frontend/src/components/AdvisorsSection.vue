<!--
介紹指導人員：
有兩個教授和俊峰和其他學長之類的介紹
-->

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const advisors = ref([])
const activeIndex = ref(null)
const usesTouchInteraction = ref(window.matchMedia('(hover: none), (pointer: coarse)').matches)
let touchMediaQuery

async function loadAdvisors() {
    try {
        const response = await fetch('/api/Advisor/data')
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        advisors.value = await response.json()
    } catch (error) {
        console.error('顧問資料載入失敗：', error)
    }
}

function cardState(index) {
    if (activeIndex.value === null) return 'is-idle'
    if (index === activeIndex.value) return 'is-active'
    return index < activeIndex.value ? 'is-left' : 'is-right'
}

function cardStyle(index) {
    return { '--card-index': index }
}

function closeCard(event) {
    if (usesTouchInteraction.value) return
    if (!event.currentTarget.contains(event.relatedTarget)) activeIndex.value = null
}

function activateFromHover(index) {
    if (!usesTouchInteraction.value) activeIndex.value = index
}

function closeFromHover() {
    if (!usesTouchInteraction.value) activeIndex.value = null
}

// 觸控裝置以點擊展開；再次點擊同一卡片不收合，保留給未來的跳轉功能。
function activateFromTouch(index) {
    if (usesTouchInteraction.value) activeIndex.value = index
}

// 點擊顧問卡片以外的空白區域時，關閉目前展開的卡片。
function closeFromOutside(event) {
    if (!usesTouchInteraction.value || activeIndex.value === null) return
    if (event.target.closest('.advisor-card')) return
    activeIndex.value = null
}

function updateInteractionMode(event) {
    usesTouchInteraction.value = event.matches
    activeIndex.value = null
}

onMounted(() => {
    loadAdvisors()
    touchMediaQuery = window.matchMedia('(hover: none), (pointer: coarse)')
    usesTouchInteraction.value = touchMediaQuery.matches
    touchMediaQuery.addEventListener('change', updateInteractionMode)
    document.addEventListener('pointerdown', closeFromOutside)
})

onUnmounted(() => {
    touchMediaQuery?.removeEventListener('change', updateInteractionMode)
    document.removeEventListener('pointerdown', closeFromOutside)
})
</script>

<template>
    <Teleport defer to="#Advisors_teleport">
    <section id="advisors" class="advisors-section" @mouseleave="closeFromHover">
        <div class="advisors-stage">
            <header class="advisors-heading">
                <p class="advisors-eyebrow">ADVISORS</p>
                <h2 class="advisors-title">技術顧問</h2>
            </header>

            <article v-for="(advisor, index) in advisors" :key="advisor.id" class="advisor-card"
                :class="[cardState(index), `advisor-card-${index}`]" :style="cardStyle(index)" tabindex="0"
                @mouseenter="activateFromHover(index)" @mouseleave="closeFromHover"
                @focus="activateFromHover(index)" @blur="closeCard" @click="activateFromTouch(index)">
                <div class="advisor-photo-wrap">
                    <img class="advisor-photo" :src="advisor.image" :alt="advisor.name" />
                </div>

                <div class="advisor-summary">
                    <p>{{ advisor.position }}</p>
                    <h3>{{ advisor.name }}</h3>
                </div>

                <div class="advisor-details">
                    <p class="advisor-position">{{ advisor.position }}</p>
                    <h3>{{ advisor.name }}</h3>
                    <p class="advisor-spell">{{ advisor.spell }}</p>
                    <div class="advisor-resume">
                        <p>{{ advisor.job }}</p>
                        <p>{{ advisor.department }} {{ advisor.major }}</p>
                    </div>
                    <p class="advisor-description">{{ advisor.description }}</p>
                    <ul class="advisor-skills" aria-label="專長">
                        <li v-for="skill in advisor.skills" :key="skill">{{ skill }}</li>
                    </ul>
                </div>
            </article>
        </div>
    </section>
    </Teleport>
</template>

<style scoped>
.advisors-section {
    position: relative;
    z-index: 2;
    padding: 50px 0 40px;
    overflow: hidden;
    background: #e0e0e0;
}

.advisors-heading {
    position: absolute;
    z-index: 0;
    top: 25%;
    left: 6vw;
    width: 25vw;
    transform: translateY(-50%);
}

.advisors-eyebrow {
    margin: 0 0 12px;
    color: #6f6c85;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.22em;
}

.advisors-title {
    margin: 0;
    color: #292832;
    font-size: clamp(40px, 4.5vw, 88px);
    line-height: 1;
    letter-spacing: 0.1em;
}

.advisors-stage {
    position: relative;
    height: 375px;
}

.advisor-card {
    --card-width: min(500px, 17.6vw);
    position: absolute;
    z-index: 1;
    /* top: 50%; */
    left: calc(45% + var(--card-index) * 20%);
    width: var(--card-width);
    height: 360px;
    overflow: hidden;
    color: #f7f6ff;
    background: #100d40;
    border-radius: 24px;
    box-shadow: 0 15px 40px rgba(18, 14, 56, 0.18);
    outline: none;
    transform: translate(-50%, 0);
    transition: left 700ms cubic-bezier(0.22, 1, 0.36, 1), width 700ms cubic-bezier(0.22, 1, 0.36, 1),
        height 700ms cubic-bezier(0.22, 1, 0.36, 1), transform 700ms cubic-bezier(0.22, 1, 0.36, 1),
        opacity 450ms ease, box-shadow 450ms ease;
}

.advisor-card:focus-visible {
    box-shadow: 0 0 0 4px #8d88ff, 0 25px 50px rgba(18, 14, 56, 0.28);
}

.advisor-card.is-active {
    z-index: 3;
    left: 65%;
    width: min(850px, 60vw);
    height: 380px;
    transform: translate(-50%, 0);
    box-shadow: 0 25px 50px rgba(18, 14, 56, 0.28);
}

.advisor-card.is-left,
.advisor-card.is-right {
    opacity: 0;
    pointer-events: none;
}

.advisor-photo-wrap {
    position: absolute;
    inset: 0 0 28% 0;
    overflow: hidden;
    transition: right 700ms cubic-bezier(0.22, 1, 0.36, 1), bottom 700ms cubic-bezier(0.22, 1, 0.36, 1);
}

.advisor-photo {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: contain;
    object-position: center bottom;
}

.advisor-card.is-active .advisor-photo-wrap { right: 56%; bottom: 0; }

.advisor-summary {
    position: absolute;
    inset: 72% 0 0;
    padding: 20px 24px;
    background: rgba(16, 13, 64, 0.96);
    transition: opacity 250ms ease;
}

.advisor-summary p,
.advisor-position {
    margin: 0 0 7px;
    color: #c9c7da;
    font-size: 14px;
    letter-spacing: 0.16em;
}

.advisor-summary h3 { margin: 0; font-size: clamp(20px, 1.75vw, 29px); letter-spacing: 0.04em; }
.advisor-card.is-active .advisor-summary { opacity: 0; pointer-events: none; }

.advisor-details {
    position: absolute;
    top: 50%;
    right: 0;
    width: 56%;
    padding: 35px clamp(22px, 3.2vw, 50px) 32px 22px;
    opacity: 0;
    transform: translate(28px, -50%);
    transition: opacity 300ms ease, transform 500ms ease;
    pointer-events: none;
}

.advisor-card.is-active .advisor-details {
    opacity: 1;
    transform: translate(0, -50%);
    transition-delay: 260ms;
}

.advisor-details h3 { margin: 0; font-size: clamp(24px, 2.55vw, 38px); line-height: 1.2; }
.advisor-spell { margin: 6px 0 24px; font-size: clamp(14px, 1.35vw, 20px); font-weight: 800; }
.advisor-resume { font-size: clamp(13px, 1.15vw, 18px); line-height: 1.65; }
.advisor-resume p, .advisor-description { margin: 0; }
.advisor-description { margin-top: 16px; color: #c9c7da; font-size: 13px; line-height: 1.7; }

.advisor-skills {
    display: flex;
    margin: 19px 0 0;
    padding: 0;
    gap: 8px;
    flex-wrap: wrap;
    list-style: none;
}

.advisor-skills li {
    padding: 6px 10px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 999px;
    font-size: 11px;
}

@media (max-width: 900px) {
    .advisors-section { padding: 80px 0; }
    .advisors-stage {
        display: grid;
        width: min(520px, 88vw);
        height: auto;
        margin: 45px auto 0;
        gap: 22px;
    }

    .advisors-heading {
        position: static;
        width: 100%;
        margin-bottom: 20px;
        transform: none;
    }

    .advisor-card,
    .advisor-card.is-active,
    .advisor-card.is-left,
    .advisor-card.is-right {
        position: relative;
        top: auto;
        left: auto;
        width: 100%;
        height: 368px;
        opacity: 1;
        transform: none;
    }

    .advisor-card.is-active .advisor-photo-wrap { right: 0; bottom: 28%; }
    .advisor-card.is-active .advisor-summary { opacity: 1; }
    .advisor-details { display: none; }
}

@media (prefers-reduced-motion: reduce) {
    .advisor-card, .advisor-photo-wrap, .advisor-summary, .advisor-details { transition: none; }
}
</style>
