import { createRouter } from 'vue-router'
import PaymentLayout from '../layouts/PaymentLayout.vue'
import Credits from '../views/Credits.vue'
import Checkout from '../views/Checkout.vue'
import Success from '../views/Success.vue'
import Cancel from '../views/Cancel.vue'

const routes = [
  {
    path: '/payments',
    component: PaymentLayout,
    children: [
      {
        path: '',
        name: 'credits',
        component: Credits,
        meta: { requiresAuth: true }
      },
      {
        path: 'checkout',
        name: 'checkout',
        component: Checkout,
        meta: { requiresAuth: true }
      },
      {
        path: 'success',
        name: 'payment-success',
        component: Success,
        meta: { requiresAuth: true }
      },
      {
        path: 'cancel',
        name: 'payment-cancel',
        component: Cancel,
        meta: { requiresAuth: true }
      }
    ]
  }
]

export default routes 