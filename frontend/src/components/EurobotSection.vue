<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import RobotViewer3D from '@/components/template/RobotViewer3D.vue'
import FilePreviewModal from '@/components/template/FilePreviewModal.vue'
import ArrowRight from '@/components/icons/FreeArrowRight.vue'
import { ArrowUpRight } from 'lucide-vue-next'

// 當年 Eurobot 資料、機器人清單與 3D 檢視狀態。
const eurobotData = ref({})
const robots = ref([])
const achievementPhoto = ref('')
const selectedRobot = ref(null)

// 從後端載入當年戰績、背景與機器人資料。
async function loadThisYearEurobotData() {
    try {
        const response = await fetch('/api/Eurobot')
        if (!response.ok) throw new Error(`HTTP ${response.status}`)

        eurobotData.value = await response.json()
        robots.value = eurobotData.value.Robot_Data
        achievementPhoto.value = eurobotData.value.Background
    } catch (error) {
        console.error(error)
    }
}

// 開啟指定機器人的 3D 檢視器，並鎖定背景捲動。
function openRobot3D(robot) {
    selectedRobot.value = robot
    document.body.style.overflow = 'hidden'
}

// 關閉 3D 檢視器並恢復頁面捲動。
function closeRobot3D() {
    selectedRobot.value = null
    document.body.style.overflow = ''
}

// 依卡片數量與位置決定機器人名稱對齊方向。
function getRobotNameAlignment(robot) {
    const index = robots.value.findIndex((item) => item.id === robot.id)
    const count = robots.value.length

    if (count % 2 === 1 && index === 0) return 'center'

    const offset = count % 2 === 1 ? index - 1 : index
    return offset % 2 === 0 ? 'right' : 'left'
}

// 元件掛載後載入 Eurobot 資料。
onMounted(loadThisYearEurobotData)

// 若開啟 3D 視窗時離開頁面，確保恢復 body 捲動。
onUnmounted(() => {
    document.body.style.overflow = ''
})
</script>

<template>
    <!-- 當年 Eurobot 戰績與機器人展示區。 -->
    <section id="featured-robot" class="robot-year-section">
        <!-- 捲動時固定在畫面後方的團隊照片。 -->
        <div class="sticky-background">
            <!-- 當年 Eurobot 團隊背景圖。 -->
            <img class="background-image" :src="achievementPhoto" alt="DIT Robotics Team" />
            <!-- 提高前景文字可讀性的深色遮罩。 -->
            <div class="background-overlay"></div>
        </div>

        <!-- 戰績與機器人卡片的前景內容。 -->
        <div class="robot-year-content">
            <!-- 當年 Eurobot 戰績區塊。 -->
            <section class="achievement-panel">
                <!-- 年份、主標題與獎項內容。 -->
                <div class="achievement-content">
                    <!-- Eurobot 年份。 -->
                    <p class="achievement-year">Eurobot {{ eurobotData.Year }}</p>

                    <!-- 當年主視覺標題。 -->
                    <h2 class="achievement-title">
                        <span v-for="text in eurobotData.BigTitle" :key="text" class="achievement-title-line">
                            {{ text }}
                        </span>
                    </h2>

                    <!-- 當年競賽獎項。 -->
                    <div class="achievement-awards" :style="{ '--text-color': eurobotData.awardsColor }">
                        <p v-for="text in eurobotData.awards" :key="text" class="achievement-award">
                            {{ text }}
                        </p>
                    </div>
                </div>
            </section>

            <!-- 當年機器人展示區。 -->
            <section class="robots-showcase">
                <!-- 機器人卡片網格。 -->
                <div class="robots-grid">
                    <!-- 單一機器人卡片。 -->
                    <article v-for="robot in robots" :key="robot.id" class="robot-card">
                        <!-- 機器人展示名稱。 -->
                        <p class="robot-name" :style="{ '--text-align': getRobotNameAlignment(robot) }">
                            <span class="robot-name-text" :style="{ color: robot.ThemeColor }">
                                {{ robot.ShowOutName }}
                            </span>
                        </p>

                        <!-- 點擊後開啟 3D 檢視器的機器人圖片。 -->
                        <div class="robot-image-container" role="button" tabindex="0" @click="openRobot3D(robot)"
                            @keydown.enter="openRobot3D(robot)" @keydown.space.prevent="openRobot3D(robot)">
                            <img class="robot-image" :src="robot.imagePath" :alt="robot.name" />

                            <!-- 圖片懸停時的 3D 檢視提示。 -->
                            <div class="image-overlay">
                                <div class="view-3d">
                                    <span class="view-icon">360°</span>
                                    <span class="view-label">INTERACTIVE VIEW</span>
                                </div>
                            </div>
                        </div>

                        <!-- 開啟機器人詳細資料的檔案預覽視窗。 -->
                        <FilePreviewModal api="/api/PopUpItem/WhiteSeeMore" title="NTHU DIT">
                            <button class="detail-button" type="button">
                                <span class="detail-button-label">See more </span>
                                <ArrowRight class="detail-button-arrow"/>
                            </button>
                        </FilePreviewModal>
                    </article>
                </div>

                <!-- 前往歷屆 Eurobot 內容的按鈕。 -->
                <button class="eurobot-history-button" type="button">
                    <span class="eurobot-history-button-label">歷屆 EUROBOT</span>
                    <ArrowUpRight class="eurobot-history-button-icon" />
                </button>

            </section>
            <div id="Advisors_teleport" style="z-index: 300;"></div>

        </div>

        <!-- 目前選取機器人的 3D 檢視視窗。 -->
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

.background-image,
.background-overlay {
    position: absolute;
    inset: 0;
}

.background-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform: scale(1.02);
}

.background-overlay {
    background: linear-gradient(to bottom, rgba(0, 0, 0, 0.18), rgba(0, 0, 0, 0.4));
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
    letter-spacing: 0.03em;
}

.achievement-title {
    margin: 0;
    display: flex;
    flex-direction: column;
    font-size: clamp(40px, 4.5vw, 96px);
    line-height: 0.98;
    letter-spacing: 0.05em;
    font-weight: 800;
}

.achievement-title-line {
    display: block;
}

.achievement-title-line:last-child {
    margin-left: -0.5em;
    margin-top: 8px;
}

.achievement-awards {
    margin-top: 38px;
    align-self: flex-end;
    text-align: right;
}

.achievement-award {
    margin: 0;
    font-size: clamp(27px, 3.2vw, 50px);
    line-height: 1;
    font-weight: 900;
    letter-spacing: 0.1em;
    color: var(--text-color);
    -webkit-text-stroke: 1.5px var(--text-color);
    text-shadow: 0 3px 4px #000;
}

.achievement-award+.achievement-award {
    margin-top: 5px;
}

.robots-showcase {
    position: relative;
    padding: 0 clamp(24px, 6vw, 100px) 70px;
    text-align: center;
    background: linear-gradient(to bottom,
            rgba(5, 5, 5, 0),
            rgba(5, 5, 5, 0.3) 50%,
            rgba(5, 5, 5, 0.7) 100%,
            #050505 90%);
}

.robots-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: clamp(24px, 4vw, 70px);
    max-width: 1500px;
    margin: -50px auto;
}

.robots-grid:has(> .robot-card:last-child:nth-child(odd))>.robot-card:first-child {
    grid-column: 1/-1;
    justify-self: center;
    width: calc((100% - clamp(24px, 4vw, 70px)) / 2);
}

.robot-card {
    min-width: 0;
}

.robot-name {
    margin: 0;
    padding: 0 2vw;
    transform: translateY(75%);
    text-align: var(--text-align);
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(19px, 3vw, 70px);
    font-weight: 600;
    line-height: 1.7;
    letter-spacing: 0.08em;
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
    transition: transform 0.3s ease;
}

.robot-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
    transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
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
    transition: background 0.35s ease;
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
    letter-spacing: 0.2em;
    transition: 0.35s ease;
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
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 50%;
    font-size: 13px;
}

.detail-button,
.eurobot-history-button {
    background: transparent;
    color: white;
    cursor: pointer;
}

.detail-button {
    margin: auto;
    padding: 0 0 18px;
    display: inline-flex;
    align-items: center;
    gap: 14px;
    border: none;
    font-family: 'League Spartan', sans-serif;
    font-size: clamp(18px, 2vw, 32px);
    font-weight: 900;
    word-spacing: 0.3em;
    transform: scale(1);
    transition: transform 0.3s ease;
}

.detail-button-arrow {
    width: 50px;
    height: 24px;
    flex: none;
    transform: scaleX(1.2);
    transform-origin: left center;
}

.detail-button:hover {
    transform: scale(1.1);
}

.eurobot-history-button {
    margin: 120px 5vw 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 40px;
    width: max-content;
    min-width: 240px;
    padding: 14px 20px;
    border: 1px solid rgba(255, 255, 255, 0.65);
    font-family: 'Orbitron', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.13em;
    transition:
        background 0.3s ease,
        color 0.3s ease,
        border-color 0.3s ease,
        transform 0.3s ease;
}

.eurobot-history-button-icon {
    width: 19px;
    height: 19px;
    transition: transform 0.3s ease;
}

.eurobot-history-button:hover {
    background: white;
    color: #050505;
    border-color: white;
    transform: translateY(-3px);
}

.eurobot-history-button:hover .eurobot-history-button-icon {
    transform: translate(4px, -4px);
}

.modal-enter-active,
.modal-leave-active {
    transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}

@media (max-width: 850px) {
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

    .achievement-title-line:last-child {
        margin-left: 0;
        margin-top: 4px;
    }

    .achievement-awards {
        align-self: flex-start;
        margin-top: 30px;
        text-align: left;
    }

    .achievement-award {
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

    .robots-grid:has(> .robot-card:last-child:nth-child(odd))>.robot-card:first-child {
        grid-column: auto;
        width: 100%;
    }

    .robot-name {
        text-align: center;
    }

    .detail-button {
        font-size: 24px;
    }

    .eurobot-history-button {
        margin: 100px 0 0;
        min-width: 210px;
    }
}

@media (max-width: 520px) {
    .achievement-panel {
        margin-top: 180px;
        padding-left: 20px;
        padding-right: 20px;
    }

    .robot-image-container {
        width: 95%;
    }

    .eurobot-history-button {
        width: 100%;
        min-width: 0;
        padding: 14px 18px;
    }
}
</style>
