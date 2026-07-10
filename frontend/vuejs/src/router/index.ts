import { createRouter, createWebHistory } from 'vue-router'
import homeRoutes from '@/apps/home/router'
import authRoutes from '@/apps/auth/router'
import paymentsRoutes from '@/apps/payments/router'
import productsImagiRoutes from '@/apps/products/imagi/router'
import marketingRoutes from '@/apps/marketing/router'
import sellRoutes from '@/apps/sell/router'
import docsRoutes from '@/apps/docs/router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...homeRoutes,
    ...authRoutes,
    ...paymentsRoutes,
    ...productsImagiRoutes,
    ...marketingRoutes,
    ...sellRoutes,
    ...docsRoutes,
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  }
})

export default router
