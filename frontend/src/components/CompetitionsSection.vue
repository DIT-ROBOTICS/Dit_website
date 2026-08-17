<!--
其他比賽的介紹：
當年其他比賽或營隊的機器人
姚哥想要有學長姐專題
-->

<script setup>
import{RotateCw,ArrowRight,ArrowLeft,ArrowUpRight,X,Plus,ArrowUp}from'lucide-vue-next'
const competitions = [
    {
        id: 1,
        title: 'ASME SPDC',
        subtitle: 'Student Professional Development Conference',
        year: '2025',
        description: 'ASME 會是新成員加入團隊後參與的第一場比賽，由於規則相較單純，很適合當作啟蒙老師，為成員們開啟機器人之路',
        backgroundImage: '/api/other_images/competition/asme.jpg'
    },
    {
        id: 2,
        title: 'TDK',
        subtitle: 'TDK Robocon',
        year: '2025',
        description: '參與 TDK 全國大專院校創思設計與製作競賽，挑戰機構、電控與策略之間的高度整合。',
        backgroundImage: '/api/other_images/competition/tdk.jpg'
    },
    {
        id: 3,
        title: 'WildBot',
        subtitle: 'WildBot Competition',
        year: '2024',
        description: '透過不同形式的機器人競賽與實作活動，探索新的機構概念、控制方式與團隊合作模式。',
        backgroundImage: '/api/other_images/competition/wildbot.jpg'
    }
]

function openCompetition(item) {
    console.log(item)
    //之後可以改 router.push(...)
}
</script>

<template>
    <section class="competition-wrapper">
        <div class="competition-header">
            <img src="@/assets/image/Canva_RibbonBanner.png" alt="" class="competition-ribbon">
            <!-- <h2 class="competition-header-title">Another Competition</h2> -->
            <svg class="competition-header-title" viewBox="0 0 1000 250">
                <defs>
                    <path id="title-curve" d="M150,175 Q500,80 850,175" />
                </defs>
                <text>
                    <textPath href="#title-curve" startOffset="50%" text-anchor="middle">
                        Other Competition
                    </textPath>
                </text>
            </svg>
        </div>
        <div class="competition-section">
            <article v-for="(item, index) in competitions" :key="item.id" class="competition-card"
                :class="`competition-card-${index + 1}`" :style="{ backgroundImage: `url('${item.backgroundImage}')` }">
                <div class="image-overlay"></div>

                <div class="content">
                    <p class="year">{{ item.year }}</p>

                    <h2>{{ item.title }}</h2>

                    <div class="detail">
                        <p class="subtitle">{{ item.subtitle }}</p>
                        <p class="description">{{ item.description }}</p>

                        <button @click="openCompetition(item)">
                            View More
                            <span><ArrowRight :size="20" :stroke-width="1.5"/></span>
                        </button>
                    </div>
                </div>
            </article>
        </div>
    </section>
</template>

<style scoped>
.competition-wrapper {
    width: 100%;
    background: #3e3e3e;
    overflow: hidden;
}

.competition-header {
    position: relative;
    width: min(950px, 90%);
    height: 270px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
}

.competition-ribbon {
    position: absolute;
    left: 50%;
    top: 50%;
    width: 100%;
    height: auto;
    transform: translate(-50%, -50%);
    object-fit: contain;
    pointer-events: none;
    user-select: none;
}

.competition-header-title {
    position: relative;
    z-index: 1;
    margin: 0 0 45px;
    color: #18181b;
    font-size: clamp(40px, 4vw, 72px);
    font-weight: 800;
    font-family:"Futura Black",Futura,sans-serif;
    line-height: 1;
    letter-spacing: -.03em;
    white-space: nowrap;
}

.competition-section {
    --Card-Angle: 100px;
    --Card-Gap: 30px;
    width: 100%;
    height: 720px;
    display: flex;
    overflow: hidden;
}

.competition-card {
    position: relative;
    flex: 1;
    min-width: 0;
    height: 100%;
    background-size: cover;
    background-position: center;
    isolation: isolate;
    transition:
        flex .6s cubic-bezier(.22, 1, .36, 1),
        filter .5s ease;
}

.competition-card-1 {
    clip-path: polygon(var(--Card-Angle) 0,
            100% 0,
            calc(100% - var(--Card-Angle) * 2) 100%,
            0 100%,
            0 50%);
    margin-right: calc(var(--Card-Angle) * -2 + var(--Card-Gap));
    z-index: 3;

    .content {
        left: calc(var(--Card-Angle) - 40px);
    }
}

.competition-card-2 {
    flex: 1.2;
    clip-path: polygon(calc(var(--Card-Angle) * 2) 0,
            100% 0,
            calc(100% - var(--Card-Angle) * 2) 100%,
            0 100%);
    margin-right: calc(var(--Card-Angle) * -2 + var(--Card-Gap));
    z-index: 2;

    .content {
        left: calc(var(--Card-Angle) + 50px);
    }
}

.competition-card-3 {
    clip-path: polygon(calc(var(--Card-Angle) * 2) 0,
            100% 0,
            100% 50%,
            calc(100% - var(--Card-Angle)) 100%,
            0 100%);
    /* text-align: center; */
    z-index: 1;

    .content {
        left: calc(var(--Card-Angle) + 60px);
    }
}

.competition-section:hover .competition-card {
    flex: .9;
}

.competition-section .competition-card:hover {
    flex: 1.25;
}

.competition-section .competition-card-2:hover {
    flex: 1.6;
}

.image-overlay {
    position: absolute;
    inset: 0;
    z-index: -1;
    background:
        linear-gradient(to top,
            rgba(0, 0, 0, .68) 0%,
            rgba(0, 0, 0, .2) 48%,
            rgba(0, 0, 0, .12) 100%);
    transition: background .5s ease;
}

.competition-card:hover .image-overlay {
    background:
        linear-gradient(to top,
            rgba(255, 255, 255, .75) 0%,
            rgba(255, 255, 255, .42) 45%,
            rgba(255, 255, 255, .18) 100%);
}

.content {
    position: absolute;
    bottom: 11%;
    width: max-content;
    color: white;
}

.year {
    margin: 0 0 8px;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: .18em;
    opacity: .7;
    transition:
        transform .5s cubic-bezier(.22, 1, .36, 1),
        color .4s ease;
}

h2 {
    margin: 0;
    font-size: clamp(38px, 4vw, 68px);
    line-height: .95;
    font-weight: 800;
    letter-spacing: -.04em;
    transition:
        transform .55s cubic-bezier(.22, 1, .36, 1),
        color .4s ease;
}

.detail {
    max-width: 440px;
    margin-top: 24px;
    opacity: 0;
    transform: translateY(30px);
    pointer-events: none;
    transition:
        opacity .4s ease,
        transform .55s cubic-bezier(.22, 1, .36, 1);
}

.competition-card:hover .year,
.competition-card:hover h2 {
    color: #27272a;
    transform: translateY(-110px);
}

.competition-card:hover .detail {
    opacity: 1;
    transform: translateY(-90px);
    pointer-events: auto;
}

.subtitle {
    margin: 0 0 10px;
    color: #27272a;
    font-size: 18px;
    font-weight: 700;
}

.description {
    margin: 0;
    color: #3f3f46;
    font-size: 15px;
    line-height: 1.7;
}

button {
    margin-top: 25px;
    padding: 0;
    border: 0;
    background: none;
    color: #18181b;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
}

button span {
    display: inline-block;
    margin-left: 8px;
    transform: translateX(0px) translateY(25%);
    transition: transform .25s ease;
}

button:hover span {
    transform: translateX(6px) translateY(25%);
}

@media(max-width:850px) {
    .competition-section {
        height: auto;
        display: block;
        background: white;
    }

    .competition-card {
        width: 100%;
        height: 520px;
        clip-path: none;
        margin: 0;
    }

    .competition-section:hover .competition-card,
    .competition-section .competition-card:hover {
        flex: none;
    }

    .content {
        left: 8%;
        right: 8%;
    }

    .competition-card:hover .year,
    .competition-card:hover h2 {
        transform: translateY(-90px);
    }

    .competition-card:hover .detail {
        transform: translateY(-70px);
    }
}
</style>
