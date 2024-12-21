import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Home from '@/apps/home/views/Home.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/auth/login',
    name: 'Login',
    component: () => import('@/apps/auth/views/Login.vue')
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: () => import('@/apps/auth/views/Register.vue')
  },
  {
    path: '/builder',
    name: 'Builder',
    component: () => import('@/apps/builder/views/Builder.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/payments/credits',
    name: 'Credits',
    component: () => import('@/apps/payments/views/Credits.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router 