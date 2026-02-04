<!--
  Projects.vue - Project Management Interface
  
  This component is responsible for:
  1. Creating new projects
  2. Deleting existing projects
  3. Listing all user projects
  4. Navigating to the workspace for editing
  
  It should NOT be responsible for:
  - Project file editing (handled by Workspace.vue)
-->
<template>
  <div>
    <!-- Confirm Modal (uses Teleport to body) -->
    <ConfirmModal
      :is-open="confirmModal.isModalOpen.value"
      :options="confirmModal.modalOptions.value"
      @confirm="confirmModal.handleConfirm"
      @cancel="confirmModal.handleCancel"
    />
    
    <DefaultLayout :isHomeNav="true">
    <div class="min-h-screen bg-white dark:bg-[#0a0a0a] relative overflow-hidden transition-colors duration-500">
      <!-- Subtle background matching home page -->
      <div class="fixed inset-0 pointer-events-none">
        <div class="absolute inset-0 bg-gradient-to-b from-gray-50/50 via-white to-white dark:from-[#0a0a0a] dark:via-[#0a0a0a] dark:to-[#0a0a0a] transition-colors duration-500"></div>
        <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]" 
             style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
      </div>

      <!-- Main Content -->
      <main class="relative z-10">
        <!-- Hero Section -->
        <section class="relative py-20 sm:py-24 md:py-28 px-6 sm:px-8 lg:px-12">
          <div class="max-w-4xl mx-auto text-center">
            <!-- Page title -->
            <h1 class="text-4xl sm:text-5xl md:text-6xl font-semibold text-gray-900 dark:text-white mb-6 tracking-tight leading-[1.1] transition-colors duration-300">
              Your Projects
            </h1>
            
            <!-- Subtitle -->
            <p class="text-lg sm:text-xl text-gray-700 dark:text-white/80 tracking-wide font-medium mb-6 max-w-2xl mx-auto transition-colors duration-300">
              Create new web applications or continue working on existing projects. Build, test, and launch with AI-powered tools.
            </p>
          </div>
        </section>

        <!-- Authentication Error -->
        <div v-if="showAuthError" class="px-6 sm:px-8 lg:px-12 pb-24">
          <div class="max-w-2xl mx-auto">
            <div class="relative p-10 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 shadow-md text-center transition-colors duration-300">
              <div class="w-16 h-16 bg-gray-100 dark:bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <i class="fas fa-lock text-2xl text-gray-600 dark:text-gray-600"></i>
              </div>
              <h2 class="text-2xl font-semibold text-gray-900 dark:text-black mb-3 transition-colors duration-300">Authentication Required</h2>
              <p class="text-gray-600 dark:text-gray-700 mb-8 max-w-md mx-auto transition-colors duration-300">Please log in to view and manage your projects.</p>
              <router-link 
                to="/auth/signin" 
                class="btn-3d group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 text-white dark:text-gray-900 rounded-full font-medium text-lg transition-all duration-300 overflow-hidden border border-gray-700/50 dark:border-gray-300/50"
              >
                <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent dark:via-white/60"></span>
                <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-black/30 to-transparent dark:via-black/10"></span>
                <i class="fas fa-sign-in-alt relative"></i>
                <span class="relative">Log In</span>
              </router-link>
            </div>
          </div>
        </div>

        <!-- Main Project Sections -->
        <div v-else class="px-6 sm:px-8 lg:px-12 pb-24">
          <div class="max-w-6xl mx-auto">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
              
              <!-- Create New Project Card -->
              <div class="relative">
                <div class="h-full p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 shadow-md transition-colors duration-300">
                  
                  <!-- Section header -->
                  <div class="mb-6">
                    <p class="text-sm font-medium text-gray-600 dark:text-gray-600 uppercase tracking-widest mb-3 transition-colors duration-300">New Project</p>
                    <h2 class="text-2xl font-semibold text-gray-900 dark:text-black mb-2 transition-colors duration-300">Create a Project</h2>
                    <p class="text-gray-600 dark:text-gray-700 transition-colors duration-300">Start building a new web application with AI assistance.</p>
                  </div>
                  
                  <!-- Create Form -->
                  <div class="space-y-5">
                    <!-- Project Name Input -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-700 mb-2 transition-colors duration-300">Project Name</label>
                      <input
                        v-model="newProjectName"
                        type="text"
                        placeholder="Enter project name..."
                        class="w-full px-4 py-3.5 bg-gray-50 dark:bg-gray-50 border border-gray-200 dark:border-gray-300 focus:border-gray-400 dark:focus:border-gray-500 rounded-xl text-gray-900 dark:text-gray-900 placeholder-gray-400 dark:placeholder-gray-500 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                        style="outline: none !important;"
                        :disabled="isCreating"
                      >
                    </div>
                    
                    <!-- Project Description Input -->
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-700 mb-2 transition-colors duration-300">
                        Description <span class="text-gray-400 dark:text-gray-500">(optional)</span>
                      </label>
                      <textarea
                        v-model="newProjectDescription"
                        placeholder="Brief description of your project..."
                        class="w-full px-4 py-3.5 bg-gray-50 dark:bg-gray-50 border border-gray-200 dark:border-gray-300 focus:border-gray-400 dark:focus:border-gray-500 rounded-xl text-gray-900 dark:text-gray-900 placeholder-gray-400 dark:placeholder-gray-500 transition-all duration-300 resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                        style="outline: none !important;"
                        :disabled="isCreating"
                        rows="3"
                      ></textarea>
                    </div>
                    
                    <!-- Create Button -->
                    <div class="pt-2">
                      <button
                        @click="createProject"
                        :disabled="!newProjectName?.trim() || isCreating"
                        class="btn-3d group relative w-full inline-flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-b from-gray-800 via-gray-900 to-gray-950 dark:from-white dark:via-gray-50 dark:to-gray-100 text-white dark:text-gray-900 rounded-full font-medium text-lg transition-all duration-300 overflow-hidden border border-gray-700/50 dark:border-gray-300/50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent dark:via-white/60"></span>
                        <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-black/30 to-transparent dark:via-black/10"></span>
                        <template v-if="isCreating">
                          <div class="relative w-5 h-5 border-2 border-white/30 border-t-white dark:border-gray-900/30 dark:border-t-gray-900 rounded-full animate-spin"></div>
                          <span class="relative">Creating...</span>
                        </template>
                        <template v-else>
                          <span class="relative">Create Project</span>
                          <svg class="relative w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                          </svg>
                        </template>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Existing Projects Card -->
              <div class="relative">
                <div class="h-full p-8 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 shadow-md transition-colors duration-300 flex flex-col">
                  
                  <!-- Section header -->
                  <div class="mb-6">
                    <p class="text-sm font-medium text-gray-600 dark:text-gray-600 uppercase tracking-widest mb-3 transition-colors duration-300">Your Projects</p>
                    <h2 class="text-2xl font-semibold text-gray-900 dark:text-black mb-2 transition-colors duration-300">Project Library</h2>
                    <p class="text-gray-600 dark:text-gray-700 transition-colors duration-300">Continue working on your existing applications.</p>
                  </div>

                  <!-- Search Input -->
                  <div class="mb-6">
                    <div class="relative">
                      <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500"></i>
                      <input
                        v-model="searchQuery"
                        type="text"
                        placeholder="Search projects..."
                        class="w-full pl-11 pr-4 py-3 bg-gray-50 dark:bg-gray-50 border border-gray-200 dark:border-gray-300 focus:border-gray-400 dark:focus:border-gray-500 rounded-xl text-gray-900 dark:text-gray-900 placeholder-gray-400 dark:placeholder-gray-500 transition-all duration-300"
                        style="outline: none !important;"
                      >
                    </div>
                  </div>

                  <!-- Content Section -->
                  <div class="flex-1 flex flex-col overflow-hidden">
                    <!-- Loading State -->
                    <div v-if="isLoading" class="flex flex-col items-center justify-center py-12">
                      <div class="w-12 h-12 bg-gray-100 dark:bg-gray-100 rounded-full flex items-center justify-center mb-4">
                        <div class="w-6 h-6 border-2 border-gray-300 dark:border-gray-400 border-t-gray-600 dark:border-t-gray-600 rounded-full animate-spin"></div>
                      </div>
                      <p class="text-gray-600 dark:text-gray-600 text-sm transition-colors duration-300">Loading your projects...</p>
                    </div>

                    <!-- Error State -->
                    <div v-else-if="error" class="flex flex-col items-center justify-center py-12">
                      <div class="w-12 h-12 bg-red-50 dark:bg-red-50 rounded-full flex items-center justify-center mb-4">
                        <i class="fas fa-exclamation-triangle text-red-500 dark:text-red-500 text-xl"></i>
                      </div>
                      <p class="text-gray-600 dark:text-gray-600 mb-4 text-center max-w-md text-sm transition-colors duration-300">{{ error }}</p>
                      <div class="flex gap-3">
                        <button
                          @click="retryFetch"
                          class="inline-flex items-center gap-2 px-5 py-2.5 bg-gray-100 dark:bg-gray-100 hover:bg-gray-200 dark:hover:bg-gray-200 border border-gray-200 dark:border-gray-300 rounded-xl text-gray-900 dark:text-gray-900 font-medium transition-all duration-300"
                        >
                          <i class="fas fa-redo text-sm"></i>
                          <span>Try Again</span>
                        </button>
                      </div>
                    </div>

                    <!-- No Search Results -->
                    <div v-else-if="searchQuery?.trim() && displayedProjects.length === 0 && projects.length > 0" class="flex flex-col items-center justify-center py-12">
                      <div class="w-12 h-12 bg-gray-100 dark:bg-gray-100 rounded-full flex items-center justify-center mb-4">
                        <i class="fas fa-search text-gray-400 dark:text-gray-500 text-xl"></i>
                      </div>
                      <h3 class="text-lg font-medium text-gray-900 dark:text-black mb-1 transition-colors duration-300">No matching projects</h3>
                      <p class="text-gray-600 dark:text-gray-600 text-center text-sm transition-colors duration-300">No projects found matching "{{ searchQuery }}"</p>
                    </div>

                    <!-- Empty State -->
                    <div v-else-if="!projects.length" class="flex flex-col items-center justify-center py-12">
                      <div class="w-12 h-12 bg-gray-100 dark:bg-gray-100 rounded-full flex items-center justify-center mb-4">
                        <i class="fas fa-folder-open text-gray-400 dark:text-gray-500 text-xl"></i>
                      </div>
                      <h3 class="text-lg font-medium text-gray-900 dark:text-black mb-1 transition-colors duration-300">No projects yet</h3>
                      <p class="text-gray-600 dark:text-gray-600 text-center mb-4 text-sm transition-colors duration-300">Create your first project to start building</p>
                      <div class="flex items-center text-gray-500 dark:text-gray-600 text-sm">
                        <i class="fas fa-arrow-left mr-2 animate-pulse"></i>
                        <span>Get started with a new project</span>
                      </div>
                    </div>

                    <!-- Projects Display -->
                    <div v-else-if="displayedProjects.length > 0" class="flex-1 flex flex-col overflow-hidden">
                      <!-- Project count -->
                      <div class="mb-4">
                        <span class="text-sm font-medium text-gray-600 dark:text-gray-600 transition-colors duration-300">
                          {{ searchQuery ? `${displayedProjects.length} Results` : `${projects.length || 0} Projects` }}
                        </span>
                      </div>
                      
                      <!-- Scrollable Project Cards -->
                      <div class="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
                        <ProjectCard
                          v-for="project in displayedProjects"
                          :key="project.id"
                          :project="project"
                          @delete="confirmDelete"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </DefaultLayout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount, onMounted, onActivated } from 'vue'
import { useRouter } from 'vue-router'
import { DefaultLayout } from '@/shared/layouts'
import { useProjectStore } from '@/apps/products/imagi/stores/projectStore'
import { useNotification } from '@/shared/composables/useNotification'
import { ProjectCard } from '@/apps/products/imagi/components/molecules'
import { useAuthStore } from '@/shared/stores/auth'
import { useConfirm } from '../composables/useConfirm'
import { useNotificationStore } from '@/shared/stores/notificationStore'
import { useProjectSearch } from '../composables/useProjectSearch'
import type { Project } from '../types/components' 
import { normalizeProject } from '../types/components'
import { toSlug } from '../utils/slug'
import { ConfirmModal } from '../components/organisms/modals'


const router = useRouter()
const projectStore = useProjectStore()
const authStore = useAuthStore()
const { showNotification } = useNotification()
const confirmModal = useConfirm()
const { confirm } = confirmModal

// State
const newProjectName = ref('')
const newProjectDescription = ref('')
const isCreating = ref(false)
const isInitializing = ref(true)

// Computed
const projects = computed(() => projectStore.projects)
const normalizedProjects = computed<Project[]>(() => {
  if (!projects.value) return [];
  return projects.value.map(project => {
    return normalizeProject(project);
  });
})
const isLoading = computed(() => projectStore.loading || isInitializing.value)
const error = computed(() => projectStore.error || '')
const showAuthError = computed(() => !authStore.isAuthenticated && !isLoading.value)

// Use project search composable
const { searchQuery, filteredProjects } = useProjectSearch(normalizedProjects, { includeDescription: true });

// Compute displayed projects
const displayedProjects = computed<Project[]>(() => {
  let deletedProjects: string[] = [];
  try {
    deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]');
  } catch (e) {
    // Handle localStorage errors silently
  }
  
  const hasSearchQuery = searchQuery.value?.trim().length > 0;
  let baseProjects: Project[] = [];
  
  if (hasSearchQuery) {
    baseProjects = filteredProjects.value || [];
  } else {
    if (!normalizedProjects.value?.length) {
      return [];
    }
    
    baseProjects = [...normalizedProjects.value]
      .sort((a, b) => {
        if (!a.updated_at) return 1;
        if (!b.updated_at) return -1;
        
        const dateA = new Date(a.updated_at).getTime()
        const dateB = new Date(b.updated_at).getTime()
        return dateB - dateA
      })
  }
  
  return baseProjects.filter(project => 
    project && project.id && !deletedProjects.includes(String(project.id))
  );
});

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
    
    // Navigate immediately to the workspace for the newly created project
    router.push({ 
      name: 'builder-workspace', 
      params: { projectName: toSlug(newProject.name) } 
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
const confirmDelete = async (project: Project) => {
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
    message: `Are you sure you want to delete "${project.name}"? This action cannot be undone.`,
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'danger'
  })
  
  if (!confirmed) {
    return
  }
  
  // Capture the project name before deletion to ensure we have it for the notification
  const projectName = project.name || `Project ${project.id}` || 'Unknown Project'
  
  // Check if user is currently in the workspace for this project
  const isCurrentlyInWorkspace = router.currentRoute.value.name === 'builder-workspace' && 
                                 router.currentRoute.value.params.projectName === toSlug(project.name)
  
  try {
    // First clear the cache to ensure fresh data
    projectStore.clearProjectsCache()
    
    // Mark project as deleted BEFORE making the API call to prevent race conditions
    const deletedProjectId = String(project.id)
    
    // Add to deleted projects list immediately to prevent any fetching attempts
    try {
      const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
      if (!deletedProjects.includes(deletedProjectId)) {
        deletedProjects.push(deletedProjectId)
        localStorage.setItem('deletedProjects', JSON.stringify(deletedProjects))
        
        // Also store timestamp for cleanup purposes
        const deletedProjectsTimestamp = JSON.parse(localStorage.getItem('deletedProjectsTimestamp') || '{}')
        deletedProjectsTimestamp[deletedProjectId] = Date.now()
        localStorage.setItem('deletedProjectsTimestamp', JSON.stringify(deletedProjectsTimestamp))
      }
    } catch (e) {
      console.error('Failed to store deleted project ID in localStorage:', e)
    }
    
    await projectStore.deleteProject(String(project.id))
    
    // If user was in the workspace for this project, navigate away from it
    if (isCurrentlyInWorkspace) {
      console.log('User was in workspace for deleted project, redirecting to dashboard')
      await router.push({ name: 'projects' })
    }
    
    // Immediately refresh the projects list to show updated state
    try {
      await fetchProjects(true) // Force refresh to get latest state from API
    } catch (refreshError) {
      console.warn('Failed to refresh projects after deletion:', refreshError)
    }
    
    // Show deletion success notification (red to indicate destructive action completed)
    showNotification({
      type: 'delete',
      message: `"${projectName}" deleted successfully`,
      duration: 4000
    })

  } catch (error: any) {
    console.error('Error deleting project:', error)
    
    // Check if the error is actually a success (project was deleted but API returned unexpected response)
    if (error.response?.status === 404) {
      // Project is gone, which means deletion was successful
      // Clear cache and refresh
      projectStore.clearProjectsCache()
      

      
      // If user was in the workspace for this project, navigate away from it
      if (isCurrentlyInWorkspace) {
        console.log('Project was deleted (404), redirecting from workspace to dashboard')
        await router.push({ name: 'projects' })
      }
      
            // Still refresh the projects list to ensure clean state
      try {
        await fetchProjects(true)
      } catch (refreshError) {
        console.warn('Failed to refresh projects after deletion:', refreshError)
      }
      
      // Show deletion success notification (red to indicate destructive action completed)
      showNotification({
        type: 'delete',
        message: `"${projectName}" deleted successfully`,
        duration: 4000
      })    } else {
      // Actual error occurred - remove the project from deleted list if it was added
      try {
        const deletedProjects = JSON.parse(localStorage.getItem('deletedProjects') || '[]')
        const updatedDeletedProjects = deletedProjects.filter((id: string) => id !== String(project.id))
        localStorage.setItem('deletedProjects', JSON.stringify(updatedDeletedProjects))
        
        // Also remove timestamp
        const deletedProjectsTimestamp = JSON.parse(localStorage.getItem('deletedProjectsTimestamp') || '{}')
        delete deletedProjectsTimestamp[String(project.id)]
        localStorage.setItem('deletedProjectsTimestamp', JSON.stringify(deletedProjectsTimestamp))
      } catch (e) {
        console.warn('Failed to remove project from deleted list after error:', e)
      }
      
              // Show actual error with captured project name
        showNotification({
          message: error?.message || `Failed to delete "${projectName}"`,
          type: 'error',
          duration: 5000
        })
    }
  }
}

// Set up watchers and lifecycle hooks
onMounted(async () => {
  console.debug('Projects mounted')
  
  // Always force refresh projects when the dashboard loads to ensure we have the latest data
  try {
    console.debug('Forcing refresh of projects on dashboard load')
    // Force refresh to always get the latest projects from API
    await fetchProjects(true)
  } catch (error) {
    console.error('Initial project fetch failed:', error)
    
    // Wait a moment and try again if authentication is confirmed
    if (authStore.isAuthenticated) {
      setTimeout(async () => {
        try {
          console.debug('Retrying project fetch after initial failure')
          await fetchProjects(true) // Force on retry after failure
        } catch (retryError) {
          console.error('Retry fetch also failed:', retryError)
        }
      }, 2000)
    }
  }
})

// Add support for keep-alive to refresh when component is re-activated
onActivated(async () => {
  console.debug('Projects activated - refreshing projects from API')
  if (authStore.isAuthenticated) {
    // Always force refresh projects when the component is activated (tab switch, navigation back, etc.)
    try {
      await fetchProjects(true) // Always force refresh to get latest state from API
    } catch (error) {
      console.error('Failed to refresh projects on activation:', error)
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
      // Don't automatically fetch projects when auth state changes
      // Projects will be fetched when needed by the component's normal flow
      // This prevents unnecessary API calls immediately after login
    }
  }
)
</script>

<style scoped>
/* Remove browser default styling for form inputs */
input, textarea {
  outline: none !important;
  box-shadow: none !important;
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
}

input:focus, textarea:focus {
  outline: none !important;
  box-shadow: none !important;
}

/* Custom scrollbar for project list */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.12) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

/* 3D Printed Button Effect - matching homepage */
.btn-3d {
  transform: translateZ(0);
  box-shadow: 
    0 2px 3px -1px rgba(0, 0, 0, 0.4),
    0 6px 12px -3px rgba(0, 0, 0, 0.35),
    0 16px 32px -8px rgba(0, 0, 0, 0.3),
    0 24px 48px -12px rgba(0, 0, 0, 0.2),
    0 3px 0 -1px rgba(0, 0, 0, 0.5),
    inset 0 2px 4px 0 rgba(255, 255, 255, 0.2),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.3);
}

.dark .btn-3d {
  box-shadow: 
    0 2px 3px -1px rgba(0, 0, 0, 0.1),
    0 6px 12px -3px rgba(0, 0, 0, 0.1),
    0 16px 32px -8px rgba(0, 0, 0, 0.1),
    0 24px 48px -12px rgba(0, 0, 0, 0.08),
    0 3px 0 -1px rgba(0, 0, 0, 0.15),
    inset 0 3px 6px 0 rgba(255, 255, 255, 0.9),
    inset 0 -4px 8px -2px rgba(0, 0, 0, 0.08);
}
</style>