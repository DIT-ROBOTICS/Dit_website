<script setup>
import { onMounted, ref } from 'vue'
import { ArrowUp, ArrowUpRight, RotateCw } from 'lucide-vue-next'
import FilePreviewModal from '@/components/template/FilePreviewModal.vue'

// 聯絡方式、其他連結與載入錯誤狀態。
const contacts = ref([])
const linkGroups = ref([])
const errorMessage = ref('')

// 從後端取得聯絡資料與分類連結。
async function loadLinks() {
    errorMessage.value = ''

    try {
        const response = await fetch('/api/jsonData/Links')

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
        }

        const linkData = await response.json()
        contacts.value = linkData.contacts
        linkGroups.value = linkData.linkGroups
    } catch (error) {
        console.error(error)
        errorMessage.value = '連結資料載入失敗'
    }
}

// Footer 版權文字使用的當前年份。
const currentYear = new Date().getFullYear()

// 平滑捲動回頁面頂端。
function backToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth',
    })
}

// 元件掛載後載入聯絡資料。
onMounted(loadLinks)
</script>

<template>
    <!-- 聯絡資訊與網站 Footer 區塊。 -->
    <section id="contact" class="contact-section">
        <!-- 主要聯絡內容。 -->
        <div class="contact-main">
            <!-- 左側行動號召與贊助入口。 -->
            <div class="contact-heading">
                <!-- 英文小標。 -->
                <p class="eyebrow">CONTACT US</p>

                <!-- 聯絡區塊主標題。 -->
                <iframe width="560" height="315"
                    src="https://www.youtube.com/embed/Dh_jmZ1kZ28?si=wVV3VIwE9Su_pLn5&amp;controls=0"
                    title="YouTube video player" frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

                <!-- 聯絡說明。 -->
                <p class="contact-description">
                    無論是技術交流、競賽合作、贊助或加入團隊， 都歡迎與 DIT Robotics 聯絡。
                </p>

                <!-- 開啟贊助方法的檔案預覽視窗。 -->
                <FilePreviewModal api="/api/PopUpItem/SponsorshipMethods" title="贊助方法">
                    <button class="contact-button" type="button">
                        SUPPORT US
                        <span class="contact-button-icon">
                            <ArrowUpRight />
                        </span>
                    </button>
                </FilePreviewModal>
            </div>

            <!-- 右側聯絡方式與其他連結。 -->
            <div class="contact-list">
                <!-- 資料載入失敗狀態。 -->
                <div v-if="errorMessage" class="contact-error">
                    <p class="contact-error-title">CONNECTION ERROR</p>
                    <p class="contact-error-message">{{ errorMessage }}</p>

                    <!-- 重新載入聯絡資料。 -->
                    <button class="retry-button" type="button" @click="loadLinks">
                        RETRY
                        <span class="retry-button-icon">
                            <RotateCw />
                        </span>
                    </button>
                </div>

                <!-- 資料載入成功後的聯絡內容。 -->
                <template v-else>
                    <!-- 單筆聯絡方式。 -->
                    <a v-for="contact in contacts" :key="contact.label" :href="contact.href" target="_blank"
                        rel="noopener noreferrer" class="contact-item">
                        <div class="contact-item-content">
                            <p class="contact-label">{{ contact.label }}</p>
                            <p class="contact-value">{{ contact.value }}</p>
                        </div>

                        <span class="contact-arrow">
                            <ArrowUpRight />
                        </span>
                    </a>

                    <!-- 依分類顯示的其他外部連結。 -->
                    <div class="more-links">
                        <p class="more-links-title">MORE LINKS</p>

                        <div class="link-groups">
                            <!-- 單一連結分類。 -->
                            <div v-for="group in linkGroups" :key="group.title" class="link-group">
                                <p class="link-group-title">{{ group.title }}</p>

                                <!-- 分類中的單一外部連結。 -->
                                <a v-for="link in group.links" :key="link.label" :href="link.href" target="_blank"
                                    rel="noopener noreferrer" class="small-link">
                                    <img v-if="link.icon" class="small-link-icon" :src="link.icon"
                                        :alt="`${link.label} icon`" />
                                    {{ link.label }}
                                    <span class="small-link-arrow">
                                        <ArrowUpRight />
                                    </span>
                                </a>
                            </div>
                        </div>
                    </div>
                </template>
            </div>
        </div>

        <!-- 品牌、版權與回到頂端連結。 -->
        <footer class="contact-footer">
            <!-- DIT 品牌資訊。 -->
            <div class="brand">
                <span class="brand-mark">DIT</span>

                <div class="brand-copy">
                    <p class="brand-name">DIT ROBOTICS</p>
                    <span class="brand-tagline">Do · Improve · Try</span>
                </div>
            </div>

            <!-- 學系識別與當前年份版權聲明。 -->
            <div class="footer-legal">
                <p class="department-label">國立清華大學動力機械工程學系</p>
                <p class="copyright">© {{ currentYear }} DIT Robotics. All rights reserved.</p>
            </div>

            <!-- 平滑捲動回頁面頂端。 -->
            <a class="back-top" href="#" @click.prevent="backToTop">
                BACK TO TOP
                <ArrowUp />
            </a>
        </footer>
    </section>
</template>

<style scoped>
.contact-section {
    position: relative;
    background: #0a0a0a;
    color: white;
    padding: 80px 7vw 40px;
    overflow: hidden;
}

.contact-section::before,
.contact-section::after {
    content: '';
    position: absolute;
    border-radius: 50%;
}

/* 背景裝飾圓形。 */
.contact-section::before {
    width: 600px;
    height: 600px;
    right: -220px;
    top: -200px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.contact-section::after {
    width: 350px;
    height: 350px;
    right: -80px;
    top: -70px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.contact-main {
    position: relative;
    z-index: 1;

    display: grid;
    grid-template-columns: 1.15fr 1fr;
    gap: 100px;

    max-width: 1500px;
    margin: 0 auto 50px;
}

.eyebrow {
    margin: 0 0 24px;

    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.22em;

    color: rgba(255, 255, 255, 0.45);
}

.contact-title {
    margin: 0;

    font-size: clamp(48px, 6vw, 100px);
    line-height: 0.92;
    letter-spacing: -0.045em;
    font-weight: 700;
}

.contact-description {
    /* max-width: 600px; */
    margin: 36px 0 0;

    color: rgba(255, 255, 255, 0.58);
    font-size: 16px;
    line-height: 1.9;
}

.contact-button {
    display: inline-flex;
    align-items: center;
    justify-content: space-between;
    gap: 70px;

    margin-top: 46px;
    padding: 18px 22px;

    min-width: 220px;

    color: #0a0a0a;
    background: white;

    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.12em;

    transition:
        background 0.3s ease,
        color 0.3s ease,
        transform 0.3s ease;
}

.contact-button:hover {
    background: transparent;
    color: white;

    outline: 1px solid rgba(255, 255, 255, 0.5);
    transform: translateY(-3px);
}

/* 右側聯絡資料 */

.contact-list {
    align-self: end;
}

.contact-item {
    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 14px 4px;

    border-top: 1px solid rgba(255, 255, 255, 0.14);

    color: white;
    text-decoration: none;
    gap: 10px;
    transition:
        padding 0.3s ease,
        border-color 0.3s ease;
}

.contact-item:last-of-type {
    border-bottom: 1px solid rgba(255, 255, 255, 0.14);
}

.contact-item:hover {
    padding-left: 14px;
    padding-right: 14px;
    border-color: rgba(255, 255, 255, 0.5);
}

.contact-label {
    margin: 0 0 9px;

    color: rgba(255, 255, 255, 0.4);

    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.18em;
}

.contact-value {
    margin: 0;

    font-size: clamp(16px, 1.5vw, 22px);
    letter-spacing: -0.02em;
}

.contact-arrow {
    color: rgba(255, 255, 255, 0.45);
    font-size: 20px;

    transition:
        color 0.25s ease,
        transform 0.25s ease;
}

.contact-item:hover .contact-arrow {
    color: white;
    transform: translate(3px, -3px);
}

/* footer */

.contact-footer {
    position: relative;
    z-index: 1;

    max-width: 1500px;
    margin: 0 auto;

    padding-top: 34px;

    border-top: 1px solid rgba(255, 255, 255, 0.12);

    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 30px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.brand-mark {
    display: flex;
    align-items: center;
    justify-content: center;

    width: 46px;
    height: 46px;

    border: 1px solid rgba(255, 255, 255, 0.3);

    font-weight: 700;
    letter-spacing: 0.05em;
}

.brand-name {
    margin: 0 0 4px;

    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.08em;
}

.brand-tagline {
    color: rgba(255, 255, 255, 0.4);
    font-size: 11px;
}

.footer-legal {
    text-align: center;
}

.department-label,
.copyright {
    margin: 0;
}

.department-label {
    margin-bottom: 7px;

    color: rgba(255, 255, 255, 0.65);
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.12em;
}

.copyright {
    color: rgba(255, 255, 255, 0.35);
    font-size: 11px;
}

.back-top {
    justify-self: end;

    color: rgba(255, 255, 255, 0.55);

    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.12em;

    text-decoration: none;

    transition: color 0.25s ease;
}

.back-top:hover {
    color: white;
}

/* RWD */

@media (max-width: 900px) {
    .contact-section {
        padding: 100px 24px 30px;
    }

    .contact-main {
        grid-template-columns: 1fr;
        gap: 80px;
        margin-bottom: 100px;
    }

    .contact-title {
        font-size: clamp(50px, 13vw, 80px);
    }

    .contact-list {
        width: 100%;
    }

    .contact-footer {
        grid-template-columns: 1fr;
        gap: 24px;
    }

    .footer-legal {
        order: 3;
        text-align: left;
    }

    .back-top {
        justify-self: start;
    }
}

@media (max-width: 520px) {
    .contact-section {
        padding-top: 80px;
    }

    .contact-title {
        font-size: 46px;
    }

    .contact-description {
        font-size: 14px;
    }

    .contact-button {
        width: 100%;
    }

    .contact-item {
        padding: 22px 2px;
    }
}

.more-links {
    margin-top: 48px;
}

.more-links-title {
    margin: 0 0 26px;

    color: rgba(255, 255, 255, 0.32);

    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.2em;
}

.link-groups {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 32px;
}

.link-group {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

.small-link-icon {
    width: 12px;
    height: 12px;
    object-fit: contain;
    flex-shrink: 0;
}

.link-group-title {
    margin: 0 0 5px;

    color: rgba(255, 255, 255, 0.7);

    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.14em;
}

.small-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;

    margin: 2px 0;

    color: rgba(255, 255, 255, 0.38);

    font-size: 12px;
    line-height: 1.6;

    text-decoration: none;

    transition:
        color 0.2s ease,
        transform 0.2s ease;
}

.small-link-arrow {
    opacity: 0;

    font-size: 10px;

    transform: translate(-3px, 2px);

    transition:
        opacity 0.2s ease,
        transform 0.2s ease;
}

.small-link:hover {
    color: white;
    transform: translateX(3px);
}

.small-link:hover .small-link-arrow {
    opacity: 1;
    transform: translate(0, 0);
}

@media (max-width: 600px) {
    .link-groups {
        grid-template-columns: repeat(1, 1fr);
        gap: 28px 20px;
    }
}
</style>
