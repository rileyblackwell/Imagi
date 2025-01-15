export default {
  path: '/',
  children: [
    {
      path: '',
      name: 'home',
      component: () => import('./views/Home.vue'),
      meta: {
        title: 'Imagi - Build Web Apps with Natural Language'
      }
    },
    {
      path: 'about',
      name: 'about',
      component: () => import('./views/About.vue'),
      meta: {
        title: 'About - Imagi'
      }
    },
    {
      path: 'privacy',
      name: 'privacy',
      component: () => import('./views/PrivacyPolicy.vue'),
      meta: {
        title: 'Privacy Policy - Imagi'
      }
    },
    {
      path: 'terms',
      name: 'terms',
      component: () => import('./views/TermsOfService.vue'),
      meta: {
        title: 'Terms of Service - Imagi'
      }
    },
    {
      path: 'cookies',
      name: 'cookies',
      component: () => import('./views/CookiePolicy.vue'),
      meta: {
        title: 'Cookie Policy - Imagi'
      }
    }
  ]
} 