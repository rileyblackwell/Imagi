import type { RouteRecordRaw } from 'vue-router'
import Workspace from '../views/Workspace.vue'

/**
 * Build routes. The build module owns only the AI app builder workspace. The
 * project library and per-project hub now live in the project-manager module,
 * which sits alongside build / marketing / sell / operate.
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/imagi/workspace/:projectName',
    name: 'builder-workspace',
    component: Workspace,
    props: route => ({
      projectName: String(route.params.projectName)
    }),
    meta: {
      requiresAuth: true,
      title: 'App Builder'
    }
  }
]

export default routes
