<template>
  <DashboardLayout>
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Header Section -->
      <div class="mb-16">
        <div class="flex flex-col items-center text-center space-y-4">
          <div class="p-3 bg-primary-500/10 rounded-2xl">
            <i class="fas fa-wand-magic-sparkles text-2xl text-primary-400"></i>
          </div>
          <h1 class="text-4xl font-bold text-white">
            Welcome to Imagi Builder
          </h1>
          <p class="text-xl text-gray-400 max-w-2xl">
            Create and manage your web projects using AI-powered tools. Transform your ideas into reality with natural language.
          </p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <!-- Create New Project Card -->
        <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
          <div class="flex flex-col h-full">
            <div class="w-14 h-14 bg-gradient-to-br from-primary-500 to-indigo-500 rounded-xl flex items-center justify-center mb-6">
              <i class="fas fa-plus-circle text-2xl text-white"></i>
            </div>
            
            <h2 class="text-2xl font-bold text-white mb-4">Create New Project</h2>
            <p class="text-gray-400 mb-8">Start fresh with a new website project. Use natural language to describe your vision and let AI bring it to life.</p>
            
            <form @submit.prevent="createProject" class="mt-auto">
              <div class="space-y-6">
                <div class="relative">
                  <input 
                    v-model="newProjectName"
                    type="text"
                    placeholder="Enter project name"
                    class="w-full px-4 py-3 bg-dark-900/50 border border-dark-600 focus:border-primary-500/50 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                    required
                  >
                </div>
                <button 
                  type="submit"
                  :disabled="isCreating || !newProjectName.trim()"
                  class="w-full flex items-center justify-center px-6 py-3 bg-gradient-to-r from-primary-500 to-indigo-500 hover:from-primary-400 hover:to-indigo-400 text-white font-medium rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:ring-offset-2 focus:ring-offset-dark-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 group"
                >
                  <i class="fas fa-magic mr-2 group-hover:rotate-12 transition-transform duration-200"></i>
                  <span v-if="isCreating">Creating Project...</span>
                  <span v-else>Create Project</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Existing Projects Card -->
        <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
          <div class="w-14 h-14 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-xl flex items-center justify-center mb-6">
            <i class="fas fa-folder-open text-2xl text-white"></i>
          </div>
          
          <h2 class="text-2xl font-bold text-white mb-4">Your Projects</h2>
          <p class="text-gray-400 mb-8">Continue working on your existing web projects and bring your ideas to life.</p>

          <div class="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
            <div v-if="isLoading" class="flex flex-col items-center justify-center py-12">
              <div class="w-14 h-14 bg-primary-500/10 rounded-full flex items-center justify-center mb-4">
                <i class="fas fa-spinner fa-spin text-2xl text-primary-400"></i>
              </div>
              <p class="text-gray-400">Loading your projects...</p>
            </div>

            <div v-else-if="error" class="flex flex-col items-center justify-center py-12">
              <div class="w-14 h-14 bg-red-500/10 rounded-full flex items-center justify-center mb-4">
                <i class="fas fa-exclamation-circle text-2xl text-red-400"></i>
              </div>
              <p class="text-gray-400 mb-4">{{ error }}</p>
              <button 
                @click="fetchProjects" 
                class="px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded-lg transition-colors"
              >
                Try Again
              </button>
            </div>

            <template v-else-if="projects && projects.length > 0">
              <div 
                v-for="project in projects" 
                :key="project.id"
                class="group bg-dark-900/50 backdrop-blur-sm rounded-xl p-4 border border-dark-700 hover:border-primary-500/50 transition-all duration-200"
              >
                <div class="flex items-center justify-between">
                  <div>
                    <h3 class="text-white font-medium mb-1">{{ project.name }}</h3>
                    <p class="text-sm text-gray-400">Last modified: {{ formatDate(project.updated_at) }}</p>
                  </div>
                  <div class="flex items-center space-x-3">
                    <router-link
                      :to="{ name: 'builder-workspace', params: { projectId: project.id }}"
                      class="p-2 text-primary-400 hover:text-primary-300 transition-colors"
                      title="Open project"
                    >
                      <i class="fas fa-arrow-right"></i>
                    </router-link>
                    <button
                      @click="confirmDelete(project)"
                      class="p-2 text-red-400 hover:text-red-300 opacity-0 group-hover:opacity-100 transition-all duration-200"
                      title="Delete project"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </div>
              </div>
            </template>

            <div v-else class="flex flex-col items-center justify-center py-12">
              <div class="w-14 h-14 bg-dark-700 rounded-full flex items-center justify-center mb-4">
                <i class="fas fa-folder-open text-2xl text-gray-400"></i>
              </div>
              <p class="text-gray-400 text-center">No projects yet. Create your first project to get started!</p>
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
import { DashboardLayout } from '@/shared/layouts'
import axios from 'axios'

export default {
  name: 'BuilderDashboard',
  components: {
    DashboardLayout
  },
  setup() {
    const router = useRouter()
    const projects = ref([])
    const isLoading = ref(true)
    const error = ref(null)
    const newProjectName = ref('')
    const isCreating = ref(false)

    const fetchProjects = async () => {
      isLoading.value = true
      error.value = null
      try {
        const response = await axios.get('/api/builder/projects/')
        projects.value = response.data.projects || []
      } catch (err) {
        console.error('Failed to fetch projects:', err)
        error.value = 'Failed to load projects. Please try again.'
      } finally {
        isLoading.value = false
      }
    }

    const createProject = async () => {
      if (!newProjectName.value.trim() || isCreating.value) return

      isCreating.value = true
      error.value = null
      try {
        const response = await axios.post('/api/builder/create-project/', {
          project_name: newProjectName.value
        })
        
        if (response.data.success) {
          router.push({
            name: 'builder-workspace',
            params: { projectId: response.data.project_id }
          })
        } else {
          throw new Error(response.data.error || 'Failed to create project')
        }
      } catch (err) {
        console.error('Failed to create project:', err)
        error.value = err.message || 'Failed to create project. Please try again.'
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
          await fetchProjects()
        } else {
          throw new Error(response.data.error || 'Failed to delete project')
        }
      } catch (err) {
        console.error('Failed to delete project:', err)
        error.value = err.message || 'Failed to delete project. Please try again.'
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
      error,
      newProjectName,
      isCreating,
      createProject,
      confirmDelete,
      formatDate,
      fetchProjects
    }
  }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: theme('colors.gray.700');
  border-radius: 8px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: theme('colors.gray.600');
}
</style> 