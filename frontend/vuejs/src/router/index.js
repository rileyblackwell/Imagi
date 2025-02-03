import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/apps/auth/store'

// Routes
import homeRoutes from '@/apps/home/router'
import authRoutes from '@/apps/auth/router'
import builderRoutes from '@/apps/builder/router'
import paymentsRoutes from '@/apps/payments/router'
import NotFound from '@/shared/views/NotFound.vue'

// Completely disable bfcache
if ('navigationPreload' in navigator.serviceWorker) {
  navigator.serviceWorker.ready.then(registration => {
    registration.navigationPreload.disable();
  });
}

// Force disable bfcache
window.addEventListener('load', () => {
  // Add no-store header
  const meta = document.createElement('meta');
  meta.httpEquiv = 'Cache-Control';
  meta.content = 'no-store';
  document.head.appendChild(meta);

  // Add no-cache header
  const pragmaMeta = document.createElement('meta');
  pragmaMeta.httpEquiv = 'Pragma';
  pragmaMeta.content = 'no-cache';
  document.head.appendChild(pragmaMeta);

  // Add expires header
  const expiresMeta = document.createElement('meta');
  expiresMeta.httpEquiv = 'Expires';
  expiresMeta.content = '0';
  document.head.appendChild(expiresMeta);
});

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes: [
    ...homeRoutes,
    ...authRoutes,
    ...builderRoutes,
    ...paymentsRoutes,
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFound
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Force page reload on back/forward
window.addEventListener('pageshow', (event) => {
  if (event.persisted || (window.performance && window.performance.navigation.type === 2)) {
    window.location.reload(true);
  }
});

// Force page reload on popstate
window.addEventListener('popstate', () => {
  window.location.reload(true);
});

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  
  // Check if route requires guest access
  if (to.meta.requiresGuest && isAuthenticated) {
    next({ name: 'home' })
    return
  }
  
  // Update document title
  document.title = to.meta.title ? `${to.meta.title} - Imagi` : 'Imagi'
  
  next()
})

// Handle navigation errors
router.onError((error) => {
  // Just log the error and continue
  console.error('Router error:', error)
})

export default router 