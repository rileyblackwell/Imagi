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
      lastNavRestoredPosition = true
      return savedPosition
    }
    lastNavRestoredPosition = false
    return { left: 0, top: 0 }
  }
})

// Set by scrollBehavior; read by the toolbar-inset guard below so it never
// fights a legitimate back/forward position restore.
let lastNavRestoredPosition = false

// The router owns scroll restoration (scrollBehavior above). Left on 'auto',
// Safari also restores scroll natively on back/forward — racing the SPA render
// and landing pages on stale offsets with the top of the page cut off.
if (typeof window !== 'undefined' && 'scrollRestoration' in window.history) {
  window.history.scrollRestoration = 'manual'
}

// iPadOS WebKit "stale toolbar inset" guard. When the browser's collapsible
// toolbar animates during a navigation, WebKit sometimes keeps a phantom
// scroll inset equal to the toolbar height (~130px): every scroll — touch and
// programmatic alike — clamps to that floor, so the top of the page becomes
// unreachable until the engine rebuilds its scroll geometry (a tab switch
// does this, and so does toggling overflow on the root element).
// After each to-top navigation, verify the top was actually reached; if the
// engine clamped us and the user hasn't scrolled on their own, rebuild and
// retry once.
if (typeof window !== 'undefined') {
  let userScrolled = false
  const markUserScroll = () => {
    userScrolled = true
  }
  window.addEventListener('touchstart', markUserScroll, { passive: true })
  window.addEventListener('wheel', markUserScroll, { passive: true })

  router.afterEach((to, from) => {
    if (from.name === undefined) return // initial load, nothing to verify
    userScrolled = false
    setTimeout(() => {
      // Only heal a small non-zero offset the user didn't create — that is
      // the phantom-inset signature, never a legitimate resting position.
      if (lastNavRestoredPosition || userScrolled) return
      if (window.scrollY === 0 || window.scrollY > 200) return
      const de = document.documentElement
      de.style.overflow = 'hidden'
      requestAnimationFrame(() => {
        de.style.overflow = ''
        window.scrollTo(0, 0)
      })
    }, 350)
  })
}

export default router
