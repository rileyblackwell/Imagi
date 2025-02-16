import type { RouteRecordRaw } from 'vue-router'
import {
  BuilderDashboard,
  BuilderWorkspace,
  Projects,
  NewProjectPage
} from '../components/pages'

const routes: RouteRecordRaw[] = [
  {
    path: '/builder',
    name: 'builder',
    redirect: { name: 'builder-dashboard' }
  },
  {
    path: '/builder/dashboard',
    name: 'builder-dashboard',
    component: BuilderDashboard,
    meta: {
      requiresAuth: true,
      title: 'Builder Dashboard'
    }
  },
  {
    path: '/builder/projects',
    name: 'builder-projects',
    component: Projects,
    meta: {
      requiresAuth: true,
      title: 'Projects'
    }
  },
  {
    path: '/builder/new',
    name: 'builder-new-project',
    component: NewProjectPage,
    meta: {
      requiresAuth: true,
      title: 'New Project'
    }
  },
  {
    path: '/builder/workspace/:projectId',
    name: 'builder-workspace',
    component: BuilderWorkspace,
    props: route => ({ 
      projectId: String(route.params.projectId)
    }),
    meta: {
      requiresAuth: true,
      title: 'Project Workspace'
    }
  }
]

export default routes
