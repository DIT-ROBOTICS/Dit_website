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
import { nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import RobotViewer3D from '@/components/template/RobotViewer3D.vue'
import ApiState from '@/components/common/ApiState.vue'
import { useApiData } from '@/composables/useApiData'
import{RotateCw,ArrowRight,ArrowLeft,ArrowUpRight,X,Plus,ArrowUp}from'lucide-vue-next'

// 只在手機寬度停用 3D，平板與桌面版仍可預覽。
const mobileBreakpoint = '(max-width: 600px)'
const BackgroundImage = ref("/api/Eurobot/History/Background")
const {
    data: robotHistory,
    loading,
    error,
    load: loadHistory,
    reload,
} = useApiData([])

const trackElement = ref(null)
const activeIndex = ref(0)
const selectedRobot = ref(null)
const isMobile = ref(window.matchMedia(mobileBreakpoint).matches)
let mobileMediaQuery

function normalizeRobot(robot = {}) {
    return {
        ...robot,
        displayName: robot.displayName ?? robot.ShowOutName ?? robot.name ?? '',
        themeColor: robot.themeColor ?? robot.ThemeColor ?? '#ffffff',
        viewerPosition: robot.viewerPosition ?? robot.View3Dpos ?? 'right',
        viewerBackground: robot.viewerBackground ?? robot.View3DBackground ?? '',
        moreDetailsPath: robot.moreDetailsPath ?? robot.SeeMoreImagePath ?? '',
        components: robot.components ?? robot.Componets ?? [],
    }
}

// 將不同年度的新舊資料格式整理成歷史頁固定使用的形狀。
function normalizeHistoryItem(item = {}) {
    const rawTitle = item.bigTitle ?? item.BigTitle ?? ''
    const bigTitle = Array.isArray(rawTitle)
        ? rawTitle
        : String(rawTitle).split(/\r?\n/).filter(Boolean)
    const robots = item.robots ?? item.Robot_Data ?? []

    return {
        ...item,
        year: item.year ?? item.Year,
        background: item.background ?? item.Background ?? '',
        bigTitle,
        awards: Array.isArray(item.awards) ? item.awards : [],
        awardsColor: item.awardsColor ?? '#ffffff',
        description: item.description ?? '',
        robots: Array.isArray(robots) ? robots.map(normalizeRobot) : [],
    }
}

async function loadHistoryEurobotData(){
    return loadHistory('/api/Eurobot/History', {
        transform: async (history, { signal }) => {
            const resolvedHistory = await Promise.all(history.map(async (item) => {
                // 兼容舊後端：History 回傳年度 API URL 陣列。
                if (typeof item === 'string') {
                    const response = await fetch(item, { signal })
                    if (!response.ok) throw new Error(`HTTP ${response.status}: ${item}`)
                    return response.json()
                }

                // 新後端會直接回傳完整年度資料。
                return item
            }))

            return resolvedHistory
                .map(normalizeHistoryItem)
                .sort((a,b) => b.year - a.year)
        },
    })
}

// 與 Sponsors、Contact 相同：資料不依賴 DOM，setup 時立即發出單一 API 請求。
loadHistoryEurobotData()

// 初次載入與手動 reload 完成後，等 DOM 更新再校正目前年份。
watch(robotHistory, async () => {
    await nextTick()
    updateActiveYear()
})

function openRobot(robot) {
    if (isMobile.value || !robot.glbPath) return

    selectedRobot.value = robot
    document.body.style.overflow = 'hidden'
}

function closeRobot() {
    selectedRobot.value = null
    document.body.style.overflow = ''
}

// 切換到手機寬度時，關閉可能已開啟的 3D 視窗。
function updateMobileState(event) {
    isMobile.value = event.matches
    if (isMobile.value && selectedRobot.value) closeRobot()
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

onMounted(() => {
    mobileMediaQuery = window.matchMedia(mobileBreakpoint)
    isMobile.value = mobileMediaQuery.matches
    mobileMediaQuery.addEventListener('change', updateMobileState)
})

onUnmounted(() => {
    mobileMediaQuery?.removeEventListener('change', updateMobileState)
    document.body.style.overflow = ''
})
</script>

<template>
    <section id="robots" class="robot-archive">
        <div class="sticky-background">
            <img :src="BackgroundImage" alt="DIT Robotics 2026 Team" class="background-image">
        </div>
        <ApiState :loading="loading" :error="error" :empty="robotHistory.length === 0" @retry="reload">
        <div class="archive-container">
            <header class="archive-header">
                <div>
                    <p class="archive-eyebrow">OUR JOURNEY</p>
                    <div class="archive-main">
                        <h2 class="archive-title">歷代Eurobot</h2>
                        <h2 class="archive-outline">ARCHIVE</h2>
                    </div>
                </div>

                <div class="archive-instruction">
                    <span>EXPLORE THE PAST</span>
                    <span class="arrow"><ArrowLeft/></span>
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
                        <p class="competition" :style="{ color: item.awardsColor }">
                            Eurobot {{ item.year }}
                        </p>

                        <h3><span v-for="value in item.bigTitle">{{ value }}<br></span></h3>

                        <p class="year-description">
                            {{ item.description }}
                        </p>

                        <div v-if="item.awards.length" class="achievements">
                            <span v-for="achievement in item.awards" :key="achievement">
                                {{ achievement }}
                            </span>
                        </div>
                    </div>

                    <div class="robots-area" :class="{ single: item.robots.length === 1 }">
                        <button v-for="robot in item.robots" :key="robot.id" class="robot-card"
                            :class="{ clickable: robot.glbPath && !isMobile }" type="button"
                            :disabled="isMobile || !robot.glbPath" @click="openRobot(robot)">
                            <div class="robot-image-wrapper">
                                <img :src="robot.imagePath" :alt="robot.name">

                                <div v-if="robot.glbPath && !isMobile" class="view-3d">
                                    VIEW 3D
                                </div>
                            </div>

                            <div class="robot-meta">
                                <div>
                                    <p>{{ robot.name }}</p>
                                    <h4 :style="{color:robot.themeColor}">{{ robot.displayName }}</h4>
                                </div>

                                <span v-if="robot.model" class="robot-arrow">
                                    <ArrowUpRight/>
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
        </ApiState>
        <Transition name="modal">
            <RobotViewer3D v-if="selectedRobot && !isMobile" :robot="selectedRobot"
                :closeRobot3D="closeRobot"/>
        </Transition>
    </section>
</template>

<style scoped>
.robot-archive {
    --title-bar-height: 76px;
    position: relative;
    width: 100%;
    /* overflow: hidden; */
    background: #171719;
    color: white;
}
.sticky-background {
    position: sticky;

    top: var(--title-bar-height);

    width: 100%;
    height: calc(100vh - var(--title-bar-height));

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
    /* 只覆蓋 sticky background，不再多往上跨出 section 76px。 */
    margin-top: calc(-100vh + var(--title-bar-height));
    padding: 10vw 0 10vw;
}

.archive-header {
    position: relative;
    z-index: 20;
    width: 100%;
    padding: 40px 5vw 0 8vw;
    display:grid;
    grid-template-columns:4fr 1fr;
    justify-content: space-between;
    align-items: flex-start;
    pointer-events: none;
}

.archive-eyebrow {
    margin: 0 10px 5px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .35em;
    opacity: .55;
}

.archive-instruction {
    margin-top: 20%;
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

.archive-main{
    position:relative;
    z-index:20;
    width:100%;
    min-height:135px;
    display:grid;
    grid-template-columns:1fr 1fr;
    pointer-events:none;
}

.archive-title,
.archive-outline{
    margin:0;
    line-height:1;
}

.archive-title{
    justify-self:start;
    font-size:clamp(42px,4vw,68px);
    font-weight:900;
    letter-spacing:.04em;
    color:#fff;
}

.archive-outline{
    justify-self:start;
    font-size:clamp(42px,4.8vw,78px);
    font-weight:700;
    letter-spacing:.05em;
    -webkit-text-stroke: 7px rgba(255,255,255,.9);
    paint-order: stroke fill;
    color:#1e1e1e;
    /* -webkit-text-stroke:2px rgba(255,255,255,.9); */
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
    color: rgba(255, 255, 255, .2);
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

@media(max-width:900px) {
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

}

@media(max-width:600px) {
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
