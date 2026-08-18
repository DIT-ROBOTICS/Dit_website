<script setup>
import {
    ref,
    onMounted,
    onUnmounted
} from 'vue'

import * as THREE from 'three'

import {
    GLTFLoader
} from 'three/addons/loaders/GLTFLoader.js'

import {
    OrbitControls
} from 'three/addons/controls/OrbitControls.js'

const props = defineProps({
    robot: {
        type: Object,
        required: true
    },
    closeRobot3D:{
        type: Function,
        required: true
    }
})

const container = ref(null)
const background_api = ref(props.robot.View3DBackground)
const selectedRobot = ref(props.robot)
const modelLoading = ref(true)
const modelProgress = ref(0)
const modelProgressIsEstimated = ref(false)
const modelLoadError = ref('')
const modelFileMissing = ref(false)

let scene
let camera
let renderer
let controls
let robot
let animationFrame
let resizeObserver

function init() {
    scene = new THREE.Scene()

    camera =
        new THREE.PerspectiveCamera(
            40,
            container.value.clientWidth /
            container.value.clientHeight,
            0.1,
            1000
        )

    const dx = props.robot.View3Dpos === "left" ? -1 : 1
    camera.position.set(4*dx,2,4)

    renderer =
        new THREE.WebGLRenderer({
            antialias: true,
            alpha: true
        })

    renderer.setPixelRatio(
        Math.min(
            window.devicePixelRatio,
            2
        )
    )

    renderer.setSize(
        container.value.clientWidth,
        container.value.clientHeight
    )

    container.value.appendChild(
        renderer.domElement
    )

    controls =
        new OrbitControls(
            camera,
            renderer.domElement
        )

    controls.enableDamping = true

    controls.dampingFactor = 0.06

    controls.enableZoom = true

    controls.enablePan = true

    controls.minDistance = 2
    controls.maxDistance = 15

    addLights()

    loadModel()

    resizeObserver =
        new ResizeObserver(resize)

    resizeObserver.observe(
        container.value
    )

    animate()
}

function addLights() {
    const ambient =
        new THREE.AmbientLight(
            0xffffff,
            2.5
        )

    scene.add(ambient)

    const mainLight =
        new THREE.DirectionalLight(
            0xffffff,
            4
        )

    mainLight.position.set(
        5,
        8,
        5
    )

    scene.add(mainLight)

    const sideLight =
        new THREE.DirectionalLight(
            0xffffff,
            2
        )

    sideLight.position.set(
        -5,
        3,
        2
    )

    scene.add(sideLight)

    const backLight =
        new THREE.DirectionalLight(
            0xffffff,
            1.5
        )

    backLight.position.set(
        0,
        4,
        -6
    )

    scene.add(backLight)
}

function loadModel() {
    modelLoading.value = true
    modelProgress.value = 0
    modelProgressIsEstimated.value = false
    modelLoadError.value = ''
    modelFileMissing.value = false

    if (!props.robot.glbPath) {
        modelLoading.value = false
        modelFileMissing.value = true
        modelLoadError.value = '目前沒有此機器的 3D 檔案'
        return
    }

    const loader =
        new GLTFLoader()

    loader.load(
        props.robot.glbPath,

        (gltf) => {
            robot = gltf.scene

            scene.add(robot)

            centerModel(robot)
            modelProgress.value = 100
            modelProgressIsEstimated.value = false

            // 連續等待兩個繪製週期，確保進度條真的呈現 100% 後才開始淡出。
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    modelLoading.value = false
                })
            })
        },

        (event) => {
            // API 提供的 glbSize 不會受 proxy 是否保留 Content-Length 影響。
            const totalBytes = Number(props.robot.glbSize) || event.total
            if (totalBytes) {
                modelProgressIsEstimated.value = false
                modelProgress.value = Math.min(Math.round((event.loaded / totalBytes) * 100), 99)
                return
            }

            // 舊 API 沒有總大小時顯示平滑估算值，並保留最後 5% 給模型解析階段。
            modelProgressIsEstimated.value = true
            const estimateBase = 40 * 1024 * 1024
            const estimatedProgress = Math.round(95 * (1 - Math.exp(-event.loaded / estimateBase)))
            modelProgress.value = Math.max(modelProgress.value, Math.min(estimatedProgress, 95))
        },

        (error) => {
            console.error(
                'GLB load error',
                error
            )

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
    const box =
        new THREE.Box3().setFromObject(
            model
        )

    let center =
        box.getCenter(
            new THREE.Vector3()
        )

    const size =
        box.getSize(
            new THREE.Vector3()
        )

    model.position.sub(center)
    model.position.y += -1.3

    const maxDimension =
        Math.max(
            size.x,
            size.y,
            size.z
        )

    const scale =
        3 / maxDimension

    model.scale.setScalar(scale)

    controls.target.set(
        0,
        0,
        0
    )

    controls.update()
}

function animate() {
    animationFrame =
        requestAnimationFrame(animate)

    controls.update()

    renderer.render(
        scene,
        camera
    )
}

function resize() {
    if (
        !container.value ||
        !camera ||
        !renderer
    ) return

    const width =
        container.value.clientWidth

    const height =
        container.value.clientHeight

    camera.aspect =
        width / height

    camera.updateProjectionMatrix()

    renderer.setSize(
        width,
        height
    )
}

onMounted(init)

onUnmounted(() => {
    cancelAnimationFrame(
        animationFrame
    )

    resizeObserver?.disconnect()

    controls?.dispose()
    renderer?.dispose()

    renderer?.domElement?.remove()
})
</script>

<template>
    <div class="robot-modal" @click.self="props.closeRobot3D">
        <div class="modal-container">
            <button class="close-button" @click="props.closeRobot3D">
                ×
            </button>

            <div class="viewer">
                <div ref="container" class="robot-viewer">
                    <div class="viewer-background" :style="{'--background-api':`url(${background_api})`}"></div>
                    <div class="viewer-overlay"></div>

                    <!-- 模型下載及初始化期間的狀態畫面。 -->
                    <Transition name="model-loader">
                        <div v-if="modelLoading || modelLoadError" class="model-loading" role="status"
                            aria-live="polite">
                            <template v-if="modelLoading">
                                <div class="model-loading-spinner" aria-hidden="true">
                                    <span class="model-loading-spinner-core"></span>
                                </div>
                                <p class="model-loading-title">LOADING 3D MODEL</p>
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
                                <p class="model-loading-error">{{ modelLoadError }}</p>
                                <button v-if="!modelFileMissing" class="model-loading-retry" type="button"
                                    @click="loadModel">
                                    重新載入
                                </button>
                            </template>
                        </div>
                    </Transition>
                </div>
                <div class="viewer-info" :style="{'--pos':selectedRobot.View3Dpos,color: selectedRobot.ThemeColor}">
                    {{ selectedRobot.ShowOutName }}
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.robot-viewer{
    position:relative;
    width:100%;
    height:100%;
    border:5px solid #c6c6c6;
    border-radius:5px;
    overflow:hidden;
    cursor:grab;
}

.viewer-background{
    position:absolute;
    inset:0;
    background-image:var(--background-api);
    background-position:center;
    background-size:cover;
    background-repeat:no-repeat;
    z-index:0;
}

.viewer-overlay{
    position:absolute;
    inset:0;
    background:
        radial-gradient(
            circle at center,
            rgba(20,20,20,0.45) 10%,
            rgba(20,20,20,0.70) 55%,
            rgba(15,15,15,0.95) 100%
        );
    z-index:1;
    pointer-events:none;
}

.robot-viewer:active{
    cursor:grabbing;
}

.robot-viewer :deep(canvas){
    position:relative;
    z-index:2;
}

.model-loading {
    position: absolute;
    z-index: 3;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 30px;
    background: rgba(8, 9, 14, 0.72);
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
    border: 2px solid rgba(255, 255, 255, 0.16);
    border-top-color: currentColor;
    border-radius: 50%;
    animation: model-loading-spin 1s linear infinite;
}

.model-loading-spinner::after {
    content: '';
    position: absolute;
    inset: 8px;
    border: 1px solid rgba(255, 255, 255, 0.28);
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
    box-shadow: 0 0 22px rgba(255, 255, 255, 0.75);
    transform: translate(-50%, -50%);
}

.model-loading-title,
.model-loading-percent,
.model-loading-error {
    margin: 0;
}

.model-loading-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(14px, 1.5vw, 20px);
    font-weight: 800;
    letter-spacing: 0.18em;
}

.model-loading-progress {
    width: min(280px, 70%);
    height: 3px;
    margin-top: 20px;
    overflow: hidden;
    background: rgba(255, 255, 255, 0.18);
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
    color: rgba(255, 255, 255, 0.68);
    font-size: 12px;
    letter-spacing: 0.12em;
}

.model-loading-retry {
    margin-top: 22px;
    padding: 10px 18px;
    border: 1px solid rgba(255, 255, 255, 0.45);
    background: transparent;
    color: #fff;
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

@keyframes model-loading-spin {
    to {
        transform: rotate(360deg);
    }
}



.robot-modal {
    position: fixed;

    inset: 0;
    

    z-index: 9999;

    display: flex;

    align-items: center;

    justify-content: center;

    padding: 120px 40px 40px;
/* 
    background:
        rgba(0, 0, 0, 0.8); */

    backdrop-filter:
        blur(14px);
}
.modal-container {
    position: relative;

    width:
        min(1200px, 100%);

    height: 85vh;

    background: #0a0a0a;

    border:
        1px solid rgba(255, 255, 255, 0.15);

    z-index: 100;
}

.close-button {
    position: absolute;

    top: 0px;

    right: 0px;

    z-index: 4;

    width: 44px;
    height: 44px;

    border:
        1px solid rgba(255, 255, 255, 0.25);

    border-radius: 50%;

    background:
        rgb(51, 51, 51);

    color: white;

    font-size: 28px;

    cursor: pointer;
    transform: translateX(50%) translateY(-50%);
}
.viewer {
    position: relative;

    width: 100%;
    height: 100%;
}
.viewer-info {
    position: absolute;
    left: 5%;
    top: 5%;
    width: 90%;
    text-align: var(--pos);
    z-index: 2;
    pointer-events: none;
    font-family: 'Orbitron', sans-serif;
    margin: 0 0 8px;
    font-size: 60px;
    letter-spacing: 0.08em;
    text-shadow: 0 3px 4px #000;
    font-weight: 900;
}
</style>
