import type { RouteRecordRaw } from 'vue-router'
import SellWorkspace from '../views/SellWorkspace.vue'
import SellOverview from '../views/SellOverview.vue'
import SellProducts from '../views/SellProducts.vue'
import SellOrders from '../views/SellOrders.vue'
import SellCustomers from '../views/SellCustomers.vue'
import SellSettings from '../views/SellSettings.vue'
import CheckoutReturn from '../views/CheckoutReturn.vue'

/**
 * Sell workspace routes, nested under a project. The static `sales` segment
 * (the tool's slug in businessTools.ts) takes precedence over the generic
 * `:category` coming-soon route.
 *
 * The /checkout/... routes are public landing pages for customers coming
 * back from a Stripe Checkout started via a payment link.
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/products/imagi/project/:projectName/sales',
    component: SellWorkspace,
    props: route => ({
      projectName: String(route.params.projectName)
    }),
    meta: {
      requiresAuth: true,
      title: 'Sell'
    },
    children: [
      {
        path: '',
        name: 'sell-overview',
        component: SellOverview,
        meta: { requiresAuth: true, title: 'Sell Overview' }
      },
      {
        path: 'products',
        name: 'sell-products',
        component: SellProducts,
        meta: { requiresAuth: true, title: 'Products' }
      },
      {
        path: 'orders',
        name: 'sell-orders',
        component: SellOrders,
        meta: { requiresAuth: true, title: 'Orders' }
      },
      {
        path: 'customers',
        name: 'sell-customers',
        component: SellCustomers,
        meta: { requiresAuth: true, title: 'Customers' }
      },
      {
        path: 'settings',
        name: 'sell-settings',
        component: SellSettings,
        meta: { requiresAuth: true, title: 'Sell Settings' }
      }
    ]
  },
  {
    path: '/checkout/:projectId/success',
    name: 'sell-checkout-success',
    component: CheckoutReturn,
    meta: { title: 'Payment' }
  },
  {
    path: '/checkout/:projectId/cancel',
    name: 'sell-checkout-cancel',
    component: CheckoutReturn,
    props: { canceled: true },
    meta: { title: 'Checkout canceled' }
  }
]

export default routes
