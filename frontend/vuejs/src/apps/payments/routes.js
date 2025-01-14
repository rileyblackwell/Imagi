export default {
  path: '/payments',
  children: [
    {
      path: 'checkout',
      name: 'checkout',
      component: () => import('./views/Checkout.vue'),
      meta: {
        title: 'Checkout - Imagi',
        requiresAuth: true
      }
    },
    {
      path: 'success',
      name: 'payment-success',
      component: () => import('./views/Success.vue'),
      meta: {
        title: 'Payment Successful - Imagi',
        requiresAuth: true
      }
    },
    {
      path: 'cancel',
      name: 'payment-cancel',
      component: () => import('./views/Cancel.vue'),
      meta: {
        title: 'Payment Cancelled - Imagi',
        requiresAuth: true
      }
    }
  ]
} 