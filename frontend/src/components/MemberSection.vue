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

const router = useRouter()

const members = ref([])
const loading = ref(true)
const errorMessage = ref('')

async function loadMembers() {
  try {
    const response = await fetch('/api/members')

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

        <h2>2026 14th幹部團隊</h2>
      </div>

      <p class="section-description">一群來自不同領域的人， 共同讓每一台機器從想法走到賽場。</p>
    </div>

    <div v-if="loading" class="state-message">載入團隊資料中……</div>

    <div v-else-if="errorMessage" class="state-message error">
      {{ errorMessage }}
    </div>

    <div v-else class="member-scroll-wrapper">
      <div class="member-scroll">
        <article v-for="member in members" :key="member.id" class="member-card" @click="openMember(member)" >
          <div class="member-photo">
            <img :src="`/api/Leader-image/${member.id}`" :alt="member.name" />

            <div class="photo-overlay"></div>
          </div>

          <div class="member-info">
            <p class="member-position">
              {{ member.position }}
            </p>

            <h3>
              {{ member.name }}
            </h3>

            <p v-if="member.description" class="member-description">
              {{ member.description }}
            </p>

            <div v-if="member.skills?.length" class="skills">
              <span v-for="skill in member.skills" :key="skill">
                {{ skill }}
              </span>
            </div>

            <button class="profile-link" type="button" @click.stop="openMember(member)">
              View Profile
              <span>↗</span>
            </button>
          </div>
        </article>

        <article class="member-card view-all-card" @click="openFullTeam">
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

<style scoped>
.members-section {
  position: relative;
  padding: 120px 0 100px;
  overflow: visible;
  background: #f5f5f3;
  color: #141414;
}

/* =========================
   Heading
========================= */

.section-heading {
  max-width: 1400px;
  margin: 0 auto 64px;
  display: grid;
  grid-template-columns:
    minmax(0, 1fr)
    minmax(260px, 420px);
  gap: 60px;
  align-items: end;
}

.eyebrow {
  margin: 0 0 14px;
  color: #777;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.24em;
}

.section-heading h2 {
  margin: 0;
  font-size: clamp(42px, 6vw, 78px);
  line-height: 1.05;
  letter-spacing: -0.04em;
}

.section-description {
  margin: 0;
  color: #777;
  font-size: 16px;
  line-height: 1.9;
}

/* =========================
   Loading / Error
========================= */

.state-message {
  max-width: 1400px;
  margin: 0 auto;
  padding: 70px 0;
  color: #777;
  font-size: 16px;
}

.state-message.error {
  color: #bb2d2d;
}

/* =========================
   Horizontal Scroll
========================= */

.member-scroll-wrapper {
  max-width: 100vw;
  margin: 0 auto;
  overflow-x: auto;
  padding-inline: 10vw;
}

.member-scroll {
  display: flex;
  gap: 26px;
  overflow-y: visible;
  padding: 10px 0 34px;
  scroll-snap-type: x mandatory;
  scroll-behavior: smooth;
  overscroll-behavior-inline: contain;
  scrollbar-width: none;

    /* IE、舊 Edge */

  -ms-overflow-style: none;
}

.member-scroll::-webkit-scrollbar {
  display: none;
}


/* =========================
   Member Card
========================= */

.member-card {
  flex: 0 0 clamp(280px, 27vw, 360px);
  scroll-snap-align: start;
  border-radius: 28px;
  overflow: hidden;
  background: #fff;
  cursor: pointer;
  transition:
    transform 0.35s cubic-bezier(0.2, 0.7, 0.2, 1),
    box-shadow 0.35s ease;
}

.member-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12);
}

/* =========================
   Photo
========================= */

.member-photo {
  position: relative;
  aspect-ratio: 4 / 5;
  overflow: hidden;
  background: #e7e7e7;
}

.member-photo img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
  transition: transform 0.65s cubic-bezier(0.2, 0.7, 0.2, 1);
}

.member-card:hover .member-photo img {
  transform: scale(1.06);
}

.photo-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.28), transparent 42%);
}

.member-number {
  position: absolute;
  right: 18px;
  bottom: 16px;
  color: rgba(255, 255, 255, 0.9);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.16em;
}

/* =========================
   Member Info
========================= */

.member-info {
  padding: 26px 26px 28px;
}

.member-position {
  margin: 0 0 8px;
  color: #777;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.member-info h3 {
  margin: 0;
  font-size: 29px;
  line-height: 1.15;
  letter-spacing: -0.025em;
}

.member-description {
  margin: 14px 0 0;
  color: #777;
  font-size: 14px;
  line-height: 1.7;
}

/* =========================
   Skills
========================= */

.skills {
  margin-top: 19px;
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.skills span {
  padding: 7px 10px;
  border: 1px solid #dddddd;
  border-radius: 999px;
  color: #555;
  background: #fafafa;
  font-size: 11px;
}

/* =========================
   Profile Button
========================= */

.profile-link {
  margin-top: 24px;
  padding: 0;
  border: none;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  color: #111;
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.profile-link span {
  display: inline-block;
  transition: transform 0.2s ease;
}

.profile-link:hover span {
  transform: translate(3px, -3px);
}

/* =========================
   View All Card
========================= */

.view-all-card {
  min-height: 530px;
  display: flex;
  color: white;
  background: #111318;
  margin-right: 10vw;
}

.view-all-card:hover {
  box-shadow: 0 30px 60px rgba(0, 0, 0, 0.2);
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

/* =========================
   Responsive
========================= */

@media (max-width: 900px) {
  .members-section {
    padding: 90px 24px 75px;
  }

  .section-heading {
    grid-template-columns: 1fr;
    gap: 24px;
    margin-bottom: 45px;
  }

  .section-description {
    max-width: 540px;
  }

  .member-card {
    flex-basis: min(82vw, 330px);
  }
}

@media (max-width: 520px) {
  .members-section {
    padding-left: 18px;
    padding-right: 18px;
  }

  .section-heading h2 {
    font-size: 42px;
  }

  .member-card {
    border-radius: 22px;
  }

  .member-info {
    padding: 22px;
  }
}
</style>
