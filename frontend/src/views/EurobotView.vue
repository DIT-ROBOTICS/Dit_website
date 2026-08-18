<script setup>
import EurobotSection from '@/components/EurobotSection.vue'
import EurobotRules from '@/components/EurobotRules.vue'
import RobotArchiveSection from '@/components/RobotArchiveSection.vue'
</script>

<template>
<EurobotSection achievement-margin-top="200px" :show-history-button="false" />
<EurobotRules/>
<RobotArchiveSection id="RobotArchive"/>
</template>
