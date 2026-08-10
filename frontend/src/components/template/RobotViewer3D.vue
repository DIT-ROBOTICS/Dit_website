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
    model: {
        type: String,
        required: true
    }
})

const container = ref(null)

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

    camera.position.set(
        4,
        3,
        5
    )

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
        props.model,

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

    const center =
        box.getCenter(
            new THREE.Vector3()
        )

    const size =
        box.getSize(
            new THREE.Vector3()
        )

    model.position.sub(center)

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
    <div
        ref="container"
        class="robot-viewer"
    ></div>
</template>

<style scoped>
.robot-viewer {
    width: 100%;
    height: 100%;

    background:
        radial-gradient(
            circle at center,
            #202020,
            #050505 70%
        );

    cursor: grab;
}

.robot-viewer:active {
    cursor: grabbing;
}
</style>