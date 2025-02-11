import Home from '../views/Home.vue'
import About from '../views/About.vue'
import Contact from '../views/Contact.vue'
import Privacy from '../views/PrivacyPolicy.vue'
import Terms from '../views/TermsOfService.vue'
import Dashboard from '../views/Dashboard.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/about',
    name: 'about',
    component: About
  },
  {
    path: '/contact',
    name: 'contact',
    component: Contact
  },
  {
    path: '/privacy',
    name: 'privacy',
    component: Privacy
  },
  {
    path: '/terms',
    name: 'terms',
    component: Terms
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

export { routes }
export default routes

// Export any additional router configuration, guards, or utilities here
export const beforeEnter = (to, from, next) => {
  // Add any route guards specific to the home app
  next()
}