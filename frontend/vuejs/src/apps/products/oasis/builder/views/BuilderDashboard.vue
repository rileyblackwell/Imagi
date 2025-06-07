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
    <!-- Enhanced Main Content with Dynamic Background -->
    <div class="min-h-screen bg-dark-900 relative overflow-hidden">
      <!-- Improved Decorative Background Elements -->
      <div class="absolute inset-0 pointer-events-none">
        <!-- Enhanced Pattern Overlay -->
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.03]"></div>
        <div class="absolute inset-0 bg-noise opacity-[0.015]"></div>
        <div class="absolute inset-0 bg-gradient-to-br from-primary-950/10 via-dark-900 to-violet-950/10"></div>
        
        <!-- Enhanced Glowing Orbs Animation -->
        <div class="absolute -top-[10%] right-[15%] w-[800px] h-[800px] rounded-full bg-indigo-600/5 blur-[150px] animate-float"></div>
        <div class="absolute bottom-[5%] left-[20%] w-[600px] h-[600px] rounded-full bg-fuchsia-600/5 blur-[120px] animate-float-delay"></div>
        
        <!-- Animated Lines and Particles -->
        <div class="absolute left-0 right-0 top-1/3 h-px bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent animate-pulse-slow"></div>
        <div class="absolute left-0 right-0 bottom-1/3 h-px bg-gradient-to-r from-transparent via-violet-500/20 to-transparent animate-pulse-slow delay-700"></div>
      </div>

      <!-- Enhanced Content Container -->
      <div class="relative z-10">
        <!-- Modern Welcome Header Section -->
        <div class="pt-16 pb-12 px-6 sm:px-8 lg:px-12">
          <div class="max-w-7xl mx-auto">
            <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-8">
              <div class="space-y-6 md:max-w-3xl">
                <!-- Enhanced Badge -->
                <div class="inline-flex items-center px-4 py-1.5 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-full">
                  <div class="w-2 h-2 rounded-full bg-indigo-400 mr-2 animate-pulse"></div>
                  <span class="text-indigo-400 font-semibold text-sm tracking-wider">PROJECT WORKSPACE</span>
                </div>
                
                <!-- Modern Title with Gradient Enhancement -->
                <h2 class="text-4xl md:text-5xl font-bold text-white leading-tight">
                  <span class="inline-block bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent pb-1">Create & Manage</span> 
                  <br class="hidden sm:block" />Your Projects
                </h2>
                
                <!-- Enhanced Description -->
                <p class="text-xl text-gray-300 max-w-2xl">
                  Leverage AI-powered tools to build web applications quickly. Start a new project or continue working on existing ones.
                </p>
              </div>
              
              <!-- Stats Overview Cards -->
              <div class="flex flex-wrap gap-4 justify-end">
                <!-- Project count moved to Project Library -->
              </div>
            </div>
            
            <!-- Animated Divider Line -->
            <div class="w-full h-px bg-gradient-to-r from-transparent via-primary-500/30 to-transparent my-12 animate-pulse-slow"></div>
          </div>
        </div>

        <!-- Authentication Error Message with Enhanced Styling -->
        <div v-if="showAuthError" class="px-6 sm:px-8 lg:px-12 pb-16">
          <div class="max-w-7xl mx-auto">
            <div class="relative group overflow-hidden">
              <!-- Animated Glow Effect -->
              <div class="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/50 to-violet-500/50 rounded-2xl opacity-0 group-hover:opacity-70 blur group-hover:blur-md transition-all duration-300"></div>
              
              <div class="relative bg-dark-900/70 backdrop-blur-lg rounded-2xl border border-gray-800/60 p-10 text-center transition-all duration-500">
                <div class="w-20 h-20 bg-gradient-to-br from-indigo-500/20 to-violet-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                  <i class="fas fa-lock text-4xl text-indigo-400 opacity-80"></i>
                </div>
                <h2 class="text-2xl font-semibold text-white mb-3">Authentication Required</h2>
                <p class="text-gray-300 mb-8 max-w-md mx-auto">Please log in to view and manage your projects.</p>
                <router-link 
                  to="/login" 
                  class="inline-flex items-center px-8 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl transform hover:-translate-y-1 transition-all duration-300 shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30"
                >
                  <i class="fas fa-sign-in-alt mr-2.5"></i>
                  Log In
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Enhanced Project Section with Modern Layout -->
        <div v-else class="px-6 sm:px-8 lg:px-12 pb-24">
          <div class="max-w-7xl mx-auto">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-10">
              <!-- New Project Card with Modern Positioning -->
              <div class="lg:col-span-5 xl:col-span-4 lg:sticky lg:top-8">
                <ProjectCard
                  v-model="newProjectName"
                  v-model:description="newProjectDescription"
                  :is-loading="isCreating"
                  :is-new="true"
                  @submit="createProject"
                />
              </div>

              <!-- Combined Project Library and Search -->
              <div class="lg:col-span-7 xl:col-span-8">
                <!-- Unified Project Library Container -->
                <div class="relative rounded-2xl border border-gray-800/60 bg-dark-900/40 backdrop-blur-sm transition-all duration-500 hover:shadow-[0_0_25px_-5px_rgba(99,102,241,0.5)] overflow-hidden p-8">
                  <!-- Background gradient -->
                  <div class="absolute inset-0 bg-gradient-to-br opacity-10 -z-10 transition-opacity duration-300 group-hover:opacity-20 from-indigo-900 to-violet-900"></div>
                  
                  <!-- Glowing orb effect -->
                  <div class="absolute -bottom-20 -right-20 w-40 h-40 rounded-full opacity-10 blur-3xl transition-opacity duration-500 group-hover:opacity-20 bg-indigo-500"></div>
                  
                  <!-- Header Section -->
                  <div class="relative z-10 mb-8">
                    <!-- Badge -->
                    <div class="inline-block px-4 py-1.5 bg-indigo-500/10 rounded-full mb-4">
                      <span class="text-indigo-400 font-semibold text-sm tracking-wider">YOUR PROJECTS</span>
                    </div>
                    
                    <!-- Title and Stats -->
                    <div class="flex items-center justify-between mb-6">
                      <div>
                        <h2 class="text-2xl font-bold text-white mb-2">Project Library</h2>
                        <p class="text-gray-300">Continue working on your existing web applications</p>
                        <!-- Decorative element -->
                        <div class="w-16 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full mt-4"></div>
                      </div>
                      
                      <!-- Project count with enhanced styling -->
                      <div class="group relative">
                        <!-- Glow effect on hover -->
                        <div class="absolute -inset-1 rounded-xl bg-gradient-to-r from-indigo-500/30 to-violet-500/30 opacity-0 group-hover:opacity-100 blur-sm transition-all duration-300"></div>
                        
                        <!-- Icon container -->
                        <div class="relative bg-dark-800/60 backdrop-blur-sm rounded-xl border border-gray-800/60 px-4 py-2 hover:border-indigo-500/30 transition-all duration-300 flex items-center gap-3">
                          <div class="w-10 h-10 rounded-lg bg-indigo-500/15 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-indigo-500/20 shadow-md shadow-indigo-500/5">
                            <i class="fas fa-folder-open text-indigo-400 text-lg"></i>
                          </div>
                          <div>
                            <p class="text-xs text-gray-400 uppercase">Total</p>
                            <p class="text-xl font-bold text-white">{{ projects.length || 0 }}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Search Input -->
                    <div class="mb-6">
                      <ProjectSearchInput 
                        v-model="searchQuery"
                        placeholder="Search projects by name or description..."
                      />
                    </div>
                  </div>

                  <!-- Content Section -->
                  <div class="relative z-10">
                    <!-- Loading State -->
                    <div v-if="isLoading" class="flex flex-col items-center justify-center py-16">
                      <div class="w-16 h-16 bg-indigo-500/10 rounded-full flex items-center justify-center mb-5 animate-pulse">
                        <i class="fas fa-spinner fa-spin text-2xl text-indigo-400"></i>
                      </div>
                      <p class="text-gray-300 text-lg">Loading your projects...</p>
                    </div>

                    <!-- Error State -->
                    <div v-else-if="error" class="flex flex-col items-center justify-center py-16">
                      <div class="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mb-5">
                        <i class="fas fa-exclamation-circle text-2xl text-red-400"></i>
                      </div>
                      <p class="text-gray-300 mb-6 text-center max-w-md">{{ error }}</p>
                      <button
                        @click="retryFetch"
                        class="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 border border-indigo-500/40 hover:border-indigo-400/50 text-white rounded-xl shadow-lg hover:shadow-indigo-500/20 transform hover:-translate-y-1 transition-all duration-300 inline-flex items-center"
                      >
                        <i class="fas fa-sync-alt mr-2"></i>
                        Try Again
                      </button>
                      
                      <!-- Diagnostic Button -->
                      <button
                        @click="retryFetchWithDiagnostics"
                        class="mt-4 px-6 py-3 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl transform hover:-translate-y-1 transition-all duration-300 shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 inline-flex items-center"
                      >
                        <i class="fas fa-tools mr-2.5"></i>
                        Diagnose Connection Issues
                      </button>
                    </div>

                    <!-- No Search Results -->
                    <div v-else-if="searchQuery?.trim() && displayedProjects.length === 0 && projects.length > 0" class="flex flex-col items-center justify-center py-16">
                      <div class="w-16 h-16 bg-gray-500/10 rounded-full flex items-center justify-center mb-5">
                        <i class="fas fa-search text-2xl text-gray-400"></i>
                      </div>
                      <h3 class="text-xl font-semibold text-white mb-2">No matching projects</h3>
                      <p class="text-gray-300 text-center max-w-md">No projects found matching "{{ searchQuery }}"</p>
                    </div>

                    <!-- Empty State -->
                    <div v-else-if="!projects.length" class="flex flex-col items-center justify-center py-16">
                      <div class="w-16 h-16 bg-indigo-500/10 rounded-full flex items-center justify-center mb-5">
                        <i class="fas fa-folder-open text-2xl text-indigo-400"></i>
                      </div>
                      <h3 class="text-xl font-semibold text-white mb-2">No projects yet</h3>
                      <p class="text-gray-300 text-center max-w-md mb-6">Create your first project to start building with Imagi</p>
                      
                      <!-- Directional hint -->
                      <div class="flex items-center text-indigo-400 animate-pulse-slow">
                        <i class="fas fa-long-arrow-alt-left text-lg mr-2"></i>
                        <span>Get started with a new project</span>
                      </div>
                    </div>

                    <!-- Recent Projects Display -->
                    <div v-else-if="displayedProjects.length > 0">
                      <div class="flex items-center bg-indigo-500/5 rounded-lg px-4 py-2 mb-6">
                        <i class="fas fa-clock text-indigo-400 mr-3"></i>
                        <h3 class="text-sm font-medium text-white uppercase tracking-wider">
                          {{ searchQuery ? `Search Results (${displayedProjects.length})` : 'Recently Opened' }}
                        </h3>
                      </div>
                      
                      <!-- Project Cards -->
                      <div class="space-y-4">
                        <ProjectCard
                          v-for="project in displayedProjects"
                          :key="project.id"
                          :project="project"
                          @delete="(project) => confirmDelete(String(project.id), project.name)"
                        />
                      </div>
                      
                      <!-- Show All Projects Link (when not searching) -->
                      <div v-if="!searchQuery && projects.length > 3" class="mt-6 text-center">
                        <router-link
                          to="/products/oasis/builder/projects"
                          class="inline-flex items-center px-6 py-3 bg-dark-800/60 hover:bg-dark-700/60 border border-gray-800/60 hover:border-indigo-500/30 text-gray-300 hover:text-white rounded-xl transition-all duration-300"
                        >
                          <i class="fas fa-folder-open mr-2"></i>
                          View All Projects ({{ projects.length }})
                        </router-link>
                      </div>
                    </div>
                  </div>
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
// Debug base path in dev
if (import.meta.env.DEV) {
  // Print the Vite/Vue base URL and current path
  // This helps confirm whether the dev server is serving at the correct base
  console.log('[BuilderDashboard] import.meta.env.BASE_URL:', import.meta.env.BASE_URL);
  console.log('[BuilderDashboard] window.location.pathname:', window.location.pathname);
}

import { ref, computed, onMounted, watch, onBeforeUnmount, type ComputedRef } from 'vue'
import { useRouter } from 'vue-router'
import { BuilderLayout } from '@/apps/products/oasis/builder/layouts'
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore'
import { useNotification } from '@/shared/composables/useNotification'
import { ProjectCard } from '@/apps/products/oasis/builder/components/molecules'
import { useAuthStore } from '@/shared/stores/auth'
import { useConfirm } from '../composables/useConfirm'
import api from '@/apps/products/oasis/builder/services/api'
import { useNotificationStore } from '@/shared/stores/notificationStore'
import ProjectSearchInput from '../components/atoms/ProjectSearchInput.vue'
import { useProjectSearch } from '../composables/useProjectSearch'
import type { Project } from '../types/components' 
import { normalizeProject } from '../types/components' // Use the normalizeProject from components.ts


const router = useRouter()
const projectStore = useProjectStore()
const authStore = useAuthStore()
const { showNotification } = useNotification()
const { confirm } = useConfirm()
const notificationStore = useNotificationStore()

// State with types - remove searchQuery since it's handled in ProjectList
const newProjectName = ref('')
const newProjectDescription = ref('') // New ref for project description
const isCreating = ref(false)
const isInitializing = ref(true) // Added to track initialization state

// Computed with types - remove filteredProjects
const projects = computed(() => projectStore.projects)
// Add a normalized projects computed property that ensures all projects have the required status field
// Ensure normalizedProjects always returns an array of Project with all required fields (including created_at)
const normalizedProjects = computed<Project[]>(() => {
  if (!projects.value) return [];
  return projects.value.map(project => {
    // normalizeProject already ensures created_at is set with fallbacks
    return normalizeProject(project);
  });
})
const isLoading = computed(() => projectStore.loading || isInitializing.value)
const error = computed(() => projectStore.error || '')
const showAuthError = computed(() => !authStore.isAuthenticated && !isLoading.value)

// Use project search composable with options to include descriptions in search
const { searchQuery, filteredProjects } = useProjectSearch(normalizedProjects, { includeDescription: true });



// Compute displayed projects - show search results if searching, otherwise show 3 most recent
const displayedProjects = computed<Project[]>(() => {
  // Check if we have a meaningful search query (not just whitespace)
  const hasSearchQuery = searchQuery.value?.trim().length > 0;
  
  if (hasSearchQuery) {
    // Return filtered search results
    return filteredProjects.value || [];
  }
  
  // Show 3 most recently updated projects when not searching
  if (!normalizedProjects.value?.length) {
    return [];
  }
  
  return [...normalizedProjects.value]
    .sort((a, b) => {
      // Handle cases where updated_at might be undefined
      if (!a.updated_at) return 1;  // If a's date is missing, b comes first
      if (!b.updated_at) return -1; // If b's date is missing, a comes first
      
      const dateA = new Date(a.updated_at).getTime()
      const dateB = new Date(b.updated_at).getTime()
      return dateB - dateA
    })
    .slice(0, 3);
});

// Navigation items
const navigationItems = [
  { 
    name: 'Dashboard',
    to: '/dashboard',
    icon: 'fas fa-home',
    exact: true
  },
  {
    name: 'Oasis Projects',
    to: '/products/oasis/builder/projects',
    icon: 'fas fa-folder',
    exact: true
  },
  {
    name: 'Create Project',
    to: '/products/oasis/builder/dashboard',
    icon: 'fas fa-plus-circle',
    exact: true
  },
  {
    name: 'Buy AI Credits',
    to: '/payments/checkout',
    icon: 'fas fa-money-bill-wave',
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
      description: newProjectDescription.value.trim() // Use the description value
    }
    
    const newProject = await projectStore.createProject(projectData)
    
    // Clear the project name and description fields after successful creation
    newProjectName.value = ''
    newProjectDescription.value = ''
    
    // Log project information to debug any ID issues
    console.debug('Created project details:', {
      project: newProject,
      id: newProject.id,
      idType: typeof newProject.id
    })
    
    // Store notification ID to be able to clear it before navigation
    const notificationId = showNotification({
      message: `Project "${newProject.name}" created successfully. Setting up your workspace...`,
      type: 'success',
      duration: 4000 // Shorter duration so it's less likely to persist
    })
    
    // Ensure ID is properly formatted as a string
    const projectId = String(newProject.id)
    console.debug(`Navigating to project workspace with ID: ${projectId}`)
    
    // Force refresh all projects to ensure the projects list is up-to-date
    try {
      await projectStore.fetchProjects(true)
    } catch (refreshError) {
      console.warn('Failed to refresh projects after creation:', refreshError)
      // Continue with navigation even if refresh fails
    }
    
    // Add a small delay to allow initialization to complete
    setTimeout(async () => {
      // Get notification store to clear notifications before navigation
      const notificationStore = useNotificationStore()
      
      // Remove the success notification to prevent it from showing in workspace
      if (notificationId) {
        notificationStore.removeNotification(notificationId)
      }
      
      // Navigate to the new project workspace
      await router.push({
        name: 'builder-workspace',
        params: { projectId }
      })
    }, 1000)
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
      type: 'success',
      duration: 4000 // Shorter duration for better UX
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
      'api/v1/builder/builder/',          // Fallback endpoint
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

/**
 * Force refresh projects (used by refresh button)
 */
const refreshProjects = async () => {
  try {
    showNotification({
      type: 'info',
      message: 'Refreshing projects...'
    })
    
    await fetchProjects(true) // Force refresh
    
    showNotification({
      type: 'success',
      message: 'Projects refreshed successfully'
    })
  } catch (error) {
    showNotification({
      type: 'error',
      message: 'Failed to refresh projects'
    })
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
  
  // Always force refresh projects when the dashboard loads to ensure fresh data
  try {
    // Always use force=true to ensure we get the latest data
    await fetchProjects(true)
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

// Clean up resources when leaving the dashboard
onBeforeUnmount(() => {
  // Clear dashboard-specific notifications when leaving
  const notificationStore = useNotificationStore()
  notificationStore.clear()
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

/* Add subtle animation for loading state */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}

.animate-pulse-slow {
  animation: pulse 3s ease-in-out infinite;
}

/* Float animation for background orbs */
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

.animate-float {
  animation: float 15s ease-in-out infinite;
}

.animate-float-delay {
  animation: float 18s ease-in-out infinite reverse;
}

.delay-700 {
  animation-delay: 700ms;
}

/* Custom scrollbar styling for project container */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.gray.700') transparent;
}

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