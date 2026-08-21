<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import RobotViewer3D from '@/components/template/RobotViewer3D.vue'
import FilePreviewModal from '@/components/template/FilePreviewModal.vue'
import ApiState from '@/components/common/ApiState.vue'
import ArrowRight from '@/components/icons/FreeArrowRight.vue'
import { useApiData } from '@/composables/useApiData'
import { ArrowUpRight } from 'lucide-vue-next'

// 手機版統一使用 600px 斷點；平板仍保留 3D 預覽功能。
const mobileBreakpoint = '(max-width: 600px)'

defineProps({
    achievementMarginTop: {
        type: String,
        default: '400px',
    },
    showHistoryButton: {
        type: Boolean,
        default: true,
    },
})

// 當年 Eurobot 資料、機器人清單與 3D 檢視狀態。
const {
    data: eurobotData,
    loading,
    error,
    load: loadThisYearEurobotData,
    reload,
} = useApiData({})
const robots = computed(() => eurobotData.value.robots || [])
const achievementPhoto = computed(() => eurobotData.value.background || '')
const selectedRobot = ref(null)
const isMobile = ref(window.matchMedia(mobileBreakpoint).matches)
const mobilePreviewNoticeId = ref(null)
let mobileMediaQuery
let mobileNoticeTimer

// 開啟指定機器人的 3D 檢視器，並鎖定背景捲動。
function openRobot3D(robot) {
    if (isMobile.value) return

    selectedRobot.value = robot
    document.body.style.overflow = 'hidden'
}

// 手機版以提示取代 3D 視窗；桌面和平板維持原本預覽功能。
function handleRobotPreview(robot) {
    if (!isMobile.value) {
        openRobot3D(robot)
        return
    }

    mobilePreviewNoticeId.value = robot.id
    clearTimeout(mobileNoticeTimer)
    mobileNoticeTimer = setTimeout(() => {
        mobilePreviewNoticeId.value = null
    }, 3000)
}

// 關閉 3D 檢視器並恢復頁面捲動。
function closeRobot3D() {
    selectedRobot.value = null
    document.body.style.overflow = ''
}

// 螢幕切換成手機寬度時立即關閉 3D 視窗，並停用所有預覽入口。
function updateMobileState(event) {
    isMobile.value = event.matches
    if (isMobile.value && selectedRobot.value) closeRobot3D()
    mobilePreviewNoticeId.value = null
}

// 依卡片數量與位置決定機器人名稱對齊方向。
function getRobotNameAlignment(robot) {
    const index = robots.value.findIndex((item) => item.id === robot.id)
    const count = robots.value.length

    if (count % 2 === 1 && index === 0) return 'center'

    const offset = count % 2 === 1 ? index - 1 : index
    return offset % 2 === 0 ? 'right' : 'left'
}

// 元件掛載後載入資料，並監聽桌面／手機斷點變化。
onMounted(() => {
    mobileMediaQuery = window.matchMedia(mobileBreakpoint)
    isMobile.value = mobileMediaQuery.matches
    mobileMediaQuery.addEventListener('change', updateMobileState)
})

// 若開啟 3D 視窗時離開頁面，確保恢復 body 捲動。
onUnmounted(() => {
    mobileMediaQuery?.removeEventListener('change', updateMobileState)
    clearTimeout(mobileNoticeTimer)
    document.body.style.overflow = ''
})
loadThisYearEurobotData('/api/Eurobot')
</script>

<template>
    <!-- 當年 Eurobot 戰績與機器人展示區。 -->
    <section id="featured-robot" class="robot-year-section"
        :style="{ '--achievement-margin-top': achievementMarginTop }">
        <ApiState v-if="loading || error || robots.length === 0"
            :loading="loading" :error="error" :empty="robots.length === 0" @retry="reload" />

        <!-- 捲動時固定在畫面後方的團隊照片。 -->
        <div v-show="!loading && !error && robots.length > 0" class="sticky-background">
            <!-- 當年 Eurobot 團隊背景圖。 -->
            <img class="background-image" :src="achievementPhoto" alt="DIT Robotics Team" />
            <!-- 提高前景文字可讀性的深色遮罩。 -->
            <div class="background-overlay"></div>
        </div>

        <!-- 戰績與機器人卡片的前景內容。 -->
        <div v-show="!loading && !error && robots.length > 0" class="robot-year-content">
            <!-- 當年 Eurobot 戰績區塊。 -->
            <section class="achievement-panel">
                <!-- 年份、主標題與獎項內容。 -->
                <div class="achievement-content">
                    <!-- Eurobot 年份。 -->
                    <p class="achievement-year">Eurobot {{ eurobotData.year }}</p>

                    <!-- 當年主視覺標題。 -->
                    <h2 class="achievement-title">{{ eurobotData.bigTitle }}</h2>

                    <!-- 當年競賽獎項。 -->
                    <div class="achievement-awards" :style="{ '--text-color': eurobotData.awardsColor }">
                        <p v-for="text in eurobotData.awards" :key="text" class="achievement-award">
                            {{ text }}
                        </p>
                    </div>
                </div>
            </section>

            <!-- 永遠建立 Teleport 目標；v-show 只隱藏，不會移除 DOM。 -->
            <section id="Eurobot_rules"></section>

            <!-- 當年機器人展示區。 -->
            <section class="robots-showcase">
                <!-- 機器人卡片網格。 -->
                <div class="robots-grid">
                    <!-- 單一機器人卡片。 -->
                    <article v-for="robot in robots" :key="robot.id" class="robot-card">
                        <!-- 機器人展示名稱。 -->
                        <p class="robot-name" :style="{ '--text-align': getRobotNameAlignment(robot) }">
                            <span class="robot-name-text" :style="{ color: robot.themeColor }">
                                {{ robot.displayName }}
                            </span>
                        </p>

                        <!-- 桌面版可點擊開啟 3D；手機版只保留一般機器人圖片。 -->
                        <div class="robot-image-container" :class="{ 'is-interactive': !isMobile }"
                            role="button" tabindex="0"
                            :aria-label="isMobile ? '顯示 3D 預覽裝置提示' : `查看 ${robot.name} 的 3D 預覽`"
                            @click="handleRobotPreview(robot)"
                            @keydown.enter="handleRobotPreview(robot)"
                            @keydown.space.prevent="handleRobotPreview(robot)">
                            <img class="robot-image" :src="robot.imagePath" :alt="robot.name" />

                            <!-- 3D 提示不會在手機版建立。 -->
                            <div v-if="!isMobile" class="image-overlay">
                                <div class="view-3d">
                                    <span class="view-icon">360°</span>
                                    <span class="view-label">INTERACTIVE VIEW</span>
                                </div>
                            </div>

                            <Transition name="mobile-preview-notice">
                                <div v-if="isMobile && mobilePreviewNoticeId === robot.id"
                                    class="mobile-3d-notice" role="status">
                                    <div class="mobile-3d-notice-content">
                                        <span class="mobile-3d-notice-icon">360°</span>
                                        <span class="mobile-3d-notice-text">
                                            請使用電腦查看 3D 機器人預覽
                                        </span>
                                    </div>
                                </div>
                            </Transition>
                        </div>

                        <!-- 開啟機器人詳細資料的檔案預覽視窗。 -->
                        <FilePreviewModal v-slot="{ open: openPreview }" api="/api/PopUpItem/whiteSeeMore"
                            title="NTHU DIT">
                            <button class="detail-button" type="button" @click.stop="openPreview">
                                <span>See more </span>
                                <ArrowRight class="detail-button-arrow"/>
                            </button>
                        </FilePreviewModal>
                    </article>
                </div>

                <!-- 前往歷屆 Eurobot 內容的按鈕。 -->
                <RouterLink v-if="showHistoryButton" class="eurobot-history-button" id="eurobot-history-button"
                    to="/Eurobot#RobotArchive">
                    <span class="eurobot-history-button-label">歷屆 EUROBOT</span>
                    <ArrowUpRight class="eurobot-history-button-icon" />
                </RouterLink>

            </section>
        </div>

        <!-- Advisor 的 Teleport 目標不依賴 Eurobot API 狀態，必須永遠存在。 -->
        <div id="Advisors_teleport" class="advisors-teleport-target"></div>

        <!-- 目前選取機器人的 3D 檢視視窗。 -->
        <Transition name="modal">
            <RobotViewer3D v-if="selectedRobot && !isMobile" :robot="selectedRobot"
                :closeRobot3D="closeRobot3D" />
        </Transition>
    </section>
</template>

<style scoped>
.robot-year-section {
    position: relative;
    background: #050505;
    color: white;
}

.advisors-teleport-target {
    position: relative;
    z-index: 300;
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
    margin-top: var(--achievement-margin-top);
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
    text-align: right;
    white-space: pre-wrap;
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
    background: transparent;
    transform: scale(1);
    transition: transform 0.3s ease;
}

.robot-image-container.is-interactive {
    cursor: pointer;
}

.mobile-3d-notice {
    position: absolute;
    z-index: 3;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: radial-gradient(circle at 50% 48%, rgba(5, 5, 5, 0.68), rgba(5, 5, 5, 0.2) 38%, transparent 70%);
    color: #fff;
    text-align: center;
    pointer-events: none;
}

.mobile-3d-notice-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    max-width: 220px;
}

.mobile-3d-notice-icon {
    width: 68px;
    height: 68px;
    display: grid;
    place-items: center;
    border: 1px solid rgba(255, 255, 255, 0.7);
    border-radius: 50%;
    font-size: 13px;
    letter-spacing: 0.08em;
}

.mobile-3d-notice-text {
    font-size: 13px;
    font-weight: 700;
    line-height: 1.65;
    letter-spacing: 0.08em;
    text-shadow: 0 2px 12px rgba(0, 0, 0, 0.9);
}

.mobile-preview-notice-enter-active,
.mobile-preview-notice-leave-active {
    transition: opacity 260ms ease;
}

.mobile-preview-notice-enter-active .mobile-3d-notice-content,
.mobile-preview-notice-leave-active .mobile-3d-notice-content {
    transition: transform 260ms ease, opacity 260ms ease;
}

.mobile-preview-notice-enter-from,
.mobile-preview-notice-leave-to {
    opacity: 0;
}

.mobile-preview-notice-enter-from .mobile-3d-notice-content,
.mobile-preview-notice-leave-to .mobile-3d-notice-content {
    opacity: 0;
    transform: translateY(12px);
}

.robot-image {
    width: 100%;
    height: 100%;
    object-fit: contain;
    transition: transform 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.robot-image-container.is-interactive:hover {
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

.robot-image-container.is-interactive:hover .image-overlay {
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

.robot-image-container.is-interactive:hover .view-3d {
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
    position: relative;
    z-index: 10;
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
    text-decoration: none;
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

@media (max-width: 900px) {
    .achievement-panel {
        margin-top: 250px;
        margin-bottom: 100px;
        padding: 110px clamp(16px, 4vw, 24px) 70px;
        align-items: flex-end;
    }

    .achievement-content {
        width: 100%;
        margin-left: 0;
        align-items: flex-start;
        transform: none;
        text-align: left;
    }

    .achievement-year {
        margin-bottom: 22px;
        font-size: 20px;
    }

    .achievement-title {
        width: 100%;
        max-width: 100%;
        font-size: clamp(36px, 11vw, 56px);
        text-align: left;
        white-space: pre-line;
        word-break: keep-all;
        overflow-wrap: anywhere;
    }

    .achievement-awards {
        align-self: flex-start;
        margin-top: 30px;
        text-align: left;
    }

    .achievement-award {
        font-size: clamp(12px, 6vw, 38px);
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
        gap: 48px;
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

@media (max-width: 600px) {
    .achievement-panel {
        margin-top: 180px;
        padding-left: 16px;
        padding-right: 16px;
    }

    .robot-image-container {
        width: 95%;
    }

    .robots-grid {
        gap: 32px;
    }

    .eurobot-history-button {
        width: 100%;
        min-width: 0;
        padding: 14px 18px;
    }
}
</style>
