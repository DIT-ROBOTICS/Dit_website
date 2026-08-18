import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import EurobotView from '../views/EurobotView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to) {
    if (to.hash === '#RobotArchive') {
      return new Promise((resolve) => {
        let finished = false

        const finish = () => {
          if (finished) return
          finished = true
          window.removeEventListener('eurobot-rules-ready', finish)
          resolve({ el: to.hash, behavior: 'smooth' })
        }

        window.addEventListener('eurobot-rules-ready', finish, { once: true })
        window.setTimeout(finish, 2500)
      })
    }

    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth',
      }
    }

    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/Eurobot',
      name: 'Eurobot',
      component: EurobotView,
    }
  ],
})

export default router
