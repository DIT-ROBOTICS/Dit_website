import { onUnmounted } from 'vue'

let lockCount = 0
let originalOverflow = ''

/** 鎖定 body 捲動；支援多個 modal 同時存在，不會互相提前解鎖。 */
export function useBodyScrollLock() {
    let lockedByThisInstance = false

    function lockBodyScroll() {
        if (lockedByThisInstance) return

        if (lockCount === 0) {
            originalOverflow = document.body.style.overflow
            document.body.style.overflow = 'hidden'
        }

        lockCount += 1
        lockedByThisInstance = true
    }

    function unlockBodyScroll() {
        if (!lockedByThisInstance) return

        lockCount = Math.max(0, lockCount - 1)
        lockedByThisInstance = false

        if (lockCount === 0) {
            document.body.style.overflow = originalOverflow
        }
    }

    onUnmounted(unlockBodyScroll)

    return { lockBodyScroll, unlockBodyScroll }
}

