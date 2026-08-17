<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import HeroSection from '@/components/HeroSection.vue'
import AboutSection from '@/components/AboutSection.vue'
import EurobotSection from '@/components/EurobotSection.vue'
import SponsorsSection from '@/components/SponsorsSection.vue'
import ContactSection from '@/components/ContactSection.vue'

const heroProgress = ref(0)

let observer

onMounted(() => {
    const sections = document.querySelectorAll('section[id]')

    observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    history.replaceState(
                        null,
                        '',
                        `#${entry.target.id}`
                    )
                }
            })
        },
        {
            threshold: 0,
            rootMargin: '-30% 0px -60% 0px'
        }
    )

    sections.forEach((section) => {
        observer.observe(section)
    })
})

onUnmounted(() => {
    observer?.disconnect()
})
</script>

<template>
    <main class="home-page" :style="{ '--hero-progress': heroProgress }">
        <HeroSection v-model:progress="heroProgress" id="hero"/>

        <div class="about-wrapper">
            <AboutSection id="team" />
            <EurobotSection id="EurobotSection" />
            <SponsorsSection id="sponsors" />
            <ContactSection id="contact" />
        </div>
    </main>
</template>

<style scoped>
.about-wrapper {
    position: relative;
    z-index: 10;

    /*
   * Hero 從 100vh 縮成 76px，
   * 將縮掉的空間補回來。
   */
    margin-top: calc(-60vh - (40vh * var(--hero-progress)) + 76px);

    background: #f5f5f3;
}
</style>