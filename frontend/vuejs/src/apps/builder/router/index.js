import BuilderWorkspace from '../views/BuilderWorkspace.vue'
import ProjectList from '../views/ProjectList.vue'
import ProjectDetail from '../views/ProjectDetail.vue'
import NewProject from '../views/NewProject.vue'

export const routes = [
  {
    path: '/builder',
    name: 'builder',
    redirect: { name: 'builder-projects' }
  },
  {
    path: '/builder/projects',
    name: 'builder-projects',
    component: ProjectList,
    meta: {
      requiresAuth: true,
      title: 'Projects'
    }
  },
  {
    path: '/builder/projects/:id',
    name: 'builder-project-detail',
    component: ProjectDetail,
    props: true,
    meta: {
      requiresAuth: true,
      title: 'Project Details'
    }
  },
  {
    path: '/builder/new',
    name: 'builder-new-project',
    component: NewProject,
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