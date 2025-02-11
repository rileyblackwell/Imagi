import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/auth',
    component: () => import('../layouts/AuthLayout.vue'),
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import('../views/Login.vue'),
        meta: {
          requiresAuth: false,
          layout: 'auth',
          title: 'Welcome to Imagi',
          subtitle: 'Transform your ideas into full-stack applications',
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
          title: 'Join Imagi Today',
          subtitle: 'Start building your next great idea',
          mainText: 'Already have an account?',
          mainLinkPath: '/auth/login',
          mainLinkText: 'Sign in'
        }
      }
    ]
  }
]

export { routes }
export default routes
