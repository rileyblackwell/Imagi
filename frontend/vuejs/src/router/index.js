import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/apps/home/views/Home.vue'
import AboutView from '@/apps/home/views/About.vue'
import ContactView from '@/apps/home/views/Contact.vue'
import CareersView from '@/apps/home/views/Careers.vue'
import CookiePolicyView from '@/apps/home/views/CookiePolicy.vue'
import PrivacyPolicyView from '@/apps/home/views/PrivacyPolicy.vue'
import TermsView from '@/apps/home/views/Terms.vue'
import NotFoundView from '@/shared/views/NotFound.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView
    },
    {
      path: '/contact',
      name: 'contact',
      component: ContactView
    },
    {
      path: '/careers',
      name: 'careers',
      component: CareersView
    },
    {
      path: '/cookies',
      name: 'cookies',
      component: CookiePolicyView
    },
    {
      path: '/privacy',
      name: 'privacy',
      component: PrivacyPolicyView
    },
    {
      path: '/terms',
      name: 'terms',
      component: TermsView
    },
    {
      path: '/auth',
      component: () => import('@/apps/auth/layouts/AuthLayout.vue'),
      children: [
        {
          path: 'login',
          name: 'login',
          component: () => import('@/apps/auth/views/Login.vue')
        },
        {
          path: 'register',
          name: 'register',
          component: () => import('@/apps/auth/views/Register.vue')
        },
        {
          path: 'forgot-password',
          name: 'forgot-password',
          component: () => import('@/apps/auth/views/ForgotPassword.vue')
        },
        {
          path: 'reset-password',
          name: 'reset-password',
          component: () => import('@/apps/auth/views/ResetPassword.vue')
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView
    }
  ]
})

export default router 