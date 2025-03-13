<!--
  BuilderDashboard.vue - Project Management Interface
  
  This component is responsible for:
  1. Creating new projects
  2. Deleting existing projects
  3. Listing all user projects
  4. Navigating to the workspace for editing
  
  It should NOT be responsible for:
  - Project file editing (handled by BuilderWorkspace.vue)
  - File creation/deletion/updates (handled by BuilderWorkspace.vue)
-->
<template>
  <BuilderLayout 
    storage-key="builderDashboardSidebarCollapsed"
    :navigation-items="navigationItems"
  >
    <!-- Main Content with Enhanced Background -->
    <div class="min-h-screen bg-dark-900 relative overflow-hidden">
      <!-- Enhanced Background Effects -->
      <div class="absolute inset-0 pointer-events-none">
        <!-- Refined gradient background -->
        <div class="absolute inset-0 bg-gradient-to-br from-primary-500/10 via-transparent to-violet-500/10"></div>
        
        <!-- Ambient glow effects -->
        <div class="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1200px] h-[800px] bg-gradient-to-r from-primary-500/15 to-violet-500/15 rounded-full blur-[120px] opacity-40"></div>
        <div class="absolute bottom-0 right-0 w-[600px] h-[600px] bg-gradient-to-r from-indigo-500/10 to-primary-500/10 rounded-full blur-[100px] opacity-30"></div>
        
        <!-- Subtle grid pattern -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02] mix-blend-overlay"></div>
      </div>

      <!-- Content Container -->
      <div class="relative z-10">
        <!-- Welcome Section with Imagi Title Styling -->
        <div class="pt-16 pb-12 px-6 sm:px-8 lg:px-12">
          <div class="max-w-7xl mx-auto">
            <div class="text-center space-y-8">
              <!-- Imagi Title with Auth Page Styling -->
              <div class="inline-flex items-center justify-center mb-6">
                <div class="rounded-2xl bg-gradient-to-br p-[1px] from-primary-300/40 to-violet-300/40
                          hover:from-primary-200/50 hover:to-violet-200/50 transition-all duration-300">
                  <div class="px-8 py-4 rounded-2xl bg-dark-800/95 backdrop-blur-xl
                            shadow-[0_0_20px_-5px_rgba(99,102,241,0.4)]">
                    <h1 class="text-4xl font-bold bg-gradient-to-r from-pink-300 via-emerald-300 to-yellow-200 
                              bg-clip-text text-transparent tracking-tight
                              drop-shadow-[0_0_12px_rgba(236,72,153,0.3)]
                              animate-gradient">
                      Imagi
                    </h1>
                  </div>
                </div>
              </div>
              
              <!-- Enhanced Badge -->
              <div class="inline-flex items-center px-5 py-2 bg-dark-800/70 backdrop-blur-sm rounded-full border border-primary-500/30 shadow-lg shadow-primary-500/10 transform hover:scale-105 transition-all duration-300">
                <i class="fas fa-sparkles text-primary-400 mr-2.5"></i>
                <span class="text-sm font-medium bg-gradient-to-r from-gray-100 to-gray-300 bg-clip-text text-transparent">
                  AI-Powered Project Builder
                </span>
              </div>
              
              <!-- Enhanced Title -->
              <h2 class="text-4xl font-bold text-white tracking-tight">
                Welcome to Your Dashboard
              </h2>
              
              <!-- Enhanced Description -->
              <p class="text-lg text-gray-300/90 max-w-2xl mx-auto leading-relaxed">
                Create and manage your web projects using AI-powered tools. Start with a new project or continue working on existing ones.
              </p>
            </div>
          </div>
        </div>

        <!-- Authentication Error Message -->
        <div v-if="showAuthError" class="px-6 sm:px-8 lg:px-12 pb-16">
          <div class="max-w-7xl mx-auto">
            <div class="bg-dark-800/80 backdrop-blur-md rounded-2xl border border-primary-500/30 p-10 text-center shadow-xl shadow-dark-950/20 transform hover:shadow-primary-500/5 transition-all duration-300">
              <i class="fas fa-lock text-5xl text-primary-400 mb-6 opacity-80"></i>
              <h2 class="text-2xl font-semibold text-white mb-3">Authentication Required</h2>
              <p class="text-gray-300 mb-6 max-w-md mx-auto">Please log in to view and manage your projects.</p>
              <router-link 
                to="/login" 
                class="inline-flex items-center px-6 py-3 bg-gradient-to-r from-primary-500 to-violet-500 text-white rounded-xl hover:from-primary-600 hover:to-violet-600 shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 transform hover:translate-y-[-2px] transition-all duration-300"
              >
                <i class="fas fa-sign-in-alt mr-2.5"></i>
                Log In
              </router-link>
            </div>
          </div>
        </div>

        <!-- Project Section with Enhanced Layout -->
        <div v-else class="px-6 sm:px-8 lg:px-12 pb-20">
          <div class="max-w-7xl mx-auto">
            <!-- Project Cards with Refined Grid -->
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">
              <!-- New Project Card -->
              <div class="lg:col-span-5 lg:sticky lg:top-8">
                <ProjectCard
                  v-model="newProjectName"
                  :is-loading="isCreating"
                  :is-new="true"
                  @submit="createProject"
                />
              </div>

              <!-- Existing Projects List -->
              <div class="lg:col-span-7 space-y-8">
                <ProjectList
                  :projects="normalizedProjects"
                  :is-loading="isLoading || false"
                  :error="error || ''"
                  @delete="confirmDelete"
                  @retry="retryFetch"
                />
                
                <!-- Diagnostic button only shown in dev mode -->
                <div v-if="error" class="mt-6 text-center">
                  <button
                    @click="retryFetchWithDiagnostics"
                    class="px-5 py-2.5 bg-indigo-600/90 text-white rounded-xl hover:bg-indigo-700 shadow-lg shadow-indigo-600/10 hover:shadow-indigo-600/20 transform hover:translate-y-[-2px] transition-all duration-300"
                  >
                    <i class="fas fa-sync-alt mr-2"></i>
                    Run Diagnostic Fetch
                  </button>
                </div>
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
import { normalizeProject } from '@/shared/types'
import { ProjectList } from '@/apps/products/oasis/builder/components/organisms'
import { ProjectCard } from '@/apps/products/oasis/builder/components/molecules'
import { useAuthStore } from '@/shared/stores/auth'
import { useConfirm } from '../composables/useConfirm'
import api from '@/apps/products/oasis/builder/services/api'

// Extend the NotificationOptions interface to include title
interface ExtendedNotificationOptions {
  title: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
}

const router = useRouter()
const projectStore = useProjectStore()
const authStore = useAuthStore()
const { showNotification } = useNotification()
const { confirm } = useConfirm()

// State with types - remove searchQuery since it's handled in ProjectList
const newProjectName = ref('')
const isCreating = ref(false)
const isInitializing = ref(true) // Added to track initialization state

// Computed with types - remove filteredProjects
const projects = computed(() => projectStore.projects)
// Add a normalized projects computed property that ensures all projects have the required status field
const normalizedProjects = computed(() => {
  if (!projects.value) return []
  return projects.value.map(project => normalizeProject(project))
})
const isLoading = computed(() => projectStore.loading || isInitializing.value)
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

/**
 * Create a new project
 */
async function createProject() {
  if (!authStore.isAuthenticated) {
    showNotification({
      message: 'Please log in to create projects',
      type: 'error'
    })
    return
  }
  
  // Validate project name
  if (!newProjectName.value.trim()) {
    showNotification({
      message: 'Project name cannot be empty',
      type: 'error'
    })
    return
  }
  
  isCreating.value = true
  
  try {
    // Create a properly formatted project data object with name and description
    const projectData = {
      name: newProjectName.value.trim(),
      description: '' // Default empty description
    }
    
    const newProject = await projectStore.createProject(projectData)
    
    // Clear the project name field after successful creation
    newProjectName.value = ''
    
    // Log project information to debug any ID issues
    console.debug('Created project details:', {
      project: newProject,
      id: newProject.id,
      idType: typeof newProject.id
    })
    
    showNotification({
      message: `Project "${newProject.name}" created successfully`,
      type: 'success'
    })
    
    // Ensure ID is properly formatted as a string
    const projectId = String(newProject.id)
    console.debug(`Navigating to project workspace with ID: ${projectId}`)
    
    // Navigate to the new project workspace
    await router.push({
      name: 'builder-workspace',
      params: { projectId }
    })
  } catch (error: any) {
    showNotification({
      message: error?.message || 'Failed to create project',
      type: 'error'
    })
  } finally {
    isCreating.value = false
  }
}

/**
 * Load/reload the projects list
 * This is the ONLY place that should handle loading the list of all projects
 */
const fetchProjects = async (force = false) => {
  if (!authStore.isAuthenticated) {
    isInitializing.value = false
    return
  }
  
  try {
    // First, ensure project store auth state is synchronized
    if (projectStore.isAuthenticated !== authStore.isAuthenticated) {
      projectStore.setAuthenticated(authStore.isAuthenticated)
    }
    
    // Ensure we have a valid token set in the API headers
    if (authStore.token && !api.defaults.headers.common['Authorization']) {
      api.defaults.headers.common['Authorization'] = `Token ${authStore.token}`
      console.debug('Set Authorization header in fetch from authStore token')
    }
    
    await projectStore.fetchProjects(force)
    
  } catch (error: any) {
    console.error('Error fetching projects:', error)
    showNotification({
      message: error?.message || 'Failed to load projects',
      type: 'error'
    })
  } finally {
    isInitializing.value = false
  }
}

/**
 * Retry fetching projects if there was an error
 */
const retryFetch = () => {
  projectStore.clearError()
  fetchProjects(true) // Force refresh when retrying
}

/**
 * Confirm and delete a project
 * This is the ONLY place in the application that should call projectStore.deleteProject
 */
const confirmDelete = async (projectId: string, projectName: string) => {
  if (!authStore.isAuthenticated) {
    showNotification({
      message: 'Please log in to delete projects',
      type: 'error'
    })
    return
  }
  
  // Use confirm dialog
  const confirmed = await confirm({
    title: 'Delete Project',
    message: `Are you sure you want to delete "${projectName}"? This action cannot be undone.`,
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'danger'
  })
  
  if (!confirmed) {
    return
  }
  
  // Use projectStore.setLoading instead of modifying the computed property
  projectStore.setLoading(true)
  
  try {
    await projectStore.deleteProject(projectId)
    
    showNotification({
      message: `Project "${projectName}" deleted successfully`,
      type: 'success'
    })
  } catch (error: any) {
    showNotification({
      message: error?.message || `Failed to delete project "${projectName}"`,
      type: 'error'
    })
  } finally {
    // Use projectStore.setLoading instead of modifying the computed property
    projectStore.setLoading(false)
  }
}

/**
 * Directly test API connection
 * This bypasses the stores and directly tests API endpoints
 */
const testApiConnection = async () => {
  try {
    // Get token
    const tokenData = localStorage.getItem('token')
    if (!tokenData) {
      return
    }
    
    const parsedToken = JSON.parse(tokenData)
    if (!parsedToken || !parsedToken.value) {
      return
    }
    
    const token = parsedToken.value
    
    // Try different API endpoints - use only standardized endpoints
    const endpoints = [
      'api/v1/project-manager/projects/',  // Primary endpoint
      'api/v1/builder/projects/',          // Fallback endpoint
      'api/v1/agents/projects/'            // Another possible endpoint
    ]
    
    for (const endpoint of endpoints) {
      try {
        const response = await api.get(endpoint, {
          headers: {
            'Authorization': `Token ${token}`
          }
        })
        
        if (Array.isArray(response.data) || response.data?.results) {
          const projectData = Array.isArray(response.data) ? response.data : response.data.results
          projectStore.updateProjects(projectData)
          console.debug(`Successfully fetched ${projectData.length} projects from ${endpoint}`)
          return
        }
      } catch (error) {
        console.debug(`API test failed for endpoint ${endpoint}:`, error)
      }
    }
  } catch (error) {
    console.debug('API test failed:', error)
  }
}

/**
 * Enhanced debug function to diagnose project loading issues
 */
const retryFetchWithDiagnostics = async () => {
  console.debug('Running diagnostic fetch...')
  
  // Check authentication state
  console.debug('Auth state:', {
    authStoreAuthenticated: authStore.isAuthenticated,
    token: authStore.token ? 'exists' : 'missing',
    projectStoreAuthenticated: projectStore.isAuthenticated
  })
  
  // Ensure token is set in API headers
  if (authStore.token) {
    api.defaults.headers.common['Authorization'] = `Token ${authStore.token}`
    console.debug('Set Authorization header for diagnostics')
  }
  
  // Try direct access to API
  await testApiConnection()
  
  // Force a regular fetch
  fetchProjects(true)
}

/**
 * Synchronize the auth state between global auth store, module auth store,
 * and project store to ensure consistency
 */
const synchronizeStores = async () => {
  try {
    // Force auth initialization if needed
    if (!authStore.initialized) {
      await authStore.initAuth()
    }
    
    // Wait to ensure auth store is completely initialized
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Sync project store auth state with auth store
    projectStore.setAuthenticated(authStore.isAuthenticated)
    
    // Check localStorage token directly as final verification
    const tokenData = localStorage.getItem('token')
    if (tokenData) {
      try {
        const parsedToken = JSON.parse(tokenData)
        if (parsedToken && parsedToken.value && (!parsedToken.expires || Date.now() < parsedToken.expires)) {
          // We have a valid token in storage
          
          // Ensure API headers are set
          api.defaults.headers.common['Authorization'] = `Token ${parsedToken.value}`
          
          // If we have a valid token but isAuthenticated is false, validate token with API
          if (!authStore.isAuthenticated) {
            try {
              await authStore.validateAuth()
            } catch (validationError) {
              // Handle error silently
            }
          }
        }
      } catch (e) {
        // Handle error silently
      }
    }
  } catch (error) {
    // Handle error silently
  } finally {
    // If still not authenticated, make sure isInitializing is set to false
    if (!authStore.isAuthenticated) {
      isInitializing.value = false
    }
  }
}

// Set up watchers and lifecycle hooks
onMounted(async () => {
  console.debug('BuilderDashboard mounted')
  // Ensure API setup is done first
  if (authStore.isAuthenticated && authStore.token) {
    if (!api.defaults.headers.common['Authorization']) {
      api.defaults.headers.common['Authorization'] = `Token ${authStore.token}`
      console.debug('Set Authorization header on mount')
    }
  }
  
  // Fetch projects with a retry mechanism in case of failure
  try {
    await fetchProjects()
  } catch (error) {
    console.error('Initial project fetch failed:', error)
    
    // Wait a moment and try again if authentication is confirmed
    if (authStore.isAuthenticated) {
      setTimeout(async () => {
        try {
          console.debug('Retrying project fetch after initial failure')
          await fetchProjects(true)
        } catch (retryError) {
          console.error('Retry fetch also failed:', retryError)
        }
      }, 2000)
    }
  }
})

// Watch auth store authentication status
watch(
  () => authStore.isAuthenticated,
  (newAuthStatus) => {
    console.debug('Auth state changed:', newAuthStatus)
    if (newAuthStatus) {
      fetchProjects(true)
    }
  }
)
</script>

<style scoped>
/* Enhanced scrollbar styling */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.gray.700') transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 5px;
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

@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.animate-gradient {
  background-size: 200% auto;
  animation: gradient-shift 4s ease infinite;
}
</style>