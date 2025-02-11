import BuilderDashboard from '../views/BuilderDashboard.vue'
import BuilderWorkspace from '../views/BuilderWorkspace.vue'
import Projects from '../views/Projects.vue'

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
  },
  {
    path: '/builder/projects',
    name: 'builder-projects',
    component: Projects,
    meta: {
      requiresAuth: true,
      title: 'Projects'
    }
  }
]

export default routes