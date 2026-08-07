<!--
介紹指導人員：
有兩個教授和俊峰和其他學長之類的介紹
-->
<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const advisors = ref([])
const loading = ref(true)
const errorMessage = ref('')

async function loadAdvisors() {
    try {
        const response = await fetch('/api/member_info/Advisor')

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`)
        }

        advisors.value = await response.json()
    } catch (error) {
        console.error(error)
        errorMessage.value = '指導教授資料載入失敗'
    } finally {
        loading.value = false
    }
}

function openAdvisor(advisor) {
    if (!advisor?.id) return

    router.push(`/advisor/${advisor.id}`)
}

function openTeam() {
    router.push('/team')
}

onMounted(loadAdvisors)
</script>

<template>
    <section id="advisors" class="advisors-section">
        <div class="section-heading">
            <div>
                <p class="eyebrow">OUR MENTORS</p>
                <h2>指導教授</h2>
            </div>

            <p class="section-description">
                在每一次嘗試與失敗背後，都有老師們給予我們方向、經驗與持續前進的勇氣。
            </p>
        </div>

        <div v-if="loading" class="state-message">載入指導教授資料中……</div>

        <div v-else-if="errorMessage" class="state-message error">{{ errorMessage }}</div>

        <div v-else class="advisor-scroll-wrapper">
            <div class="advisor-scroll">
                <article v-for="advisor in advisors" :key="advisor.id" class="advisor-card"
                    @click="openAdvisor(advisor)">
                    <div class="advisor-photo">
                        <img :src="`/api/member_images/advisor-image/${advisor.id}`" :alt="advisor.name">
                        <div class="photo-overlay"></div>

                        <div class="advisor-index">
                            {{ String(advisor.id).padStart(2, '0') }}
                        </div>
                    </div>

                    <div class="advisor-info">
                        <p class="advisor-position">{{ advisor.position }}</p>

                        <h3>{{ advisor.name }}</h3>

                        <p v-if="advisor.department" class="advisor-department">{{ advisor.department }}</p>

                        <p v-if="advisor.description" class="advisor-description">{{ advisor.description }}</p>

                        <div v-if="advisor.research?.length" class="research-tags">
                            <span v-for="item in advisor.research" :key="item">{{ item }}</span>
                        </div>

                        <button class="profile-link" type="button" @click.stop="openAdvisor(advisor)">
                            View Profile
                            <span>↗</span>
                        </button>
                    </div>
                </article>

                <article class="advisor-card view-team-card" @click="openTeam">
                    <div class="view-team-content">
                        <div class="view-team-arrow">→</div>

                        <div>
                            <p>BEHIND THE ROBOTS</p>

                            <h3>
                                其他頂級<br>
                                學長姐們
                            </h3>
                        </div>

                        <div class="view-team-footer">
                            Meet the people behind DIT Robotics
                        </div>
                    </div>
                </article>
            </div>

        </div>
    </section>
</template>

<style scoped>
.advisors-section {
    position: relative;
    padding: 120px 0 100px;
    overflow: hidden;
    background: #585858;
    color: rgb(223, 223, 223);
}

.section-heading {
    max-width: 1400px;
    margin: 0 auto 64px;
    padding: 0 8vw;
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(280px, 420px);
    gap: 60px;
    align-items: end;
}

.eyebrow {
    margin: 0 0 14px;
    color: rgba(214, 214, 214, 0.45);
    font-size: 12px;
    font-weight: 600;
    letter-spacing: .24em;
}

.section-heading h2 {
    margin: 0;
    font-size: clamp(42px, 6vw, 78px);
    line-height: 1.05;
    letter-spacing: -.04em;
}

.section-description {
    margin: 0;
    color: rgba(255, 255, 255, .56);
    font-size: 16px;
    line-height: 1.9;
}

.state-message {
    padding: 70px 8vw;
    color: rgba(255, 255, 255, .5);
}

.state-message.error {
    color: #ff8d8d;
}

.advisor-scroll-wrapper {
    width: 100%;
    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
}

.advisor-scroll-wrapper::-webkit-scrollbar {
    display: none;
}

.advisor-scroll {
    display: flex;
    width: max-content;
    gap: 28px;
    padding: 12px 8vw 38px;
    scroll-snap-type: x mandatory;
    scroll-behavior: smooth;
}

.advisor-card {
    flex: 0 0 clamp(300px, 29vw, 390px);
    scroll-snap-align: start;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, .08);
    border-radius: 28px;
    background: #191c22;
    cursor: pointer;

    display: flex;
    flex-direction: column;

    transition: transform .35s cubic-bezier(.2, .7, .2, 1), border-color .35s ease, box-shadow .35s ease;
}

.advisor-card:hover {
    transform: translateY(-10px);
    border-color: rgba(255, 255, 255, .18);
    box-shadow: 0 10px 20px rgba(0, 0, 0, .28);
}

.advisor-photo {
    position: relative;
    aspect-ratio: 4 / 5;
    overflow: hidden;
    background: #20242b;
}

.advisor-photo img {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: cover;
    filter: saturate(.9);
    transition: transform .7s cubic-bezier(.2, .7, .2, 1), filter .35s ease;
}

.advisor-card:hover .advisor-photo img {
    transform: scale(1.055);
    filter: saturate(1);
}

.photo-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0, 0, 0, .42), transparent 45%);
}

.advisor-index {
    position: absolute;
    right: 18px;
    bottom: 16px;
    color: rgba(255, 255, 255, .75);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .16em;
}

.advisor-info {
    padding: 27px 27px 30px;

    display: flex;
    flex-direction: column;
    flex: 1;
}

.advisor-position {
    margin: 0 0 9px;
    color: rgba(255, 255, 255, .42);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .17em;
    text-transform: uppercase;
}

.advisor-info h3 {
    margin: 0;
    font-size: 30px;
    line-height: 1.15;
    letter-spacing: -.025em;
}

.advisor-department {
    margin: 8px 0 0;
    color: rgba(255, 255, 255, .55);
    font-size: 13px;
}

.advisor-description {
    margin: 17px 0 0;
    color: rgba(255, 255, 255, .58);
    font-size: 14px;
    line-height: 1.75;
}

.research-tags {
    margin-top: auto;
    display: inline-flex;
    flex-wrap: wrap;
    align-self: flex-start;
    gap: 7px;
}

.research-tags span {
    padding: 7px 10px;
    border: 1px solid rgba(255, 255, 255, .12);
    border-radius: 999px;
    color: rgba(255, 255, 255, .68);
    background: rgba(255, 255, 255, .035);
    font-size: 11px;
}

.profile-link {
    padding-top: 24px;
    border: none;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    align-self: flex-start;
    background: transparent;
    color: white;
    font: inherit;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
}

.profile-link span {
    display: inline-block;
    transition: transform .2s ease;
}

.profile-link:hover span {
    transform: translate(3px, -3px);
}

.view-team-card {
    min-height: 560px;
    background: #f4f3ef;
    color: #111318;
}

.view-team-content {
    width: 100%;
    min-height: 100%;
    padding: 32px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.view-team-arrow {
    align-self: flex-end;
    width: 54px;
    height: 54px;
    display: grid;
    place-items: center;
    border: 1px solid rgba(0, 0, 0, .18);
    border-radius: 50%;
    font-size: 25px;
    transition: transform .3s ease, background .3s ease, color .3s ease;
}

.view-team-card:hover .view-team-arrow {
    transform: translateX(6px);
    background: #111318;
    color: white;
}

.view-team-content p {
    margin: 0 0 12px;
    color: rgba(0, 0, 0, .42);
    font-size: 11px;
    letter-spacing: .2em;
}

.view-team-content h3 {
    margin: 0;
    font-size: clamp(34px, 4vw, 48px);
    line-height: 1.08;
    letter-spacing: -.04em;
}

.view-team-footer {
    color: rgba(0, 0, 0, .48);
    font-size: 12px;
    letter-spacing: .06em;
}

.scroll-hint {
    padding: 4px 8vw 0;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
    color: rgba(255, 255, 255, .35);
    font-size: 10px;
    letter-spacing: .14em;
    text-transform: uppercase;
}

.scroll-line {
    width: 60px;
    height: 1px;
    background: rgba(255, 255, 255, .22);
}

@media (max-width: 900px) {
    .advisors-section {
        padding: 90px 0 75px;
    }

    .section-heading {
        padding: 0 24px;
        grid-template-columns: 1fr;
        gap: 24px;
        margin-bottom: 45px;
    }

    .advisor-scroll {
        padding-left: 24px;
        padding-right: 24px;
    }

    .advisor-card {
        flex-basis: min(82vw, 350px);
    }

    .scroll-hint {
        padding-left: 24px;
        padding-right: 24px;
    }
}

@media (max-width: 520px) {
    .section-heading {
        padding-left: 18px;
        padding-right: 18px;
    }

    .advisor-scroll {
        padding-left: 18px;
        padding-right: 18px;
    }

    .section-heading h2 {
        font-size: 42px;
    }

    .advisor-card {
        border-radius: 22px;
    }

    .advisor-info {
        padding: 22px;
    }
}
</style>