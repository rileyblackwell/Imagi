import AuthLayout from './layouts/AuthLayout.vue'
import Login from './views/Login.vue'
import Register from './views/Register.vue'
import ForgotPassword from './views/ForgotPassword.vue'

const authRoutes = {
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
    },
    {
      path: 'forgot-password',
      name: 'forgot-password',
      component: ForgotPassword,
      meta: {
        title: 'Reset Password - Imagi',
        requiresGuest: true
      }
    }
  ]
}

export default authRoutes 