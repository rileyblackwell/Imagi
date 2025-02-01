<template>
  <DashboardLayout>
    <div class="builder-landing-container">
      <div class="landing-header text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Welcome to Imagi Builder
        </h1>
        <p class="text-xl text-gray-600 dark:text-gray-400">
          Create and manage your web projects using AI-powered tools
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- Create New Project Card -->
        <div class="bg-white dark:bg-dark-800 rounded-xl p-8 border border-gray-200 dark:border-dark-700 hover:border-primary-500 transition-all duration-300">
          <div class="flex flex-col h-full">
            <div class="w-14 h-14 bg-primary-500 bg-opacity-10 rounded-xl flex items-center justify-center mb-6">
              <i class="fas fa-plus-circle text-2xl text-primary-500"></i>
            </div>
            
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Create New Project</h2>
            <p class="text-gray-600 dark:text-gray-400 mb-6">Start fresh with a new website project. Use natural language to describe your vision.</p>
            
            <form @submit.prevent="createProject" class="mt-auto">
              <div class="space-y-4">
                <div>
                  <input 
                    v-model="newProjectName"
                    type="text"
                    placeholder="Enter project name"
                    class="w-full px-4 py-3 bg-white dark:bg-dark-900 border border-gray-300 dark:border-dark-700 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                    required
                  >
                </div>
                <button 
                  type="submit"
                  :disabled="isCreating || !newProjectName.trim()"
                  class="w-full flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                >
                  <i class="fas fa-magic mr-2"></i>
                  <span v-if="isCreating">Creating Project...</span>
                  <span v-else>Create Project</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Existing Projects Card -->
        <div class="bg-white dark:bg-dark-800 rounded-xl p-8 border border-gray-200 dark:border-dark-700">
          <div class="w-14 h-14 bg-primary-500 bg-opacity-10 rounded-xl flex items-center justify-center mb-6">
            <i class="fas fa-folder-open text-2xl text-primary-500"></i>
          </div>
          
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Your Projects</h2>
          <p class="text-gray-600 dark:text-gray-400 mb-6">Continue working on your existing web projects</p>

          <div class="space-y-3 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
            <div v-if="isLoading" class="text-center py-8">
              <i class="fas fa-spinner fa-spin text-2xl text-primary-500"></i>
              <p class="mt-2 text-gray-600 dark:text-gray-400">Loading projects...</p>
            </div>

            <template v-else-if="projects.length">
              <div 
                v-for="project in projects" 
                :key="project.id"
                class="group bg-gray-50 dark:bg-dark-900 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-dark-700 transition-all duration-200"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-gray-900 dark:text-white font-medium">{{ project.name }}</h3>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Last modified: {{ formatDate(project.updated_at) }}</p>
                  </div>
                  <div class="flex items-center space-x-3">
                    <router-link
                      :to="{ name: 'builder-workspace', params: { projectId: project.id }}"
                      class="text-primary-500 hover:text-primary-400 transition-colors"
                      title="Open project"
                    >
                      <i class="fas fa-arrow-right"></i>
                    </router-link>
                    <button
                      @click="confirmDelete(project)"
                      class="text-red-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                      title="Delete project"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            </template>

            <div v-else class="text-center py-8">
              <i class="fas fa-folder-open text-4xl text-gray-400 dark:text-gray-600 mb-4"></i>
              <p class="text-gray-600 dark:text-gray-400">No projects yet. Create your first project to get started!</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DashboardLayout from '@/shared/layouts/DashboardLayout.vue'
import axios from 'axios'

export default {
  name: 'BuilderLanding',
  components: {
    DashboardLayout
  },
  setup() {
    const router = useRouter()
    const projects = ref([])
    const isLoading = ref(true)
    const newProjectName = ref('')
    const isCreating = ref(false)

    const fetchProjects = async () => {
      isLoading.value = true
      try {
        const response = await axios.get('/api/builder/projects/')
        projects.value = response.data.projects
      } catch (error) {
        console.error('Failed to fetch projects:', error)
      } finally {
        isLoading.value = false
      }
    }

    const createProject = async () => {
      if (!newProjectName.value.trim() || isCreating.value) return

      isCreating.value = true
      try {
        const response = await axios.post('/api/builder/create-project/', {
          project_name: newProjectName.value
        })
        
        if (response.data.success) {
          // Navigate to the new project's workspace
          router.push({
            name: 'builder-workspace',
            params: { projectId: response.data.project_id }
          })
        } else {
          throw new Error(response.data.error || 'Failed to create project')
        }
      } catch (error) {
        console.error('Failed to create project:', error)
        // TODO: Add error notification
      } finally {
        isCreating.value = false
      }
    }

    const confirmDelete = async (project) => {
      if (!confirm(`Are you sure you want to delete "${project.name}"? This action cannot be undone.`)) {
        return
      }

      try {
        const response = await axios.delete(`/api/builder/projects/${project.id}/`)
        if (response.data.success) {
          await fetchProjects() // Refresh the list
        } else {
          throw new Error(response.data.error || 'Failed to delete project')
        }
      } catch (error) {
        console.error('Failed to delete project:', error)
        // TODO: Add error notification
      }
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(async () => {
      await fetchProjects()
    })

    return {
      projects,
      isLoading,
      newProjectName,
      isCreating,
      createProject,
      confirmDelete,
      formatDate
    }
  }
}
</script>

<style scoped>
.builder-landing-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: theme('colors.gray.300');
  border-radius: 8px;
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: theme('colors.gray.700');
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: theme('colors.gray.400');
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: theme('colors.gray.600');
}
</style> 