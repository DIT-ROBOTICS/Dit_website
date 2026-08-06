<script setup>
import HeroSection from '@/components/HeroSection.vue'
import AboutSection from '@/components/AboutSection.vue'  
import TeamSection from '@/components/TeamSection.vue'
import FeaturedRobotSection from '@/components/FeaturedRobotSection.vue'
import RobotArchiveSection from '@/components/RobotArchiveSection.vue'
import AdvisorsSection from '@/components/AdvisorsSection.vue'
import SponsorsSection from '@/components/SponsorsSection.vue'
import ContactSection from '@/components/ContactSection.vue'
</script>

<template>
  <main>
    <HeroSection />

    <AboutSection />

    <TeamSection id="team" />

    <FeaturedRobotSection id="featured-robot" />

    <RobotArchiveSection id="robots" />

    <AdvisorsSection id="advisors" />

    <SponsorsSection id="sponsors" />

    <ContactSection id="contact" />
  </main>
</template>