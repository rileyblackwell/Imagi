import type { RouteRecordRaw } from 'vue-router'
import PricingView from '../views/PricingView.vue'

export const routes: RouteRecordRaw[] = [
  {
    path: '/payments',
    redirect: '/payments/pricing'
  },
  {
    path: '/payments/pricing',
    name: 'Pricing',
    component: PricingView,
    meta: {
      requiresAuth: false,
      title: 'Pricing - Imagi'
    }
  },
  {
    path: '/payments/checkout',
    redirect: '/payments/pricing'
  },
  {
    path: '/payments/success',
    name: 'PaymentSuccess',
    component: () => import('../views/PaymentSuccessView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Payment Successful - Imagi'
    }
  },
  {
    path: '/payments/cancel',
    name: 'PaymentCancel',
    component: () => import('../views/PaymentCancelView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Payment Cancelled - Imagi'
    }
  }
]

export default routes 