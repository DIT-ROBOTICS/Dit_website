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
    const loader =
        new GLTFLoader()

    loader.load(
        props.robot.glbPath,

        (gltf) => {
            robot = gltf.scene

            scene.add(robot)

            centerModel(robot)
        },

        undefined,

        (error) => {
            console.error(
                'GLB load error',
                error
            )
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

    height:
        min(780px, 85vh);

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