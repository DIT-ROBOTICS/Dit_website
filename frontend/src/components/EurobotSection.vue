<!--
介紹當年的機器：
先是一個大的版面顯示今年的戰績和照片
再來是並排的兩個機器展示區
最上面是當年的機器帥照 點擊之後可以進入一個3d環繞展示機器的彈窗
下面是機器的技術大綱 展示區最下面有詳細資訊連結
點開可以進入詳細的技術展示網頁 或是彈窗
兩個機器展示區中間的下面有進入模擬對戰的按鈕
我預期的規劃是看有沒有辦法直接連接到當年的主程式
讓主程式去控制網頁上的機器人移動和做任務
然後場地是3d的展示區
左右可以選擇機器人的plan
-->

<script setup>
import { ref, onMounted } from 'vue'
import RobotViewer3D from '@/components/template/RobotViewer3D.vue'
import FilePreviewModal from '@/components/template/FilePreviewModal.vue'
import { ArrowUpRight } from 'lucide-vue-next'

const FullJson = ref({})
const robots = ref([])
const achievementPhoto = ref('')
const selectedRobot = ref(null)

async function loadThisYearEurobotData() {
    try {
        const response = await fetch('/api/Eurobot')
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        FullJson.value = await response.json()
        robots.value = FullJson.value.Robot_Data
        achievementPhoto.value = FullJson.value.Background
    } catch (error) {
        console.error(error)
    }
}

function openRobot3D(robot) {
    selectedRobot.value = robot
    document.body.style.overflow = 'hidden'
}

function closeRobot3D() {
    selectedRobot.value = null
    document.body.style.overflow = ''
}

function Robot_Team_Align(robot) {
    const index = robots.value.findIndex(r => r.id === robot.id)
    const count = robots.value.length
    if (count % 2 === 1 && index === 0) return 'center'
    const offset = count % 2 === 1 ? index - 1 : index
    return offset % 2 === 0 ? 'right' : 'left'
}

onMounted(loadThisYearEurobotData)
</script>

<template>
    <section id="featured-robot" class="robot-year-section">
        <div class="sticky-background">
            <img :src="achievementPhoto" alt="DIT Robotics Team" class="background-image">
            <div class="background-overlay"></div>
        </div>

        <div class="robot-year-content">
            <section class="achievement-panel">
                <div class="achievement-content">
                    <p class="achievement-year">
                        Eurobot {{ FullJson.Year }}
                    </p>

                    <h2 class="achievement-title">
                        <span v-for="text in FullJson.BigTitle" :key="text">{{ text }}</span>
                    </h2>

                    <div class="achievement-awards" :style="{ '--text-color': FullJson.awardsColor }">
                        <p v-for="text in FullJson.awards" :key="text">{{ text }}</p>
                    </div>
                </div>
            </section>

            <section class="robots-showcase">
                <div class="robots-grid">
                    <article v-for="robot in robots" :key="robot.id" class="robot-card">
                        <p class="shadowText" :style="{ '--text-align': Robot_Team_Align(robot) }">
                            <span :style="{ color: robot.ThemeColor }">{{ robot.ShowOutName }}</span>
                        </p>

                        <div class="robot-image-container" @click="openRobot3D(robot)">
                            <img :src="robot.imagePath" :alt="robot.name">

                            <div class="image-overlay">
                                <div class="view-3d">
                                    <span class="view-icon">360°</span>
                                    <span>INTERACTIVE VIEW</span>
                                </div>
                            </div>
                        </div>

                        <FilePreviewModal api="/api/PopUpItem/WhiteSeeMore" title="NTHU DIT">
                            <button class="detail-button">
                                <span>See more</span>
                                <img src="@/assets/image/Canva_Arrow.png" alt="arrow">
                            </button>
                        </FilePreviewModal>
                    </article>
                </div>

                <button class="simulation-button">
                    <span>歷屆 EUROBOT</span>
                    <ArrowUpRight />
                </button>
            </section>
        </div>

        <Transition name="modal">
            <RobotViewer3D v-if="selectedRobot" :robot="selectedRobot" :closeRobot3D="closeRobot3D" />
        </Transition>
    </section>
</template>

<style scoped>
.robot-year-section {
    position: relative;
    background: #050505;
    color: white;
}

.sticky-background {
    position: sticky;
    top: 0;
    width: 100%;
    height: 100vh;
    overflow: hidden;
    z-index: 0;
}

.background-image {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform: scale(1.02);
}

.background-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, rgba(0, 0, 0, .18), rgba(0, 0, 0, .4));
}

.robot-year-content {
    position: relative;
    z-index: 2;
    margin-top: -100vh;
}

.achievement-panel {
    position: relative;
    margin-top: 400px;
    margin-bottom: 150px;
    display: flex;
    padding: clamp(90px, 10vh, 140px) clamp(40px, 10vw, 120px);
}

.achievement-content {
    width: min(1000px, 70vw);
    margin-left: auto;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    transform: translateY(-1vh);
    font-family: 'Orbitron', sans-serif;
}

.achievement-year {
    margin: 0 0 34px;
    font-size: clamp(20px, 2.5vw, 34px);
    font-weight: 700;
    letter-spacing: .03em;
    color: white;
}

.achievement-title {
    margin: 0;
    display: flex;
    flex-direction: column;
    font-size: clamp(40px, 4.5vw, 96px);
    line-height: .98;
    letter-spacing: .05em;
    font-weight: 800;
    color: white;
}

.achievement-title span {
    display: block;
}

.achievement-title span:last-child {
    margin-left: -.5em;
    margin-top: 8px;
}

.achievement-awards {
    margin-top: 38px;
    align-self: flex-end;
    text-align: right;
}

.achievement-awards p {
    margin: 0;
    font-size: clamp(27px, 3.2vw, 50px);
    line-height: 1;
    font-weight: 900;
    letter-spacing: .1em;
    color: var(--text-color);
    -webkit-text-stroke: 1.5px var(--text-color);
    text-shadow: 0 3px 4px #000;
}

.achievement-awards p+p {
    margin-top: 5px;
}

.robots-showcase {
    position: relative;
    padding: 0 clamp(24px, 6vw, 100px) 70px;
    text-align: center;
    background: linear-gradient(to bottom, rgba(5, 5, 5, 0), rgba(5, 5, 5, .3) 50%, rgba(5, 5, 5, .7) 100%, #050505 90%);
}

.robots-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: clamp(24px, 4vw, 70px);
    max-width: 1500px;
    margin: -50px auto;
}

.robots-grid:has(>.robot-card:last-child:nth-child(odd))>.robot-card:first-child {
    grid-column: 1/-1;
    justify-self: center;
    width: calc((100% - clamp(24px, 4vw, 70px))/2);
}

.robot-card {
    min-width: 0;
}

.robot-card>p {
    margin: 0;
    padding: 0 2vw;
    transform: translateY(75%);
    text-align: var(--text-align);
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(19px, 3vw, 70px);
    font-weight: 600;
    line-height: 1.7;
    letter-spacing: .08em;
}

.shadowText {
    text-shadow: 0 3px 4px #000;
}

.robot-image-container {
    position: relative;
    width: 80%;
    margin: 0 auto;
    overflow: hidden;
    cursor: pointer;
    background: transparent;
    transform: scale(1);
    transition: transform .3s ease;
}

.robot-image-container>img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    transition: transform .8s cubic-bezier(.16, 1, .3, 1);
}

.robot-image-container:hover {
    transform: scale(1.045);
}

.image-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 10px;
    background: rgba(0, 0, 0, 0);
    transition: background .35s ease;
}

.robot-image-container:hover .image-overlay {
    background: radial-gradient(circle at 50% 45%, #24242472, #ffffff00 70%);
}

.view-3d {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    opacity: 0;
    transform: translateY(12px);
    font-size: 11px;
    letter-spacing: .2em;
    transition: .35s ease;
}

.robot-image-container:hover .view-3d {
    opacity: 1;
    transform: translateY(0);
}

.view-icon {
    width: 68px;
    height: 68px;
    display: grid;
    place-items: center;
    border: 1px solid rgba(255, 255, 255, .6);
    border-radius: 50%;
    font-size: 13px;
}

.detail-button {
    margin: auto;
    padding: 0 0 18px;
    border: none;
    background: transparent;
    color: white;
    cursor: pointer;
    font-family: 'League Spartan', sans-serif;
    font-size: clamp(18px, 2vw, 32px);
    font-weight: 900;
    word-spacing: .3em;
    transform: scale(1);
    transition: transform .3s ease;
}

.detail-button img {
    width: clamp(40px, 4vw, 70px);
    height: 15px;
    object-fit: contain;
}

.detail-button:hover {
    transform: scale(1.1);
}

.simulation-button {
    margin: 120px 5vw 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 40px;
    width: max-content;
    min-width: 240px;
    padding: 14px 20px;
    border: 1px solid rgba(255, 255, 255, .65);
    background: transparent;
    color: white;
    cursor: pointer;
    font-family: 'Orbitron', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: .13em;
    transition: background .3s ease, color .3s ease, border-color .3s ease, transform .3s ease;
}

.simulation-button svg {
    width: 19px;
    height: 19px;
    transition: transform .3s ease;
}

.simulation-button:hover {
    background: white;
    color: #050505;
    border-color: white;
    transform: translateY(-3px);
}

.simulation-button:hover svg {
    transform: translate(4px, -4px);
}

.modal-enter-active,
.modal-leave-active {
    transition: opacity .3s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}

@media(max-width:850px) {
    .achievement-panel {
        margin-top: 250px;
        margin-bottom: 100px;
        padding: 110px 24px 70px;
        align-items: flex-end;
    }

    .achievement-content {
        width: 100%;
        margin-left: 0;
        align-items: flex-start;
        transform: none;
    }

    .achievement-year {
        margin-bottom: 22px;
        font-size: 20px;
    }

    .achievement-title {
        font-size: clamp(48px, 14vw, 72px);
    }

    .achievement-title span:last-child {
        margin-left: 0;
        margin-top: 4px;
    }

    .achievement-awards {
        align-self: flex-start;
        margin-top: 30px;
        text-align: left;
    }

    .achievement-awards p {
        font-size: clamp(25px, 8vw, 38px);
    }

    .background-image {
        object-position: 40% center;
    }

    .robots-showcase {
        padding-left: 20px;
        padding-right: 20px;
    }

    .robots-grid {
        grid-template-columns: 1fr;
        gap: 100px;
    }

    .robots-grid:has(>.robot-card:last-child:nth-child(odd))>.robot-card:first-child {
        grid-column: auto;
        width: 100%;
    }

    .robot-card>p {
        text-align: center;
    }

    .detail-button {
        font-size: 24px;
    }

    .simulation-button {
        margin: 100px 0 0;
        min-width: 210px;
    }
}

@media(max-width:520px) {
    .achievement-panel {
        margin-top: 180px;
        padding-left: 20px;
        padding-right: 20px;
    }

    .robot-image-container {
        width: 95%;
    }

    .simulation-button {
        width: 100%;
        min-width: 0;
        padding: 14px 18px;
    }
}
</style>