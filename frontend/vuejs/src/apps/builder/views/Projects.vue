<template>
  <DefaultLayout>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-bold text-white">My Projects</h1>
        <button
          @click="createNewProject"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <i class="fas fa-plus mr-2"></i>
          New Project
        </button>
      </div>

      <!-- Projects Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-if="isLoading" class="col-span-full text-center py-12">
          <i class="fas fa-spinner fa-spin text-2xl text-primary-500"></i>
          <p class="mt-2 text-gray-400">Loading projects...</p>
        </div>

        <template v-else-if="projects.length">
          <div
            v-for="project in projects"
            :key="project.id"
            class="bg-dark-800 rounded-lg shadow-xl overflow-hidden hover:ring-2 hover:ring-primary-500 transition-all duration-300"
          >
            <div class="p-6">
              <h3 class="text-xl font-semibold text-white mb-2">{{ project.name }}</h3>
              <p class="text-gray-400 text-sm mb-4">
                Last modified: {{ formatDate(project.updated_at) }}
              </p>
              <div class="flex justify-between items-center">
                <router-link
                  :to="{ name: 'project-detail', params: { id: project.id }}"
                  class="text-primary-500 hover:text-primary-400 font-medium flex items-center"
                >
                  <span>Open Project</span>
                  <i class="fas fa-arrow-right ml-2"></i>
                </router-link>
                <button
                  @click.stop="deleteProject(project)"
                  class="text-red-500 hover:text-red-400"
                  title="Delete project"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </div>
          </div>
        </template>

        <div v-else class="col-span-full text-center py-12">
          <div class="bg-dark-800 rounded-lg p-8 max-w-lg mx-auto">
            <i class="fas fa-folder-open text-4xl text-gray-600 mb-4"></i>
            <h3 class="text-xl font-semibold text-white mb-2">No Projects Yet</h3>
            <p class="text-gray-400 mb-6">Create your first project to get started building with AI</p>
            <button
              @click="createNewProject"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <i class="fas fa-plus mr-2"></i>
              Create New Project
            </button>
          </div>
        </div>
      </div>
    </div>
  </DefaultLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DefaultLayout from '@/shared/layouts/DefaultLayout.vue'
import { useProjects } from '@/apps/builder/composables/useProjects'

export default {
  name: 'Projects',
  components: {
    DefaultLayout
  },
  setup() {
    const router = useRouter()
    const { projects, isLoading, fetchProjects, createProject, deleteProject: removeProject } = useProjects()

    onMounted(async () => {
      await fetchProjects()
    })

    const createNewProject = async () => {
      try {
        const project = await createProject()
        router.push({ name: 'project-detail', params: { id: project.id }})
      } catch (error) {
        console.error('Failed to create project:', error)
        // TODO: Add error handling/notification
      }
    }

    const deleteProject = async (project) => {
      if (!confirm(`Are you sure you want to delete "${project.name}"? This action cannot be undone.`)) {
        return
      }

      try {
        await removeProject(project.id)
        await fetchProjects() // Refresh the list
      } catch (error) {
        console.error('Failed to delete project:', error)
        // TODO: Add error handling/notification
      }
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    return {
      projects,
      isLoading,
      createNewProject,
      deleteProject,
      formatDate
    }
  }
}
</script> 