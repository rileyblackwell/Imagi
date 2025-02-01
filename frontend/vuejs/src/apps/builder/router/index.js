import BuilderLanding from '../views/BuilderLanding.vue'
import BuilderWorkspace from '../views/BuilderWorkspace.vue'

export const routes = [
  {
    path: '/builder',
    name: 'builder-landing',
    component: BuilderLanding,
    meta: {
      requiresAuth: true,
      title: 'Imagi Builder'
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