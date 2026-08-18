<script setup>
import {onMounted} from 'vue'
import EurobotSection from '@/components/EurobotSection.vue'
import EurobotRules from '@/components/EurobotRules.vue'
import RobotArchiveSection from '@/components/RobotArchiveSection.vue'

function delete_eurobot_history_button(){
    document.getElementById("eurobot-history-button")?.remove()
}
onMounted(delete_eurobot_history_button)
</script>

<template>
<EurobotSection achievement-margin-top="200px" />
<EurobotRules/>
<RobotArchiveSection id="RobotArchive"/>
</template>
