export default [{
  path: '/auth',
  component: () => import('../layouts/AuthLayout.vue'),
  children: [
    {
      path: 'login',
      name: 'login',
      component: () => import('../views/Login.vue'),
      meta: {
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
      component: () => import('../views/Register.vue'),  // Changed to dynamic import
      meta: {
        title: 'Join Imagi Today',
        subtitle: 'Start building your next great idea',
        mainText: 'Already have an account?',
        mainLinkPath: '/auth/login',
        mainLinkText: 'Sign in'
      }
    }
  ]
}]