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
                  :projects="projects || []"
                  :is-loading="isLoading || false"
                  :error="error || ''"
                  @delete="confirmDelete"
                  @retry="retryFetch"
                />
                
                <!-- Diagnostic button only shown in dev mode -->
                <div v-if="error" class="mt-4 text-center">
                  <button
                    @click="retryFetchWithDiagnostics"
                    class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
                  >
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
import { ProjectList } from '@/apps/products/oasis/builder/components/organisms'
import { ProjectCard } from '@/apps/products/oasis/builder/components/molecules'
import { useAuthStore } from '@/shared/stores/auth'
import { useConfirm } from '../composables/useConfirm'
import api from '@/apps/products/oasis/builder/services/api'

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
 * This is the ONLY place in the application that should call projectStore.createProject
 */
async function createProject(projectData: { name: string; description: string }) {
  if (!authStore.isAuthenticated) {
    showNotification({
      title: 'Authentication Required',
      message: 'Please log in to create projects',
      type: 'error'
    })
    return
  }
  
  isCreating.value = true
  
  try {
    console.log('Creating new project:', projectData)
    
    const newProject = await projectStore.createProject(projectData)
    
    showNotification({
      title: 'Success',
      message: `Project "${newProject.name}" created successfully`,
      type: 'success'
    })
    
    // Navigate to the new project workspace
    await router.push({
      name: 'builder-workspace',
      params: { id: newProject.id.toString() }
    })
  } catch (error: any) {
    console.error('Error creating project:', error)
    
    showNotification({
      title: 'Error',
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
  console.log('BuilderDashboard: fetchProjects called', {
    authState: authStore.isAuthenticated,
    projectStoreAuthState: projectStore.isAuthenticated,
    force,
    isInitializing: isInitializing.value
  })
  
  if (!authStore.isAuthenticated) {
    console.log('User not authenticated, skipping project fetch')
    isInitializing.value = false
    return
  }
  
  try {
    // First, ensure project store auth state is synchronized
    if (projectStore.isAuthenticated !== authStore.isAuthenticated) {
      console.log('Synchronizing project store auth state with global auth store')
      projectStore.setAuthenticated(authStore.isAuthenticated)
    }
    
    // Ensure we have a valid token set in the API headers
    if (authStore.token && !api.defaults.headers.common['Authorization']) {
      console.log('Setting authorization header from auth store token')
      api.defaults.headers.common['Authorization'] = `Token ${authStore.token}`
    }
    
    console.log('Fetching projects list, force =', force)
    await projectStore.fetchProjects(force)
    
    if (!projectStore.hasProjects && !projectStore.error) {
      console.log('No projects found')
    } else {
      console.log('Projects loaded successfully:', projectStore.projects.length)
    }
  } catch (error: any) {
    console.error('Error fetching projects:', error)
    
    showNotification({
      title: 'Error',
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
  console.log('Retrying fetch with enhanced diagnostics...')
  projectStore.clearError()
  retryFetchWithDiagnostics()
}

/**
 * Confirm and delete a project
 * This is the ONLY place in the application that should call projectStore.deleteProject
 */
const confirmDelete = async (projectId: string, projectName: string) => {
  if (!authStore.isAuthenticated) {
    showNotification({
      title: 'Authentication Required',
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
    console.log('Project deletion cancelled by user')
    return
  }
  
  // Use projectStore.setLoading instead of modifying the computed property
  projectStore.setLoading(true)
  
  try {
    console.log('Deleting project:', projectId)
    
    await projectStore.deleteProject(projectId)
    
    showNotification({
      title: 'Success',
      message: `Project "${projectName}" deleted successfully`,
      type: 'success'
    })
  } catch (error: any) {
    console.error('Error deleting project:', error)
    
    showNotification({
      title: 'Error',
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
  console.log('Testing API connection directly...')
  
  try {
    // Get token
    const tokenData = localStorage.getItem('token')
    if (!tokenData) {
      console.error('No token found in localStorage')
      return
    }
    
    const parsedToken = JSON.parse(tokenData)
    if (!parsedToken || !parsedToken.value) {
      console.error('Invalid token format')
      return
    }
    
    const token = parsedToken.value
    
    // Try different API endpoints
    const endpoints = [
      'project-manager/projects/',  // Try this first based on backend structure
      'builder/projects/',
      'products/oasis/project-manager/projects/',
      'products/oasis/builder/projects/'
    ]
    
    for (const endpoint of endpoints) {
      try {
        console.log(`Testing endpoint: ${endpoint}`)
        const response = await api.get(endpoint, {
          headers: {
            'Authorization': `Token ${token}`
          }
        })
        
        console.log(`Endpoint ${endpoint} response:`, {
          status: response.status,
          data: response.data
        })
        
        // If we get a successful response, use it to update projects
        if (Array.isArray(response.data) || response.data?.results) {
          const projectData = Array.isArray(response.data) ? response.data : response.data.results
          projectStore.updateProjects(projectData)
          console.log('Projects updated from direct API test:', projectData.length)
          return
        }
      } catch (error) {
        console.error(`Error testing endpoint ${endpoint}:`, error)
      }
    }
  } catch (error) {
    console.error('Error in API connection test:', error)
  }
}

// Retry utility
const retryFetchWithDiagnostics = async () => {
  console.log('Retrying fetch with diagnostics...')
  projectStore.clearError()
  
  // First try direct API testing
  await testApiConnection()
  
  // Then try normal fetch
  fetchProjects(true)
}

/**
 * Synchronize the auth state between global auth store, module auth store,
 * and project store to ensure consistency
 */
const synchronizeStores = async () => {
  try {
    console.log('Synchronizing stores...')
    
    // Force auth initialization if needed
    if (!authStore.initialized) {
      console.log('Auth store not initialized, initializing...')
      await authStore.initAuth()
    }
    
    // Wait to ensure auth store is completely initialized
    await new Promise(resolve => setTimeout(resolve, 100))
    
    // Sync project store auth state with auth store
    console.log('Setting project store auth state to match auth store:', authStore.isAuthenticated)
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
          console.log('Set API headers from localStorage token')
          
          // If we have a valid token but isAuthenticated is false, validate token with API
          if (!authStore.isAuthenticated) {
            console.log('Valid token in storage but auth state is false, validating with API...')
            try {
              await authStore.validateAuth()
            } catch (validationError) {
              console.error('Auth validation failed:', validationError)
            }
          }
        }
      } catch (e) {
        console.error('Error parsing token from localStorage:', e)
      }
    }
    
    console.log('Store synchronization complete', {
      authStoreState: authStore.isAuthenticated,
      projectStoreState: projectStore.isAuthenticated
    })
  } catch (error) {
    console.error('Error synchronizing stores:', error)
  } finally {
    // If still not authenticated, make sure isInitializing is set to false
    if (!authStore.isAuthenticated) {
      isInitializing.value = false
    }
  }
}

// Initialize on component mount
onMounted(async () => {
  console.log('BuilderDashboard mounted, auth state:', authStore.isAuthenticated)
  
  // Set initializing flag
  isInitializing.value = true
  
  // Synchronize all stores
  await synchronizeStores()
  
  if (authStore.isAuthenticated) {
    console.log('User is authenticated, fetching projects...')
    await fetchProjects(true) // Force refresh on initial load
  } else {
    console.log('User is not authenticated, skipping project fetch')
    isInitializing.value = false
  }
})

// Watch for authentication state changes
watch(
  () => authStore.isAuthenticated,
  (newValue, oldValue) => {
    // Only respond to meaningful changes
    if (newValue !== oldValue) {
      console.log('Auth state changed from', oldValue, 'to', newValue)
      
      // Sync auth state with project store whenever it changes
      projectStore.setAuthenticated(newValue)
      
      if (newValue === true) {
        // User just logged in, fetch projects
        fetchProjects(true)
      }
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