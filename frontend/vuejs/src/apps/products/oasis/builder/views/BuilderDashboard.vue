<template>
  <BuilderLayout 
    storage-key="builderDashboardSidebarCollapsed"
    :navigation-items="navigationItems"
  >
    <!-- Main Content with Refined Background -->
    <div class="min-h-screen bg-dark-900 relative overflow-hidden">
      <!-- Enhanced Background Effects -->
      <div class="absolute inset-0 pointer-events-none">
        <!-- Subtle gradient background -->
        <div class="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-transparent to-violet-500/5"></div>
        
        <!-- Centered glow effect -->
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-r from-primary-500/10 to-violet-500/10 rounded-full blur-[80px] opacity-30"></div>
        
        <!-- Grid pattern with reduced opacity -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.015] mix-blend-overlay"></div>
      </div>

      <!-- Content Container -->
      <div class="relative">
        <!-- Welcome Section with Refined Styling -->
        <div class="pt-12 pb-8 px-4 sm:px-6 lg:px-8">
          <div class="max-w-7xl mx-auto">
            <div class="text-center space-y-6">
              <!-- Enhanced Badge -->
              <div class="inline-flex items-center px-4 py-1.5 bg-dark-800/70 backdrop-blur-sm rounded-full border border-primary-500/20 shadow-lg shadow-primary-500/5">
                <i class="fas fa-sparkles text-primary-400 mr-2"></i>
                <span class="text-sm font-medium bg-gradient-to-r from-gray-200 to-gray-100 bg-clip-text text-transparent">
                  AI-Powered Project Builder
                </span>
              </div>
              
              <!-- Enhanced Title -->
              <h1 class="text-4xl font-bold text-white">
                Welcome to Your Dashboard
              </h1>
              
              <!-- Enhanced Description -->
              <p class="text-lg text-gray-300/90 max-w-2xl mx-auto leading-relaxed">
                Create and manage your web projects using AI-powered tools. Start with a new project or continue working on existing ones.
              </p>
            </div>
          </div>
        </div>

        <!-- Authentication Error Message -->
        <div v-if="showAuthError" class="px-4 sm:px-6 lg:px-8 pb-12">
          <div class="max-w-7xl mx-auto">
            <div class="bg-dark-800/70 backdrop-blur-sm rounded-lg border border-primary-500/20 p-8 text-center">
              <i class="fas fa-lock text-4xl text-primary-400 mb-4"></i>
              <h2 class="text-xl font-semibold text-white mb-2">Authentication Required</h2>
              <p class="text-gray-300 mb-4">Please log in to view and manage your projects.</p>
              <router-link 
                to="/login" 
                class="inline-flex items-center px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
              >
                <i class="fas fa-sign-in-alt mr-2"></i>
                Log In
              </router-link>
            </div>
          </div>
        </div>

        <!-- Project Section with Enhanced Layout -->
        <div v-else class="px-4 sm:px-6 lg:px-8 pb-12">
          <div class="max-w-7xl mx-auto">
            <!-- Project Cards with Refined Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <!-- New Project Card -->
              <div class="lg:sticky lg:top-8">
                <ProjectCard
                  v-model="newProjectName"
                  :is-loading="isCreating"
                  :is-new="true"
                  @submit="createProject"
                />
              </div>

              <!-- Existing Projects List -->
              <div class="space-y-6">
                <ProjectList
                  :projects="projects"
                  :is-loading="isLoading"
                  :error="error"
                  @delete="confirmDelete"
                  @retry="retryFetch"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </BuilderLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts'
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore'
import { useNotification } from '@/shared/composables/useNotification'
import type { Project } from '@/shared/types'
import { ProjectList } from '@/apps/products/oasis/builder/components/organisms'
import { ProjectCard } from '@/apps/products/oasis/builder/components/molecules'
import { useAuthStore } from '@/apps/auth/store'

const router = useRouter()
const projectStore = useProjectStore()
const authStore = useAuthStore()
const { showNotification } = useNotification()

// State with types - remove searchQuery since it's handled in ProjectList
const newProjectName = ref('')
const isCreating = ref(false)

// Computed with types - remove filteredProjects
const projects = computed(() => projectStore.projects)
const isLoading = computed(() => projectStore.loading)
const error = computed(() => projectStore.error || '')
const showAuthError = computed(() => !authStore.isAuthenticated && !isLoading.value)

// Navigation items
const navigationItems = [
  { 
    name: 'Main Dashboard',
    to: '/dashboard',
    icon: 'fas fa-th-large',
    exact: true
  },
  {
    name: 'Projects',
    to: '/products/oasis/builder/projects',
    icon: 'fas fa-folder',
    exact: true
  }
];

// Methods
const createProject = async () => {
  if (!newProjectName.value.trim() || isCreating.value) return

  isCreating.value = true
  try {
    const project = await projectStore.createProject({
      name: newProjectName.value.trim(),
      description: ''
    })
    
    if (project?.id === undefined) { // Fix type comparison
      throw new Error('Failed to create project - no ID returned')
    }

    showNotification({
      type: 'success',
      message: 'Project created successfully!'
    })

    newProjectName.value = ''
    
    await new Promise(resolve => setTimeout(resolve, 100))
    
    await router.push({
      name: 'builder-workspace',
      params: { projectId: String(project.id) }
    })
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Failed to create project'
    console.error('Project creation error in dashboard:', errorMessage)
    showNotification({
      type: 'error',
      message: errorMessage
    })
  } finally {
    isCreating.value = false
  }
}

const confirmDelete = async (project: Project) => {
  if (!project?.id) {
    showNotification({
      type: 'error',
      message: 'Invalid project data'
    })
    return
  }

  if (!confirm(`Are you sure you want to delete "${project.name}"?`)) {
    return
  }

  try {
    await projectStore.deleteProject(String(project.id))
    showNotification({
      type: 'success',
      message: 'Project deleted successfully'
    })
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Failed to delete project'
    console.error('Project deletion error:', errorMessage)
    showNotification({
      type: 'error',
      message: errorMessage
    })
  }
}

async function retryFetch() {
  projectStore.clearError()
  await fetchProjects()
}

const fetchProjects = async () => {
  try {
    console.debug('Dashboard: Initiating project fetch')
    await projectStore.fetchProjects(true) // Force refresh
    console.debug('Dashboard: Projects loaded:', projectStore.projects.length)
  } catch (error: unknown) { // Add type annotation
    const errorMessage = error instanceof Error ? error.message : 'Failed to fetch projects'
    console.error('Dashboard: Project fetch error:', errorMessage)
    showNotification({
      type: 'error',
      message: errorMessage
    })
  }
}

// Lifecycle
onMounted(async () => {
  console.debug('Dashboard: Component mounted', {
    isAuthenticated: authStore.isAuthenticated
  })
  
  projectStore.setAuthenticated(authStore.isAuthenticated)
  await fetchProjects()
})

// Add watcher for project loading state
watch(() => projectStore.loading, (isLoading) => {
  console.debug('Project loading state changed:', isLoading)
})

// Add watcher for projects array
watch(() => projectStore.projects, (projects) => {
  console.debug('Projects updated:', projects.length)
}, { deep: true })

// Add watcher for authentication state
watch(() => authStore.isAuthenticated, async (newValue) => {
  console.debug('Authentication state changed:', newValue)
  projectStore.setAuthenticated(newValue)
  if (newValue) {
    await fetchProjects()
  }
})
</script>

<style scoped>
/* Enhanced scrollbar styling */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.gray.700') transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: theme('colors.gray.700');
  border-radius: 9999px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: theme('colors.gray.600');
}
</style>