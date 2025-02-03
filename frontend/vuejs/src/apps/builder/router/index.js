import BuilderDashboard from '../views/BuilderDashboard.vue'
import BuilderWorkspace from '../views/BuilderWorkspace.vue'
import Dashboard from '../views/Dashboard.vue'

export const routes = [
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: {
      requiresAuth: true,
      title: 'Dashboard'
    }
  },
  {
    path: '/builder/dashboard',
    name: 'builder-dashboard',
    component: BuilderDashboard,
    meta: {
      requiresAuth: true,
      title: ''
    }
  },
  {
    path: '/builder/project/:projectId',
    name: 'builder-workspace',
    component: BuilderWorkspace,
    meta: {
      requiresAuth: true,
      title: 'Project Workspace'
    },
    props: true
  }
]

export default routes 