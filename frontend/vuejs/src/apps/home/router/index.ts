import type { RouteRecordRaw, NavigationGuardWithThis } from 'vue-router'
import Home from '@/apps/home/views/Home.vue'
import About from '@/apps/home/views/About.vue'
import Contact from '@/apps/home/views/Contact.vue'
import Privacy from '@/apps/home/views/PrivacyPolicy.vue'
import Terms from '@/apps/home/views/TermsOfService.vue'
import Dashboard from '@/apps/home/views/Dashboard.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: Home,
    meta: {
      requiresAuth: false,
      title: 'Home'
    }
  },
  {
    path: '/about',
    name: 'about',
    component: About,
    meta: {
      requiresAuth: false,
      title: 'About'
    }
  },
  {
    path: '/contact',
    name: 'contact',
    component: Contact,
    meta: {
      requiresAuth: false,
      title: 'Contact'
    }
  },
  {
    path: '/privacy',
    name: 'privacy',
    component: Privacy,
    meta: {
      requiresAuth: false,
      title: 'Privacy Policy'
    }
  },
  {
    path: '/terms',
    name: 'terms',
    component: Terms,
    meta: {
      requiresAuth: false,
      title: 'Terms of Service'
    }
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: {
      requiresAuth: true,
      title: 'Dashboard'
    }
  }
]

// Route guard with proper TypeScript typing
export const beforeEnter: NavigationGuardWithThis<undefined> = (to, from, next) => {
  // Add any route guards specific to the home app
  next()
}

export { routes }
export default routes
