import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/shared/stores/auth'
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

/**
 * One auth guard for the whole app.
 *
 * Forty routes declare `meta.requiresAuth`, but the only thing enforcing it
 * used to be an onMounted check inside DashboardLayout — which just two of
 * those routes render inside. The rest either checked for themselves or, in the
 * case of the three tool workspaces, returned early from their loader and sat
 * on an empty page forever. Now the flag means the same thing everywhere.
 *
 * The auth store reads its token from localStorage synchronously when it is
 * created, so `isAuthenticated` is already correct on the first navigation.
 */
router.beforeEach((to) => {
  if (!to.meta.requiresAuth) return true
  if (useAuthStore().isAuthenticated) return true
  return { name: 'login', query: { redirect: to.fullPath } }
})

export default router
