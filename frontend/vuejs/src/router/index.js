import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store'

// Routes
import homeRoutes from '@/apps/home/router'
import authRoutes from '@/apps/auth/router'
import builderRoutes from '@/apps/builder/router'
import paymentsRoutes from '@/apps/payments/router'
import NotFound from '@/shared/views/NotFound.vue'

const routes = [
  ...homeRoutes,
  authRoutes,
  ...builderRoutes,
  ...paymentsRoutes,
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  
  // Check if route requires guest access
  if (to.meta.requiresGuest && isAuthenticated) {
    next({ name: 'home' })
    return
  }
  
  // Update document title
  document.title = to.meta.title ? `${to.meta.title} - Imagi` : 'Imagi'
  
  next()
})

export default router 