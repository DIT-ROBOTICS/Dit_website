import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(router)

// 等待 Router 完成首次網址解析後再掛載 App。
// 否則直接開啟 /Eurobot 時，啟動畫面可能短暫誤判為首頁，
// 進而等待一個永遠不會出現的 Hero 影片事件。
router.isReady().then(() => {
  app.mount('#app')
})
