<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
    color: {
        type: String,
        required: true
    },

    info: {
        type: Object,
        required: true
    },

    type: {
        type: String,
        required: true,
        validator(value) {
            return ['advisor', 'Leader'].includes(value)
        }
    }
})

const BackgroundColor = ref('#191c22')
const TextColor = ref('#191c22')
if(props.color === 'black'){
    BackgroundColor.value = '#191c22'
    TextColor.value = '#ffffff'
} else if(props.color === 'white'){
    BackgroundColor.value = 'white'
    TextColor.value = '#191c22'
}


function openFullInfoWindow() {
    if (!props.info?.id) return

    router.push(`/advisor/${props.info.id}`)
}


</script>


<template>
    <article :key="props.info.id" class="people-card"  :style="{ '--Card-Theme': BackgroundColor, '--Text-Theme': TextColor }" @click="openFullInfoWindow()">
        <div class="people-photo">
            <img :src="`/api/member_images/${props.type}-image/${props.info.id}`" :alt="props.info.name">
            <div class="photo-overlay"></div>
        </div>

        <div class="people-info">
            <p class="people-position">{{ props.info.position }}</p>

            <h3>{{ props.info.name }}</h3>

            <p v-if="props.info.department" class="people-department">{{ props.info.department }}</p>

            <p v-if="props.info.description" class="people-description">{{ props.info.description }}</p>

            <div v-if="props.info.skills?.length" class="skills-tags">
                <span v-for="item in props.info.skills" :key="item">{{ item }}</span>
            </div>

            <button class="profile-link" type="button" @click.stop="openFullInfoWindow()">
                View Profile
                <span>↗</span>
            </button>
        </div>
    </article>
</template>

<style scoped src="@/assets/styles/member-scroller.css"></style>
