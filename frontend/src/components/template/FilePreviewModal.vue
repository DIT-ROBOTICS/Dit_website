<script setup>
import { nextTick, onUnmounted, ref } from 'vue'
import *as pdfjsLib from 'pdfjs-dist'
import pdfWorker from 'pdfjs-dist/build/pdf.worker.mjs?url'

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker

const props = defineProps({
    api: {
        type: String,
        required: true
    },
    title: {
        type: String,
        default: ''
    },
    mobileBreakpoint: {
        type: Number,
        default: 768
    }
})

const show = ref(false)
const loading = ref(false)
const error = ref('')
const fileType = ref('')
const pdfContainer = ref(null)
let pdfDocument = null

function isMobile() {
    return window.matchMedia(`(max-width:${props.mobileBreakpoint}px)`).matches
}

async function open() {
    if (isMobile()) {
        window.open(props.api, '_blank', 'noopener,noreferrer')
        return
    }

    show.value = true
    lockBody()
    await loadFileType()

    if (isPDF()) {
        await nextTick()
        await renderPDF()
    }
}

async function loadFileType() {
    loading.value = true
    error.value = ''

    try {
        const response = await fetch(props.api, {
            method: 'HEAD'
        })

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
        }

        fileType.value = response.headers.get('content-type')?.split(';')[0] || ''
    } catch (err) {
        console.error(err)

        try {
            const response = await fetch(props.api, {
                method: 'GET'
            })

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`)
            }

            fileType.value = response.headers.get('content-type')?.split(';')[0] || ''
        } catch (secondError) {
            console.error(secondError)
            error.value = '檔案載入失敗'
        }
    } finally {
        loading.value = false
    }
}

async function renderPDF() {
    if (!pdfContainer.value) return

    loading.value = true
    error.value = ''
    pdfContainer.value.innerHTML = ''

    try {
        const response = await fetch(props.api)

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
        }

        const buffer = await response.arrayBuffer()

        const loadingTask = pdfjsLib.getDocument({
            data: new Uint8Array(buffer)
        })

        pdfDocument = await loadingTask.promise

        for (let pageNumber = 1; pageNumber <= pdfDocument.numPages; pageNumber++) {
            const page = await pdfDocument.getPage(pageNumber)
            const baseViewport = page.getViewport({ scale: 1 })
            const availableWidth = pdfContainer.value.clientWidth
            const scale = availableWidth / baseViewport.width
            const viewport = page.getViewport({ scale })

            const canvas = document.createElement('canvas')
            const context = canvas.getContext('2d')
            const pixelRatio = window.devicePixelRatio || 1

            canvas.width = Math.floor(viewport.width * pixelRatio)
            canvas.height = Math.floor(viewport.height * pixelRatio)
            canvas.style.width = `${viewport.width}px`
            canvas.style.height = `${viewport.height}px`
            canvas.className = 'pdf-page'

            pdfContainer.value.appendChild(canvas)

            await page.render({
                canvasContext: context,
                viewport,
                transform: pixelRatio !== 1
                    ? [pixelRatio, 0, 0, pixelRatio, 0, 0]
                    : null
            }).promise
        }
    } catch (err) {
        console.error('PDF render error:', err)
        error.value = `PDF 載入失敗：${err.message}`
    } finally {
        loading.value = false
    }
}

function close() {
    show.value = false
    unlockBody()

    if (pdfContainer.value) {
        pdfContainer.value.innerHTML = ''
    }

    pdfDocument?.destroy()
    pdfDocument = null
}

function lockBody() {
    document.body.style.overflow = 'hidden'
}

function unlockBody() {
    document.body.style.overflow = ''
}

function isImage() {
    return fileType.value.startsWith('image/')
}

function isPDF() {
    return fileType.value === 'application/pdf'
}

function isHTML() {
    return fileType.value === 'text/html'
}

function isVideo() {
    return fileType.value.startsWith('video/')
}

function isAudio() {
    return fileType.value.startsWith('audio/')
}

function openNewTab() {
    window.open(props.api, '_blank', 'noopener,noreferrer')
}

function handleKeydown(event) {
    if (event.key === 'Escape' && show.value) {
        close()
    }
}

window.addEventListener('keydown', handleKeydown)

onUnmounted(() => {
    if (show.value) {
        unlockBody()
    }

    pdfDocument?.destroy()
    window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
    <div class="file-preview-trigger" @click="open">
        <slot />
    </div>

    <Teleport to="body">
        <Transition name="preview">
            <div v-if="show" class="preview-overlay" @click.self="close">
                <div class="preview-modal">
                    <header class="preview-header">
                        <div class="preview-actions">
                            <button type="button" class="action-button close-button" @click="close">
                                ×
                            </button>

                            <button type="button" class="action-button" @click="openNewTab">
                                ↗
                            </button>
                        </div>

                        <div class="preview-title">
                            {{ title }}
                        </div>
                    </header>

                    <main class="preview-content">
                        <div v-if="loading && !isPDF()" class="preview-state">
                            Loading...
                        </div>

                        <div v-else-if="error" class="preview-state error">
                            {{ error }}

                            <button type="button" class="open-button" @click="openNewTab">
                                直接開啟檔案
                            </button>
                        </div>

                        <div v-else-if="isPDF()" ref="pdfContainer" class="pdf-container" />

                        <img v-else-if="isImage()" :src="api" class="preview-image">

                        <iframe v-else-if="isHTML()" :src="api" class="preview-frame" />

                        <video v-else-if="isVideo()" :src="api" class="preview-video" controls />

                        <audio v-else-if="isAudio()" :src="api" class="preview-audio" controls />

                        <div v-else class="preview-state">
                            此檔案格式無法直接預覽

                            <button type="button" class="open-button" @click="openNewTab">
                                開啟檔案
                            </button>
                        </div>
                    </main>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<style scoped>
.file-preview-trigger {
    display: contents;
}

.preview-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100dvh;
    z-index: 9999;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    background: rgba(0, 0, 0, .72);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
}

.preview-modal {
    display: flex;
    flex-direction: column;
    width: min(1200px, 95vw);
    height: min(850px, 95dvh);
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, .12);
    border-radius: 20px;
    background: #161616;
    box-shadow: 0 30px 100px rgba(0, 0, 0, .65);
}

.preview-header {
    position: relative;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    height: max(42px, 5%);
    box-sizing: border-box;
    padding: 0 15px;
    border-bottom: 1px solid rgba(255, 255, 255, .1);
    background: #1b1b1b;
    color: #fff;
}

.preview-title {
    position: absolute;
    left: 50%;
    max-width: 60%;
    overflow: hidden;
    transform: translateX(-50%);
    color: rgba(255, 255, 255, .88);
    font-size: 16px;
    font-weight: 600;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.preview-actions {
    display: flex;
    align-items: center;
    gap: 5px;
    height: 100%;
}

.action-button {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    height: 80%;
    aspect-ratio: 1;
    padding: 0;
    border: 0;
    border-radius: 50%;
    background: transparent;
    color: rgba(255, 255, 255, .8);
    font-size: 22px;
    cursor: pointer;
    transition: .2s;
}

.action-button:hover {
    color: #fff;
    transform: scale(1.4);
}

.close-button {
    font-size: 28px;
}

.preview-content {
    position: relative;
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
    overscroll-behavior: contain;
    background: #242424;
}

.pdf-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 24px;
    width: 100%;
    min-height: 100%;
    padding: 28px;
    box-sizing: border-box;
    background: #242424;
}

.pdf-container :deep(.pdf-page) {
    display: block;
    max-width: 100%;
    height: auto !important;
    background: #fff;
    box-shadow: 0 4px 24px rgba(0, 0, 0, .45);
}

.preview-frame {
    display: block;
    width: 100%;
    height: 100%;
    min-height: 70vh;
    border: 0;
    background: #fff;
}

.preview-image {
    display: block;
    max-width: 100%;
    height: auto;
    margin: auto;
}

.preview-video {
    display: block;
    max-width: 100%;
    max-height: 100%;
    margin: auto;
}

.preview-audio {
    display: block;
    width: min(600px, 90%);
    margin: 80px auto;
}

.preview-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 20px;
    min-height: 100%;
    padding: 40px;
    box-sizing: border-box;
    color: rgba(255, 255, 255, .75);
    text-align: center;
}

.error {
    color: #ff7777;
}

.open-button {
    padding: 10px 18px;
    border: 1px solid rgba(255, 255, 255, .2);
    border-radius: 8px;
    background: rgba(255, 255, 255, .1);
    color: #fff;
    cursor: pointer;
}

.preview-enter-active,
.preview-leave-active {
    transition: opacity .2s;
}

.preview-enter-from,
.preview-leave-to {
    opacity: 0;
}

.preview-enter-active .preview-modal,
.preview-leave-active .preview-modal {
    transition: transform .2s;
}

.preview-enter-from .preview-modal,
.preview-leave-to .preview-modal {
    transform: translateY(15px) scale(.98);
}
</style>
