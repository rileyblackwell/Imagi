import { createRouter, createWebHistory } from 'vue-router'

// Layouts
import MainLayout from '@/components/layout/MainLayout.vue'
import AuthLayout from '@/components/layout/AuthLayout.vue'

// Views
import Home from '@/views/home/Home.vue'
import About from '@/views/home/About.vue'
import Privacy from '@/views/home/Privacy.vue'
import Terms from '@/views/home/Terms.vue'
import Contact from '@/views/home/Contact.vue'
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'
import ForgotPassword from '@/views/auth/ForgotPassword.vue'
import ResetPassword from '@/views/auth/ResetPassword.vue'
import Dashboard from '@/views/dashboard/Dashboard.vue'
import Projects from '@/views/dashboard/Projects.vue'
import ProjectDetails from '@/views/dashboard/ProjectDetails.vue'
import Profile from '@/views/dashboard/Profile.vue'
import Checkout from '@/views/payments/Checkout.vue'
import PaymentSuccess from '@/views/payments/Success.vue'
import PaymentCancel from '@/views/payments/Cancel.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        name: 'Home',
        component: Home
      },
      {
        path: 'about',
        name: 'About',
        component: About
      },
      {
        path: 'privacy',
        name: 'Privacy',
        component: Privacy
      },
      {
        path: 'terms',
        name: 'Terms',
        component: Terms
      },
      {
        path: 'contact',
        name: 'Contact',
        component: Contact
      }
    ]
  },
  {
    path: '/auth',
    component: AuthLayout,
    meta: { hideNavbar: true, hideFooter: true },
    children: [
      {
        path: 'login',
        name: 'Login',
        component: Login
      },
      {
        path: 'register',
        name: 'Register',
        component: Register
      },
      {
        path: 'forgot-password',
        name: 'ForgotPassword',
        component: ForgotPassword
      },
      {
        path: 'reset-password/:token',
        name: 'ResetPassword',
        component: ResetPassword
      }
    ]
  },
  {
    path: '/dashboard',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: 'projects',
        name: 'Projects',
        component: Projects
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetails',
        component: ProjectDetails,
        props: true
      },
      {
        path: 'profile',
        name: 'Profile',
        component: Profile
      }
    ]
  },
  {
    path: '/payments',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'checkout',
        name: 'Checkout',
        component: Checkout
      },
      {
        path: 'success',
        name: 'PaymentSuccess',
        component: PaymentSuccess
      },
      {
        path: 'cancel',
        name: 'PaymentCancel',
        component: PaymentCancel
      }
    ]
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
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const isAuthenticated = localStorage.getItem('token') // You might want to use Vuex or a more secure method
  
  if (requiresAuth && !isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router 