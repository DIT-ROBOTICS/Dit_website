<script setup>
import { onMounted, ref } from 'vue'

const advisors = ref([])
const loading = ref(true)
const errorMessage = ref('')
const selectedAdvisor = ref(null)

async function loadAdvisors() {
    try {
        const response = await fetch('/api/member_info/Advisor')

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
        }

        advisors.value = await response.json()
    } catch (error) {
        console.error(error)
        errorMessage.value = '指導教授資料載入失敗'
    } finally {
        loading.value = false
    }
}

function openAdvisor(advisor) {
    selectedAdvisor.value = advisor
}

function closeAdvisor() {
    selectedAdvisor.value = null
}

function getDisplayTitle(advisor) {
    let pos = advisor.position.length
    const first = advisor.position.slice(0,Math.ceil(pos/2))
    const last = advisor.position.slice(Math.ceil(pos/2))
    return [first,last]
}

function getImage(advisor) {
    return `/api/member_images/advisor-image/${advisor.id}`
}

onMounted(loadAdvisors)
</script>

<template>
    <section id="advisors" class="advisor-section">
        <header class="advisor-heading">
            <p>團隊的靠山</p>
        </header>

        <div v-if="loading" class="state-message">
            載入指導教授資料中……
        </div>

        <div v-else-if="errorMessage" class="state-message">
            {{ errorMessage }}
        </div>

        <div v-else class="advisor-stage" :class="{ 'detail-mode': selectedAdvisor }">
            <article v-for="advisor in advisors" :key="advisor.id" class="advisor-card" :class="{
                selected: selectedAdvisor?.id === advisor.id,
                hidden: selectedAdvisor && selectedAdvisor.id !== advisor.id
            }" @click="openAdvisor(advisor)">
                <div class="advisor-portrait">
                    <span class="role-word role-word-left">
                        {{ getDisplayTitle(advisor)[0] }}
                    </span>

                    <img :src="getImage(advisor)" :alt="advisor.name">

                    <span class="role-word role-word-right">
                        {{ getDisplayTitle(advisor)[1] }}
                    </span>
                </div>

                <h3>{{ advisor.name }}</h3>
            </article>

            <Transition name="detail">
                <div v-if="selectedAdvisor" class="advisor-detail">
                    <button class="detail-close" type="button" @click="closeAdvisor">
                        ×
                    </button>

                    <p class="detail-role">
                        {{ selectedAdvisor.position }}
                    </p>
                    <p class="detail-role">
                        {{ selectedAdvisor.name }}
                    </p>
                    <p class="detail-role">
                        {{ selectedAdvisor.spell }}
                    </p>
                    <p class="detail-role">
                        {{ selectedAdvisor.job }}
                    </p>
                    <p class="detail-role">
                        {{ selectedAdvisor.department }}
                    </p>
                    <p class="detail-role">
                        {{ selectedAdvisor.major }}
                    </p>

                    <div class="skills-tags">
                        <span v-for="skill in selectedAdvisor.skills" :key="skill">
                            {{ skill }}
                        </span>
                    </div>
                </div>
            </Transition>
        </div>
    </section>
</template>

<style scoped src="@/styles/member-scroller.css"></style>
<style scoped>
.advisor-section {
    width: 100%;
    background: #303033;
    color: #eee;
    overflow: hidden;
}

.advisor-heading {
    height: 120px;
    padding: 0 7vw;
    display: flex;
    align-items: center;
    background: #303033;
}

.advisor-heading p {
    margin: 0;
    font-size: clamp(38px, 4vw, 64px);
    font-weight: 900;
    letter-spacing: .02em;
}

.advisor-stage {
    position: relative;
    /* min-height: 480px; */
    padding: 20px 5vw 30px;
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    align-items: end;
    gap: 3vw;
    background: #69696f;
    transition:background .5s ease;
}

.advisor-card {
    position: relative;
    min-width: 0;
    cursor: pointer;
    font-weight: 900;
    transition:transform .7s cubic-bezier(.22,1,.36,1),opacity .4s ease;
}

.advisor-card:hover {
    transform: translateY(-10px);
}

.advisor-portrait {
    position: relative;
    width: 100%;
    height: 280px;
    display: flex;
    justify-content: center;
    align-items: flex-end;
}

.advisor-portrait img {
    position: relative;
    z-index: 2;
    display: block;
    width: 85%;
    height: 100%;
    object-fit: contain;
    object-position: center bottom;
    transition: width .7s cubic-bezier(.22, 1, .36, 1);
}

.role-word {
    position: absolute;
    z-index: 1;
    font-size: clamp(42px, 4vw, 70px);
    font-weight: 500;
    white-space: nowrap;
    pointer-events: none;
}

.role-word-left {
    left: 0;
    top: 20px;
    transform: rotate(-6deg);
}

.role-word-right {
    right: 0;
    top: 140px;
    transform: rotate(7deg);
}

.advisor-card h3 {
    position: relative;
    z-index: 3;
    margin: 20px 0 0;
    text-align: center;
    font-size: clamp(24px, 2.1vw, 36px);
    font-weight: 600;
    letter-spacing: .05em;
}

.advisor-stage.detail-mode {
    grid-template-columns: 32% 68%;
    gap: 0;
    padding: 0;
    min-height: 520px;
    background: #b5b5ba;
}

.advisor-stage.detail-mode .advisor-card.selected {
    grid-column: 1;
    grid-row: 1;
    width: 100%;
    height: 100%;
    padding: 30px 25px;
    background: #69696f;
    transform: none;
    cursor: default;
}

.advisor-stage.detail-mode .advisor-card.selected .advisor-portrait {
    height: 360px;
}

.advisor-stage.detail-mode .advisor-card.selected .advisor-portrait img {
    width: 90%;
}

.advisor-stage.detail-mode .advisor-card.hidden {
    position: absolute;
    opacity: 0;
    pointer-events: none;
    transform: translateY(40px) scale(.92);
}

.advisor-detail {
    position: relative;
    grid-column: 2;
    grid-row: 1;
    min-height: 520px;
    padding: 55px 7vw 50px 4vw;
    display: flex;
    flex-direction: column;
    justify-content: center;
    color: #fff;
    background: #b5b5ba;
}

.detail-close {
    position: absolute;
    top: 25px;
    right: 30px;
    width: 45px;
    height: 45px;
    border: 1px solid rgba(255, 255, 255, .55);
    border-radius: 50%;
    background: transparent;
    color: #fff;
    font-size: 28px;
    cursor: pointer;
}

.detail-role {
    margin: 0 0 20px;
    font-size: clamp(25px, 2.5vw, 42px);
    font-weight: 300;
}

.advisor-detail h2 {
    margin: 0 0 18px;
    font-size: clamp(36px, 4vw, 60px);
    line-height: 1;
    font-weight: 300;
    letter-spacing: .04em;
}

.detail-english {
    margin: 0 0 25px;
    font-size: clamp(18px, 2vw, 30px);
    letter-spacing: .18em;
    text-transform: uppercase;
}

.detail-lines {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.detail-lines p {
    margin: 0;
    font-size: clamp(20px, 2.2vw, 34px);
    font-weight: 300;
    line-height: 1.3;
}

.detail-description {
    max-width: 700px;
    margin: 28px 0 0;
    font-size: 16px;
    line-height: 1.8;
}

.detail-leave-active{
    position:absolute;
    top:0;
    right:0;
    width:68%;
    height:100%;
    z-index:10;
    transition:opacity .45s ease,transform .65s cubic-bezier(.22,1,.36,1);
}

.detail-enter-active{
    transition:opacity .45s ease,transform .65s cubic-bezier(.22,1,.36,1);
}

.detail-enter-from,
.detail-leave-to{
    opacity:0;
    transform:translateX(60px);
}

@media(max-width:850px) {
    .advisor-heading {
        height: 90px;
        padding: 0 25px;
    }

    .advisor-stage {
        grid-template-columns: 1fr;
        gap: 30px;
        padding: 30px 25px;
    }

    .advisor-portrait {
        height: 300px;
    }

    .advisor-stage.detail-mode {
        display: flex;
        flex-direction: column;
    }

    .advisor-stage.detail-mode .advisor-card.selected {
        width: 100%;
    }

    .advisor-detail {
        width: 100%;
        min-height: 400px;
        padding: 50px 30px;
    }
}
</style>