<script setup>
import{ref,onMounted,onUnmounted}from'vue'
import*as THREE from'three'
import{GLTFLoader}from'three/addons/loaders/GLTFLoader.js'
import{OrbitControls}from'three/addons/controls/OrbitControls.js'

const props=defineProps({
    robot:{
        type:Object,
        required:true
    },
    closeRobot3D:{
        type:Function,
        required:true
    }
})

const container=ref(null)
const background_api=ref(props.robot.View3DBackground)
const selectedRobot=ref(props.robot)
const modelLoading=ref(true)
const modelProgress=ref(0)
const modelProgressIsEstimated=ref(false)
const modelLoadError=ref('')
const modelFileMissing=ref(false)

const showLabels=ref(true)
const showControlPanel=ref(true)
const selectedPart=ref(null)
const guideParts=ref([])

let scene
let camera
let renderer
let controls
let robot
let animationFrame
let resizeObserver
let raycaster
let clock

const tempWorldPosition=new THREE.Vector3()
const tempDirection=new THREE.Vector3()

function init(){
    scene=new THREE.Scene()
    raycaster=new THREE.Raycaster()
    clock=new THREE.Clock()

    camera=new THREE.PerspectiveCamera(
        40,
        container.value.clientWidth/container.value.clientHeight,
        0.1,
        1000
    )

    const dx=props.robot.View3Dpos==="left"?-1:1
    camera.position.set(4*dx,2,4)

    renderer=new THREE.WebGLRenderer({
        antialias:true,
        alpha:true
    })

    renderer.setPixelRatio(Math.min(window.devicePixelRatio,2))
    renderer.setSize(container.value.clientWidth,container.value.clientHeight)
    container.value.appendChild(renderer.domElement)

    controls=new OrbitControls(camera,renderer.domElement)
    controls.enableDamping=true
    controls.dampingFactor=0.06
    controls.enableZoom=true
    controls.enablePan=true
    controls.minDistance=2
    controls.maxDistance=15

    addLights()
    loadModel()

    resizeObserver=new ResizeObserver(resize)
    resizeObserver.observe(container.value)

    animate()
}

function addLights(){
    const ambient=new THREE.AmbientLight(0xffffff,2.5)
    scene.add(ambient)

    const mainLight=new THREE.DirectionalLight(0xffffff,4)
    mainLight.position.set(5,8,5)
    scene.add(mainLight)

    const sideLight=new THREE.DirectionalLight(0xffffff,2)
    sideLight.position.set(-5,3,2)
    scene.add(sideLight)

    const backLight=new THREE.DirectionalLight(0xffffff,1.5)
    backLight.position.set(0,4,-6)
    scene.add(backLight)
}

function loadModel(){
    modelLoading.value=true
    modelProgress.value=0
    modelProgressIsEstimated.value=false
    modelLoadError.value=''
    modelFileMissing.value=false
    selectedPart.value=null
    guideParts.value=[]

    if(robot){
        scene.remove(robot)
        disposeObject(robot)
        robot=null
    }

    if(!props.robot.glbPath){
        modelLoading.value=false
        modelFileMissing.value=true
        modelLoadError.value='目前沒有此機器的 3D 檔案'
        return
    }

    const loader=new GLTFLoader()

    loader.load(
        props.robot.glbPath,
        gltf=>{
            robot=gltf.scene
            scene.add(robot)

            centerModel(robot)
            setupGuideParts()

            modelProgress.value=100
            modelProgressIsEstimated.value=false

            requestAnimationFrame(()=>{
                requestAnimationFrame(()=>{
                    modelLoading.value=false
                })
            })
        },
        event=>{
            const totalBytes=Number(props.robot.glbSize)||event.total

            if(totalBytes){
                modelProgressIsEstimated.value=false
                modelProgress.value=Math.min(Math.round(event.loaded/totalBytes*100),99)
                return
            }

            modelProgressIsEstimated.value=true
            const estimateBase=40*1024*1024
            const estimatedProgress=Math.round(95*(1-Math.exp(-event.loaded/estimateBase)))
            modelProgress.value=Math.max(modelProgress.value,Math.min(estimatedProgress,95))
        },
        error=>{
            console.error('GLB load error',error)

            const status=error?.target?.status??error?.response?.status
            const errorMessage=String(error?.message||error||'')
            const isNotFound=status===404||/\b404\b|not found/i.test(errorMessage)

            modelLoading.value=false
            modelFileMissing.value=isNotFound
            modelLoadError.value=isNotFound
                ?'目前沒有此機器的 3D 檔案，欲查看檔案請聯絡DIT'
                :'模型載入失敗，可能是檔案損毀或無法解析，請聯絡DIT'
        }
    )
}

function centerModel(model){
    const box=new THREE.Box3().setFromObject(model)
    const center=box.getCenter(new THREE.Vector3())
    const size=box.getSize(new THREE.Vector3())

    model.position.sub(center)
    model.position.y-=1.3

    const maxDimension=Math.max(size.x,size.y,size.z)
    const scale=3/maxDimension

    model.scale.setScalar(scale)
    model.updateMatrixWorld(true)

    controls.target.set(0,0,0)
    controls.update()
}

function setupGuideParts(){
    if(!robot)return

    // 零件標註與詳細資料統一由機器人資料的 detail 陣列提供。
    // 非陣列時使用空陣列，避免後端資料缺少時 map() 發生錯誤。
    const parts=Array.isArray(props.robot.detail)?props.robot.detail:[]

    robot.updateMatrixWorld(true)

    guideParts.value=parts.map(part=>{
        const object=robot.getObjectByName(part.objectName)

        if(!object){
            console.warn(`找不到零件:${part.objectName}`)

            return{
                ...part,
                object:null,
                anchorLocal:null,
                show:part.show!==false,
                visible:false,
                screenX:0,
                screenY:0,
                labelX:0,
                labelY:0
            }
        }

        const box=new THREE.Box3().setFromObject(object)
        const worldCenter=box.getCenter(new THREE.Vector3())
        const anchorLocal=object.worldToLocal(worldCenter.clone())

        return{
            ...part,
            object,
            anchorLocal,
            show:part.show!==false,
            visible:true,
            screenX:0,
            screenY:0,
            labelX:0,
            labelY:0
        }
    })

    if(guideParts.value.length){
        const firstValid=guideParts.value.find(part=>part.object)
        if(firstValid)selectedPart.value=firstValid
    }
}

function getPartWorldPosition(part,target){
    if(!part.object||!part.anchorLocal)return null

    target.copy(part.anchorLocal)
    part.object.localToWorld(target)

    return target
}

function updateGuidePositions(){
    if(!container.value||!camera||!robot)return

    const width=container.value.clientWidth
    const height=container.value.clientHeight

    robot.updateMatrixWorld(true)
    camera.updateMatrixWorld(true)

    guideParts.value.forEach(part=>{
        if(!part.object||!part.anchorLocal){
            part.visible=false
            return
        }

        getPartWorldPosition(part,tempWorldPosition)

        const projected=tempWorldPosition.clone().project(camera)

        part.screenX=(projected.x*0.5+0.5)*width
        part.screenY=(-projected.y*0.5+0.5)*height

        const offset=part.labelOffset||[100,-60]

        part.labelX=part.screenX+offset[0]
        part.labelY=part.screenY+offset[1]

        const insideCamera=
            projected.z>=-1&&
            projected.z<=1&&
            projected.x>=-1.2&&
            projected.x<=1.2&&
            projected.y>=-1.2&&
            projected.y<=1.2

        if(!insideCamera){
            part.visible=false
            return
        }

        part.visible=!isPartOccluded(part,tempWorldPosition)
    })
}

function isPartOccluded(part,worldPosition){
    tempDirection.copy(worldPosition).sub(camera.position)

    const targetDistance=tempDirection.length()

    tempDirection.normalize()

    raycaster.set(camera.position,tempDirection)

    const intersections=raycaster.intersectObject(robot,true)

    if(!intersections.length)return false

    const first=intersections[0]

    if(first.distance>=targetDistance-0.05)return false

    return!belongsToPart(first.object,part.object)
}

function belongsToPart(object,target){
    let current=object

    while(current){
        if(current===target)return true
        current=current.parent
    }

    return false
}

function selectPart(part){
    if(!part.object)return
    selectedPart.value=part
}

function focusPart(part){
    if(!part.object)return

    selectPart(part)

    const position=new THREE.Vector3()

    getPartWorldPosition(part,position)

    controls.target.copy(position)
    controls.update()
}

function resetCamera(){
    const dx=props.robot.View3Dpos==="left"?-1:1

    camera.position.set(4*dx,2,4)
    controls.target.set(0,0,0)
    controls.update()
}

function toggleAllParts(value){
    guideParts.value.forEach(part=>{
        part.show=value
    })
}

function updateRobotAnimation(delta){
    if(!robot)return

    /*
    之後可以在這裡加入動畫。

    const lidar=robot.getObjectByName('YDLIDAR_G6:1')

    if(lidar){
        lidar.rotation.y+=delta*2
    }
    */
}

function animate(){
    animationFrame=requestAnimationFrame(animate)

    const delta=clock?.getDelta()||0

    controls?.update()
    updateRobotAnimation(delta)
    updateGuidePositions()

    renderer?.render(scene,camera)
}

function resize(){
    if(!container.value||!camera||!renderer)return

    const width=container.value.clientWidth
    const height=container.value.clientHeight

    camera.aspect=width/height
    camera.updateProjectionMatrix()
    renderer.setSize(width,height)
}

function disposeObject(object){
    object.traverse(child=>{
        if(child.geometry)child.geometry.dispose()

        if(child.material){
            const materials=Array.isArray(child.material)
                ?child.material
                :[child.material]

            materials.forEach(material=>{
                Object.values(material).forEach(value=>{
                    if(value?.isTexture)value.dispose()
                })

                material.dispose()
            })
        }
    })
}

onMounted(init)

onUnmounted(()=>{
    cancelAnimationFrame(animationFrame)

    resizeObserver?.disconnect()
    controls?.dispose()

    if(robot)disposeObject(robot)

    renderer?.dispose()
    renderer?.domElement?.remove()
})
</script>

<template>
    <div class="robot-modal" @click.self="props.closeRobot3D">
        <div class="modal-container">
            <button class="close-button" @click="props.closeRobot3D">×</button>

            <div class="viewer">
                <div ref="container" class="robot-viewer">
                    <div
                        class="viewer-background"
                        :style="{'--background-api':`url(${background_api})`}"
                    ></div>

                    <div class="viewer-overlay"></div>

                    <div
                        class="viewer-info"
                        :style="{
                            '--pos':selectedRobot.View3Dpos,
                            color:selectedRobot.ThemeColor
                        }"
                    >
                        {{selectedRobot.ShowOutName}}
                    </div>

                    <div
                        v-if="showControlPanel&&!modelLoading&&!modelLoadError"
                        class="guide-control"
                    >
                        <div class="guide-control-header">
                            <span>COMPONENTS</span>

                            <button
                                type="button"
                                class="panel-collapse"
                                @click="showControlPanel=false"
                            >
                                ‹
                            </button>
                        </div>

                        <label class="guide-master-switch">
                            <input v-model="showLabels" type="checkbox">
                            <span>顯示零件標註</span>
                        </label>

                        <div class="guide-buttons">
                            <div
                                v-for="part in guideParts"
                                :key="part.id"
                                class="guide-part-row"
                                :class="{
                                    active:selectedPart?.id===part.id,
                                    missing:!part.object
                                }"
                            >
                                <input
                                    v-model="part.show"
                                    type="checkbox"
                                    :disabled="!part.object"
                                    @click.stop
                                >

                                <button
                                    type="button"
                                    :disabled="!part.object"
                                    @click="focusPart(part)"
                                >
                                    {{part.title}}
                                </button>
                            </div>
                        </div>

                        <div class="guide-control-actions">
                            <button type="button" @click="toggleAllParts(true)">
                                全部顯示
                            </button>

                            <button type="button" @click="toggleAllParts(false)">
                                全部隱藏
                            </button>

                            <button type="button" @click="resetCamera">
                                重設視角
                            </button>
                        </div>
                    </div>

                    <button
                        v-else-if="!modelLoading&&!modelLoadError"
                        class="open-control-panel"
                        type="button"
                        @click="showControlPanel=true"
                    >
                        ›
                    </button>

                    <svg
                        v-if="showLabels"
                        class="guide-lines"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <defs>
                            <marker
                                id="guide-arrow"
                                markerWidth="10"
                                markerHeight="10"
                                refX="8"
                                refY="5"
                                orient="auto"
                            >
                                <path d="M0,0 L10,5 L0,10 Z"></path>
                            </marker>
                        </defs>

                        <line
                            v-for="part in guideParts"
                            v-show="part.show&&part.visible"
                            :key="part.id"
                            :x1="part.labelX"
                            :y1="part.labelY"
                            :x2="part.screenX"
                            :y2="part.screenY"
                            marker-end="url(#guide-arrow)"
                        />
                    </svg>

                    <button
                        v-for="part in guideParts"
                        v-show="showLabels&&part.show&&part.visible"
                        :key="`label-${part.id}`"
                        type="button"
                        class="part-label"
                        :class="{active:selectedPart?.id===part.id}"
                        :style="{
                            left:`${part.labelX}px`,
                            top:`${part.labelY}px`,
                            '--part-color':part.color||selectedRobot.ThemeColor
                        }"
                        @click.stop="selectPart(part)"
                    >
                        <span class="part-label-dot"></span>
                        {{part.title}}
                    </button>

                    <Transition name="detail-panel">
                        <aside
                            v-if="selectedPart&&!modelLoading&&!modelLoadError"
                            class="part-detail"
                        >
                            <button
                                class="detail-close"
                                type="button"
                                @click="selectedPart=null"
                            >
                                ×
                            </button>

                            <p class="part-detail-index">
                                {{selectedPart.category||'COMPONENT'}}
                            </p>

                            <h2>{{selectedPart.title}}</h2>

                            <p
                                v-if="selectedPart.subtitle"
                                class="part-detail-subtitle"
                            >
                                {{selectedPart.subtitle}}
                            </p>

                            <div
                                v-if="selectedPart.image"
                                class="part-detail-image"
                            >
                                <img
                                    :src="selectedPart.image"
                                    :alt="selectedPart.title"
                                >
                            </div>

                            <p class="part-detail-description">
                                {{selectedPart.description}}
                            </p>

                            <div
                                v-if="selectedPart.details?.length"
                                class="part-detail-items"
                            >
                                <div
                                    v-for="item in selectedPart.details"
                                    :key="item.title"
                                    class="part-detail-item"
                                >
                                    <span>{{item.title}}</span>
                                    <p>{{item.content}}</p>
                                </div>
                            </div>

                            <button
                                class="focus-button"
                                type="button"
                                @click="focusPart(selectedPart)"
                            >
                                FOCUS COMPONENT
                            </button>
                        </aside>
                    </Transition>

                    <Transition name="model-loader">
                        <div
                            v-if="modelLoading||modelLoadError"
                            class="model-loading"
                            role="status"
                            aria-live="polite"
                        >
                            <template v-if="modelLoading">
                                <div
                                    class="model-loading-spinner"
                                    aria-hidden="true"
                                >
                                    <span class="model-loading-spinner-core"></span>
                                </div>

                                <p class="model-loading-title">
                                    LOADING 3D MODEL
                                </p>

                                <div
                                    class="model-loading-progress"
                                    aria-hidden="true"
                                >
                                    <span
                                        class="model-loading-progress-value"
                                        :class="{'is-estimated':modelProgressIsEstimated}"
                                        :style="{width:`${modelProgress}%`}"
                                    ></span>
                                </div>

                                <p class="model-loading-percent">
                                    {{modelProgressIsEstimated?`約 ${modelProgress}%`:`${modelProgress}%`}}
                                </p>
                            </template>

                            <template v-else>
                                <p class="model-loading-title">
                                    {{modelFileMissing?'3D MODEL NOT AVAILABLE':'LOAD FAILED'}}
                                </p>

                                <p class="model-loading-error">
                                    {{modelLoadError}}
                                </p>

                                <button
                                    v-if="!modelFileMissing"
                                    class="model-loading-retry"
                                    type="button"
                                    @click="loadModel"
                                >
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
.robot-modal{
    position:fixed;
    inset:0;
    z-index:9999;
    display:flex;
    align-items:center;
    justify-content:center;
    padding:120px 40px 40px;
    backdrop-filter:blur(14px);
}

.modal-container{
    position:relative;
    width:min(1500px,100%);
    height:85vh;
    background:#0a0a0a;
    border:1px solid rgba(255,255,255,.15);
    z-index:100;
}

.close-button{
    position:absolute;
    top:0;
    right:0;
    z-index:20;
    width:44px;
    height:44px;
    border:1px solid rgba(255,255,255,.25);
    border-radius:50%;
    background:#333;
    color:#fff;
    font-size:28px;
    cursor:pointer;
    transform:translate(50%,-50%);
}

.viewer{
    position:relative;
    width:100%;
    height:100%;
}

.robot-viewer{
    position:relative;
    width:100%;
    height:100%;
    border:5px solid #c6c6c6;
    border-radius:5px;
    overflow:hidden;
    cursor:grab;
}

.robot-viewer:active{
    cursor:grabbing;
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
    background:radial-gradient(
        circle at center,
        rgba(20,20,20,.45) 10%,
        rgba(20,20,20,.70) 55%,
        rgba(15,15,15,.95) 100%
    );
    z-index:1;
    pointer-events:none;
}

.robot-viewer :deep(canvas){
    position:relative;
    z-index:2;
}

.viewer-info{
    position:absolute;
    left:5%;
    top:5%;
    width:90%;
    z-index:3;
    text-align:var(--pos);
    pointer-events:none;
    font-family:'Orbitron',sans-serif;
    font-size:clamp(28px,4vw,60px);
    letter-spacing:.08em;
    text-shadow:0 3px 4px #000;
    font-weight:900;
}

.guide-control{
    position:absolute;
    top:50%;
    left:20px;
    z-index:10;
    width:240px;
    max-height:70%;
    padding:18px;
    border:1px solid rgba(255,255,255,.18);
    background:rgba(12,12,16,.82);
    color:#fff;
    transform:translateY(-50%);
    backdrop-filter:blur(12px);
}

.guide-control-header{
    display:flex;
    align-items:center;
    justify-content:space-between;
    margin-bottom:16px;
    font-family:'Orbitron',sans-serif;
    font-size:14px;
    font-weight:800;
    letter-spacing:.14em;
}

.panel-collapse{
    border:0;
    background:transparent;
    color:#fff;
    font-size:24px;
    cursor:pointer;
}

.guide-master-switch{
    display:flex;
    align-items:center;
    gap:10px;
    margin-bottom:14px;
    padding-bottom:14px;
    border-bottom:1px solid rgba(255,255,255,.12);
    font-size:13px;
    cursor:pointer;
}

.guide-buttons{
    display:flex;
    flex-direction:column;
    gap:4px;
    max-height:330px;
    overflow:auto;
}

.guide-part-row{
    display:grid;
    grid-template-columns:24px 1fr;
    align-items:center;
    transition:.2s;
}

.guide-part-row input{
    margin:0;
}

.guide-part-row button{
    padding:9px 8px;
    border:0;
    background:transparent;
    color:rgba(255,255,255,.7);
    text-align:left;
    cursor:pointer;
}

.guide-part-row.active button{
    color:#fff;
    font-weight:700;
}

.guide-part-row.missing{
    opacity:.35;
}

.guide-part-row button:disabled{
    cursor:not-allowed;
}

.guide-control-actions{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:6px;
    margin-top:14px;
}

.guide-control-actions button{
    padding:7px;
    border:1px solid rgba(255,255,255,.18);
    background:transparent;
    color:#fff;
    font-size:11px;
    cursor:pointer;
}

.guide-control-actions button:last-child{
    grid-column:1/-1;
}

.open-control-panel{
    position:absolute;
    left:0;
    top:50%;
    z-index:10;
    width:36px;
    height:70px;
    border:1px solid rgba(255,255,255,.2);
    border-left:0;
    background:rgba(10,10,12,.85);
    color:#fff;
    font-size:25px;
    cursor:pointer;
    transform:translateY(-50%);
}

.guide-lines{
    position:absolute;
    inset:0;
    width:100%;
    height:100%;
    z-index:5;
    pointer-events:none;
}

.guide-lines line{
    stroke:rgba(255,255,255,.85);
    stroke-width:1.5;
}

.guide-lines path{
    fill:rgba(255,255,255,.9);
}

.part-label{
    position:absolute;
    z-index:7;
    display:flex;
    align-items:center;
    gap:8px;
    padding:8px 13px;
    border:1px solid rgba(255,255,255,.28);
    background:rgba(10,10,13,.82);
    color:#fff;
    font-family:'Orbitron',sans-serif;
    font-size:11px;
    font-weight:700;
    letter-spacing:.07em;
    cursor:pointer;
    transform:translate(-50%,-50%);
    white-space:nowrap;
    backdrop-filter:blur(6px);
    transition:border-color .2s,background .2s,transform .2s;
}

.part-label:hover,
.part-label.active{
    border-color:var(--part-color);
    background:rgba(20,20,24,.95);
    transform:translate(-50%,-50%) scale(1.05);
}

.part-label-dot{
    width:7px;
    height:7px;
    border-radius:50%;
    background:var(--part-color);
    box-shadow:0 0 10px var(--part-color);
}

.part-detail{
    position:absolute;
    top:0;
    right:0;
    z-index:12;
    width:min(380px,32%);
    height:100%;
    padding:70px 32px 32px;
    overflow:auto;
    border-left:1px solid rgba(255,255,255,.15);
    background:rgba(8,8,11,.93);
    color:#fff;
    cursor:auto;
    backdrop-filter:blur(15px);
}

.detail-close{
    position:absolute;
    top:20px;
    right:20px;
    width:34px;
    height:34px;
    border:1px solid rgba(255,255,255,.2);
    border-radius:50%;
    background:transparent;
    color:#fff;
    font-size:20px;
    cursor:pointer;
}

.part-detail-index{
    margin:0 0 8px;
    color:rgba(255,255,255,.4);
    font-family:'Orbitron',sans-serif;
    font-size:10px;
    letter-spacing:.2em;
    text-transform:uppercase;
}

.part-detail h2{
    margin:0;
    font-family:'Orbitron',sans-serif;
    font-size:30px;
    line-height:1.1;
}

.part-detail-subtitle{
    margin:10px 0 0;
    color:rgba(255,255,255,.55);
}

.part-detail-image{
    width:100%;
    margin-top:24px;
    overflow:hidden;
}

.part-detail-image img{
    display:block;
    width:100%;
    aspect-ratio:16/9;
    object-fit:cover;
}

.part-detail-description{
    margin-top:24px;
    color:rgba(255,255,255,.72);
    line-height:1.8;
}

.part-detail-items{
    margin-top:24px;
    border-top:1px solid rgba(255,255,255,.12);
}

.part-detail-item{
    padding:16px 0;
    border-bottom:1px solid rgba(255,255,255,.12);
}

.part-detail-item span{
    display:block;
    margin-bottom:5px;
    color:rgba(255,255,255,.4);
    font-size:11px;
    letter-spacing:.1em;
}

.part-detail-item p{
    margin:0;
    line-height:1.6;
}

.focus-button{
    width:100%;
    margin-top:24px;
    padding:12px;
    border:1px solid rgba(255,255,255,.3);
    background:transparent;
    color:#fff;
    font-family:'Orbitron',sans-serif;
    font-size:11px;
    letter-spacing:.1em;
    cursor:pointer;
}

.model-loading{
    position:absolute;
    z-index:30;
    inset:0;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    padding:30px;
    background:rgba(8,9,14,.72);
    color:#fff;
    text-align:center;
    backdrop-filter:blur(8px);
    -webkit-backdrop-filter:blur(8px);
}

.model-loading-spinner{
    position:relative;
    width:76px;
    height:76px;
    margin-bottom:24px;
    border:2px solid rgba(255,255,255,.16);
    border-top-color:currentColor;
    border-radius:50%;
    animation:model-loading-spin 1s linear infinite;
}

.model-loading-spinner::after{
    content:'';
    position:absolute;
    inset:8px;
    border:1px solid rgba(255,255,255,.28);
    border-right-color:transparent;
    border-radius:50%;
    animation:model-loading-spin 1.6s linear infinite reverse;
}

.model-loading-spinner-core{
    position:absolute;
    top:50%;
    left:50%;
    width:10px;
    height:10px;
    border-radius:50%;
    background:currentColor;
    box-shadow:0 0 22px rgba(255,255,255,.75);
    transform:translate(-50%,-50%);
}

.model-loading-title,
.model-loading-percent,
.model-loading-error{
    margin:0;
}

.model-loading-title{
    font-family:'Orbitron',sans-serif;
    font-size:clamp(14px,1.5vw,20px);
    font-weight:800;
    letter-spacing:.18em;
}

.model-loading-progress{
    width:min(280px,70%);
    height:3px;
    margin-top:20px;
    overflow:hidden;
    background:rgba(255,255,255,.18);
}

.model-loading-progress-value{
    display:block;
    height:100%;
    background:currentColor;
}

.model-loading-progress-value.is-estimated{
    transition:width 180ms ease;
}

.model-loading-percent,
.model-loading-error{
    margin-top:12px;
    color:rgba(255,255,255,.68);
    font-size:12px;
    letter-spacing:.12em;
}

.model-loading-retry{
    margin-top:22px;
    padding:10px 18px;
    border:1px solid rgba(255,255,255,.45);
    background:transparent;
    color:#fff;
    cursor:pointer;
}

.model-loader-enter-active,
.model-loader-leave-active{
    transition:opacity 300ms ease;
}

.model-loader-enter-from,
.model-loader-leave-to{
    opacity:0;
}

.detail-panel-enter-active,
.detail-panel-leave-active{
    transition:transform .3s ease,opacity .3s ease;
}

.detail-panel-enter-from,
.detail-panel-leave-to{
    opacity:0;
    transform:translateX(100%);
}

@keyframes model-loading-spin{
    to{
        transform:rotate(360deg);
    }
}

@media(max-width:900px){
    .robot-modal{
        padding:80px 15px 20px;
    }

    .modal-container{
        height:88vh;
    }

    .guide-control{
        width:190px;
        left:10px;
    }

    .part-detail{
        top:auto;
        bottom:0;
        width:100%;
        height:45%;
        padding:50px 22px 22px;
        border-top:1px solid rgba(255,255,255,.15);
        border-left:0;
    }

    .part-label{
        font-size:9px;
        padding:6px 9px;
    }
}
</style>ＦＦＦ
