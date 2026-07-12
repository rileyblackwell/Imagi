import type { RouteRecordRaw } from 'vue-router'
import Projects from '../views/Projects.vue'
import ProjectHub from '../views/ProjectHub.vue'
import ToolCategory from '../views/ToolCategory.vue'

/**
 * Project-manager routes. This module is the central hub for creating and
 * managing Imagi projects and sits alongside the build / marketing / sell /
 * operate modules rather than inside any one of them.
 *
 * The paths stay under `/imagi` (not `/imagi/build`) because they were never
 * build-specific: the project library, the per-project hub, and the generic
 * coming-soon tool template are shared entry points into every module.
 */
const routes: RouteRecordRaw[] = [
  {
    path: '/imagi',
    name: 'builder',
    redirect: { name: 'projects' }
  },
  {
    path: '/imagi/projects',
    name: 'projects',
    component: Projects,
    meta: {
      requiresAuth: true,
      title: 'Projects'
    }
  },
  {
    path: '/imagi/project/:projectName',
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
    path: '/imagi/project/:projectName/:category',
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
  }
]

export default routes
