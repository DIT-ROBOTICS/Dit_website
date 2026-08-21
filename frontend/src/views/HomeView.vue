<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import HeroSection from '@/features/hero/HeroSection.vue'
import AboutSection from '@/features/about/AboutSection.vue'
import AdvisorsSection from '@/features/advisors/AdvisorsSection.vue'
import EurobotSection from '@/features/eurobot/components/EurobotSection.vue'
import SponsorsSection from '@/features/sponsors/SponsorsSection.vue'
import ContactSection from '@/features/contact/ContactSection.vue'

const heroProgress = ref(0)

let observer

onMounted(() => {
    const sections = document.querySelectorAll('.about-wrapper section[id]')

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
        <div id="aboutSection" class="about-scroll-target" aria-hidden="true"></div>

        <div class="about-wrapper">
            <AboutSection />
            <EurobotSection id="EurobotSection">
                <template #afterContent>
                    <AdvisorsSection />
                </template>
            </EurobotSection>
            <SponsorsSection id="sponsors" />
            <ContactSection id="contact" />
        </div>
    </main>
</template>

<style scoped>
.home-page {
    position: relative;
}

/*
 * Hero 完成收合時的固定座標：
 * scroll target top (60vh) - TitleBar (76px) = Hero 動畫完整距離。
 */
.about-scroll-target {
    position: absolute;
    top: 60vh;
    width: 1px;
    height: 1px;
    pointer-events: none;
    scroll-margin-top: var(--title-bar-height);
}

.about-wrapper {
    position: relative;
    z-index: 10;
    margin-top: calc(-60vh - (40vh * var(--hero-progress)) + var(--title-bar-height));
    background: #f5f5f3;
}

@media (max-width: 900px) {
    .about-scroll-target {
        top: calc(155svh - 100vh);
    }
}

</style>
