<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const props = defineProps({
    model: {
        type: String,
        required: true
    }
})

const container = ref(null)
const modelLoaded = ref(false)

let scene = null
let camera = null
let renderer = null
let robotGroup = null

let animationFrame = null
let resizeObserver = null
let intersectionObserver = null

let isVisible = false
let isDestroyed = false


/* ========================================
   Init
======================================== */

function init() {
    if (!container.value || isDestroyed) return

    const width = container.value.clientWidth
    const height = container.value.clientHeight

    if (width <= 0 || height <= 0) {
        console.warn('Preview container size invalid:', width, height)
        return
    }

    console.log('Preview size:', width, height)

    scene = new THREE.Scene()

    camera = new THREE.PerspectiveCamera(
        35,
        width / height,
        0.01,
        1000
    )

    renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        powerPreference: 'low-power'
    })

    renderer.setClearColor(0x000000, 0)

    /*
        Preview 不需要非常高解析度。

        Retina 可能 devicePixelRatio = 2，
        如果兩台模型同時 render，
        canvas GPU buffer 會明顯增加。

        Preview 限制到 1.5 就夠了。
    */
    renderer.setPixelRatio(
        Math.min(
            window.devicePixelRatio,
            1.5
        )
    )

    renderer.setSize(
        width,
        height,
        false
    )

    renderer.outputColorSpace = THREE.SRGBColorSpace

    container.value.appendChild(
        renderer.domElement
    )

    addLights()
    setupIntersectionObserver()
    setupResizeObserver()
    loadModel()

    animate()
}


/* ========================================
   Lights
======================================== */

function addLights() {
    if (!scene) return

    const ambient =
        new THREE.AmbientLight(
            0xffffff,
            2.5
        )

    scene.add(ambient)

    const main =
        new THREE.DirectionalLight(
            0xffffff,
            4
        )

    main.position.set(
        5,
        8,
        5
    )

    scene.add(main)

    const back =
        new THREE.DirectionalLight(
            0xffffff,
            2
        )

    back.position.set(
        -5,
        4,
        -5
    )

    scene.add(back)
}


/* ========================================
   Load Model
======================================== */

function loadModel() {
    // return
    const loader =
        new GLTFLoader()

    loader.load(
        props.model,

        (gltf) => {
            if (isDestroyed) {
                disposeObject(gltf.scene)
                return
            }

            console.log(
                'Preview GLB loaded:',
                gltf
            )

            const robot =
                gltf.scene

            /*
                額外建立 Group。

                之後旋轉 Group，
                不直接旋轉 CAD 本身，
                比較不容易受到 CAD 原始 transform 影響。
            */
            robotGroup =
                new THREE.Group()

            scene.add(
                robotGroup
            )

            robotGroup.add(
                robot
            )

            fitModel(robot)

            logModelInfo(robot)

            modelLoaded.value = true

            /*
                模型剛載完立刻 render 一次，
                即使 IntersectionObserver 還沒更新，
                也不會整塊空白。
            */
            renderFrame()
        },

        undefined,

        (error) => {
            modelLoaded.value = false

            console.error(
                'Preview GLB error:',
                error
            )
        }
    )
}


/* ========================================
   Fit Model
======================================== */

function fitModel(model) {
    if (!camera) return

    model.updateMatrixWorld(true)

    let box =
        new THREE.Box3()
            .setFromObject(model)

    const originalSize =
        new THREE.Vector3()

    box.getSize(originalSize)

    const maxSize =
        Math.max(
            originalSize.x,
            originalSize.y,
            originalSize.z
        )

    console.log(
        'Original model size:',
        originalSize
    )

    if (
        !Number.isFinite(maxSize) ||
        maxSize <= 0
    ) {
        console.error(
            'Invalid model size:',
            maxSize
        )

        return
    }


    /* ========================================
       Scale
    ======================================== */

    const targetSize = 3

    const scale =
        targetSize /
        maxSize

    model.scale.setScalar(
        scale
    )

    model.updateMatrixWorld(true)


    /* ========================================
       Center
    ======================================== */

    box =
        new THREE.Box3()
            .setFromObject(model)

    const center =
        new THREE.Vector3()

    box.getCenter(center)

    model.position.x -= center.x
    model.position.y -= center.y
    model.position.z -= center.z

    model.updateMatrixWorld(true)


    /* ========================================
       Final Size
    ======================================== */

    box =
        new THREE.Box3()
            .setFromObject(model)

    const finalSize =
        new THREE.Vector3()

    box.getSize(finalSize)

    const finalMax =
        Math.max(
            finalSize.x,
            finalSize.y,
            finalSize.z
        )

    console.log(
        'Final model size:',
        finalSize
    )


    /* ========================================
       Camera
    ======================================== */

    camera.position.set(
        finalMax * 1.4,
        finalMax * 0.8,
        finalMax * 1.4
    )

    camera.lookAt(
        0,
        0,
        0
    )

    camera.near =
        Math.max(
            finalMax / 100,
            0.001
        )

    camera.far =
        Math.max(
            finalMax * 100,
            100
        )

    camera.updateProjectionMatrix()
}


/* ========================================
   Render
======================================== */

function renderFrame() {
    if (
        isDestroyed ||
        !renderer ||
        !scene ||
        !camera
    ) return

    renderer.render(
        scene,
        camera
    )
}


function animate() {
    if (isDestroyed) return

    animationFrame =
        requestAnimationFrame(
            animate
        )

    /*
        不在畫面中就完全不 render。

        requestAnimationFrame 還存在，
        但裡面幾乎沒有 GPU 工作。
    */
    if (!isVisible) {
        return
    }

    if (robotGroup) {
        robotGroup.rotation.y +=
            0.004
    }

    renderFrame()
}


/* ========================================
   Intersection Observer

   只有畫面真的看到 Preview 時
   才持續 render。
======================================== */

function setupIntersectionObserver() {
    if (!container.value) return

    intersectionObserver =
        new IntersectionObserver(
            ([entry]) => {
                isVisible =
                    entry.isIntersecting

                /*
                    剛進入畫面時先 render 一次，
                    避免第一幀延遲。
                */
                if (isVisible) {
                    renderFrame()
                }
            },
            {
                threshold: 0.01,

                /*
                    快接近畫面時就開始 render，
                    看起來比較自然。
                */
                rootMargin: '150px'
            }
        )

    intersectionObserver.observe(
        container.value
    )
}


/* ========================================
   Resize Observer
======================================== */

function setupResizeObserver() {
    if (!container.value) return

    resizeObserver =
        new ResizeObserver(() => {
            resize()
        })

    resizeObserver.observe(
        container.value
    )
}


function resize() {
    if (
        !container.value ||
        !camera ||
        !renderer ||
        isDestroyed
    ) return

    const width =
        container.value.clientWidth

    const height =
        container.value.clientHeight

    if (
        width <= 0 ||
        height <= 0
    ) return

    camera.aspect =
        width /
        height

    camera.updateProjectionMatrix()

    renderer.setSize(
        width,
        height,
        false
    )

    renderFrame()
}


/* ========================================
   Debug

   看 CAD 到底有多重
======================================== */

function logModelInfo(model) {
    let meshes = 0
    let triangles = 0
    let materials = 0
    const textures =
        new Set()

    model.traverse((child) => {
        if (!child.isMesh) return

        meshes++

        const geometry =
            child.geometry

        if (geometry) {
            if (geometry.index) {
                triangles +=
                    geometry.index.count / 3
            }
            else if (
                geometry.attributes.position
            ) {
                triangles +=
                    geometry
                        .attributes
                        .position
                        .count / 3
            }
        }

        const materialList =
            Array.isArray(child.material)
                ? child.material
                : [child.material]

        materialList.forEach(
            (material) => {
                if (!material) return

                materials++

                Object.values(
                    material
                ).forEach(
                    (value) => {
                        if (value?.isTexture) {
                            textures.add(value)
                        }
                    }
                )
            }
        )
    })

    console.log(
        '======= Preview Model Info ======='
    )

    console.log(
        'Meshes:',
        meshes
    )

    console.log(
        'Triangles:',
        Math.round(
            triangles
        ).toLocaleString()
    )

    console.log(
        'Materials:',
        materials
    )

    console.log(
        'Textures:',
        textures.size
    )

    console.log(
        '=================================='
    )
}


/* ========================================
   Dispose Material
======================================== */

function disposeMaterial(material) {
    if (!material) return

    /*
        Three.js Material 裡面可能有：

        map
        normalMap
        roughnessMap
        metalnessMap
        aoMap
        emissiveMap
        alphaMap
        envMap
        ...

        全部找出 Texture dispose。
    */

    Object.values(
        material
    ).forEach(
        (value) => {
            if (value?.isTexture) {
                value.dispose()
            }
        }
    )

    material.dispose()
}


/* ========================================
   Dispose Object
======================================== */

function disposeObject(object) {
    if (!object) return

    object.traverse(
        (child) => {
            if (!child.isMesh) return

            child.geometry?.dispose()

            if (
                Array.isArray(
                    child.material
                )
            ) {
                child.material.forEach(
                    disposeMaterial
                )
            }
            else {
                disposeMaterial(
                    child.material
                )
            }
        }
    )
}


/* ========================================
   Destroy
======================================== */

function destroyThree() {
    isDestroyed = true

    modelLoaded.value = false
    isVisible = false


    /* animation */

    if (animationFrame !== null) {
        cancelAnimationFrame(
            animationFrame
        )

        animationFrame = null
    }


    /* observers */

    intersectionObserver
        ?.disconnect()

    intersectionObserver = null

    resizeObserver
        ?.disconnect()

    resizeObserver = null


    /* model */

    if (robotGroup) {
        disposeObject(
            robotGroup
        )

        scene?.remove(
            robotGroup
        )

        robotGroup.clear()

        robotGroup = null
    }


    /* renderer */

    if (renderer) {

        /*
            清 Three.js internal render lists。
        */
        renderer.renderLists?.dispose()

        /*
            dispose renderer 本身。
        */
        renderer.dispose()

        /*
            主動釋放 WebGL context。

            對 SPA / Vue 頁面切換很重要，
            不然瀏覽器可能暫時繼續保留 GPU memory。
        */
        renderer.forceContextLoss()

        /*
            移除 canvas。
        */
        renderer.domElement?.remove()

        renderer = null
    }


    /* scene */

    if (scene) {
        scene.clear()
        scene = null
    }

    camera = null
}


/* ========================================
   Vue Lifecycle
======================================== */

onMounted(() => {

    /*
        等父元素先完成 layout，
        避免第一次拿到 0 × 0。
    */

    requestAnimationFrame(() => {
        if (!isDestroyed) {
            init()
        }
    })

})


onUnmounted(() => {
    destroyThree()
})
</script>


<template>
    <div
        ref="container"
        class="robot-preview"
        :class="{
            loaded: modelLoaded
        }"
    ></div>
</template>


<style scoped>
.robot-preview {
    position: absolute;

    inset: 0;

    width: 100%;
    height: 100%;

    pointer-events: none;

    background:
        radial-gradient(
            circle at 50% 45%,
            #242424,
            #080808 70%
        );

    transition:
        background 0.5s ease;
}


.robot-preview.loaded {
    background:
        transparent;
}


.robot-preview :deep(canvas) {
    display: block;

    width: 100%;
    height: 100%;
}
</style>