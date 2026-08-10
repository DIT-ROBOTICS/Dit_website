<template>
    <!-- <article v-for="advisor in advisors" :key="advisor.id" class="advisor-card"
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
    </article> -->
</template>