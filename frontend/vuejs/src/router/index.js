import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store'

// Routes
import { routes as homeRoutes } from '@/apps/home/router/index.js'
import { routes as authRoutes } from '@/apps/auth/router'
import { routes as builderRoutes } from '@/apps/builder/router'
import NotFound from '@/shared/views/NotFound.vue'

const routes = [
  ...homeRoutes,
  authRoutes,
  builderRoutes,
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
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
  
  next()
})

export default router 