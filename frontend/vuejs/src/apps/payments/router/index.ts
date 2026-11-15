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
  // The paid plans' checkout and its return pages were removed with them;
  // old links land on pricing.
  { path: '/payments/checkout', redirect: '/payments/pricing' },
  { path: '/payments/success', redirect: '/payments/pricing' },
  { path: '/payments/cancel', redirect: '/payments/pricing' }
]

export default routes 