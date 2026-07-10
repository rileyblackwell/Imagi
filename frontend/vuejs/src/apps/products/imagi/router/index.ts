import type { RouteRecordRaw } from 'vue-router'
import Projects from '../views/Projects.vue'
import ProjectHub from '../views/ProjectHub.vue'
import ToolCategory from '../views/ToolCategory.vue'
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
    path: '/products/imagi/project/:projectName',
    name: 'project-hub',
    component: ProjectHub,
    props: route => ({
      projectName: String(route.params.projectName)
    }),
    meta: {
      requiresAuth: true,
      title: 'Project Workspace'
    }
  },
  {
    path: '/products/imagi/project/:projectName/:category',
    name: 'project-tool',
    component: ToolCategory,
    props: route => ({
      projectName: String(route.params.projectName),
      category: String(route.params.category)
    }),
    meta: {
      requiresAuth: true,
      title: 'Business Tools'
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
      title: 'App Builder'
    }
  }
]

export default routes
