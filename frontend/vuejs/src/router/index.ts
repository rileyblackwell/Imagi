import { createRouter, createWebHistory } from 'vue-router'
import homeRoutes from '@/apps/home/router'
import authRoutes from '@/apps/auth/router'
import paymentsRoutes from '@/apps/payments/router'
import buildRoutes from '@/apps/imagi/build/router'
import projectManagerRoutes from '@/apps/imagi/project-manager/router'
import marketingRoutes from '@/apps/imagi/marketing/router'
import sellRoutes from '@/apps/imagi/sell/router'
import operateRoutes from '@/apps/imagi/operate/router'
import docsRoutes from '@/apps/docs/router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    ...homeRoutes,
    ...authRoutes,
    ...paymentsRoutes,
    ...buildRoutes,
    ...projectManagerRoutes,
    ...marketingRoutes,
    ...sellRoutes,
    ...operateRoutes,
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
