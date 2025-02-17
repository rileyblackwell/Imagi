<template>
  <BuilderLayout 
    storage-key="builderDashboardSidebarCollapsed"
    :navigation-items="navigationItems"
  >
    <!-- Main Content with Gradient Background -->
    <div class="min-h-screen bg-dark-900 relative">
      <!-- Enhanced Background Effects -->
      <div class="absolute inset-0">
        <div class="absolute inset-0 bg-gradient-to-br from-primary-500/5 via-dark-900 to-violet-500/5"></div>
        <div class="absolute top-20 left-1/2 -translate-x-1/2 w-[1000px] h-[600px] bg-gradient-to-r from-primary-500/10 to-violet-500/10 rounded-full blur-[120px] opacity-50"></div>
        <div class="absolute inset-0 bg-[url('/grid-pattern.svg')] opacity-[0.02]"></div>
      </div>

      <!-- Content -->
      <div class="relative py-12 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
          <!-- Welcome Section -->
          <div class="text-center mb-12">
            <div class="inline-block px-4 py-1 bg-dark-800/50 backdrop-blur-sm rounded-full border border-primary-500/50 mb-6">
              <span class="text-sm font-medium text-gray-300">
                <i class="fas fa-sparkles text-primary-500 mr-2"></i>
                AI-Powered Project Builder
              </span>
            </div>
            <h1 class="text-4xl font-bold text-white mb-4">Welcome to Your Dashboard</h1>
            <p class="text-xl text-gray-300 max-w-2xl mx-auto">
              Create and manage your web projects using AI-powered tools. Start with a new project or continue working on existing ones.
            </p>
          </div>

          <!-- Project Cards Grid -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Remove the search input since it's now in ProjectList -->
            
            <!-- New Project Card -->
            <NewProjectCard
              v-model="newProjectName"
              :is-loading="isCreating"
              @submit="createProject"
            />

            <!-- Existing Projects - Pass unfiltered projects -->
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
  </BuilderLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { BuilderLayout } from '@/apps/products/builder/layouts'
import { useProjectStore } from '@/apps/products/builder/stores/projectStore'
import { useNotification } from '@/shared/composables/useNotification'
import type { Project } from '@/shared/types'
import { NewProjectCard, ProjectList } from '@/apps/products/builder/components/organisms'

const router = useRouter()
const projectStore = useProjectStore()
const { showNotification } = useNotification()

// State with types - remove searchQuery since it's handled in ProjectList
const newProjectName = ref('')
const isCreating = ref(false)

// Computed with types - remove filteredProjects
const projects = computed(() => projectStore.projects)
const isLoading = computed(() => projectStore.loading)
const error = computed(() => projectStore.error || '') // Provide empty string default

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
    to: '/builder/projects',
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
  console.debug('Dashboard: Component mounted')
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
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: var(--color-gray-700) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgb(var(--color-gray-700));
  border-radius: 9999px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgb(var(--color-gray-600));
}
</style>