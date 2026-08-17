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
import RobotPreview3D from '@/components/template/RobotPreview3D.vue'
import FilePreviewModal from '@/components/template/FilePreviewModal.vue'
import { RotateCw, ArrowRight, ArrowLeft, ArrowUpRight, X, Plus, ArrowUp } from 'lucide-vue-next'

const FullJson = ref({})
const robots = ref([])
const achievementPhoto = ref("")
const selectedRobot = ref(null)

async function loadThisYearEurobotData() {
    try {
        const response = await fetch('/api/Eurobot')

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
        }

        FullJson.value = await response.json()
        robots.value = FullJson.value.Robot_Data
        achievementPhoto.value = FullJson.value.Background
    } catch (error) {
        console.error(error)
    } finally {
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

function openDetails(robot) {
    // 之後可以改成：
    // router.push(`/robots/2026/${robot.id}`)
    console.log('open details:', robot)
}

function RobotsAmount() {
    let a = robots.value.length
    let title = [
        "", "Our Robot", "Two Robots", "Three Robots"
    ]
    return title[a]
}

function Robot_Team_Align(robot) {
    const index = robots.value.findIndex(r => r.id === robot.id)
    const count = robots.value.length

    if (count % 2 === 1 && index === 0) return "center"

    const offset = count % 2 === 1 ? index - 1 : index
    return offset % 2 === 0 ? "right" : "left"
}

onMounted(loadThisYearEurobotData)
</script>

<template>
    <section id="featured-robot" class="robot-year-section">
        <div class="sticky-background">
            <img :src="achievementPhoto" alt="DIT Robotics 2026 Team" class="background-image">
            <div class="background-overlay"></div>
        </div>

        <!-- 真正會滾動的內容 -->
        <div class="robot-year-content">
            <section class="achievement-panel">
                <div class="achievement-content">

                    <p class="achievement-year">
                        Eurobot {{ FullJson.Year }}
                    </p>

                    <h2 class="achievement-title">
                        <span v-for="text in FullJson.BigTitle">{{ text }}</span>
                    </h2>

                    <div class="achievement-awards" :style="{ '--text-color': FullJson.awardsColor }">
                        <p v-for="text in FullJson.awards">{{ text }}</p>
                    </div>

                </div>
            </section>


            <!-- ===== 機器人展示 ===== -->

            <section class="robots-showcase">
                <div class="section-heading">
                    <h2>{{ RobotsAmount() }} for Eurobot</h2>
                </div>

                <div class="robots-grid">
                    <article v-for="robot in robots" :key="robot.id" class="robot-card">
                        <p class="shadowText" :style="{ '--text-align': Robot_Team_Align(robot) }">
                            <span :style="{ color: robot.ThemeColor }">{{ robot.ShowOutName }}</span>
                        </p>
                        <div class="robot-image-container" @click="openRobot3D(robot)">
                            <!-- <RobotPreview3D :model="robot.glbPath" /> -->
                            <img :src="robot.imagePath" :alt="robot.name">
                            <div class="image-overlay">
                                <div class="view-3d">
                                    <span class="view-icon"> 360° </span>
                                    <span>INTERACTIVE VIEW</span>
                                </div>
                            </div>
                        </div>
                        <FilePreviewModal api="/api/PopUpItem/WhiteSeeMore" title="NTHU DIT">
                            <button class="detail-button" @click="openDetails(robot)">
                                <span>See more </span>
                                <img src="@/assets/image/Canva_Arrow.png" alt="arrow" style="width: 4vw; height: 15px;">
                            </button>
                        </FilePreviewModal>
                    </article>
                </div>
            </section>

            <!-- ===== 模擬對戰入口 ===== -->

            <section class="simulation-section">

                <div class="simulation-card">

                    <p class="eyebrow">
                        歷屆EUROBOT
                    </p>

                    <h2>
                        SEE OUR HISTORY
                    </h2>

                    <p>
                        查看團隊的競賽歷史
                    </p>
                    <button class="simulation-button">
                        歷屆EUROBOT
                        <span>
                            <ArrowUpRight />
                        </span>
                    </button>
                </div>
            </section>
        </div>


        <!-- ===== 3D Viewer 彈窗 ===== -->

        <Transition name="modal">
            <RobotViewer3D v-if="selectedRobot" :robot="selectedRobot" :closeRobot3D="closeRobot3D" />
        </Transition>

    </section>
</template>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=League+Spartan:wght@400;500;600;700;800&display=swap');

.robot-year-section {
    position: relative;
    background: #050505;
    color: white;
}


/* ========================================
   Sticky Background
======================================== */

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

    background:
        linear-gradient(to bottom,
            rgba(0, 0, 0, 0.18),
            rgba(0, 0, 0, 0.4));
}


/*
    這裡很重要。

    sticky-background 本身仍然佔據 100vh，
    用負 margin 把後面的內容拉回來，
    讓 achievement-panel 直接蓋在背景上。
*/

.robot-year-content {
    position: relative;

    z-index: 2;

    margin-top: -100vh;
}


/* ========================================
   Achievement Hero
======================================== */

.achievement-panel {
    position: relative;

    min-height: 100vh;

    margin-top: 400px;

    display: flex;
    align-items: right;

    padding:
        clamp(90px, 10vh, 140px) clamp(40px, 10vw, 120px);
}


/*
    文字放在右半邊
*/
.achievement-content {
    width: min(620px, 46vw);
    font-family: 'League Spartan', sans-serif;
    margin-left: auto;

    display: flex;
    flex-direction: column;

    align-items: flex-end;

    transform: translateY(-1vh);
}


/* Eurobot 2026 */
.achievement-year {
    margin: 0 0 34px;

    font-size:
        clamp(20px, 2.5vw, 34px);

    font-weight: 700;

    letter-spacing: -0.02em;

    color: white;
}


/* THIS YEAR / We Made IT */
.achievement-title {
    margin: 0;

    display: flex;
    flex-direction: column;

    font-size:
        clamp(54px, 5.6vw, 96px);

    line-height: 0.98;

    letter-spacing: 0.05em;

    font-weight: 800;

    color: white;
}

.achievement-title span {
    display: block;
}


/*
    第二行稍微往左，
    模仿 Canva 裡 We Made IT 的位置
*/
.achievement-title span:last-child {
    margin-left: -0.5em;

    margin-top: 8px;
}


/* 戰績 */
.achievement-awards {
    margin-top: 38px;
    align-self: flex-end;
    text-align: right;
}

.achievement-awards p {
    margin: 0;

    font-size:
        clamp(27px, 2.8vw, 47px);

    line-height: 1;

    font-weight: 700;

    letter-spacing: 0.025em;

    color: white;

    /*
        白字 + 紅色外框
    */
    -webkit-text-stroke:
        clamp(3px, 0.44vw, 20px) var(--text-color);
    paint-order: stroke fill;
    text-shadow:
        0 2px 4px rgba(0, 0, 0, 0.4);
}

.achievement-awards p+p {
    margin-top: 5px;
}

/* ========================================
   Scroll hint
======================================== */

.scroll-hint {
    position: absolute;

    right:
        clamp(30px, 7vw, 120px);

    bottom: 80px;

    display: flex;

    align-items: center;

    gap: 18px;

    transform: rotate(90deg);

    transform-origin: right bottom;

    font-size: 10px;

    letter-spacing: 0.2em;

    opacity: 0.65;
}

.scroll-line {
    width: 70px;
    height: 1px;

    background:
        rgba(255, 255, 255, 0.7);
}


/* ========================================
   Robot Showcase
======================================== */

.robots-showcase {
    position: relative;

    min-height: 80vh;
    align-items: center;
    text-align: center;
    padding:
        0px clamp(24px, 6vw, 100px) 70px;

    background:
        linear-gradient(to bottom,
            rgba(5, 5, 5, 0.0),
            rgba(5, 5, 5, 0.3) 50%,
            rgba(5, 5, 5, 0.7) 100%,
            #050505 90%);
}

.section-heading {
    /* margin-bottom: 80px; */
    font-family: 'League Spartan', sans-serif;
}

.section-heading h2 {
    margin: 0 0 22px;
    text-align: center;
    font-size:
        clamp(38px, 6vw, 100px);

    letter-spacing: 0.05em;
    line-height: 1;
}

.robot-card p {
    text-align: var(--text-align);
    font-weight: 600;
    font-size:
        clamp(19px, 3.5vw, 70px);
    margin: 0;
    line-height: 1.7;
    padding: 0 2vw;
    transform: translateY(75%);
}

.shadowText {
    text-shadow: -3.5px 3.5px white;
}


/* ========================================
   Cards
======================================== */

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

.robot-image-container {
    position: relative;

    width: 80%;

    margin: 0 auto;
    overflow: hidden;

    cursor: pointer;

    background: transparent;
    transform: scale(1);
    transition: transform 0.3s ease;
}

.robot-image-container img {
    width: 100%;
    height: 100%;

    object-fit: contain;

    transition:
        transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.robot-image-container:hover {

    transform: scale(1.045);
    transition: transform 0.3s ease;
}

.image-overlay {
    position: absolute;

    inset: 0;

    display: flex;

    align-items: center;

    justify-content: center;
    border-radius: 10px;

    background:
        rgba(0, 0, 0, 0);

    transition:
        background 0.35s ease;
}

.robot-image-container:hover .image-overlay {
    background:
        radial-gradient(circle at 50% 45%,
            #24242472,
            #ffffff00 70%);
}

.view-3d {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    opacity: 0;
    transform: translateY(12px);

    transition: 0.35s ease;
    font-size: 11px;
    letter-spacing: 0.2em;
}

.robot-image-container:hover .view-3d {
    opacity: 1;

    transform:
        translateY(0);
}

.view-icon {
    width: 68px;
    height: 68px;
    display: grid;
    place-items: center;
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 50%;
    font-size: 13px;
}

.robot-number {
    position: absolute;
    right: 20px;
    bottom: 16px;
    font-size: 14px;
    letter-spacing: 0.15em;
}

/* ========================================
   Detail button
======================================== */

.detail-button {
    font-family: 'League Spartan', sans-serif;
    width: content;
    margin: auto;
    padding:
        0 0 18px;
    /* display: flex; */
    align-items: center;
    /* justify-content: space-between; */
    border: none;
    background: transparent;
    color: white;
    cursor: pointer;
    font-size: 2vw;
    word-spacing: 0.3em;
    font-weight: 900;
    transform: scale(1);
    transition: transform 0.3s ease;
}

.detail-button:hover {
    transform: scale(1.1);
    transition: transform 0.3s ease;
}


/* ========================================
   Simulation
======================================== */

.simulation-section {
    position: relative;

    min-height: 80vh;

    display: flex;

    align-items: center;

    justify-content: center;

    padding: 50px 30px;

    background: rgba(5, 5, 5, 0.7);
}

.simulation-card {
    width: min(1100px, 100%);

    padding: clamp(45px, 3vw, 50px);

    background: rgba(5, 5, 5, 1);
    border: 1px solid rgba(255, 255, 255, 1);
}

.simulation-card h2 {
    margin: 0;

    font-size:
        clamp(54px, 6vw, 120px);

    line-height: 0.88;

    letter-spacing: -0.06em;
}

.simulation-card>p:not(.eyebrow) {
    max-width: 500px;

    margin-top: 30px;

    line-height: 1.7;

    color:
        rgba(255, 255, 255, 0.6);
}

.simulation-button {
    margin-top: 45px;

    display: flex;

    align-items: center;

    gap: 40px;

    padding:
        18px 24px;

    border: 1px solid white;

    background: white;

    color: rgba(5, 5, 5, 1);

    cursor: pointer;

    font-size: 11px;

    font-weight: 700;

    letter-spacing: 0.13em;

    transition:
        0.3s ease;
}

.simulation-button:hover {
    background: transparent;

    color: white;
}


/* ========================================
   Modal animation
======================================== */

.modal-enter-active,
.modal-leave-active {
    transition:
        opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}

/* ========================================
   RWD
======================================== */

@media (max-width: 850px) {

    .achievement-panel {
        align-items: flex-end;

        padding:
            110px 24px 70px;
    }

    .achievement-content {
        width: 100%;

        margin-left: 0;

        transform: none;
    }

    .achievement-year {
        margin-bottom: 22px;

        font-size: 20px;
    }

    .achievement-title {
        font-size:
            clamp(48px, 14vw, 72px);
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
        font-size:
            clamp(25px, 8vw, 38px);
    }

    .background-image {
        object-position: 40% center;
    }

    .robots-grid {
        grid-template-columns: 1fr;

        gap: 100px;
    }

    .scroll-hint {
        display: none;
    }

    .robots-showcase {
        padding-left: 20px;

        padding-right: 20px;
    }

    .robot-modal {
        padding: 15px;
    }

}
</style>