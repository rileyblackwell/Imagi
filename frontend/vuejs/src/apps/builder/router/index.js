import BuilderDashboard from '../views/BuilderDashboard.vue'
import BuilderWorkspace from '../views/BuilderWorkspace.vue'

export const routes = [
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
    path: '/builder/project/:projectId',
    name: 'builder-workspace',
    component: BuilderWorkspace,
    props: route => ({ 
      projectId: String(route.params.projectId)
    }),
    meta: {
      requiresAuth: true,
      title: 'Project Workspace'
    },
    beforeEnter: (to, from, next) => {
      const projectId = to.params.projectId;
      if (!projectId || isNaN(projectId)) {
        next({ name: 'builder-dashboard' });
      } else {
        next();
      }
    }
  }
]

export default routes