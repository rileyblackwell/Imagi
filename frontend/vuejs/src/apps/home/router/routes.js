import BaseLayout from '@/shared/layouts/BaseLayout.vue'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import Contact from '../views/Contact.vue'
import Privacy from '../views/PrivacyPolicy.vue'
import Terms from '../views/TermsOfService.vue'

export default {
  path: '/',
  component: BaseLayout,
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
    }
  ]
} 