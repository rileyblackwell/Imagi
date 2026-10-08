import type { RouteRecordRaw } from 'vue-router'
import { brand } from '../brand'

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
          title: brand.signIn.title,
          subtitle: brand.signIn.subtitle
        }
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('../views/Register.vue'),
        meta: {
          requiresAuth: false,
          layout: 'auth',
          title: brand.register.title,
          subtitle: brand.register.subtitle
        }
      }
    ]
  }
]

export { routes }
export default routes
