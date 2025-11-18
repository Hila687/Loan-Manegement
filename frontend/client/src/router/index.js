import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'   // ← זה החדש שאת מוסיפה

const routes = [
  { path: '/', component: Home }      // ← וזה נכנס במקום המערך הריק
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
