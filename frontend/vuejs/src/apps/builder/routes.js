export default {
  path: '',
  children: [
    {
      path: '',
      name: 'builder',
      component: () => import('./views/Builder.vue'),
      meta: {
        title: 'Oasis Builder - Imagi',
        requiresAuth: true
      }
    },
    {
      path: 'projects',
      name: 'projects',
      component: () => import('./views/Projects.vue'),
      meta: {
        title: 'My Projects - Imagi',
        requiresAuth: true
      }
    },
    {
      path: 'projects/:id',
      name: 'project-detail',
      component: () => import('./views/ProjectDetail.vue'),
      meta: {
        title: 'Project Details - Imagi',
        requiresAuth: true
      }
    }
  ]
} 