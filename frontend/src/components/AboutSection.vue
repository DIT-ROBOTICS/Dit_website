<script setup>
import teamPhoto from '@/assets/Hero_Image.png'

const departments = [
    {
        title: 'Team',
        subtitle: '團隊歷史',
        icon: '⚙️'
    },
    {
        title: 'Competition',
        subtitle: '競賽歷史',
        icon: '💻'
    },
    {
        title: 'technology',
        subtitle: '技術路線',
        icon: '⚡'
    },
    {
        title: 'Future',
        subtitle: '未來規劃',
        icon: '🛰'
    }
]
</script>

<template>
    <section class="about-section">

        <div class="title">

            <p>WHO WE ARE</p>

            <h2>
                我們打造的不只是機器人，
                <br>
                更是一群能一起完成夢想的人。
            </h2>

        </div>

        <div class="photo">
            <img :src="teamPhoto" alt="">
        </div>

        <div class="description">
            <p>
                DIT Robotics 成立於 2012 年，
                持續投入 Eurobot 國際機器人競賽，
                團隊涵蓋機構、電控、軟體與策略，
                讓每一位隊員都能真正參與一台機器人的誕生。
            </p>
        </div>

        <div class="department-grid">
            <div v-for="item in departments" :key="item.title" class="department-card">
                <div class="icon">
                    {{ item.icon }}
                </div>
                <h3>
                    {{ item.title }}
                </h3>
                <span>
                    {{ item.subtitle }}
                </span>
            </div>
        </div>
    </section>
</template>

<style scoped>
.about-section {
    padding: 120px 8vw;
    background: #fafafa;
}

.title {
    max-width: 900px;
    margin: auto;
    text-align: center;
}

.title p {
    letter-spacing: .3em;
    font-size: 13px;
    color: #888;
    margin-bottom: 18px;
}

.title h2 {
    font-size: clamp(42px, 5vw, 72px);
    line-height: 1.15;
    font-weight: 700;
    margin: 0;
}

.photo {
    margin-top: 90px;
    display: flex;
    justify-content: center;
}

.photo img {
    width: min(1200px, 100%);
    border-radius: 30px;
    box-shadow:
        0 40px 80px rgba(0, 0, 0, .12);
}

.description {
    max-width: 900px;
    margin: 70px auto;
    text-align: center;
    font-size: 20px;
    line-height: 2;
    color: #555;
}

.department-grid {
    display: grid;
    grid-template-columns:
        repeat(4, 1fr);
    gap: 25px;
}

.department-card {
    padding: 35px;
    border-radius: 24px;
    background: white;
    transition: .35s;
    cursor: pointer;
}

.department-card:hover {
    transform: translateY(-8px);
    box-shadow:
        0 25px 60px rgba(0, 0, 0, .12);
}

.icon {
    font-size: 42px;
    margin-bottom: 18px;
}

.department-card h3 {
    margin: 0;
    font-size: 24px;
}

.department-card span {
    display: block;
    margin-top: 8px;
    color: #777;
}

@media(max-width:900px) {
    .department-grid {
        grid-template-columns:
            repeat(2, 1fr);
    }
}
</style>