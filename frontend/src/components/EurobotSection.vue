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
import { ref } from 'vue'

import robot1Photo from '@/assets/Hero_Image.png'
import robot2Photo from '@/assets/Hero_Image.png'

const achievementPhoto = '/api/other_images/competition/background.png'

const robots = [
    {
        id: 1,
        name: '黑機',
        subtitle: 'DIT ROBOTICS',
        image: robot1Photo,
        description:
            '負責主要得分任務，整合導航、物件辨識、機構控制與自動路徑規劃。',
        technologies: [
            '四面手臂',
            'Computer Vision',
            'Path Planning',
            'STM32',
            'CAN Bus'
        ]
    },
    {
        id: 2,
        name: '白機',
        subtitle: 'NTHU DIT',
        image: robot2Photo,
        description:
            '負責協同任務與場地互動，透過定位系統與主機器人交換即時狀態。',
        technologies: [
            '三面手臂',
            'LiDAR',
            'Motion Control',
            'Embedded System',
            'Robot Communication'
        ]
    }
]

const selectedRobot = ref(null)

function openRobot3D(robot) {
    selectedRobot.value = robot
}

function closeRobot3D() {
    selectedRobot.value = null
}

function openDetails(robot) {
    // 之後可以改成：
    // router.push(`/robots/2026/${robot.id}`)
    console.log('open details:', robot)
}
</script>

<template>
    <section id="featured-robot" class="robot-year-section">
        <div class="sticky-background">
            <img :src="achievementPhoto" alt="DIT Robotics 2026 Team" class="background-image" >
            <div class="background-overlay"></div>
        </div>

        <!-- 真正會滾動的內容 -->
        <div class="robot-year-content">
            <section class="achievement-panel">
                <div class="achievement-content">
                    <p class="eyebrow">
                        EUROBOT 2026
                    </p>

                    <h2>
                        THIS YEAR,<br>WE MADE IT.
                    </h2>

                    <p class="achievement-description">
                        從設計、製造、程式到正式站上競賽場地，
                        這是 DIT Robotics 在 2026 年留下的成果。
                    </p>

                    <div class="achievement-stats">
                        <div class="stat">
                            <strong>2026</strong>
                            <span>EUROBOT</span>
                        </div>
                        <div class="stat">
                            <strong>2</strong>
                            <span>ROBOTS</span>
                        </div>
                        <div class="stat">
                            <strong>Top 1</strong>
                            <span>積分賽</span>
                        </div>
                        <div class="stat">
                            <strong>Top 2</strong>
                            <span>對抗賽</span>
                        </div>
                    </div>
                </div>

                <div class="scroll-hint">
                    <span>DISCOVER OUR ROBOTS</span>
                    <div class="scroll-line"></div>
                </div>
            </section>


            <!-- ===== 機器人展示 ===== -->

            <section class="robots-showcase">
                <div class="section-heading">
                    <p class="eyebrow">
                        OUR MACHINES
                    </p>
                    <h2>為競賽而生的兩台機器</h2>
                    <p>
                        從機構、電子到軟體，
                        每一個系統都是團隊共同完成的成果。
                    </p>
                </div>

                <div class="robots-grid">
                    <article v-for="(robot, index) in robots" :key="robot.id" class="robot-card">
                        <div class="robot-image-container" @click="openRobot3D(robot)">
                            <img :src="robot.image" :alt="robot.name">
                            <div class="image-overlay">
                                <div class="view-3d">
                                    <span class="view-icon">
                                        360°
                                    </span>
                                    <span>
                                        VIEW IN 3D
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div class="robot-info">
                            <div class="robot-title">
                                <div>
                                    <p>{{ robot.subtitle }}</p>

                                    <h3>{{ robot.name }}</h3>
                                </div>
                            </div>

                            <p class="robot-description">
                                {{ robot.description }}
                            </p>

                            <div class="technologies">
                                <span v-for="technology in robot.technologies" :key="technology">
                                    {{ technology }}
                                </span>
                            </div>

                            <button class="detail-button" @click="openDetails(robot)">
                                <span>
                                    VIEW TECHNICAL DETAILS
                                </span>

                                <span class="arrow">
                                    →
                                </span>
                            </button>
                        </div>
                    </article>
                </div>
            </section>

            <!-- ===== 模擬對戰入口 ===== -->

            <section class="simulation-section">

                <div class="simulation-card">

                    <p class="eyebrow">
                        SIMULATION
                    </p>

                    <h2>
                        SEE THEM
                        <br>
                        IN ACTION.
                    </h2>

                    <p>
                        選擇機器人的策略，
                        在虛擬 Eurobot 場地中觀看兩台機器執行任務。
                    </p>

                    <!--
                        目前先只做視覺
                        之後再接模擬系統
                    -->
                    <button class="simulation-button">

                        ENTER SIMULATION

                        <span>
                            ↗
                        </span>

                    </button>

                </div>

            </section>

        </div>


        <!-- ===== 3D Viewer 彈窗 ===== -->

        <Transition name="modal">

            <div
                v-if="selectedRobot"
                class="robot-modal"
                @click.self="closeRobot3D"
            >

                <div class="modal-container">

                    <button
                        class="close-button"
                        @click="closeRobot3D"
                    >
                        ×
                    </button>

                    <div class="viewer-placeholder">

                        <p>
                            INTERACTIVE 3D VIEWER
                        </p>

                        <h2>
                            {{ selectedRobot.name }}
                        </h2>

                        <span>
                            之後這裡可以放 Three.js / model-viewer
                        </span>

                    </div>

                </div>

            </div>

        </Transition>

    </section>
</template>


<style scoped>
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
        linear-gradient(
            to bottom,
            rgba(0, 0, 0, 0.18),
            rgba(0, 0, 0, 0.4)
        );
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

    display: flex;

    flex-direction: column;

    justify-content: flex-end;

    padding:
        clamp(110px, 12vh, 160px)
        clamp(30px, 7vw, 120px)
        clamp(60px, 8vh, 100px);
}

.achievement-content {
    max-width: 100%;
}

.eyebrow {
    margin: 0 0 20px;

    font-size: 13px;
    font-weight: 700;

    letter-spacing: 0.28em;

    opacity: 0.72;
}

.achievement-content h2 {
    margin: 0;

    font-size:
        clamp(58px, 9vw, 150px);

    line-height: 0.85;

    letter-spacing: -0.055em;

    font-weight: 800;
}

.achievement-description {
    max-width: 620px;

    margin-top: 34px;

    font-size:
        clamp(16px, 1.3vw, 21px);

    line-height: 1.8;

    color:
        rgba(255, 255, 255, 0.8);
}


/* ========================================
   Statistics
======================================== */

.achievement-stats {
    display: flex;

    gap: 60px;

    margin-top: 54px;
}

.stat {
    display: flex;

    flex-direction: column;

    gap: 8px;
}

.stat strong {
    font-size:
        clamp(26px, 3vw, 46px);

    font-weight: 700;
}

.stat span {
    font-size: 11px;

    letter-spacing: 0.2em;

    opacity: 0.55;
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

    min-height: 100vh;

    padding:
        140px
        clamp(24px, 6vw, 100px)
        70px;

    background:
        linear-gradient(
            to bottom,
            rgba(5, 5, 5, 0.0),
            rgba(5, 5, 5, 0.3) 50%,
            rgba(5, 5, 5, 0.7) 100%,
            #050505 90%
        );
}

.section-heading {
    max-width: 800px;

    margin-bottom: 80px;
}

.section-heading h2 {
    margin: 0 0 22px;

    font-size:
        clamp(38px, 5vw, 72px);

    letter-spacing: -0.045em;

    line-height: 1;
}

.section-heading > p:last-child {
    max-width: 560px;

    margin: 0;

    line-height: 1.7;

    color:
        rgba(255, 255, 255, 0.6);
}


/* ========================================
   Cards
======================================== */

.robots-grid {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap:
        clamp(24px, 4vw, 70px);

    max-width: 1500px;

    margin: 0 auto;
}

.robot-card {
    min-width: 0;
}

.robot-image-container {
    position: relative;

    aspect-ratio: 4 / 5;

    overflow: hidden;

    cursor: pointer;

    background: #111;
}

.robot-image-container img {
    width: 100%;
    height: 100%;

    object-fit: cover;

    transition:
        transform 0.8s
        cubic-bezier(0.16, 1, 0.3, 1);
}

.robot-image-container:hover img {
    transform:
        scale(1.045);
}

.image-overlay {
    position: absolute;

    inset: 0;

    display: flex;

    align-items: center;

    justify-content: center;

    background:
        rgba(0, 0, 0, 0);

    transition:
        background 0.35s ease;
}

.robot-image-container:hover .image-overlay {
    background:
        rgba(0, 0, 0, 0.38);
}

.view-3d {
    display: flex;

    flex-direction: column;

    align-items: center;

    gap: 10px;

    opacity: 0;

    transform:
        translateY(12px);

    transition:
        0.35s ease;

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

    border:
        1px solid
        rgba(255, 255, 255, 0.6);

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
   Robot information
======================================== */

.robot-info {
    padding-top: 30px;
}

.robot-title p {
    margin: 0 0 7px;

    font-size: 11px;

    letter-spacing: 0.2em;

    color:
        rgba(255, 255, 255, 0.5);

    text-transform: uppercase;
}

.robot-title h3 {
    margin: 0;

    font-size:
        clamp(34px, 3vw, 52px);

    letter-spacing: -0.04em;
}

.robot-description {
    max-width: 600px;

    margin-top: 20px;

    font-size: 15px;

    line-height: 1.8;

    color:
        rgba(255, 255, 255, 0.62);
}


/* ========================================
   Technology tags
======================================== */

.technologies {
    display: flex;

    flex-wrap: wrap;

    gap: 8px;

    margin-top: 25px;
}

.technologies span {
    padding:
        8px
        12px;

    border:
        1px solid
        rgba(255, 255, 255, 0.18);

    border-radius: 999px;

    font-size: 10px;

    letter-spacing: 0.08em;

    color:
        rgba(255, 255, 255, 0.68);
}


/* ========================================
   Detail button
======================================== */

.detail-button {
    width: 100%;

    margin-top: 30px;

    padding:
        18px 0;

    display: flex;

    align-items: center;

    justify-content: space-between;

    border: none;

    border-top:
        1px solid
        rgba(255, 255, 255, 0.18);

    border-bottom:
        1px solid
        rgba(255, 255, 255, 0.18);

    background: transparent;

    color: white;

    cursor: pointer;

    font-size: 11px;

    letter-spacing: 0.15em;

    transition:
        padding 0.3s ease;
}

.detail-button:hover {
    padding-left: 12px;

    padding-right: 12px;
}

.arrow {
    font-size: 20px;
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

    padding: 100px 30px;

    background: rgba(5, 5, 5, 0.7);
}

.simulation-card {
    width: min(1100px, 100%);

    padding:
        clamp(45px, 7vw, 100px);

    background: rgba(5, 5, 5, 1);
    border:
        1px solid
        rgba(255, 255, 255, 1);
}

.simulation-card h2 {
    margin: 0;

    font-size:
        clamp(54px, 8vw, 120px);

    line-height: 0.88;

    letter-spacing: -0.06em;
}

.simulation-card > p:not(.eyebrow) {
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
        18px
        24px;

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
   3D modal
======================================== */

.robot-modal {
    position: fixed;

    inset: 0;

    z-index: 1000;

    display: flex;

    align-items: center;

    justify-content: center;

    padding: 40px;

    background:
        rgba(0, 0, 0, 0.8);

    backdrop-filter:
        blur(14px);
}

.modal-container {
    position: relative;

    width:
        min(1200px, 100%);

    height:
        min(780px, 85vh);

    background: #0a0a0a;

    border:
        1px solid
        rgba(255, 255, 255, 0.15);
}

.close-button {
    position: absolute;

    top: 20px;

    right: 22px;

    z-index: 4;

    width: 44px;
    height: 44px;

    border:
        1px solid
        rgba(255, 255, 255, 0.25);

    border-radius: 50%;

    background:
        rgba(0, 0, 0, 0.4);

    color: white;

    font-size: 28px;

    cursor: pointer;
}

.viewer-placeholder {
    width: 100%;
    height: 100%;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;
}

.viewer-placeholder p {
    font-size: 11px;

    letter-spacing: 0.25em;

    opacity: 0.5;
}

.viewer-placeholder h2 {
    margin:
        10px
        0;

    font-size:
        clamp(50px, 8vw, 120px);

    letter-spacing: -0.06em;
}

.viewer-placeholder span {
    color:
        rgba(255, 255, 255, 0.45);
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
        padding-left: 24px;

        padding-right: 24px;
    }

    .achievement-stats {
        gap: 28px;
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