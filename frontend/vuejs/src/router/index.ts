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

// SCROLL HANDLING POLICY — keep it minimal and standard.
//
// iPad Chrome (WebKit) can wedge its NATIVE scroll inset: the scroll floor
// gets stuck at the toolbar height (~132px) and the page top becomes
// unreachable — for touch AND programmatic scrolling alike — until the tab
// is re-activated. On-device probing proved page JS cannot heal that state
// (overflow/height/geometry rebuilds all fail), so the only page-level lever
// is avoiding the trigger: interfering with the browser's own scroll
// management around loads, tab restores, and toolbar animations.
//
// vue-router silently sets history.scrollRestoration = 'manual' whenever
// scrollBehavior is defined. Set it back to 'auto' so the BROWSER owns
// scroll restoration on load/tab-restore/back-forward — the phases where the
// native inset wedges. scrollBehavior still applies its positions after
// render (last write wins), so in-app navigation behavior is unchanged.
//
// Also deliberately absent: pageshow/visibility scroll "nudges" and
// post-navigation scroll verification/retries. The single scrollBehavior
// scroll above is the only programmatic scroll in the app.
if (typeof window !== 'undefined' && 'scrollRestoration' in window.history) {
  window.history.scrollRestoration = 'auto'
}

export default router
