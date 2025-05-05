import type { RouteRecordRaw } from 'vue-router'
import CheckoutView from '../views/CheckoutView.vue'

export const routes: RouteRecordRaw[] = [
  {
    path: '/payments',
    redirect: '/payments/checkout'
  },
  {
    path: '/payments/checkout',
    name: 'Checkout',
    component: CheckoutView,
    meta: {
      requiresAuth: true,
      title: 'Checkout - Imagi Oasis'
    }
  },
  {
    path: '/payments/history',
    name: 'PaymentHistory',
    component: () => import('../views/PaymentHistoryView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Payment History - Imagi Oasis'
    }
  },
  {
    path: '/payments/success',
    name: 'PaymentSuccess',
    component: () => import('../views/PaymentSuccessView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Payment Successful - Imagi Oasis'
    }
  },
  {
    path: '/payments/cancel',
    name: 'PaymentCancel',
    component: () => import('../views/PaymentCancelView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Payment Cancelled - Imagi Oasis'
    }
  }
]

export default routes 