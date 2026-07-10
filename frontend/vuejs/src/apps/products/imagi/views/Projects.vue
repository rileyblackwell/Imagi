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
    <div class="bg-orange-50 dark:bg-[#16120e] relative transition-colors duration-500 min-h-screen overflow-hidden">
      <!-- Subtle background matching home page -->
      <div class="absolute inset-0 pointer-events-none">
        <div class="absolute inset-0 opacity-[0.015] dark:opacity-[0.02]"
             style="background-image: linear-gradient(rgba(128,128,128,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(128,128,128,0.1) 1px, transparent 1px); background-size: 64px 64px;"></div>
      </div>

      <!-- Main Content (pt-20 clears the fixed h-14 navbar) -->
      <main class="relative z-10 flex flex-col px-6 sm:px-8 lg:px-12 pt-20 pb-8 min-h-screen">
        <!-- Compact Hero -->
        <section class="flex-shrink-0 max-w-6xl mx-auto w-full text-center mb-6 md:mb-8">
          <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-blue-200/70 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-[0.18em] mb-4 transition-colors duration-300">Workspace</p>
          <h1 class="text-3xl sm:text-4xl font-semibold text-blue-950 dark:text-white mb-2 tracking-tight transition-colors duration-300">
            Your Projects
          </h1>
          <p class="text-base text-blue-950/70 dark:text-blue-100/70 transition-colors duration-300">
            Start a new business or keep building and running an existing one.
          </p>
        </section>

        <!-- Authentication Error -->
        <div v-if="showAuthError" class="flex-1 flex items-center justify-center">
          <div class="max-w-2xl mx-auto w-full">
            <div class="crisp-card relative p-10 rounded-2xl bg-white dark:bg-white/[0.05] border border-blue-200/70 dark:border-blue-300/[0.16] text-center transition-colors duration-300">
              <div class="w-16 h-16 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.12] rounded-full flex items-center justify-center mx-auto mb-6">
                <i class="fas fa-lock text-2xl text-blue-700 dark:text-blue-300"></i>
              </div>
              <h2 class="text-2xl font-semibold text-blue-950 dark:text-white mb-3 transition-colors duration-300">Authentication Required</h2>
              <p class="text-blue-950/70 dark:text-blue-100/70 mb-8 max-w-md mx-auto transition-colors duration-300">Please log in to view and manage your projects.</p>
              <router-link
                to="/auth/signin"
                class="btn-3d btn-accent group relative inline-flex items-center justify-center gap-3 px-8 py-4 text-blue-950 rounded-full font-medium text-lg overflow-hidden border border-white/60 dark:border-white/30"
              >
                <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent"></span>
                <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-900/15 to-transparent"></span>
                <i class="fas fa-sign-in-alt relative"></i>
                <span class="relative">Log In</span>
              </router-link>
            </div>
          </div>
        </div>

        <!-- Main 2-column layout -->
        <div v-else class="flex-1 min-h-0 max-w-6xl mx-auto w-full">
          <div class="h-full grid grid-cols-1 lg:grid-cols-2 gap-6">

            <!-- Section A: Create a Project -->
            <section class="min-h-0">
              <div class="crisp-card h-full p-6 md:p-8 rounded-2xl bg-white dark:bg-white/[0.05] border border-blue-200/70 dark:border-blue-300/[0.16] transition-colors duration-300 flex flex-col">

                <!-- Section header -->
                <div class="mb-5 flex-shrink-0">
                  <p class="inline-flex items-center px-3 py-1 rounded-full border border-blue-200/70 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-[0.18em] mb-3 transition-colors duration-300">New Project</p>
                  <h2 class="text-2xl font-semibold text-blue-950 dark:text-white mb-2 transition-colors duration-300">Create a Project</h2>
                  <p class="text-sm text-blue-950/70 dark:text-blue-100/70 transition-colors duration-300">Start a new business — build your product, then sell, market, and run it.</p>
                </div>

                <!-- Create Form -->
                <div class="flex-1 flex flex-col space-y-4 min-h-0">
                  <!-- Project Name Input -->
                  <div class="flex-shrink-0">
                    <label class="block text-sm font-medium text-blue-950/80 dark:text-blue-100/80 mb-2 transition-colors duration-300">Project Name</label>
                    <input
                      v-model="newProjectName"
                      type="text"
                      placeholder="Enter project name..."
                      class="w-full px-4 py-3 bg-white dark:bg-white/[0.04] border border-blue-200/70 dark:border-white/[0.12] focus:border-blue-400 dark:focus:border-blue-300/50 rounded-xl text-blue-950 dark:text-white placeholder-blue-950/40 dark:placeholder-white/40 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                      style="outline: none !important;"
                      :disabled="isCreating"
                    >
                  </div>

                  <!-- Project Description Input -->
                  <div class="flex-1 flex flex-col min-h-0">
                    <label class="block text-sm font-medium text-blue-950/80 dark:text-blue-100/80 mb-2 flex-shrink-0 transition-colors duration-300">
                      Description <span class="text-blue-950/40 dark:text-white/40">(optional)</span>
                    </label>
                    <textarea
                      v-model="newProjectDescription"
                      placeholder="Brief description of your project..."
                      class="w-full flex-1 min-h-[80px] px-4 py-3 bg-white dark:bg-white/[0.04] border border-blue-200/70 dark:border-white/[0.12] focus:border-blue-400 dark:focus:border-blue-300/50 rounded-xl text-blue-950 dark:text-white placeholder-blue-950/40 dark:placeholder-white/40 transition-all duration-300 resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                      style="outline: none !important;"
                      :disabled="isCreating"
                    ></textarea>
                  </div>

                  <!-- Create Button -->
                  <div class="flex-shrink-0 pt-1">
                    <button
                      @click="createProject"
                      :disabled="!newProjectName?.trim() || isCreating"
                      class="btn-3d btn-accent group relative w-full inline-flex items-center justify-center gap-3 px-8 py-3.5 text-blue-950 rounded-full font-medium text-base overflow-hidden border border-white/60 dark:border-white/30 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <span class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/70 to-transparent"></span>
                      <span class="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-blue-900/15 to-transparent"></span>
                      <template v-if="isCreating">
                        <div class="relative w-5 h-5 border-2 border-blue-950/30 border-t-blue-950 rounded-full animate-spin"></div>
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
            </section>

            <!-- Section B: Project Library -->
            <section class="min-h-0">
              <div class="crisp-card h-full p-6 md:p-8 rounded-2xl bg-white dark:bg-white/[0.05] border border-orange-200/70 dark:border-orange-300/[0.16] transition-colors duration-300 flex flex-col">

                <!-- Section header -->
                <div class="mb-5 flex-shrink-0">
                  <p class="inline-flex items-center px-3 py-1 rounded-full border border-orange-200/70 dark:border-orange-400/25 bg-orange-50/80 dark:bg-orange-400/10 text-xs font-semibold text-orange-700 dark:text-orange-300 uppercase tracking-[0.18em] mb-3 transition-colors duration-300">Your Projects</p>
                  <div class="flex items-end justify-between gap-3 mb-2">
                    <h2 class="text-2xl font-semibold text-blue-950 dark:text-white transition-colors duration-300">Project Library</h2>
                    <span
                      v-if="!isLoading && !error && displayedProjects.length > 0"
                      class="text-xs font-medium text-blue-950/50 dark:text-blue-100/50 pb-1 transition-colors duration-300"
                    >
                      {{ searchQuery ? `${displayedProjects.length} Results` : `${projects.length || 0} Projects` }}
                    </span>
                  </div>
                  <p class="text-sm text-blue-950/70 dark:text-blue-100/70 transition-colors duration-300">Continue working on your existing applications.</p>
                </div>

                <!-- Search Input -->
                <div class="mb-4 flex-shrink-0">
                  <div class="relative">
                    <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-blue-950/40 dark:text-white/40 text-sm"></i>
                    <input
                      v-model="searchQuery"
                      type="text"
                      placeholder="Search projects..."
                      class="w-full pl-11 pr-4 py-2.5 bg-white dark:bg-white/[0.04] border border-blue-200/70 dark:border-white/[0.12] focus:border-blue-400 dark:focus:border-blue-300/50 rounded-xl text-blue-950 dark:text-white placeholder-blue-950/40 dark:placeholder-white/40 text-sm transition-all duration-300"
                      style="outline: none !important;"
                    >
                  </div>
                </div>

                <!-- Inline Delete Success Notification -->
                <Transition
                  enter-active-class="transition-all duration-300 ease-out"
                  enter-from-class="opacity-0 -translate-y-2"
                  enter-to-class="opacity-100 translate-y-0"
                  leave-active-class="transition-all duration-200 ease-in"
                  leave-from-class="opacity-100 translate-y-0"
                  leave-to-class="opacity-0 -translate-y-2"
                >
                  <div
                    v-if="deletedProjectMessage"
                    class="mb-4 p-3 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-400/30 flex items-center gap-3 flex-shrink-0"
                  >
                    <div class="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-500/20 border border-red-200 dark:border-red-400/30 flex items-center justify-center flex-shrink-0">
                      <i class="fas fa-trash-alt text-red-600 dark:text-red-300 text-sm"></i>
                    </div>
                    <p class="flex-1 text-sm font-medium text-blue-950 dark:text-red-100">{{ deletedProjectMessage }}</p>
                    <button
                      @click="clearDeletedProjectMessage"
                      class="w-6 h-6 rounded-lg flex items-center justify-center text-red-400 dark:text-red-300/70 hover:text-red-600 dark:hover:text-red-200 hover:bg-red-100 dark:hover:bg-red-500/20 transition-all duration-200"
                      aria-label="Dismiss"
                    >
                      <i class="fas fa-times text-xs"></i>
                    </button>
                  </div>
                </Transition>

                <!-- Content Section -->
                <div class="flex-1 flex flex-col min-h-0">
                  <!-- Loading State -->
                  <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center">
                    <div class="w-12 h-12 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.12] rounded-full flex items-center justify-center mb-4">
                      <div class="w-6 h-6 border-2 border-blue-200 dark:border-blue-300/30 border-t-blue-600 dark:border-t-blue-300 rounded-full animate-spin"></div>
                    </div>
                    <p class="text-blue-950/70 dark:text-blue-100/70 text-sm transition-colors duration-300">Loading your projects...</p>
                  </div>

                  <!-- Error State -->
                  <div v-else-if="error" class="flex-1 flex flex-col items-center justify-center">
                    <div class="w-12 h-12 bg-red-50 dark:bg-red-500/10 border border-red-200/60 dark:border-red-400/30 rounded-full flex items-center justify-center mb-4">
                      <i class="fas fa-exclamation-triangle text-red-500 dark:text-red-300 text-xl"></i>
                    </div>
                    <p class="text-blue-950/70 dark:text-blue-100/70 mb-4 text-center max-w-md text-sm transition-colors duration-300">{{ error }}</p>
                    <button
                      @click="retryFetch"
                      class="inline-flex items-center gap-2 px-5 py-2.5 bg-white dark:bg-white/[0.06] hover:bg-blue-50 dark:hover:bg-white/[0.1] border border-blue-200/70 dark:border-white/[0.12] rounded-xl text-blue-950 dark:text-white font-medium text-sm transition-all duration-300"
                    >
                      <i class="fas fa-redo text-sm"></i>
                      <span>Try Again</span>
                    </button>
                  </div>

                  <!-- No Search Results -->
                  <div v-else-if="searchQuery?.trim() && displayedProjects.length === 0 && projects.length > 0" class="flex-1 flex flex-col items-center justify-center">
                    <div class="w-12 h-12 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.12] rounded-full flex items-center justify-center mb-4">
                      <i class="fas fa-search text-blue-950/40 dark:text-white/40 text-xl"></i>
                    </div>
                    <h3 class="text-lg font-medium text-blue-950 dark:text-white mb-1 transition-colors duration-300">No matching projects</h3>
                    <p class="text-blue-950/70 dark:text-blue-100/70 text-center text-sm transition-colors duration-300">No projects found matching "{{ searchQuery }}"</p>
                  </div>

                  <!-- Empty State -->
                  <div v-else-if="!projects.length" class="flex-1 flex flex-col items-center justify-center">
                    <div class="w-12 h-12 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.12] rounded-full flex items-center justify-center mb-4">
                      <i class="fas fa-folder-open text-blue-950/40 dark:text-white/40 text-xl"></i>
                    </div>
                    <h3 class="text-lg font-medium text-blue-950 dark:text-white mb-1 transition-colors duration-300">No projects yet</h3>
                    <p class="text-blue-950/70 dark:text-blue-100/70 text-center mb-4 text-sm transition-colors duration-300">Create your first project to start building</p>
                    <div class="flex items-center text-blue-950/50 dark:text-blue-100/50 text-sm">
                      <i class="fas fa-arrow-left mr-2 animate-pulse"></i>
                      <span>Use the form to get started</span>
                    </div>
                  </div>

                  <!-- Scrollable Project List -->
                  <div v-else-if="displayedProjects.length > 0" class="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar min-h-0">
                    <ProjectCard
                      v-for="project in displayedProjects"
                      :key="project.id"
                      :project="project"
                      @delete="confirmDelete"
                    />
                  </div>
                </div>
              </div>
            </section>

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
const deletedProjectMessage = ref('')
let deleteMessageTimeout: ReturnType<typeof setTimeout> | null = null

// Clear the inline delete success message
const clearDeletedProjectMessage = () => {
  deletedProjectMessage.value = ''
  if (deleteMessageTimeout) {
    clearTimeout(deleteMessageTimeout)
    deleteMessageTimeout = null
  }
}

// Show inline delete success message with auto-clear
const showDeleteSuccess = (projectName: string) => {
  // Clear any existing timeout
  if (deleteMessageTimeout) {
    clearTimeout(deleteMessageTimeout)
  }
  deletedProjectMessage.value = `"${projectName}" deleted successfully`
  // Auto-clear after 4 seconds
  deleteMessageTimeout = setTimeout(() => {
    deletedProjectMessage.value = ''
    deleteMessageTimeout = null
  }, 4000)
}

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
    
    // Navigate immediately to the project hub for the newly created project
    router.push({
      name: 'project-hub',
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
    
    // Show inline deletion success message in the Project Library section
    showDeleteSuccess(projectName)

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
      
      // Show inline deletion success message in the Project Library section
      showDeleteSuccess(projectName)
    } else {
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
  
  // Clear delete message timeout
  if (deleteMessageTimeout) {
    clearTimeout(deleteMessageTimeout)
    deleteMessageTimeout = null
  }
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

.dark .custom-scrollbar {
  scrollbar-color: rgba(255, 255, 255, 0.12) transparent;
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Crisp, sharply-defined cards matching Home/About - hairline edge + tight layered shadow */
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

.dark .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

/* Soft 3D button effect matching the hero "Start Building" button - blue-tinted shadows for the baby-blue fill. */
.btn-3d {
  transform: translateY(0) translateZ(0);
  transition: transform 0.3s ease, box-shadow 0.3s ease, background 0.3s ease;
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.14),
    0 4px 10px -2px rgba(30, 58, 138, 0.16),
    0 10px 20px -6px rgba(30, 58, 138, 0.18),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.12);
}

.btn-3d:active {
  transform: translateY(0) translateZ(0);
  transition-duration: 0.1s;
}

/* Soft baby-blue gradient fill */
.btn-accent {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
}

.dark .btn-accent {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
}

/* On dark, ground the light button with deep neutral shadows; keep the inner sheen */
.dark .btn-3d {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 10px 20px -6px rgba(0, 0, 0, 0.5),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.18);
}
</style>