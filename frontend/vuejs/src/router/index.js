import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Home from '@/apps/home/views/Home.vue'
import AuthLayout from '@/apps/auth/layouts/AuthLayout.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/apps/auth/views/Login.vue')
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/apps/auth/views/Register.vue')
      }
    ]
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
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('@/apps/home/views/About.vue')
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('@/apps/home/views/Privacy.vue')
  },
  {
    path: '/terms',
    name: 'Terms',
    component: () => import('@/apps/home/views/Terms.vue')
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('@/apps/home/views/Contact.vue')
  },
  {
    path: '/cookie-policy',
    name: 'CookiePolicy',
    component: () => import('@/apps/home/views/CookiePolicy.vue')
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