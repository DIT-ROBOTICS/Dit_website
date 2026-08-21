import { onMounted, onUnmounted, ref } from 'vue'

const DEFAULT_QUERY = '(hover: none), (pointer: coarse)'

/** 統一監聽滑鼠／觸控互動模式，並在元件卸載時清除 listener。 */
export function useInteractionMode({ query = DEFAULT_QUERY, onChange } = {}) {
    const usesTouchInteraction = ref(window.matchMedia(query).matches)
    let mediaQuery

    function updateInteractionMode(event) {
        usesTouchInteraction.value = event.matches
        onChange?.(event.matches)
    }

    onMounted(() => {
        mediaQuery = window.matchMedia(query)
        usesTouchInteraction.value = mediaQuery.matches
        mediaQuery.addEventListener('change', updateInteractionMode)
    })

    onUnmounted(() => {
        mediaQuery?.removeEventListener('change', updateInteractionMode)
    })

    return { usesTouchInteraction }
}

