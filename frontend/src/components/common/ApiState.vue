<script setup>
defineProps({
    loading: Boolean,
    error: {
        type: [Error, Object, String],
        default: null,
    },
    empty: Boolean,
    loadingMessage: {
        type: String,
        default: '資料載入中…',
    },
    emptyMessage: {
        type: String,
        default: '目前沒有資料',
    },
})

defineEmits(['retry'])
</script>

<template>
    <div v-if="loading" class="api-state" role="status">
        <span class="api-state-spinner" aria-hidden="true"></span>
        <p>{{ loadingMessage }}</p>
    </div>

    <div v-else-if="error" class="api-state api-state-error" role="alert">
        <p>資料載入失敗，請稍後再試。</p>
        <button type="button" @click="$emit('retry')">重新載入</button>
    </div>

    <div v-else-if="empty" class="api-state" role="status">
        <p>{{ emptyMessage }}</p>
        <button type="button" @click="$emit('retry')">重新載入</button>
    </div>

    <slot v-else />
</template>

<style scoped>
.api-state {
    display: grid;
    place-items: center;
    align-content: center;
    gap: 14px;
    width: 100%;
    min-height: 240px;
    padding: 40px 20px;
    text-align: center;
}

.api-state p {
    margin: 0;
}

.api-state-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid rgba(127, 127, 127, 0.25);
    border-top-color: currentColor;
    border-radius: 50%;
    animation: api-state-spin 0.8s linear infinite;
}

.api-state button {
    padding: 10px 18px;
    border: 1px solid currentColor;
    border-radius: 999px;
    color: inherit;
    background: transparent;
    cursor: pointer;
}

@keyframes api-state-spin {
    to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
    .api-state-spinner { animation: none; }
}
</style>
