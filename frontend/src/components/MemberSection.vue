<!--
團隊成員介紹：
在教授下面一區
在首頁只顯示當下的幹部
是橫向捲動的形式
捲動的後面有一個查看完整團隊的連結
打開後的網站有1-14(最新)的團員的資訊和技術路線之類的
-->
<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import MemberCard from '@/components/template/MemberCard.vue'

const router = useRouter()

const members = ref([])
const loading = ref(true)
const errorMessage = ref('')

async function loadMembers() {
  try {
    const response = await fetch('/api/member_info/Leader')

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    members.value = await response.json()
  } catch (error) {
    console.error(error)
    errorMessage.value = '成員資料載入失敗'
  } finally {
    loading.value = false
  }
}

function openMember(member) {
  if (!member?.id) {
    return
  }

  router.push(`/team/${member.id}`)
}

function openFullTeam() {
  router.push('/team')
}

onMounted(loadMembers)
</script>

<template>
  <section id="team" class="members-section">
    <div class="section-heading">
      <div>
        <p class="eyebrow">CURRENT LEADERS</p>

        <h2>15th幹部團隊</h2>
      </div>

      <p class="section-description">一群來自不同領域的人， 共同讓每一台機器從想法走到賽場。</p>
    </div>

    <div v-if="loading" class="state-message">載入團隊資料中……</div>

    <div v-else-if="errorMessage" class="state-message error">
      {{ errorMessage }}
    </div>

    <div v-else class="member-scroll-wrapper">
      <div class="member-scroll">
        <MemberCard v-for="member in members" :key="member.id" :info="member" color="white" type="Leader" @click="openMember(member)" />

        <article class="people-card view-all-card" @click="openFullTeam">
          <div class="view-all-content">
            <div class="view-all-arrow">→</div>

            <div>
              <p>EXPLORE THE TEAM</p>

              <h3>
                查看完整<br />
                團隊成員
              </h3>
            </div>

            <div class="generation">1st — 14th Generation</div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped src="@/styles/member-scroller.css"></style>
<style scoped>
.members-section {
  background: #f5f5f3;
  color: #141414;
}


.eyebrow {
  color: #777;
}

.section-description {
  color: #777;
}

/* =========================
   View All Card
========================= */

.view-all-card {
  min-height: 530px;
  color: white;
  background: #111318;
}

.view-all-card:hover {
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.view-all-content {
  width: 100%;
  min-height: 100%;
  padding: 32px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.view-all-arrow {
  align-self: flex-end;
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 50%;
  font-size: 25px;
  transition:
    transform 0.3s ease,
    background 0.3s ease;
}

.view-all-card:hover .view-all-arrow {
  transform: translateX(6px);
  background: white;
  color: #111318;
}

.view-all-content p {
  margin: 0 0 12px;
  color: rgba(255, 255, 255, 0.52);
  font-size: 11px;
  letter-spacing: 0.2em;
}

.view-all-content h3 {
  margin: 0;
  font-size: clamp(34px, 4vw, 48px);
  line-height: 1.08;
  letter-spacing: -0.04em;
}

.generation {
  color: rgba(255, 255, 255, 0.54);
  font-size: 12px;
  letter-spacing: 0.08em;
}

/* =========================
   Scroll Hint
========================= */

.scroll-hint {
  margin-top: 8px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  color: #888;
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
}

.scroll-line {
  width: 60px;
  height: 1px;
  background: #bbb;
}

</style>
