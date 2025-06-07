import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/shared/stores/auth'
import type { RouteModule } from './types'
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore'

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
  },
  // Payment system routes - explicitly defined for clarity
  {
    path: '/payments/success',
    name: 'payment-success',
    component: () => import('@/apps/payments/views/PaymentSuccessView.vue'),
    meta: { requiresAuth: true, title: 'Payment Successful - Imagi Oasis' }
  },
  {
    path: '/payments/cancel',
    name: 'payment-cancel',
    component: () => import('@/apps/payments/views/PaymentCancelView.vue'),
    meta: { requiresAuth: true, title: 'Payment Cancelled - Imagi Oasis' }
  },
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

// Keep track of navigation type
let navigationFromPopState = false

// Add popstate listener to detect browser back/forward navigation
window.addEventListener('popstate', () => {
  navigationFromPopState = true
  
  // Handle immediate state restoration from localStorage
  const authStore = useAuthStore()
  try {
    const tokenData = localStorage.getItem('token')
    const userData = localStorage.getItem('user')
    
    if (tokenData && userData) {
      try {
        const token = JSON.parse(tokenData)?.value
        const user = JSON.parse(userData)
        
        if (token && user && !authStore.isAuthenticated) {
          console.log('Restoring auth state from localStorage during popstate')
          // Just restore the state without API validation
          authStore.restoreAuthState(user, token)
        }
      } catch (error) {
        console.error('Failed to restore auth state:', error)
      }
    }
  } catch (error) {
    console.error('Error handling popstate event:', error)
  }
  
  // Reset after a short delay
  setTimeout(() => {
    navigationFromPopState = false
  }, 100)
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  // Set page title
  document.title = `${to.meta.title || 'Imagi'} | AI-Powered Web Builder`

  // Get auth store
  const auth = useAuthStore()
  
  // Special handling for browser back/forward navigation
  if (navigationFromPopState) {
    console.log('Handling popstate navigation in router guard')
    // For back/forward navigation, we've already restored auth state from localStorage
    // Just let the navigation continue
    next()
    return
  }
  
  // Regular navigation handling
  // Check auth requirements
  if (to.meta.requiresAuth) {
    // Wait for auth initialization
    if (!auth.initialized) {
      await auth.initAuth()
    }
    
    if (!auth.isAuthenticated) {
      // Store original destination for post-login redirect
      next({
        name: 'login',
        query: { redirect: to.fullPath },
        replace: true
      })
      return
    }
  }

  // Special handling for login route - check if user is already authenticated
  if (to.name === 'login' && to.query.redirect) {
    if (!auth.initialized) {
      await auth.initAuth()
    }
    
    // If already authenticated, redirect directly to the original destination
    if (auth.isAuthenticated && to.query.redirect) {
      next({ path: to.query.redirect as string })
      return
    }
  }

  // Check if navigating to a project-related view
  const projectRoutes = [
    'builder-dashboard',
    'builder-projects', 
    'builder-workspace', 
    'dashboard'
  ]
  
  if (projectRoutes.includes(String(to.name))) {
    // Remove automatic project fetching on navigation
    // Projects should only be fetched by the specific pages that need them
    // when they mount, not automatically on every navigation
  }

  next()
})

export default router
