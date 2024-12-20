import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

// Layouts
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'
import DashboardLayout from '@/layouts/DashboardLayout.vue'

// Views
import Home from '@/views/Home.vue'
import About from '@/views/About.vue'
import Contact from '@/views/Contact.vue'
import Privacy from '@/views/Privacy.vue'
import Terms from '@/views/Terms.vue'
import CookiePolicy from '@/views/CookiePolicy.vue'
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'
import ForgotPassword from '@/views/auth/ForgotPassword.vue'
import Dashboard from '@/views/dashboard/Dashboard.vue'
import ChangePassword from '@/views/auth/ChangePassword.vue'

const routes = [
  {
    path: '/',
    component: DefaultLayout,
    children: [
      {
        path: '',
        name: 'home',
        component: Home
      },
      {
        path: 'about',
        name: 'about',
        component: About
      },
      {
        path: 'contact',
        name: 'contact',
        component: Contact
      },
      {
        path: 'privacy',
        name: 'privacy',
        component: Privacy
      },
      {
        path: 'terms',
        name: 'terms',
        component: Terms
      },
      {
        path: 'cookie-policy',
        name: 'cookie-policy',
        component: CookiePolicy
      }
    ]
  },
  {
    path: '/',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'login',
        component: Login
      },
      {
        path: 'register',
        name: 'register',
        component: Register
      },
      {
        path: 'forgot-password',
        name: 'forgot-password',
        component: ForgotPassword
      }
    ]
  },
  {
    path: '/dashboard',
    component: DashboardLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: Dashboard
      },
      {
        path: 'change-password',
        name: 'change-password',
        component: ChangePassword
      }
    ]
  },
  {
    path: '/reset-password/:uid/:token',
    name: 'PasswordResetConfirm',
    component: () => import('@/views/auth/PasswordResetConfirm.vue'),
    meta: {
      requiresAuth: false,
      layout: 'auth'
    }
  },
  {
    path: '/reset-password/complete',
    name: 'PasswordResetComplete',
    component: () => import('@/views/auth/PasswordResetComplete.vue'),
    meta: {
      requiresAuth: false,
      layout: 'auth'
    }
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

// Navigation guard for protected routes
router.beforeEach(async (to, from, next) => {
  const { isAuthenticated } = useAuth()

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated.value) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router 