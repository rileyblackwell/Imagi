import type { RouteRecordRaw } from 'vue-router'
import BuilderDashboard from '../views/BuilderDashboard.vue'
import BuilderWorkspace from '../views/BuilderWorkspace.vue'
import Projects from '../views/Projects.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/products/oasis/builder',
    name: 'builder',
    redirect: { name: 'builder-dashboard' }
  },
  {
    path: '/products/oasis/builder/dashboard',
    name: 'builder-dashboard',
    component: BuilderDashboard,
    meta: {
      requiresAuth: true,
      title: 'Builder Dashboard'
    }
  },
  {
    path: '/products/oasis/builder/projects',
    name: 'builder-projects',
    component: Projects,
    meta: {
      requiresAuth: true,
      title: 'Projects'
    }
  },
  {
    path: '/products/oasis/builder/workspace/:projectId',
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
