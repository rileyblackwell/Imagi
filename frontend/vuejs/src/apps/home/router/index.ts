import type { RouteRecordRaw, NavigationGuardWithThis } from 'vue-router'
import Home from '@/apps/home/views/Home.vue'
import About from '@/apps/home/views/About.vue'
import Privacy from '@/apps/home/views/PrivacyPolicy.vue'
import Terms from '@/apps/home/views/TermsOfService.vue'

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
  }
]

// Route guard with proper TypeScript typing
export const beforeEnter: NavigationGuardWithThis<undefined> = (to, from, next) => {
  // Add any route guards specific to the home app
  next()
}

export { routes }
export default routes
