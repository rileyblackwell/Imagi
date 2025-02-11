import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store'
import type { RouteModule } from './types'

// Import route modules
const modules = import.meta.glob<RouteModule>('@/apps/**/router/index.ts', { eager: true })

// Extract routes from modules
const routeModules = Object.values(modules)
  .map(module => 'default' in module ? module.default : module.routes)
  .flat()

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: { name: 'home' }
  },
  ...routeModules,
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/shared/components/pages/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  // Set page title
  document.title = `${to.meta.title || 'Imagi'} | AI-Powered Web Builder`

  // Check auth requirements
  if (to.meta.requiresAuth) {
    const auth = useAuthStore()
    if (!auth.isAuthenticated) {
      next({
        name: 'login',
        query: { redirect: to.fullPath }
      })
      return
    }
  }

  next()
})

export default router
