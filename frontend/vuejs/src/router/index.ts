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
    return { left: 0, top: 0 }
  }
})

// The router owns scroll restoration (scrollBehavior above). Left on 'auto',
// Safari also restores scroll natively on back/forward — racing the SPA render
// and landing pages on stale offsets with the top of the page cut off.
if (typeof window !== 'undefined' && 'scrollRestoration' in window.history) {
  window.history.scrollRestoration = 'manual'
}

export default router
