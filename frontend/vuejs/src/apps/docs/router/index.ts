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
    path: '/docs/concepts',
    name: 'docs-concepts',
    component: () => import('../views/DocsConcepts.vue'),
    meta: {
      requiresAuth: false,
      title: 'Key Concepts'
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
  },
  {
    path: '/docs/project-structure',
    name: 'docs-project-structure',
    component: () => import('../views/DocsProjectStructure.vue'),
    meta: {
      requiresAuth: false,
      title: 'Project Structure'
    }
  },
  {
    path: '/docs/building-ui',
    name: 'docs-building-ui',
    component: () => import('../views/DocsBuildingUI.vue'),
    meta: {
      requiresAuth: false,
      title: 'Building UIs'
    }
  },
  {
    path: '/docs/backend',
    name: 'docs-backend',
    component: () => import('../views/DocsBackend.vue'),
    meta: {
      requiresAuth: false,
      title: 'Backend Development'
    }
  },
  {
    path: '/docs/deployment',
    name: 'docs-deployment',
    component: () => import('../views/DocsDeployment.vue'),
    meta: {
      requiresAuth: false,
      title: 'Deployment Guide'
    }
  },
  {
    path: '/docs/best-practices',
    name: 'docs-best-practices',
    component: () => import('../views/DocsBestPractices.vue'),
    meta: {
      requiresAuth: false,
      title: 'Best Practices'
    }
  }
]

export { routes }
export default routes 