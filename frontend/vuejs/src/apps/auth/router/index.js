import AuthLayout from '../layouts/AuthLayout.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import ForgotPassword from '../views/ForgotPassword.vue'

const authRoutes = [{
  path: '/auth',
  component: AuthLayout,
  children: [
    {
      path: '',
      redirect: { name: 'login' }
    },
    {
      path: 'login',
      name: 'login',
      component: () => import('../views/Login.vue'),
      meta: {
        title: 'Login - Imagi',
        requiresGuest: true
      }
    },
    {
      path: 'register',
      name: 'register',
      component: () => import('../views/Register.vue'),
      meta: {
        title: 'Register - Imagi',
        requiresGuest: true
      }
    },
    {
      path: 'forgot-password',
      name: 'forgot-password',
      component: () => import('../views/ForgotPassword.vue'),
      meta: {
        title: 'Reset Password - Imagi',
        requiresGuest: true
      }
    }
  ]
}]

export default authRoutes 