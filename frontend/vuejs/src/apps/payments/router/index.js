import PaymentLayout from '../layouts/PaymentLayout.vue'
import Checkout from '../views/Checkout.vue'
import Success from '../views/Success.vue'
import Cancel from '../views/Cancel.vue'
import History from '../views/History.vue'

const routes = [
  {
    path: '/payments',
    component: PaymentLayout,
    children: [
      {
        path: 'checkout',
        name: 'payments-checkout',
        component: Checkout,
        meta: {
          requiresAuth: true,
          title: 'Add Funds'
        }
      },
      {
        path: 'success',
        name: 'payments-success',
        component: Success,
        meta: {
          requiresAuth: true,
          title: 'Payment Successful'
        }
      },
      {
        path: 'cancel',
        name: 'payments-cancel',
        component: Cancel,
        meta: {
          requiresAuth: true,
          title: 'Payment Cancelled'
        }
      },
      {
        path: 'history',
        name: 'payments-history',
        component: History,
        meta: {
          requiresAuth: true,
          title: 'Payment History'
        }
      },
      // Redirect root to checkout page
      {
        path: '',
        redirect: { name: 'payments-checkout' }
      }
    ]
  }
]

export default routes 