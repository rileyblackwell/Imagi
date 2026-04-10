import { createRouter, createWebHistory } from 'vue-router'
import homeRoutes from '@/apps/home/router'
import authRoutes from '@/apps/auth/router'

// Placeholder routes for apps not yet implemented
const placeholderRoutes = [
  { path: '/products/:pathMatch(.*)*', name: 'products', redirect: '/' },
  { path: '/payments/:pathMatch(.*)*', name: 'payments', redirect: '/' },
  { path: '/docs/:pathMatch(.*)*', name: 'docs', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...homeRoutes,
    ...authRoutes,
    ...placeholderRoutes,
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  }
})

export default router
