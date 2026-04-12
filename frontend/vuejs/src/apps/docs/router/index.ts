import type { RouteRecordRaw } from 'vue-router'

// Views
import DocsIntroduction from '../views/DocsIntroduction.vue'
import DocsQuickStart from '../views/DocsQuickStart.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/docs',
    name: 'docs',
    component: DocsIntroduction,
    meta: {
      requiresAuth: false,
      title: 'Documentation'
    }
  },
  {
    path: '/docs/quickstart',
    name: 'docs-quickstart',
    component: DocsQuickStart,
    meta: {
      requiresAuth: false,
      title: 'Quick Start Guide'
    }
  },
  {
    path: '/docs/creating-projects',
    name: 'docs-creating-projects',
    component: () => import('../views/DocsCreatingProjects.vue'),
    meta: {
      requiresAuth: false,
      title: 'Creating Projects'
    }
  }
]

export { routes }
export default routes 