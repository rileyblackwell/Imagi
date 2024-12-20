import AuthLayout from '@/shared/layouts/AuthLayout.vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'

export default {
  path: '/auth',
  component: AuthLayout,
  children: [
    {
      path: 'login',
      name: 'login',
      component: Login,
      meta: {
        title: 'Login - Imagi',
        requiresGuest: true
      }
    },
    {
      path: 'register',
      name: 'register',
      component: Register,
      meta: {
        title: 'Register - Imagi',
        requiresGuest: true
      }
    }
  ]
} 