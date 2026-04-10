import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/auth',
    component: () => import('../layouts/AuthLayout.vue'),
    children: [
      {
        path: 'signin',
        name: 'login',
        component: () => import('../views/Login.vue'),
        meta: {
          requiresAuth: false,
          layout: 'auth',
          title: 'Welcome Back',
          subtitle: 'Sign in to continue building amazing applications',
          badge: 'Secure Login',
          mainText: 'Looking to create an account?',
          mainLinkPath: '/auth/register',
          mainLinkText: 'Sign up'
        }
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('../views/Register.vue'),
        meta: {
          requiresAuth: false,
          layout: 'auth',
          title: 'Create Account',
          subtitle: 'Start building your next great idea with AI',
          badge: 'Get Started',
          mainText: 'Already have an account?',
          mainLinkPath: '/auth/signin',
          mainLinkText: 'Sign in'
        }
      }
    ]
  }
]

export { routes }
export default routes
