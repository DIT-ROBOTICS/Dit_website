<!--
介紹指導人員：
有兩個教授和俊峰和其他學長之類的介紹
-->
<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import MemberCard from '@/components/template/MemberCard.vue'
import{RotateCw,ArrowRight,ArrowLeft,ArrowUpRight,X,Plus,ArrowUp}from'lucide-vue-next'

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
    <section id="advisors" class="members-section">
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

        <div v-else class="member-scroll-wrapper">
            <div class="member-scroll">
                <MemberCard v-for="advisor in advisors" :key="advisor.id" :info="advisor" color='black' :type="'advisor'" />

                <article class="people-card view-team-card" @click="openTeam">
                    <div class="view-team-content">
                        <div class="view-team-arrow"><ArrowRight/></div>

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

<style scoped src="@/styles/member-scroller.css"></style>
<style scoped>
.members-section {
    background: #535252;
    color: rgb(223, 223, 223);
}


.eyebrow {
    color: rgba(214, 214, 214, 0.45);
}

.view-team-card {
    min-height: 530px;
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

</style>