import type { RouteRecordRaw } from 'vue-router'
import { paymentsConfig } from '../config'

const returnRoutes = (base: string, name: string): RouteRecordRaw[] => [
  {
    path: `${base}/success`,
    name: `${name}-checkout-success`,
    component: () => import('../views/CheckoutReturnView.vue'),
    props: { backPath: base },
    meta: { title: 'Payment' }
  },
  {
    path: `${base}/cancel`,
    name: `${name}-checkout-cancel`,
    component: () => import('../views/CheckoutReturnView.vue'),
    props: { backPath: base, canceled: true },
    meta: { title: 'Checkout canceled' }
  }
]

const routes: RouteRecordRaw[] = []

if (paymentsConfig.pages.pricing) {
  routes.push(
    {
      path: '/pricing',
      name: 'pricing',
      component: () => import('../views/PricingView.vue'),
      meta: { title: 'Pricing' }
    },
    ...returnRoutes('/pricing', 'pricing')
  )
}

if (paymentsConfig.pages.store) {
  routes.push(
    {
      path: '/store',
      name: 'store',
      component: () => import('../views/StoreView.vue'),
      meta: { title: 'Store' }
    },
    ...returnRoutes('/store', 'store')
  )
}

export { routes }
export default routes
