import type { RouteRecordRaw } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import AddCreditsView from '../views/AddCreditsView.vue'

export const routes: RouteRecordRaw[] = [
  {
    path: '/payments',
    redirect: '/payments/dashboard'
  },
  {
    path: '/payments/dashboard',
    name: 'PaymentsDashboard',
    component: DashboardView,
    meta: {
      requiresAuth: true,
      title: 'Credits Dashboard - Imagi Oasis'
    }
  },
  {
    path: '/payments/add-credits',
    name: 'AddCredits',
    component: AddCreditsView,
    meta: {
      requiresAuth: true,
      title: 'Add Credits - Imagi Oasis'
    }
  },
  // Adding a route for /payments/checkout that redirects to /payments/add-credits
  {
    path: '/payments/checkout',
    redirect: '/payments/add-credits'
  }
]

export default routes 