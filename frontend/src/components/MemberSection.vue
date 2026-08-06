<script setup>
import { onMounted, ref } from 'vue'

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

onMounted(loadMembers)
</script>

<template>
  <section class="members">
    <h2>團隊成員</h2>

    <p v-if="loading">
      載入中……
    </p>

    <p v-else-if="errorMessage">
      {{ errorMessage }}
    </p>

    <div
      v-else
      class="member-grid"
    >
      <article
        v-for="member in members"
        :key="member.id"
      >
        <img
          :src="member.image"
          :alt="member.name"
        />

        <h3>{{ member.name }}</h3>
        <p>{{ member.role }}</p>
      </article>
    </div>
  </section>
</template>

<style scoped>
.members {
  padding: 100px 8vw;
}

.heading p {
  color: #777;
  letter-spacing: 0.2em;
  font-size: 12px;
}

.heading h2 {
  margin: 12px 0 45px;
  font-size: clamp(36px, 5vw, 64px);
}

.member-grid {
  display: grid;
  grid-template-columns:
    repeat(auto-fit, minmax(220px, 1fr));
  gap: 28px;
}

.member-card img {
  width: 100%;
  aspect-ratio: 4 / 5;
  object-fit: cover;
}

.member-card h3 {
  margin: 18px 0 5px;
  font-size: 22px;
}

.member-card p {
  margin: 0;
  color: #777;
}
</style>