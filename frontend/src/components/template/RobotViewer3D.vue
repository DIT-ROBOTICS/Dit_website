<script setup>
import { computed, markRaw, ref, onMounted, onUnmounted } from 'vue'
import *as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'

const props = defineProps({
    robot: {
        type: Object,
        required: true
    },
    closeRobot3D: {
        type: Function,
        required: true
    }
})

// Template DOM 引用：3D 畫布容器、右側標題與零件連接線。
const container = ref(null)
const detailTitle = ref(null)
const partConnector = ref(null)

// 模型載入狀態。
const modelLoading = ref(true)
const modelProgress = ref(0)
const modelProgressIsEstimated = ref(false)
const modelLoadError = ref('')
const modelFileMissing = ref(false)

// 零件導覽與目前選取狀態。
const showControlPanel = ref(true)
const selectedPart = ref(null)
const guideParts = ref([])

// 只有 Componets 存在且至少有一筆時，才建立左右零件導覽 UI。
const hasComponents = computed(
    () => Array.isArray(props.robot.Componets) && props.robot.Componets.length > 0
)

// Three.js 場景物件與畫面生命週期資源。
let scene
let camera
let renderer
let controls
let robot
let animationFrame
let resizeObserver
let highlightedMeshes = []
let highlightStartedAt = 0
let cameraFocusAnimation = null

const PART_HIGHLIGHT_INTERVAL_MS = 2000
const PART_HIGHLIGHT_FLASH_MS = 420
const CAMERA_FOCUS_DURATION_MS = 700

const tempWorldPosition = new THREE.Vector3()

function init() {
    scene = new THREE.Scene()

    // 根據後端資料決定初始視角從機器左側或右側觀看。
    camera = new THREE.PerspectiveCamera(
        40,
        container.value.clientWidth / container.value.clientHeight,
        0.1,
        1000
    )

    const dx = props.robot.View3Dpos === 'left' ? -1 : 1
    camera.position.set(4 * dx, 2, 4)

    renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true
    })

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    renderer.setSize(container.value.clientWidth, container.value.clientHeight)
    container.value.appendChild(renderer.domElement)

    controls = new OrbitControls(camera, renderer.domElement)
    controls.enableDamping = true
    controls.dampingFactor = 0.06
    controls.enableZoom = true
    controls.enablePan = true
    controls.minDistance = 2
    controls.maxDistance = 15

    addLights()
    loadModel()

    resizeObserver = new ResizeObserver(resize)
    resizeObserver.observe(container.value)

    animate()
}

function addLights() {
    const ambient = new THREE.AmbientLight(0xffffff, 2.5)
    scene.add(ambient)

    const mainLight = new THREE.DirectionalLight(0xffffff, 4)
    mainLight.position.set(5, 8, 5)
    scene.add(mainLight)

    const sideLight = new THREE.DirectionalLight(0xffffff, 2)
    sideLight.position.set(-5, 3, 2)
    scene.add(sideLight)

    const backLight = new THREE.DirectionalLight(0xffffff, 1.5)
    backLight.position.set(0, 4, -6)
    scene.add(backLight)
}

function loadModel() {
    // 每次重載前先重置 UI 狀態與舊模型資源。
    modelLoading.value = true
    modelProgress.value = 0
    modelProgressIsEstimated.value = false
    modelLoadError.value = ''
    modelFileMissing.value = false
    selectedPart.value = null
    guideParts.value = []

    if (robot) {
        scene.remove(robot)
        disposeObject(robot)
        robot = null
    }

    if (!props.robot.glbPath) {
        modelLoading.value = false
        modelFileMissing.value = true
        modelLoadError.value = '目前沒有此機器的 3D 檔案'
        return
    }

    const loader = new GLTFLoader()

    loader.load(
        props.robot.glbPath,
        gltf => {
            robot = gltf.scene
            scene.add(robot)

            centerModel(robot)
            setupGuideParts()

            modelProgress.value = 100
            modelProgressIsEstimated.value = false

            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    modelLoading.value = false
                })
            })
        },
        event => {
            // 優先使用 API 提供的 glbSize；event.total 不可用時才顯示估算進度。
            const totalBytes = Number(props.robot.glbSize) || event.total

            if (totalBytes) {
                modelProgressIsEstimated.value = false
                modelProgress.value = Math.min(Math.round(event.loaded / totalBytes * 100), 99)
                return
            }

            modelProgressIsEstimated.value = true
            const estimateBase = 40 * 1024 * 1024
            const estimatedProgress = Math.round(95 * (1 - Math.exp(-event.loaded / estimateBase)))
            modelProgress.value = Math.max(modelProgress.value, Math.min(estimatedProgress, 95))
        },
        error => {
            console.error('GLB load error', error)

            const status = error?.target?.status ?? error?.response?.status
            const errorMessage = String(error?.message || error || '')
            const isNotFound = status === 404 || /\b404\b|not found/i.test(errorMessage)

            modelLoading.value = false
            modelFileMissing.value = isNotFound
            modelLoadError.value = isNotFound
                ? '目前沒有此機器的 3D 檔案，欲查看檔案請聯絡DIT'
                : '模型載入失敗，可能是檔案損毀或無法解析，請聯絡DIT'
        }
    )
}

function centerModel(model) {
    // 以整體包圍盒將模型置中，並統一縮放到檢視器適合的尺寸。
    const box = new THREE.Box3().setFromObject(model)
    const center = box.getCenter(new THREE.Vector3())
    const size = box.getSize(new THREE.Vector3())

    model.position.sub(center)
    model.position.y -= 1.3

    const maxDimension = Math.max(size.x, size.y, size.z)
    const scale = 3 / maxDimension

    model.scale.setScalar(scale)
    model.updateMatrixWorld(true)

    controls.target.set(0, 0, 0)
    controls.update()
}

function setupGuideParts() {
    if (!robot) return

    // 零件標註與詳細資料統一由機器人資料的 Componets 陣列提供。
    // 非陣列時使用空陣列，避免後端資料缺少時 map() 發生錯誤。
    const parts = Array.isArray(props.robot.Componets) ? props.robot.Componets : []

    robot.updateMatrixWorld(true)

    guideParts.value = parts.map((part, index) => {
        // objectName 可為單一字串或陣列；第一個找到的節點負責箭頭定位。
        const objectNames = Array.isArray(part.objectName)
            ? part.objectName
            : part.objectName
                ? [part.objectName]
                : []
        const objects = objectNames
            .map(objectName => {
                const object = findRobotPart(objectName)
                if (!object) console.warn(`找不到零件:${objectName}`)
                return object
            })
            .filter(Boolean)
        const object = objects[0] || null

        // 新舊資料的文字欄位不同，在此統一成檢視器使用的格式。
        const normalizedPart = {
            ...part,
            id: part.id ?? `part-${index + 1}`,
            description: part.description ?? part.content ?? ''
        }

        if (!object) {
            return {
                ...normalizedPart,
                object: null,
                objects: [],
                anchorLocal: null,
                screenX: 0,
                screenY: 0
            }
        }

        const box = new THREE.Box3().setFromObject(object)
        const worldCenter = box.getCenter(new THREE.Vector3())
        const anchorLocal = object.worldToLocal(worldCenter.clone())

        return {
            ...normalizedPart,
            // Three.js 類別實例不可由 Vue 深層代理，否則矩陣與座標更新可能失效。
            object: markRaw(object),
            objects: objects.map(item => markRaw(item)),
            anchorLocal: markRaw(anchorLocal),
            screenX: 0,
            screenY: 0
        }
    })

    // 文字細節不依賴 3D 節點；即使 objectName 尚未設定也可顯示第一筆說明。
    if (guideParts.value.length) selectPart(guideParts.value[0])
}

// GLTFLoader 會把節點名稱中的空格、冒號等字元清理後存入 object.name，
// 但 GLB 原始名稱仍保留在 object.userData.name。
function findRobotPart(objectName) {
    const directMatch = robot.getObjectByName(objectName)
    if (directMatch) return directMatch

    const sanitizedName = THREE.PropertyBinding.sanitizeNodeName(objectName)
    let originalNameMatch = null
    let sanitizedNameMatch = null

    robot.traverse(object => {
        if (originalNameMatch) return

        if (object.userData?.name === objectName) {
            originalNameMatch = object
            return
        }

        if (!sanitizedNameMatch && object.name === sanitizedName) {
            sanitizedNameMatch = object
        }
    })

    return originalNameMatch || sanitizedNameMatch
}

function getPartWorldPosition(part, target) {
    if (!part.object || !part.anchorLocal) return null

    target.copy(part.anchorLocal)
    part.object.localToWorld(target)

    return target
}

function updateGuidePositions() {
    if (!container.value || !camera || !robot) return

    const width = container.value.clientWidth
    const height = container.value.clientHeight

    robot.updateMatrixWorld(true)
    camera.updateMatrixWorld(true)

    guideParts.value.forEach(part => {
        if (!part.object || !part.anchorLocal) {
            return
        }

        getPartWorldPosition(part, tempWorldPosition)

        const projected = tempWorldPosition.clone().project(camera)

        part.screenX = (projected.x * 0.5 + 0.5) * width
        part.screenY = (-projected.y * 0.5 + 0.5) * height

        // 每個 animation frame 都重新投影零件的世界座標，
        // 因此模型旋轉、縮放或平移時，連接線的零件端會同步追蹤。
    })

    // 右側 detail 標題是 DOM 元素，需轉換成相對於 3D 畫布的座標。
    // 每幀更新可確保視窗縮放或 detail 面板動畫時，連接線仍貼住標題。
    const connector = partConnector.value
    const part = selectedPart.value

    if (connector && detailTitle.value && part?.object) {
        const containerRect = container.value.getBoundingClientRect()
        const titleRect = detailTitle.value.getBoundingClientRect()
        const startX = titleRect.left - containerRect.left
        const startY = titleRect.top - containerRect.top + titleRect.height / 2
        const deltaX = part.screenX - startX
        const deltaY = part.screenY - startY
        const color = part.color || props.robot.ThemeColor || '#ffffff'

        // Three.js 每幀直接更新 DOM，避免將 Object3D 放入 Vue reactive 後沒有觸發樣式重繪。
        connector.style.left = `${startX}px`
        connector.style.top = `${startY}px`
        connector.style.width = `${Math.hypot(deltaX, deltaY)}px`
        connector.style.transform = `rotate(${Math.atan2(deltaY, deltaX)}rad)`
        connector.style.setProperty('--part-color', color)
        connector.style.opacity = '1'
    } else if (connector) {
        connector.style.opacity = '0'
    }
}

function selectPart(part) {
    selectedPart.value = part
    startPartHighlight(part)
}

// 複製被選零件的材質，避免閃爍效果影響共用同一材質的其他機器人部位。
function startPartHighlight(part) {
    clearPartHighlight()
    if (!part?.object) return

    const highlightColor = new THREE.Color(part.color || props.robot.ThemeColor || '#ffffff')
    const highlightedMeshSet = new Set()

    // 同一筆詳細資料可綁定多個 3D 節點，所有節點共用同一閃爍週期。
    part.objects.forEach(object => {
        object.traverse(child => {
            if (!child.isMesh || !child.material || highlightedMeshSet.has(child)) return
            highlightedMeshSet.add(child)

            const originalMaterial = child.material
            const sourceMaterials = Array.isArray(originalMaterial) ? originalMaterial : [originalMaterial]
            const highlightMaterials = sourceMaterials.map(material => material.clone())

            child.material = Array.isArray(originalMaterial)
                ? highlightMaterials
                : highlightMaterials[0]

            highlightedMeshes.push({
                mesh: child,
                originalMaterial,
                highlightColor,
                materials: highlightMaterials.map(material => ({
                    material,
                    baseColor: material.color?.clone() || null,
                    baseEmissive: material.emissive?.clone() || null,
                    baseEmissiveIntensity: material.emissiveIntensity ?? 0
                }))
            })
        })
    })

    highlightStartedAt = performance.now()
}

function updatePartHighlight(timestamp) {
    if (!highlightedMeshes.length) return

    const elapsed = timestamp - highlightStartedAt
    const cycleTime = elapsed % PART_HIGHLIGHT_INTERVAL_MS

    // 每兩秒亮起一次，其餘時間完全恢復原本材質顏色。
    const strength = cycleTime < PART_HIGHLIGHT_FLASH_MS
        ? Math.sin(Math.PI * cycleTime / PART_HIGHLIGHT_FLASH_MS)
        : 0

    highlightedMeshes.forEach(entry => {
        entry.materials.forEach(({ material, baseColor, baseEmissive, baseEmissiveIntensity }) => {
            if (material.emissive && baseEmissive) {
                material.emissive.copy(baseEmissive).lerp(entry.highlightColor, strength)
                material.emissiveIntensity = baseEmissiveIntensity + strength * 2
            } else if (material.color && baseColor) {
                material.color.copy(baseColor).lerp(entry.highlightColor, strength * 0.7)
            }
        })
    })
}

function clearPartHighlight() {
    highlightedMeshes.forEach(entry => {
        entry.mesh.material = entry.originalMaterial
        entry.materials.forEach(({ material }) => material.dispose())
    })

    highlightedMeshes = []
}

function closePartDetail() {
    selectedPart.value = null
    clearPartHighlight()
}

function focusPart(part) {
    selectPart(part)

    if (!part.object) return

    const partPosition = new THREE.Vector3()
    getPartWorldPosition(part, partPosition)

    // 保持相機高度、距離與機器中心不變，只水平旋轉到零件所在方向。
    controls.target.set(0, 0, 0)

    const radius = Math.hypot(camera.position.x, camera.position.z)
    const startAngle = Math.atan2(camera.position.x, camera.position.z)
    const requestedAngle = Math.atan2(partPosition.x, partPosition.z)
    const angleDifference = Math.atan2(
        Math.sin(requestedAngle - startAngle),
        Math.cos(requestedAngle - startAngle)
    )

    cameraFocusAnimation = {
        startTime: performance.now(),
        startAngle,
        angleDifference,
        radius,
        height: camera.position.y
    }
}

function updateCameraFocus(timestamp) {
    if (!cameraFocusAnimation) return

    const animation = cameraFocusAnimation
    const progress = Math.min((timestamp - animation.startTime) / CAMERA_FOCUS_DURATION_MS, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    const angle = animation.startAngle + animation.angleDifference * eased

    camera.position.x = Math.sin(angle) * animation.radius
    camera.position.z = Math.cos(angle) * animation.radius
    camera.position.y = animation.height
    controls.target.set(0, 0, 0)

    if (progress >= 1) cameraFocusAnimation = null
}

function animate(timestamp) {
    animationFrame = requestAnimationFrame(animate)

    // 每幀更新 Focus 旋轉、材質閃爍與 DOM 連接線，最後繪製 Three.js 場景。
    updateCameraFocus(timestamp)
    controls?.update()
    updatePartHighlight(timestamp)
    updateGuidePositions()

    renderer?.render(scene, camera)
}

function resize() {
    if (!container.value || !camera || !renderer) return

    const width = container.value.clientWidth
    const height = container.value.clientHeight

    camera.aspect = width / height
    camera.updateProjectionMatrix()
    renderer.setSize(width, height)
}

function disposeObject(object) {
    object.traverse(child => {
        if (child.geometry) child.geometry.dispose()

        if (child.material) {
            const materials = Array.isArray(child.material)
                ? child.material
                : [child.material]

            materials.forEach(material => {
                Object.values(material).forEach(value => {
                    if (value?.isTexture) value.dispose()
                })

                material.dispose()
            })
        }
    })
}

onMounted(init)

onUnmounted(() => {
    cancelAnimationFrame(animationFrame)

    resizeObserver?.disconnect()
    controls?.dispose()
    clearPartHighlight()

    if (robot) disposeObject(robot)

    renderer?.dispose()
    renderer?.domElement?.remove()
})
</script>

<template>
    <!-- 全螢幕 3D 檢視視窗；點擊遮罩空白處可關閉。 -->
    <div class="robot-modal" @click.self="props.closeRobot3D">
        <div class="modal-container">
            <!-- 關閉整個 3D 視窗。 -->
            <button class="close-button" @click="props.closeRobot3D">×</button>

            <div class="viewer">
                <!-- Three.js canvas 與所有 HUD 元素的共用座標容器。 -->
                <div ref="container" class="robot-viewer">
                    <!-- 後端資料指定的視覺背景與閱讀性遮罩。 -->
                    <div class="viewer-background"
                        :style="{ '--background-api': `url(${props.robot.View3DBackground})` }"></div>

                    <div class="viewer-overlay"></div>

                    <!-- 機器展示名稱；左側導覽展開時會自動向右移動。 -->
                    <div class="viewer-info"
                        :class="{ 'guide-is-open': hasComponents && showControlPanel && !modelLoading && !modelLoadError }"
                        :style="{
                            color: props.robot.ThemeColor
                        }">
                        {{ props.robot.ShowOutName }}
                    </div>

                    <!-- 左側零件檔案總管：選取後會 Focus、閃爍並顯示右側詳細資料。 -->
                    <div v-if="hasComponents && showControlPanel && !modelLoading && !modelLoadError"
                        class="guide-control">
                        <div class="guide-control-header">
                            <span>COMPONENTS</span>

                            <button type="button" class="panel-collapse" @click="showControlPanel = false">
                                ‹
                            </button>
                        </div>

                        <div class="guide-buttons">
                            <button v-for="part in guideParts" :key="part.id" type="button" class="guide-part-row"
                                :class="{
                                    active: selectedPart?.id === part.id,
                                    missing: !part.object
                                }" @click="focusPart(part)">
                                {{ part.title }}
                            </button>
                        </div>
                    </div>

                    <button v-else-if="hasComponents && !modelLoading && !modelLoadError"
                        class="open-control-panel" type="button"
                        @click="showControlPanel = true">
                        ›
                    </button>

                    <!-- 由 JS 動畫迴圈直接定位，連接 detail 標題與 3D 零件。 -->
                    <div v-if="hasComponents" ref="partConnector" class="part-connector" aria-hidden="true"></div>

                    <!-- 右側零件詳細資料。 -->
                    <Transition name="detail-panel">
                        <aside v-if="hasComponents && selectedPart && !modelLoading && !modelLoadError"
                            class="part-detail">
                            <button class="detail-close" type="button" @click="closePartDetail">
                                ×
                            </button>

                            <p class="part-detail-index">
                                {{ selectedPart.category || 'COMPONENT' }}
                            </p>

                            <h2 ref="detailTitle">{{ selectedPart.title }}</h2>

                            <p v-if="selectedPart.product" class="part-detail-product">
                                {{ selectedPart.product }}
                            </p>

                            <div v-if="selectedPart.image" class="part-detail-image">
                                <img :src="selectedPart.image" :alt="selectedPart.title">
                            </div>

                            <p class="part-detail-description">
                                {{ selectedPart.description }}
                            </p>

                            <div v-if="selectedPart.details?.length" class="part-detail-items">
                                <div v-for="item in selectedPart.details" :key="item.title" class="part-detail-item">
                                    <span>{{ item.title }}</span>
                                    <p>{{ item.content }}</p>
                                </div>
                            </div>

                            <button v-if="selectedPart.object" class="focus-button" type="button"
                                @click="focusPart(selectedPart)">
                                FOCUS COMPONENT
                            </button>
                        </aside>
                    </Transition>

                    <!-- 模型下載進度、檔案不存在與載入失敗狀態。 -->
                    <Transition name="model-loader">
                        <div v-if="modelLoading || modelLoadError" class="model-loading" role="status" aria-live="polite">
                            <template v-if="modelLoading">
                                <div class="model-loading-spinner" aria-hidden="true">
                                    <span class="model-loading-spinner-core"></span>
                                </div>

                                <p class="model-loading-title">
                                    LOADING 3D MODEL
                                </p>

                                <div class="model-loading-progress" aria-hidden="true">
                                    <span class="model-loading-progress-value"
                                        :class="{ 'is-estimated': modelProgressIsEstimated }"
                                        :style="{ width: `${modelProgress}%` }"></span>
                                </div>

                                <p class="model-loading-percent">
                                    {{ modelProgressIsEstimated ? `約 ${modelProgress}%` : `${modelProgress}%` }}
                                </p>
                            </template>

                            <template v-else>
                                <p class="model-loading-title">
                                    {{ modelFileMissing ? '3D MODEL NOT AVAILABLE' : 'LOAD FAILED' }}
                                </p>

                                <p class="model-loading-error">
                                    {{ modelLoadError }}
                                </p>

                                <button v-if="!modelFileMissing" class="model-loading-retry" type="button"
                                    @click="loadModel">
                                    重新載入
                                </button>
                            </template>
                        </div>
                    </Transition>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* ===== Modal shell ===== */
.robot-modal {
    position: fixed;
    inset: 0;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 120px 40px 40px;
    backdrop-filter: blur(14px);
}

.modal-container {
    position: relative;
    width: min(1500px, 100%);
    height: 85vh;
    background: #0a0a0a;
    border: 1px solid rgba(255, 255, 255, .15);
    z-index: 100;
}

.close-button {
    position: absolute;
    top: 0;
    right: 0;
    z-index: 20;
    width: 44px;
    height: 44px;
    border: 1px solid rgba(255, 255, 255, .25);
    border-radius: 50%;
    background: #333;
    color: #fff;
    font-size: 28px;
    transform: translate(50%, -50%);
}

.viewer,
.robot-viewer {
    position: relative;
    width: 100%;
    height: 100%;
}

.robot-viewer {
    --guide-control-width: clamp(210px, 22vw, 300px);

    border: 5px solid #c6c6c6;
    border-radius: 5px;
    overflow: hidden;
    cursor: grab;
}

.robot-viewer:active {
    cursor: grabbing;
}

/* ===== Three.js canvas and background ===== */
.viewer-background {
    position: absolute;
    inset: 0;
    background: var(--background-api) center / cover no-repeat;
    z-index: 0;
}

.viewer-overlay {
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at center,
            rgba(20, 20, 20, .45) 10%,
            rgba(20, 20, 20, .70) 55%,
            rgba(15, 15, 15, .95) 100%);
    z-index: 1;
    pointer-events: none;
}

.robot-viewer :deep(canvas) {
    position: relative;
    z-index: 2;
}

/* ===== Viewer heading and component explorer ===== */
.viewer-info {
    position: absolute;
    left: 24px;
    right: 5%;
    top: 5%;
    z-index: 3;
    text-align: left;
    pointer-events: none;
    font-size: clamp(28px, 4vw, 60px);
    letter-spacing: .08em;
    text-shadow: 0 3px 4px #000;
    font-weight: 900;
    transition: left .25s ease;
}

.viewer-info.guide-is-open {
    left: calc(var(--guide-control-width) + 24px);
}

.guide-control {
    position: absolute;
    inset: 0 auto 0 0;
    z-index: 10;
    width: var(--guide-control-width);
    height: 100%;
    padding: 22px 12px;
    border-right: 1px solid rgba(255, 255, 255, .16);
    background: rgba(12, 12, 16, .94);
    color: #fff;
    backdrop-filter: blur(12px);
}

.guide-control-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
    padding: 0 8px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, .12);
    font-size: 14px;
    font-weight: 800;
    letter-spacing: .14em;
}

.panel-collapse {
    display: grid;
    place-items: center;
    width: 28px;
    height: 28px;
    border: 0;
    border-radius: 4px;
    background: transparent;
    color: #fff;
    font-size: 24px;
}

.panel-collapse:hover {
    background: rgba(255, 255, 255, .1);
}

.guide-buttons {
    display: flex;
    flex-direction: column;
    gap: 2px;
    max-height: calc(100% - 64px);
    overflow: auto;
}

.guide-part-row {
    width: 100%;
    padding: 10px 12px;
    border: 0;
    border-left: 2px solid transparent;
    border-radius: 3px;
    background: transparent;
    color: rgba(255, 255, 255, .7);
    text-align: left;
    transition: background .15s ease, color .15s ease, border-color .15s ease;
}

.guide-part-row:hover {
    background: rgba(255, 255, 255, .07);
    color: rgba(255, 255, 255, .92);
}

.guide-part-row.active {
    border-left-color: rgba(255, 255, 255, .9);
    background: rgba(255, 255, 255, .16);
    color: #fff;
    font-weight: 700;
}

.guide-part-row.missing {
    opacity: .35;
}

.open-control-panel {
    position: absolute;
    left: 0;
    top: 50%;
    z-index: 10;
    width: 38px;
    height: 72px;
    border: 1px solid rgba(255, 255, 255, .2);
    border-left: 0;
    background: rgba(10, 10, 12, .85);
    color: #fff;
    font-size: 25px;
    transform: translateY(-50%);
}

/* ===== Live connector and component details ===== */
.part-connector {
    position: absolute;
    z-index: 13;
    height: 2px;
    opacity: 0;
    background: var(--part-color, #fff);
    box-shadow: 0 0 6px var(--part-color, #fff);
    transform-origin: left center;
    pointer-events: none;
}

.part-connector::after {
    content: '';
    position: absolute;
    top: 50%;
    right: -1px;
    width: 0;
    height: 0;
    border-top: 6px solid transparent;
    border-bottom: 6px solid transparent;
    border-left: 10px solid var(--part-color, #fff);
    transform: translateY(-50%);
}

.part-detail {
    position: absolute;
    top: 0;
    right: 0;
    z-index: 12;
    width: min(380px, 32%);
    height: 100%;
    padding: 70px 32px 32px;
    overflow: auto;
    border-left: 1px solid rgba(255, 255, 255, .15);
    background: rgba(8, 8, 11, .93);
    color: #fff;
    cursor: auto;
    backdrop-filter: blur(15px);
}

.detail-close {
    position: absolute;
    top: 20px;
    right: 20px;
    width: 34px;
    height: 34px;
    border: 1px solid rgba(255, 255, 255, .2);
    border-radius: 50%;
    background: transparent;
    color: #fff;
    font-size: 20px;
}

.part-detail-index {
    margin: 0 0 8px;
    color: rgba(255, 255, 255, .4);
    font-size: 10px;
    letter-spacing: .2em;
    text-transform: uppercase;
}

.part-detail h2 {
    margin: 0;
    font-size: 30px;
    line-height: 1.1;
}

.part-detail-product {
    margin: 10px 0 0;
    color: rgba(255, 255, 255, .55);
}

.part-detail-image {
    width: 100%;
    margin-top: 24px;
    overflow: hidden;
}

.part-detail-image img {
    display: block;
    width: 100%;
    aspect-ratio: 16/9;
    object-fit: cover;
}

.part-detail-description {
    margin-top: 24px;
    color: rgba(255, 255, 255, .72);
    line-height: 1.8;
}

.part-detail-items {
    margin-top: 24px;
    border-top: 1px solid rgba(255, 255, 255, .12);
}

.part-detail-item {
    padding: 16px 0;
    border-bottom: 1px solid rgba(255, 255, 255, .12);
}

.part-detail-item span {
    display: block;
    margin-bottom: 5px;
    color: rgba(255, 255, 255, .4);
    font-size: 11px;
    letter-spacing: .1em;
}

.part-detail-item p {
    margin: 0;
    line-height: 1.6;
}

.focus-button {
    width: 100%;
    margin-top: 24px;
    padding: 12px;
    border: 1px solid rgba(255, 255, 255, .3);
    background: transparent;
    color: #fff;
    font-size: 11px;
    letter-spacing: .1em;
}

/* ===== Loading and error state ===== */
.model-loading {
    position: absolute;
    z-index: 30;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 30px;
    background: rgba(8, 9, 14, .72);
    color: #fff;
    text-align: center;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

.model-loading-spinner {
    position: relative;
    width: 76px;
    height: 76px;
    margin-bottom: 24px;
    border: 2px solid rgba(255, 255, 255, .16);
    border-top-color: currentColor;
    border-radius: 50%;
    animation: model-loading-spin 1s linear infinite;
}

.model-loading-spinner::after {
    content: '';
    position: absolute;
    inset: 8px;
    border: 1px solid rgba(255, 255, 255, .28);
    border-right-color: transparent;
    border-radius: 50%;
    animation: model-loading-spin 1.6s linear infinite reverse;
}

.model-loading-spinner-core {
    position: absolute;
    top: 50%;
    left: 50%;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: currentColor;
    box-shadow: 0 0 22px rgba(255, 255, 255, .75);
    transform: translate(-50%, -50%);
}

.model-loading-title,
.model-loading-percent,
.model-loading-error {
    margin: 0;
}

.model-loading-title {
    font-size: clamp(14px, 1.5vw, 20px);
    font-weight: 800;
    letter-spacing: .18em;
}

.model-loading-progress {
    width: min(280px, 70%);
    height: 3px;
    margin-top: 20px;
    overflow: hidden;
    background: rgba(255, 255, 255, .18);
}

.model-loading-progress-value {
    display: block;
    height: 100%;
    background: currentColor;
}

.model-loading-progress-value.is-estimated {
    transition: width 180ms ease;
}

.model-loading-percent,
.model-loading-error {
    margin-top: 12px;
    color: rgba(255, 255, 255, .68);
    font-size: 12px;
    letter-spacing: .12em;
}

.model-loading-retry {
    margin-top: 22px;
    padding: 10px 18px;
    border: 1px solid rgba(255, 255, 255, .45);
    background: transparent;
    color: #fff;
}

.viewer-info,
.guide-control-header,
.part-detail-index,
.part-detail h2,
.focus-button,
.model-loading-title {
    font-family: 'Orbitron', sans-serif;
}

.close-button,
.panel-collapse,
.guide-part-row,
.open-control-panel,
.detail-close,
.focus-button,
.model-loading-retry {
    cursor: pointer;
}

.model-loader-enter-active,
.model-loader-leave-active {
    transition: opacity 300ms ease;
}

.model-loader-enter-from,
.model-loader-leave-to {
    opacity: 0;
}

.detail-panel-enter-active,
.detail-panel-leave-active {
    transition: transform .3s ease, opacity .3s ease;
}

.detail-panel-enter-from,
.detail-panel-leave-to {
    opacity: 0;
    transform: translateX(100%);
}

@keyframes model-loading-spin {
    to {
        transform: rotate(360deg);
    }
}

/* ===== Tablet layout ===== */
@media(max-width:900px) {
    .robot-modal {
        padding: 80px 15px 20px;
    }

    .modal-container {
        height: 88vh;
    }

    .robot-viewer {
        --guide-control-width: 190px;
    }

    .part-detail {
        top: auto;
        bottom: 0;
        width: 100%;
        height: 45%;
        padding: 50px 22px 22px;
        border-top: 1px solid rgba(255, 255, 255, .15);
        border-left: 0;
    }

}
</style>
