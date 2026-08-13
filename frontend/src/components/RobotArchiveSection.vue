<!--
歷年機器：
當年其他比賽或營隊的機器人
一樣有詳細資訊可以去查看團隊歷年的機器人
-->
<!--
歷年機器：
當年其他比賽或營隊的機器人
一樣有詳細資訊可以去查看團隊歷年的機器人
-->

<script setup>
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import RobotViewer3D from '@/components/template/RobotViewer3D.vue'
import blackRobot2026 from '@/assets/Eurobot2026黑機.glb?url'
import whiteRobot2026 from '@/assets/Eurobot2026白機.glb?url'

const BackgroundImage = ref("/api/other_images/competition/background.png")
const robotHistory = ref([
    {
        year: 2026,
        competition: 'EUROBOT 2026',
        title: 'Two Robots, One Goal.',
        description: '2026 年，我們以兩台不同定位的機器共同完成 Eurobot 賽場任務，在機構、控制、定位與策略上持續挑戰更高的完成度。',
        achievements: ['World TOP 2', 'Team Choice Award'],
        background: '/api/other_images/competition/background.png',
        themeColor: '#ef907e',
        robots: [
            {
                id: '2026-white',
                name: '白機',
                team: 'NTHU DIT',
                image: '/api/other_images/competition/2026/Eurobot/Eurobot2026白機.png',
                model: whiteRobot2026,
                pos: 'left',
                description: '三面手臂設計，兼顧快速任務執行、模組化維修與定位穩定性。'
            },
            {
                id: '2026-black',
                name: '黑機',
                team: 'DIT Robotics',
                image: '/api/other_images/competition/2026/Eurobot/Eurobot2026黑機.png',
                model: blackRobot2026,
                pos: 'right',
                description: '四面手臂架構，整合高速移動、任務機構、定位與無限鏡視覺設計。'
            }
        ]
    },
    {
        year: 2025,
        competition: 'EUROBOT 2025',
        title: 'Built to Go Further.',
        description: '延續前一代機器的經驗，我們重新調整底盤、模組配置與任務結構，在有限空間中追求更高的可靠性。',
        achievements: ['Eurobot Taiwan'],
        background: '/api/other_images/competition/background.png',
        themeColor: '#e78172',
        robots: [
            {
                id: '2025-white',
                name: '白機',
                team: 'NTHU DIT',
                image: '/api/other_images/competition/2025/Eurobot/Eurobot2025白機.png',
                model: null,
                pos: 'left',
                description: '以快速執行任務與穩定移動為核心所設計的年度機器。'
            },
            {
                id: '2025-black',
                name: '黑機',
                team: 'DIT Robotics',
                image: '/api/other_images/competition/2025/Eurobot/Eurobot2025黑機.png',
                model: null,
                pos: 'right',
                description: '針對 Eurobot 任務重新設計機構配置與控制流程。'
            }
        ]
    },
    {
        year: 2024,
        competition: 'EUROBOT 2024',
        title: 'Learning Through Every Iteration.',
        description: '每一代機器都是下一代設計的基礎。從機構失敗、控制誤差到比賽現場的臨場問題，都成為團隊持續改進的重要經驗。',
        achievements: ['Eurobot Taiwan'],
        background: '/api/other_images/competition/background.png',
        themeColor: '#d77667',
        robots: [
            {
                id: '2024-main',
                name: '2024 Robot',
                team: 'DIT Robotics',
                image: '/api/other_images/competition/2024/Eurobot/robot.png',
                model: null,
                pos: 'left',
                description: 'Eurobot 2024 年度參賽機器。'
            }
        ]
    },
    {
        year: 2023,
        competition: 'EUROBOT 2023',
        title: 'Where Ideas Became Machines.',
        description: '持續累積製造、電控與程式經驗，讓越來越多想法真正成為能夠在賽場上運作的機器。',
        achievements: [],
        background: '/api/other_images/competition/background.png',
        themeColor: '#c6685e',
        robots: [
            {
                id: '2023-main',
                name: '2023 Robot',
                team: 'DIT Robotics',
                image: '/api/other_images/competition/2023/Eurobot/robot.png',
                model: null,
                pos: 'left',
                description: 'DIT Robotics 2023 年度機器。'
            }
        ]
    }
])

const trackElement = ref(null)
const activeIndex = ref(0)
const selectedRobot = ref(null)

function openRobot(robot) {
    if (!robot.model) {
        console.log('這台機器目前沒有 GLB：', robot.name)
        return
    }
    selectedRobot.value = robot
    document.body.style.overflow = 'hidden'
}

function closeRobot() {
    selectedRobot.value = null
    document.body.style.overflow = ''
}

function scrollToYear(index) {
    const track = trackElement.value
    if (!track) return
    const page = track.children[index]
    if (!page) return
    page.scrollIntoView({
        behavior: 'smooth',
        inline: 'center',
        block: 'nearest'
    })
}

function updateActiveYear() {
    const track = trackElement.value
    if (!track) return
    const pages = [...track.children]
    const trackRect = track.getBoundingClientRect()
    const trackCenter = trackRect.left + trackRect.width / 2
    let nearestIndex = 0
    let nearestDistance = Infinity
    pages.forEach((page, index) => {
        const rect = page.getBoundingClientRect()
        const pageCenter = rect.left + rect.width / 2
        const distance = Math.abs(pageCenter - trackCenter)
        if (distance < nearestDistance) {
            nearestDistance = distance
            nearestIndex = index
        }
    })
    activeIndex.value = nearestIndex
}

onMounted(async () => {
    await nextTick()
    updateActiveYear()
})

onUnmounted(() => {
    document.body.style.overflow = ''
})
</script>

<template>
    <section id="robots" class="robot-archive">
        <div class="sticky-background">
            <img :src="BackgroundImage" alt="DIT Robotics 2026 Team" class="background-image">
        </div>
        <div class="archive-container">
            <header class="archive-header">
                <div>
                    <p class="archive-eyebrow">OUR JOURNEY</p>
                    <h2>
                        ROBOT
                        <span>ARCHIVE</span>
                    </h2>
                </div>

                <div class="archive-instruction">
                    <span>EXPLORE THE PAST</span>
                    <span class="arrow">←</span>
                </div>
            </header>

            <div ref="trackElement" class="archive-track" @scroll.passive="updateActiveYear">
                <article v-for="(item, yearIndex) in robotHistory" :key="item.year" class="year-page"
                    :class="{ active: activeIndex === yearIndex }">
                    <!-- <div class="year-background" :style="{ backgroundImage: `url(${item.background})` }"></div> -->

                    <div class="year-overlay"></div>

                    <div class="background-year">
                        {{ item.year }}
                    </div>

                    <div class="year-info">
                        <p class="competition" :style="{ color: item.themeColor }">
                            {{ item.competition }}
                        </p>

                        <h3>{{ item.title }}</h3>

                        <p class="year-description">
                            {{ item.description }}
                        </p>

                        <div v-if="item.achievements.length" class="achievements">
                            <span v-for="achievement in item.achievements" :key="achievement">
                                {{ achievement }}
                            </span>
                        </div>
                    </div>

                    <div class="robots-area" :class="{ single: item.robots.length === 1 }">
                        <button v-for="robot in item.robots" :key="robot.id" class="robot-card"
                            :class="{ clickable: robot.model }" type="button" @click="openRobot(robot)">
                            <div class="robot-image-wrapper">
                                <img :src="robot.image" :alt="robot.name">

                                <div v-if="robot.model" class="view-3d">
                                    VIEW 3D
                                </div>
                            </div>

                            <div class="robot-meta">
                                <div>
                                    <p>{{ robot.team }}</p>
                                    <h4>{{ robot.name }}</h4>
                                </div>

                                <span v-if="robot.model" class="robot-arrow">
                                    ↗
                                </span>
                            </div>
                        </button>
                    </div>
                </article>
            </div>

            <div class="timeline">
                <div class="timeline-line"></div>

                <button v-for="(item, index) in robotHistory" :key="item.year" class="timeline-point"
                    :class="{ active: activeIndex === index }" type="button" @click="scrollToYear(index)">
                    <span class="timeline-dot"></span>
                    <span class="timeline-year">{{ item.year }}</span>
                </button>
            </div>
        </div>

        <Transition name="modal">
            <div v-if="selectedRobot" class="robot-modal" @click.self="closeRobot">
                <button class="close-button" type="button" @click="closeRobot">
                    ×
                </button>

                <RobotViewer3D :model="selectedRobot.model" :pos="selectedRobot.pos" />

                <div class="viewer-info">
                    <p>{{ selectedRobot.team }}</p>
                    <h3>{{ selectedRobot.name }}</h3>
                    <span>DRAG TO ROTATE · SCROLL TO ZOOM</span>
                </div>
            </div>
        </Transition>
    </section>
</template>

<style scoped>
.robot-archive {
    position: relative;
    width: 100%;
    /* overflow: hidden; */
    background: #171719;
    color: white;
}
.sticky-background {
    position: sticky;

    top: 76px;

    width: 100%;
    height: calc(100vh - 76px);

    overflow: hidden;

    z-index: 0;

    img{
        width:100%;
        height:100%;
        object-fit:cover;
    }
}
.sticky-background::after{
    content:'';
    position:absolute;
    inset:0;
    pointer-events:none;
    background:rgba(0,0,0,.22);
}

.archive-container {
    position: relative;
    width: 100%;
    z-index: 2;
    margin-top: -100vh;
    padding: 20% 0 15%;
}

.archive-header {
    position: relative;
    z-index: 20;
    width: 100%;
    padding: 0 5vw 40px;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    pointer-events: none;
}

.archive-eyebrow {
    margin: 0 0 5px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .35em;
    opacity: .55;
}

.archive-header h2 {
    margin: 0;
    font-size: clamp(38px, 4.2vw, 72px);
    line-height: .85;
    font-weight: 900;
    letter-spacing: -.045em;
}

.archive-header h2 span {
    display: block;
    color: transparent;
    -webkit-text-stroke: 1px rgba(255, 255, 255, .65);
}

.archive-instruction {
    margin-top: 6%;
    display: flex;
    align-items: center;
    gap: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .2em;
    opacity: .6;
}

.archive-instruction .arrow {
    font-size: 30px;
    font-weight: 300;
    letter-spacing: 0;
}

.archive-track {
    width: 100%;
    display: flex;
    gap: 30px;
    padding: 0 7vw 30px;
    overflow-x: auto;
    overflow-y: hidden;
    scroll-snap-type: x mandatory;
    scroll-behavior: smooth;
    scrollbar-width: none;
    overscroll-behavior-x: contain;
    -webkit-overflow-scrolling: touch;
}

.archive-track::-webkit-scrollbar {
    display: none;
}

.year-page {
    position: relative;
    flex: 0 0 min(1200px, 86vw);
    width: min(1400px, 95vw);
    height: min(700px, 70vh);
    min-height: 620px;
    overflow: hidden;
    display: grid;
    grid-template-columns: 1fr 1.25fr;
    align-items: center;
    padding: 110px 5vw 80px;
    border-radius: 30px;
    scroll-snap-align: center;
    isolation: isolate;
    opacity: .65;
    transform: scale(.97);
    transition: opacity .45s ease, transform .45s ease;
}

.year-page::before{
    content:'';
    position:absolute;
    z-index:-1;
    inset:0;
    border-radius:30px;
    background:linear-gradient(90deg,rgba(10,10,12,.82) 0%,rgba(10,10,12,.58) 36%,rgba(10,10,12,.18) 62%,rgba(10,10,12,.35) 100%);
    backdrop-filter:blur(2px);
    -webkit-backdrop-filter:blur(2px);
}

.year-page.active {
    opacity: 1;
    transform: scale(1);
}

.year-background {
    position: absolute;
    z-index: -4;
    inset: 0;
    background-size: cover;
    background-position: center;
    opacity: .2;
    transform: scale(1.08);
    filter: grayscale(.4);
}

.year-overlay {
    position: absolute;
    z-index: -3;
    inset: 0;
    /* background: linear-gradient(90deg, rgba(20, 20, 22, .96) 0%, rgba(20, 20, 22, .84) 38%, rgba(20, 20, 22, .45) 70%, rgba(20, 20, 22, .72) 100%); */
}

.background-year {
    position: absolute;
    z-index: -2;
    right: 1vw;
    bottom: 3vh;
    font-size: clamp(150px, 20vw, 350px);
    line-height: .7;
    font-weight: 900;
    letter-spacing: -.08em;
    color: rgba(255, 255, 255, .035);
    user-select: none;
    pointer-events: none;
}

.year-info {
    position: relative;
    z-index: 5;
    align-self: end;
    padding-bottom: 30px;
    max-width: 520px;
}

.competition {
    margin: 0 0 14px;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: .24em;
}

.year-info h3 {
    margin: 0 0 22px;
    max-width: 540px;
    font-size: clamp(38px, 4.5vw, 76px);
    line-height: .88;
    letter-spacing: -.055em;
    font-weight: 850;
}

.year-description {
    max-width: 480px;
    margin: 0;
    font-size: clamp(13px, 1vw, 17px);
    line-height: 1.8;
    opacity: .65;
}

.achievements {
    margin-top: 32px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.achievements span {
    padding: 8px 13px;
    border: 1px solid rgba(255, 255, 255, .2);
    border-radius: 100px;
    background: rgba(255, 255, 255, .04);
    backdrop-filter: blur(10px);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .12em;
    text-transform: uppercase;
}

.robots-area {
    position: relative;
    z-index: 5;
    height: 58vh;
    max-height: 600px;
    display: flex;
    justify-content: center;
    align-items: flex-end;
    gap: clamp(0px, 1vw, 25px);
}

.robots-area.single .robot-card {
    max-width: 430px;
}

.robot-card {
    position: relative;
    width: min(23vw, 390px);
    padding: 0;
    border: 0;
    color: inherit;
    background: transparent;
    text-align: left;
    font: inherit;
    cursor: default;
    transition: transform .45s cubic-bezier(.22, 1, .36, 1);
}

.robot-card.clickable {
    cursor: pointer;
}

.robot-card.clickable:hover {
    transform: translateY(-15px);
}

.robot-image-wrapper {
    position: relative;
    width: 100%;
    aspect-ratio: 4/5;
    display: flex;
    align-items: flex-end;
    justify-content: center;
}

.robot-image-wrapper img {
    position: relative;
    z-index: 2;
    width: 100%;
    height: 100%;
    object-fit: contain;
    filter: drop-shadow(0 30px 30px rgba(0, 0, 0, .38));
    transition: transform .45s cubic-bezier(.22, 1, .36, 1);
}

.robot-card.clickable:hover .robot-image-wrapper img {
    transform: scale(1.035);
}

.view-3d {
    position: absolute;
    z-index: 4;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%) translateY(10px);
    padding: 9px 15px;
    border-radius: 100px;
    background: rgba(255, 255, 255, .9);
    color: #151515;
    font-size: 9px;
    font-weight: 800;
    letter-spacing: .15em;
    white-space: nowrap;
    opacity: 0;
    transition: .3s ease;
}

.robot-card:hover .view-3d {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
}

.robot-meta {
    margin-top: 4px;
    padding-top: 13px;
    border-top: 1px solid rgba(255, 255, 255, .16);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.robot-meta p {
    margin: 0 0 3px;
    font-size: 9px;
    letter-spacing: .18em;
    font-weight: 700;
    opacity: .45;
    text-transform: uppercase;
}

.robot-meta h4 {
    margin: 0;
    font-size: clamp(18px, 1.6vw, 28px);
    font-weight: 800;
}

.robot-arrow {
    font-size: 23px;
    opacity: .5;
}

.year-index {
    position: absolute;
    right: 2vw;
    top: 50%;
    transform: translateY(-50%) rotate(90deg);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .2em;
    opacity: .25;
}

.timeline {
    position: relative;
    z-index: 30;
    width: min(720px, 70vw);
    height: 30px;
    margin: 0px auto 0;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
}

.timeline-line {
    position: absolute;
    top: 5px;
    left: 0;
    width: 100%;
    height: 1px;
    background: rgba(255, 255, 255, .18);
}

.timeline-point {
    position: relative;
    z-index: 2;
    border: 0;
    padding: 0;
    background: transparent;
    color: white;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

.timeline-dot {
    width: 11px;
    height: 11px;
    border-radius: 50%;
    border: 2px solid rgba(255, 255, 255, .55);
    background: #171719;
    transition: .3s ease;
}

.timeline-year {
    font-size: 9px;
    font-weight: 700;
    letter-spacing: .12em;
    opacity: .4;
    transition: .3s ease;
}

.timeline-point.active .timeline-dot {
    background: white;
    border-color: white;
    transform: scale(1.35);
}

.timeline-point.active .timeline-year {
    opacity: 1;
}

.robot-modal {
    position: fixed;
    z-index: 99999;
    inset: 0;
    background: rgba(10, 10, 12, .45);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 70px 40px 40px;
}

.close-button {
    position: absolute;
    z-index: 5;
    top: 30px;
    right: 35px;
    width: 52px;
    height: 52px;
    border: 1px solid rgba(255, 255, 255, .3);
    border-radius: 50%;
    background: rgba(255, 255, 255, .07);
    color: white;
    font-size: 30px;
    font-weight: 200;
    cursor: pointer;
}

.viewer-info {
    position: absolute;
    left: 5vw;
    bottom: 5vh;
}

.viewer-info p {
    margin: 0 0 5px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .18em;
    opacity: .5;
}

.viewer-info h3 {
    margin: 0 0 8px;
    font-size: clamp(35px, 5vw, 70px);
    line-height: 1;
    font-weight: 850;
}

.viewer-info span {
    font-size: 9px;
    letter-spacing: .16em;
    opacity: .45;
}

.modal-enter-active,
.modal-leave-active {
    transition: opacity .35s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}

@media(max-width:1100px) {
    .year-page {
        grid-template-columns: .65fr 1.35fr;
        flex-basis: 90vw;
        width: 90vw;
        padding-left: 4vw;
        padding-right: 4vw;
    }

    .robot-card {
        width: 28vw;
    }

    .year-info h3 {
        font-size: clamp(36px, 5vw, 60px);
    }
}

@media(max-width:850px) {
    .robot-archive {
        padding: 60px 0 45px;
    }

    .archive-header {
        padding: 0 25px 30px;
    }

    .archive-header h2 {
        font-size: 35px;
    }

    .archive-instruction span:first-child {
        display: none;
    }

    .archive-instruction .arrow {
        font-size: 26px;
    }

    .archive-track {
        gap: 15px;
        padding: 0 7vw 20px;
        scroll-snap-type: x mandatory;
    }

    .year-page {
        flex: 0 0 86vw;
        width: 86vw;
        height: 72vh;
        min-height: 570px;
        grid-template-columns: 1fr;
        align-content: end;
        padding: 90px 25px 45px;
        border-radius: 24px;
    }

    .year-info {
        order: 2;
        padding: 0;
        max-width: 100%;
    }

    .competition {
        font-size: 10px;
    }

    .year-info h3 {
        max-width: 90%;
        margin-bottom: 12px;
        font-size: 38px;
    }

    .year-description {
        display: none;
    }

    .achievements {
        margin-top: 15px;
    }

    .robots-area {
        order: 1;
        height: 42vh;
        align-items: flex-end;
        margin-bottom: 12px;
    }

    .robot-card {
        width: 41vw;
    }

    .robots-area.single .robot-card {
        width: 64vw;
    }

    .robot-meta {
        display: none;
    }

    .view-3d {
        display: none;
    }

    .background-year {
        right: -3vw;
        bottom: 15vh;
        font-size: 38vw;
    }

    .timeline {
        width: calc(100% - 50px);
        margin-top: 20px;
    }

    .timeline-year {
        font-size: 8px;
    }

    .year-index {
        display: none;
    }

    .robot-modal {
        padding: 70px 10px 20px;
    }

    .close-button {
        top: 18px;
        right: 18px;
        width: 45px;
        height: 45px;
    }

    .viewer-info {
        left: 25px;
        bottom: 30px;
    }
}

@media(max-width:520px) {
    .archive-eyebrow {
        font-size: 9px;
    }

    .archive-header h2 {
        font-size: 30px;
    }

    .year-page {
        flex-basis: 88vw;
        width: 88vw;
        height: 68vh;
        min-height: 530px;
    }

    .robots-area {
        gap: 0;
        height: 38vh;
    }

    .robot-card {
        width: 43vw;
    }

    .year-info h3 {
        font-size: 33px;
    }

    .achievements span {
        padding: 6px 9px;
        font-size: 8px;
    }
}
</style>