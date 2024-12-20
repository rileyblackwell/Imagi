import { createRouter, createWebHistory } from 'vue-router'
import AuthService from '@/apps/auth/services/auth.service'

// Import app routes
import authRoutes from '@/apps/auth/routes'
import homeRoutes from '@/apps/home/routes'
import paymentsRoutes from '@/apps/payments/routes'
import builderRoutes from '@/apps/builder/routes'

// Import layouts
import MainLayout from '@/shared/layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      // Home routes
      {
        path: '',
        ...homeRoutes
      },
    ]
  },
  // Auth routes
  authRoutes,
  // Payments routes
  {
    path: '/payments',
    ...paymentsRoutes
  },
  // Builder routes
  {
    path: '/builder',
    ...builderRoutes
  },
  // 404 route
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/shared/views/NotFound.vue')
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

// Navigation Guards
router.beforeEach(async (to, from, next) => {
  // Set page title
  document.title = to.meta.title || 'Imagi'

  // Check auth requirements
  const isAuthenticated = !!localStorage.getItem('token')
  const currentUser = isAuthenticated ? await AuthService.getCurrentUser() : null
  
  // Handle auth routes
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ 
      name: 'login', 
      query: { redirect: to.fullPath },
      replace: true 
    })
    return
  }
  
  if (to.meta.requiresGuest && isAuthenticated) {
    next({ name: 'dashboard' })
    return
  }

  // Handle payment routes
  if (to.meta.requiresAuth && to.path.startsWith('/payments')) {
    if (!currentUser) {
      next({ 
        name: 'login', 
        query: { redirect: to.fullPath },
        replace: true 
      })
      return
    }
  }

  // Handle builder routes
  if (to.meta.requiresAuth && to.path.startsWith('/builder')) {
    if (!currentUser) {
      next({ 
        name: 'login', 
        query: { redirect: to.fullPath },
        replace: true 
      })
      return
    }
  }

  next()
})

// Handle auth errors
router.onError((error) => {
  if (error.message === 'Session expired') {
    router.push({ 
      name: 'login', 
      query: { 
        redirect: router.currentRoute.value.fullPath,
        session_expired: true 
      }
    })
  }
})

export default router 