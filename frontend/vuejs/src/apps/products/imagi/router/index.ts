import type { RouteRecordRaw } from 'vue-router'
import Projects from '../views/Projects.vue'
import Workspace from '../views/Workspace.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/products/imagi',
    name: 'builder',
    redirect: { name: 'projects' }
  },
  {
    path: '/products/imagi/projects',
    name: 'projects',
    component: Projects,
    meta: {
      requiresAuth: true,
      title: 'Projects'
    }
  },
  {
    path: '/products/imagi/workspace/:projectId',
    name: 'builder-workspace',
    component: Workspace,
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
