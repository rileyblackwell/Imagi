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
    <div class="projects-page relative transition-colors duration-500 min-h-screen overflow-hidden font-body">
      <!-- Grain texture over the porcelain canvas -->
      <div class="grain-overlay absolute inset-0 z-[1] pointer-events-none" aria-hidden="true"></div>

      <!-- Atmosphere: one soft apricot wash behind the header -->
      <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div class="page-glow-warm absolute -top-40 left-1/2 -translate-x-1/2 w-[760px] h-[440px]"></div>
      </div>

      <!-- Main Content (pt-20 clears the fixed h-14 navbar) -->
      <main class="relative z-10 flex flex-col px-6 sm:px-8 lg:px-12 pt-20 pb-8 min-h-screen">
        <!-- Compact Hero -->
        <section class="rise-item flex-shrink-0 max-w-6xl mx-auto w-full text-center mb-6 md:mb-8" style="animation-delay: 0ms">
          <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-blue-200/70 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-[0.18em] mb-4 transition-colors duration-300">Workspace</p>
          <h1 class="font-display text-4xl sm:text-5xl font-semibold text-blue-950 dark:text-white mb-3 tracking-[-0.02em] leading-[1.05] text-balance transition-colors duration-300">
            Your <em class="accent-ink not-italic">Projects</em>
          </h1>
          <p class="text-base sm:text-lg text-blue-950/65 dark:text-blue-100/65 leading-relaxed transition-colors duration-300">
            Start a new business or keep building and running an existing one.
          </p>
        </section>

        <!-- Authentication Error -->
        <div v-if="showAuthError" class="rise-item flex-1 flex items-center justify-center" style="animation-delay: 90ms">
          <div class="max-w-2xl mx-auto w-full">
            <div class="crisp-card relative p-10 rounded-2xl bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm border border-blue-200/70 dark:border-blue-300/[0.14] text-center transition-colors duration-300">
              <div class="w-16 h-16 bg-blue-50 dark:bg-white/[0.06] border border-blue-200/60 dark:border-white/[0.14] rounded-full flex items-center justify-center mx-auto mb-6">
                <i class="fas fa-lock text-2xl text-blue-700 dark:text-blue-300"></i>
              </div>
              <h2 class="text-2xl font-semibold tracking-tight text-blue-950 dark:text-white mb-3 transition-colors duration-300">Authentication Required</h2>
              <p class="text-blue-950/70 dark:text-blue-100/70 mb-8 max-w-md mx-auto transition-colors duration-300">Please log in to view and manage your projects.</p>
              <router-link
                to="/auth/signin"
                class="group inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full font-medium text-lg bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)] hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)] dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
              >
                <i class="fas fa-sign-in-alt"></i>
                <span>Log In</span>
              </router-link>
            </div>
          </div>
        </div>

        <!-- Main 2-column layout -->
        <div v-else class="flex-1 min-h-0 max-w-6xl mx-auto w-full">
          <div class="h-full grid grid-cols-1 lg:grid-cols-2 gap-6">

            <!-- Section A: Create a Project -->
            <section class="rise-item min-h-0" style="animation-delay: 90ms">
              <div class="crisp-card h-full p-6 md:p-8 rounded-2xl bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm border border-blue-200/70 dark:border-blue-300/[0.14] transition-colors duration-300 flex flex-col">

                <!-- Section header -->
                <div class="mb-5 flex-shrink-0">
                  <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-blue-200/70 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-xs font-semibold text-blue-700 dark:text-blue-300 uppercase tracking-[0.18em] mb-3 transition-colors duration-300">New Project</p>
                  <h2 class="text-2xl font-semibold tracking-tight text-blue-950 dark:text-white mb-2 transition-colors duration-300">Create a Project</h2>
                  <p class="text-sm text-blue-950/65 dark:text-blue-100/65 leading-relaxed transition-colors duration-300">Start a new business — describe it, and Imagi builds the first version of your app.</p>
                </div>

                <!-- Create Form -->
                <div class="flex-1 flex flex-col space-y-4 min-h-0">
                  <!-- Business Name Input -->
                  <div class="flex-shrink-0">
                    <label class="block text-sm font-medium text-blue-950/80 dark:text-blue-100/80 mb-2 transition-colors duration-300">Business Name</label>
                    <input
                      v-model="newProjectName"
                      type="text"
                      placeholder="Enter your business name..."
                      class="w-full px-4 py-3 bg-white dark:bg-white/[0.04] border border-blue-200/70 dark:border-white/[0.14] focus:border-blue-400 dark:focus:border-blue-300/50 rounded-xl text-blue-950 dark:text-white placeholder-blue-950/40 dark:placeholder-blue-100/40 transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e] disabled:opacity-50 disabled:cursor-not-allowed"
                      :disabled="isCreating"
                    >
                  </div>

                  <!-- Business Description Input -->
                  <div class="flex-1 flex flex-col min-h-0">
                    <label class="block text-sm font-medium text-blue-950/80 dark:text-blue-100/80 mb-1 flex-shrink-0 transition-colors duration-300">
                      Business Description
                    </label>
                    <p class="text-xs text-blue-950/70 dark:text-blue-100/55 mb-2 flex-shrink-0 transition-colors duration-300">
                      Imagi's AI uses this to build the first version of your app.
                    </p>
                    <textarea
                      v-model="newProjectDescription"
                      placeholder="What does your business do? Who are its customers? What does the market look like, and how will you sell?"
                      class="w-full flex-1 min-h-[80px] px-4 py-3 bg-white dark:bg-white/[0.04] border border-blue-200/70 dark:border-white/[0.14] focus:border-blue-400 dark:focus:border-blue-300/50 rounded-xl text-blue-950 dark:text-white placeholder-blue-950/40 dark:placeholder-blue-100/40 transition-all duration-300 resize-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e] disabled:opacity-50 disabled:cursor-not-allowed"
                      :disabled="isCreating"
                    ></textarea>
                  </div>

                  <!-- Create Button -->
                  <div class="flex-shrink-0 pt-1">
                    <button
                      @click="createProject"
                      :disabled="!canCreate || isCreating"
                      class="group w-full inline-flex items-center justify-center gap-3 px-8 py-3.5 rounded-full font-medium text-base bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-all duration-200 hover:-translate-y-0.5 active:translate-y-0 shadow-[0_1px_2px_rgba(23,37,84,0.25),0_8px_20px_-6px_rgba(23,37,84,0.35),inset_0_1px_0_rgba(255,255,255,0.12)] hover:shadow-[0_2px_3px_rgba(23,37,84,0.22),0_14px_28px_-8px_rgba(23,37,84,0.4),inset_0_1px_0_rgba(255,255,255,0.12)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.5),0_10px_24px_-8px_rgba(0,0,0,0.55)] dark:hover:shadow-[0_2px_3px_rgba(0,0,0,0.5),0_14px_30px_-8px_rgba(0,0,0,0.6)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e] disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <template v-if="isCreating">
                        <div class="w-5 h-5 border-2 border-[#fdf9f2]/30 border-t-[#fdf9f2] dark:border-blue-950/30 dark:border-t-blue-950 rounded-full animate-spin"></div>
                        <span>Creating...</span>
                      </template>
                      <template v-else>
                        <span>Create Project</span>
                        <svg class="w-5 h-5 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                        </svg>
                      </template>
                    </button>
                  </div>
                </div>
              </div>
            </section>

            <!-- Section B: Project Library -->
            <section class="rise-item min-h-0" style="animation-delay: 180ms">
              <div class="crisp-card h-full p-6 md:p-8 rounded-2xl bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm border border-orange-200/70 dark:border-orange-300/[0.14] transition-colors duration-300 flex flex-col">

                <!-- Section header -->
                <div class="mb-5 flex-shrink-0">
                  <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/25 bg-orange-50/80 dark:bg-orange-400/10 text-xs font-semibold text-orange-700 dark:text-orange-300 uppercase tracking-[0.18em] mb-3 transition-colors duration-300">Your Projects</p>
                  <div class="flex items-end justify-between gap-3 mb-2">
                    <h2 class="text-2xl font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300">Project Library</h2>
                    <span
                      v-if="!isLoading && !error && displayedProjects.length > 0"
                      class="inline-flex items-center px-2.5 py-1 mb-0.5 rounded-full border border-blue-200/60 dark:border-white/[0.14] bg-white/85 dark:bg-white/[0.04] text-xs font-medium text-blue-950/70 dark:text-blue-100/55 transition-colors duration-300"
                    >
                      {{ searchQuery ? `${displayedProjects.length} Results` : `${projects.length || 0} Projects` }}
                    </span>
                  </div>
                  <p class="text-sm text-blue-950/65 dark:text-blue-100/65 leading-relaxed transition-colors duration-300">Continue working on your existing applications.</p>
                </div>

                <!-- Search Input -->
                <div class="mb-4 flex-shrink-0">
                  <div class="relative">
                    <i class="fas fa-search absolute left-4 top-1/2 -translate-y-1/2 text-blue-950/40 dark:text-blue-100/40 text-sm"></i>
                    <input
                      v-model="searchQuery"
                      type="text"
                      placeholder="Search projects..."
                      class="w-full pl-11 pr-4 py-2.5 bg-white dark:bg-white/[0.04] border border-blue-200/70 dark:border-white/[0.14] focus:border-blue-400 dark:focus:border-blue-300/50 rounded-xl text-blue-950 dark:text-white placeholder-blue-950/40 dark:placeholder-blue-100/40 text-sm transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
                    >
                  </div>
                </div>

                <!-- Content Section -->
                <div class="flex-1 flex flex-col min-h-0">
                  <!-- Loading State -->
                  <div v-if="isLoading" class="flex-1 flex flex-col items-center justify-center">
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-1 ring-blue-900/[0.08] dark:ring-blue-300/[0.18] flex items-center justify-center mb-4">
                      <div class="w-6 h-6 border-2 border-blue-200 dark:border-blue-300/30 border-t-blue-600 dark:border-t-blue-300 rounded-full animate-spin"></div>
                    </div>
                    <p class="text-blue-950/70 dark:text-blue-100/70 text-sm transition-colors duration-300">Loading your projects...</p>
                  </div>

                  <!-- Error State -->
                  <div v-else-if="error" class="flex-1 flex flex-col items-center justify-center">
                    <div class="w-12 h-12 rounded-xl bg-red-50 dark:bg-red-500/10 ring-1 ring-red-900/[0.08] dark:ring-red-400/30 flex items-center justify-center mb-4">
                      <i class="fas fa-exclamation-triangle text-red-500 dark:text-red-300 text-xl"></i>
                    </div>
                    <p class="text-blue-950/70 dark:text-blue-100/70 mb-4 text-center max-w-md text-sm transition-colors duration-300">{{ error }}</p>
                    <button
                      @click="retryFetch"
                      class="inline-flex items-center gap-2 px-5 py-2.5 rounded-full border border-blue-950/[0.14] text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06] font-medium text-sm transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
                    >
                      <i class="fas fa-redo text-sm"></i>
                      <span>Try Again</span>
                    </button>
                  </div>

                  <!-- No Search Results -->
                  <div v-else-if="searchQuery?.trim() && displayedProjects.length === 0 && projects.length > 0" class="flex-1 flex flex-col items-center justify-center">
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-1 ring-blue-900/[0.08] dark:ring-blue-300/[0.18] flex items-center justify-center mb-4">
                      <i class="fas fa-search text-blue-600 dark:text-blue-300 text-lg"></i>
                    </div>
                    <h3 class="text-lg font-medium text-blue-950 dark:text-white mb-1 transition-colors duration-300">No matching projects</h3>
                    <p class="text-blue-950/70 dark:text-blue-100/70 text-center text-sm transition-colors duration-300">No projects found matching "{{ searchQuery }}"</p>
                  </div>

                  <!-- Empty State -->
                  <!--
                    Keyed off displayedProjects (what's actually shown) rather than
                    the raw store list, so deleting the last project immediately
                    surfaces this "No projects yet" state instead of a blank panel.
                  -->
                  <div v-else-if="!displayedProjects.length" class="flex-1 flex flex-col items-center justify-center">
                    <div class="w-12 h-12 rounded-xl bg-orange-100 dark:bg-orange-400/[0.14] ring-1 ring-orange-900/[0.08] dark:ring-orange-300/[0.18] flex items-center justify-center mb-4">
                      <i class="fas fa-folder-open text-orange-600 dark:text-orange-300 text-lg"></i>
                    </div>
                    <h3 class="text-lg font-medium text-blue-950 dark:text-white mb-1 transition-colors duration-300">No projects yet</h3>
                    <p class="text-blue-950/70 dark:text-blue-100/70 text-center text-sm transition-colors duration-300">Create your first project to start building</p>
                  </div>

                  <!-- Scrollable Project List -->
                  <div v-else class="flex-1 overflow-y-auto pr-2 pl-0.5 pt-1 pb-2 space-y-3 custom-scrollbar min-h-0">
                    <ProjectCard
                      v-for="(project, index) in displayedProjects"
                      :key="project.id"
                      :project="project"
                      :accent="index % 2 === 1 ? 'orange' : 'blue'"
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
import { useProjectStore } from '@/apps/imagi/build/stores/projectStore'
import { useNotification } from '@/shared/composables/useNotification'
import { ProjectCard } from '../components/molecules/cards'
import { useAuthStore } from '@/shared/stores/auth'
import { useConfirm } from '@/apps/imagi/build/composables/useConfirm'
import { useNotificationStore } from '@/shared/stores/notificationStore'
import { useProjectSearch } from '../composables/useProjectSearch'
import type { Project } from '@/apps/imagi/build/types/components'
import { normalizeProject } from '@/apps/imagi/build/types/components'
import { toSlug } from '@/apps/imagi/build/utils/slug'
import { ConfirmModal } from '@/apps/imagi/build/components/organisms/modals'


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

// The description seeds the initial AI build, so require enough signal to
// work with. Keep in sync with MIN_DESCRIPTION_LENGTH on the backend
// (ProjectManager/api/serializers.py).
const MIN_DESCRIPTION_LENGTH = 20
const canCreate = computed(() =>
  Boolean(newProjectName.value.trim()) &&
  newProjectDescription.value.trim().length >= MIN_DESCRIPTION_LENGTH
)
const isInitializing = ref(true)

// Show a global toast confirming a project was deleted.
const showDeleteSuccess = (projectName: string) => {
  showNotification({
    type: 'delete',
    message: `"${projectName}" deleted successfully`,
    duration: 4000
  })
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
  const hasSearchQuery = searchQuery.value?.trim().length > 0;

  if (hasSearchQuery) {
    return (filteredProjects.value || []).filter(project => project && project.id);
  }

  if (!normalizedProjects.value?.length) {
    return [];
  }

  return [...normalizedProjects.value]
    .filter(project => project && project.id)
    .sort((a, b) => {
      if (!a.updated_at) return 1;
      if (!b.updated_at) return -1;

      const dateA = new Date(a.updated_at).getTime()
      const dateB = new Date(b.updated_at).getTime()
      return dateB - dateA
    });
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
  
  // Validate business name
  if (!newProjectName.value.trim()) {
    showNotification({
      message: 'Business name cannot be empty',
      type: 'error'
    })
    return
  }

  // Validate business description — it seeds the initial AI build
  if (newProjectDescription.value.trim().length < MIN_DESCRIPTION_LENGTH) {
    showNotification({
      message: 'Please describe your business — what it does, who its customers are, and how it will sell. Imagi uses this to build the first version of your app.',
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
    // The store owns the delete: it optimistically removes the project from the
    // list, records the deletion tombstone, clears the cache, and treats a 404
    // from the server as success. Because the list updates optimistically, the
    // UI reflects the deletion the moment this resolves — the remaining projects
    // (or the "No projects yet" empty state) render immediately without waiting
    // on a forced refetch that could hang or race and leave the panel spinning.
    await projectStore.deleteProject(String(project.id))

    // Confirm the deletion right away, independent of any background refresh.
    showDeleteSuccess(projectName)

    // If the user was in the workspace for this project, navigate away from it.
    if (isCurrentlyInWorkspace) {
      await router.push({ name: 'projects' })
    }
  } catch (error: any) {
    console.error('Error deleting project:', error)

    // A real failure (the store already treats 404 as success). The optimistic
    // removal leaves the project missing from the list, so reconcile with the
    // server to bring it back, then report the error.
    showNotification({
      message: error?.message || `Failed to delete "${projectName}"`,
      type: 'error',
      duration: 5000
    })

    try {
      await fetchProjects(true)
    } catch (refreshError) {
      console.warn('Failed to refresh projects after failed deletion:', refreshError)
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
/* Warm porcelain canvas fading to white so the page hands off to the footer
   (footer is bg-white / dark #0a0a0a) — matches Home.vue */
.projects-page {
  background: linear-gradient(180deg, #fdf9f2 0%, #faf7f1 45%, #ffffff 100%);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}

.dark .projects-page {
  background: linear-gradient(180deg, #0c0c0e 0%, #0a0b0f 50%, #0a0a0a 100%);
}

/* Fine film grain keeps large soft gradients from banding and adds texture */
.grain-overlay {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160' viewBox='0 0 160 160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
  background-size: 160px 160px;
  opacity: 0.035;
  mix-blend-mode: multiply;
}

.dark .grain-overlay {
  opacity: 0.05;
  mix-blend-mode: overlay;
}

/* Soft apricot wash behind the page header */
.page-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.13), rgba(251, 146, 60, 0.04) 55%, transparent 75%);
  filter: blur(48px);
}

.dark .page-glow-warm {
  background: radial-gradient(closest-side, rgba(251, 146, 60, 0.07), rgba(251, 146, 60, 0.02) 55%, transparent 75%);
}

/* Italic serif accent with the hero's warm gradient ink */
.accent-ink {
  font-style: italic;
  font-variation-settings: 'SOFT' 30, 'WONK' 1;
  background: linear-gradient(115deg, #c2410c 5%, #ea580c 55%, #b45309 95%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  padding-right: 0.06em;
}

.dark .accent-ink {
  background: linear-gradient(115deg, #fb923c 5%, #fcd34d 60%, #f59e0b 95%);
  -webkit-background-clip: text;
  background-clip: text;
}

/* Page-load rise: header and panels fade up in sequence */
.rise-item {
  animation: rise-up 0.7s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes rise-up {
  from {
    opacity: 0;
    transform: translateY(18px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (prefers-reduced-motion: reduce) {
  .rise-item {
    animation: none;
  }
}

/* Quiet native input decorations (rings are applied via focus-visible classes) */
input, textarea {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
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

</style>

<!-- Unscoped: brand-tinted text selection on the projects page -->
<style>
.projects-page ::selection {
  background: rgba(158, 205, 243, 0.55);
  color: #172554;
}

.dark .projects-page ::selection {
  background: rgba(96, 165, 250, 0.4);
  color: #eff6ff;
}
</style>
