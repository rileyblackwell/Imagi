import PaymentLayout from '../layouts/PaymentLayout.vue'
import Checkout from '../views/Checkout.vue'
import Credits from '../views/Credits.vue'
import Success from '../views/Success.vue'
import Cancel from '../views/Cancel.vue'
import History from '../views/History.vue'

const routes = [
  {
    path: '/payments',
    component: PaymentLayout,
    children: [
      {
        path: 'credits',
        name: 'payments-credits',
        component: Credits,
        meta: {
          requiresAuth: true,
          title: 'Add Credits'
        }
      },
      {
        path: 'checkout',
        name: 'payments-checkout',
        component: Checkout,
        meta: {
          requiresAuth: true,
          title: 'Checkout'
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
      // Redirect root to credits page
      {
        path: '',
        redirect: { name: 'payments-credits' }
      }
    ]
  }
]

export default routes 