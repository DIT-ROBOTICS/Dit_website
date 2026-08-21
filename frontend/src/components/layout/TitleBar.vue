<script setup>
import { useRoute } from 'vue-router'
import logoUrl from '@/assets/dit_logo.png'

const route = useRoute()

function sectionHref(hash) {
    return route.path === '/' ? hash : `/${hash}`
}

defineProps({
    progress: {
        type: Number,
        default: 0,
    },
})
</script>

<template>
    <!-- 掛載到 body，避免受 Hero 容器的裁切與堆疊環境影響。 -->
    <Teleport to="body">
        <header class="title-bar" :style="{ '--progress': progress }">
            <a :href="sectionHref('#hero')" class="title-brand">
                <img class="title-brand-logo" :src="logoUrl" alt="DIT Logo" />
                <strong class="title-brand-name">DIT Robotics</strong>
            </a>

            <nav class="title-navigation" aria-label="主要導覽">
                <a class="title-navigation-link mobile-hidden" :href="sectionHref('#aboutSection')">團隊</a>
                <a class="title-navigation-link" href="/Eurobot">Eurobot</a>
                <a class="title-navigation-link mobile-hidden" :href="sectionHref('Eurobot#RobotArchive')">歷年機器人</a>
                <a class="title-navigation-link" :href="sectionHref('Competition')">其他競賽</a>
                <a class="title-navigation-link" :href="sectionHref('#advisors')">指導教授</a>
                <a class="title-navigation-link" :href="sectionHref('#sponsors')">贊助商</a>
                <a class="title-navigation-link" :href="sectionHref('#contact')">聯絡我們</a>
            </nav>
        </header>
    </Teleport>
</template>

<style scoped>
.title-bar,
.title-brand,
.title-navigation {
    display: flex;
    align-items: center;
}

.title-bar,
.title-brand {
    gap: 14px;
}

.title-brand,
.title-navigation-link {
    text-decoration: none;
}

.title-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 54;
    box-sizing: border-box;
    height: var(--title-bar-height);
    padding-inline: 5vw;
    opacity: var(--progress);
    color: white;
    transform: translateY(calc((1 - var(--progress)) * -24px));
    background: rgba(10, 12, 17, 1);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
}

.title-brand {
    margin-right: auto;
    color: white;
    cursor: pointer;
}

.title-brand-logo {
    width: 42px;
    height: 42px;
    object-fit: contain;
    border-radius: 10px;
}

.title-brand-name {
    font-size: 16px;
}

.title-navigation {
    gap: 2.4vw;
}

.title-navigation-link {
    color: rgba(255, 255, 255, 0.72);
    font-size: 13px;
    transition: color 0.2s ease, transform 0.2s ease;
}

.title-navigation-link:hover {
    color: white;
    transform: translateY(-1px);
}

@media (max-width: 900px) {
    .title-bar {
        gap: 10px;
        padding-inline: 16px;
    }

    .title-brand {
        flex-shrink: 0;
    }

    .title-brand-name {
        display: none;
    }

    .title-navigation {
        min-width: 0;
        flex: 1;
        gap: 18px;
        overflow-x: auto;
        overscroll-behavior-x: contain;
        scrollbar-width: none;
    }

    .title-navigation::-webkit-scrollbar {
        display: none;
    }

    .title-navigation-link {
        flex-shrink: 0;
        white-space: nowrap;
    }

}

@media (max-width: 400px) {
    .title-bar {
        padding-inline: 12px;
    }
}

@media (max-width: 600px) {
    .title-navigation-link.mobile-hidden {
        display: none;
    }
}

@media (min-width: 1333.34px) {
    .title-navigation {
        gap: 32px;
    }
}

@media (min-width: 1440px) {
    .title-bar {
        padding-inline: 72px;
    }
}
</style>
