<script setup>
import EurobotSection from '@/features/eurobot/components/EurobotSection.vue'
import EurobotRules from '@/features/eurobot/components/EurobotRules.vue'
import RobotArchiveSection from '@/features/eurobot/components/RobotArchiveSection.vue'
</script>

<template>
<EurobotSection achievement-margin-top="200px" :show-history-button="false">
    <template #rules>
        <EurobotRules />
    </template>
</EurobotSection>
<RobotArchiveSection id="RobotArchive"/>
</template>
