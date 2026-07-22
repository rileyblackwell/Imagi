import type { RouteRecordRaw } from 'vue-router'

// Views
import DocsIntroduction from '../views/DocsIntroduction.vue'

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
    path: '/docs/building',
    name: 'docs-building',
    component: () => import('../views/DocsBuildingWithAI.vue'),
    meta: {
      requiresAuth: false,
      title: 'Building with AI'
    }
  },
  {
    path: '/docs/running-your-business',
    name: 'docs-running-your-business',
    component: () => import('../views/DocsRunningYourBusiness.vue'),
    meta: {
      requiresAuth: false,
      title: 'Running Your Business'
    }
  },
  {
    path: '/docs/models',
    name: 'docs-models',
    component: () => import('../views/DocsModels.vue'),
    meta: {
      requiresAuth: false,
      title: 'Models & Reasoning'
    }
  },
  {
    path: '/docs/plans',
    name: 'docs-plans',
    component: () => import('../views/DocsPlansAndUsage.vue'),
    meta: {
      requiresAuth: false,
      title: 'Plans & Usage'
    }
  }
]

export { routes }
export default routes
