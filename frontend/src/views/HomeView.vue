<script setup>
import { ref } from 'vue'
import HeroSection from '@/components/HeroSection.vue'
import AboutSection from '@/components/AboutSection.vue'  
import TeamSection from '@/components/TeamSection.vue'
import FeaturedRobotSection from '@/components/FeaturedRobotSection.vue'
import RobotArchiveSection from '@/components/RobotArchiveSection.vue'
import AdvisorsSection from '@/components/AdvisorsSection.vue'
import SponsorsSection from '@/components/SponsorsSection.vue'
import ContactSection from '@/components/ContactSection.vue'

const heroProgress = ref(0)
// provide('heroProgress', heroProgress)
</script>

<template>
  <main class="home-page" :style="{ '--hero-progress': heroProgress }">
    <HeroSection v-model:progress="heroProgress"/>

    <div class="about-wrapper">
      <AboutSection />
      <TeamSection id="team" />
      <FeaturedRobotSection id="featured-robot" />
      <RobotArchiveSection id="robots" />
      <AdvisorsSection id="advisors" />
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
  margin-top: calc( -60vh - (40vh * var(--hero-progress)) + 76px);

  background: #f5f5f3;
}
</style>