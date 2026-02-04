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
    path: '/products/imagi/workspace/:projectName',
    name: 'builder-workspace',
    component: Workspace,
    props: route => ({ 
      projectName: String(route.params.projectName)
    }),
    meta: {
      requiresAuth: true,
      title: 'Project Workspace'
    }
  }
]

export default routes
