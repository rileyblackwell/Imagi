export default [{
  path: '/auth',
  component: () => import('../layouts/AuthLayout.vue'),
  children: [
    {
      path: 'login',
      name: 'login',
      component: () => import('../views/Login.vue'),
      meta: {
        title: 'Welcome Back',
        subtitle: 'Sign in to continue to Imagi',
        mainText: 'New to Imagi?',
        mainLinkPath: '/auth/register',
        mainLinkText: 'Create an account'
      }
    },
    {
      path: 'register',
      name: 'register',
      component: () => import('../views/Register.vue'),
      meta: {
        title: 'Create Account',
        subtitle: 'Join Imagi and start building',
        mainText: 'Already have an account?',
        mainLinkPath: '/auth/login',
        mainLinkText: 'Sign in'
      }
    },
    {
      path: 'verify-email/:key',
      name: 'verify-email',
      component: () => import('../views/VerifyEmail.vue'),
      meta: {
        title: 'Verify Email',
        subtitle: 'Confirming your email address',
        mainText: 'Need help?',
        mainLinkPath: '/contact',
        mainLinkText: 'Contact Support'
      }
    }
  ]
}]