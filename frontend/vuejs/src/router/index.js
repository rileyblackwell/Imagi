import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'
import HomePage from '@/views/Home.vue'

// Layouts
import AuthLayout from '@/views/auth/AuthLayout.vue'
import DashboardLayout from '@/views/dashboard/DashboardLayout.vue'

// Auth components
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'

// Other components
import About from '@/views/About.vue'
import Privacy from '@/views/Privacy.vue'
import Terms from '@/views/Terms.vue'
import Contact from '@/views/Contact.vue'
import Dashboard from '@/views/Dashboard.vue'
import Projects from '@/views/Projects.vue'
import ProjectDetails from '@/views/ProjectDetails.vue'
import Profile from '@/views/Profile.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomePage
  },
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: Login,
        meta: { guest: true }
      },
      {
        path: 'register',
        name: 'Register',
        component: Register,
        meta: { guest: true }
      }
    ]
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: Privacy
  },
  {
    path: '/terms',
    name: 'Terms',
    component: Terms
  },
  {
    path: '/contact',
    name: 'Contact',
    component: Contact
  },
  {
    path: '/dashboard',
    component: DashboardLayout,
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard,
        meta: { requiresAuth: true }
      },
      {
        path: 'projects',
        name: 'Projects',
        component: Projects,
        meta: { requiresAuth: true }
      },
      {
        path: 'projects/:id',
        name: 'ProjectDetails',
        component: ProjectDetails,
        meta: { requiresAuth: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: Profile,
        meta: { requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = store.getters['auth/isAuthenticated']
  
  // Routes that require authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next({
        path: '/auth/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  }
  
  // Routes for guests only (login, register)
  else if (to.matched.some(record => record.meta.guest)) {
    if (isAuthenticated) {
      next('/dashboard')
    } else {
      next()
    }
  }
  
  // Public routes
  else {
    next()
  }
})

export default router 