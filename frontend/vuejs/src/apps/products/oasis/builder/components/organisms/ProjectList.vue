<template>
  <div>
    <!-- Empty State -->
    <div v-if="isEmpty" class="bg-dark-800/60 rounded-xl p-6 text-center border border-dark-700/50 backdrop-blur-sm">
      <div class="mb-4 mx-auto w-16 h-16 flex items-center justify-center rounded-full bg-dark-700/40">
        <i class="fas fa-folder-open text-xl text-gray-400"></i>
      </div>
      <h3 class="text-xl font-medium text-white mb-2">No Projects Yet</h3>
      <p class="text-gray-400 mb-6">Create your first project to get started.</p>
      
      <div class="flex justify-center space-x-3">
        <button 
          @click="emit('refresh')"
          class="px-4 py-2 bg-dark-700 hover:bg-dark-600 text-gray-300 rounded-lg border border-dark-600 flex items-center"
        >
          <i class="fas fa-sync-alt mr-2"></i>
          Refresh
        </button>
        <button 
          @click="navigateToNewProject"
          class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg border border-indigo-500/40 flex items-center"
        >
          <i class="fas fa-plus mr-2"></i>
          New Project
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-else-if="isLoading" class="bg-dark-800/60 rounded-xl p-6 text-center border border-dark-700/50 backdrop-blur-sm">
      <div class="inline-block w-10 h-10 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin mb-4"></div>
      <p class="text-white">Loading your projects...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-dark-800/60 rounded-xl p-6 text-center border border-dark-700/50 backdrop-blur-sm">
      <div class="mb-4 mx-auto w-16 h-16 flex items-center justify-center rounded-full bg-red-500/10">
        <i class="fas fa-exclamation-circle text-xl text-red-500"></i>
      </div>
      <h3 class="text-xl font-medium text-white mb-2">Oops! Something went wrong</h3>
      <p class="text-gray-400 mb-6">{{ error }}</p>
      <button 
        @click="emit('retry')" 
        class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl border border-indigo-500/40 hover:border-indigo-400/50 shadow-lg hover:shadow-indigo-500/20 transform hover:-translate-y-1 transition-all duration-300"
      >
        <i class="fas fa-sync-alt mr-2"></i>
        Try Again
      </button>
    </div>

    <!-- Projects List -->
    <div v-else>
      <!-- List Header with Actions -->
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-xl text-white font-medium">
          Your Projects 
          <span class="text-gray-400 text-lg">({{ filteredProjects.length }})</span>
        </h3>
        
        <div class="flex items-center space-x-3">
          <!-- Refresh Button -->
          <button
            @click="emit('refresh')"
            class="p-2 bg-dark-800 hover:bg-dark-700 text-gray-300 rounded-lg border border-dark-700/50 transition-colors"
            title="Refresh Projects"
          >
            <i class="fas fa-sync-alt"></i>
          </button>
          
          <!-- Search Field with Icon -->
          <div class="relative">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search projects..." 
              class="pl-10 pr-4 py-2 bg-dark-800/80 border border-dark-700/50 rounded-lg text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-transparent transition-all duration-200 backdrop-blur-sm w-48 sm:w-60"
            />
            <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500"></i>
          </div>
          
          <!-- Sort Dropdown -->
          <select 
            v-model="sortBy"
            class="px-3 py-2 bg-dark-800/80 border border-dark-700/50 rounded-lg text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-transparent transition-all duration-200 backdrop-blur-sm"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="name">Name A-Z</option>
            <option value="name-desc">Name Z-A</option>
          </select>
        </div>
      </div>
      
      <!-- Project Grid -->
      <div class="grid gap-4 md:grid-cols-1 lg:grid-cols-1">
        <ProjectCard
          v-for="project in filteredProjects" 
          :key="project.id"
          :project="project"
          @delete="confirmDelete(project)"
          @edit="openProject(project)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import ProjectCard from '../molecules/ProjectCard.vue'
import type { Project } from '@/shared/types'

const router = useRouter()

// Define props
const props = defineProps<{
  projects: Project[]
  isLoading: boolean
  error: string
}>()

// Define emits
const emit = defineEmits(['delete', 'retry', 'refresh'])

// State
const searchQuery = ref('')
const sortBy = ref('newest')

// Computed properties
const isEmpty = computed(() => {
  return !props.isLoading && !props.error && (!props.projects || props.projects.length === 0)
})

const filteredProjects = computed(() => {
  if (!props.projects) return []
  
  // Filter projects by search query
  let result = props.projects.filter(project => {
    if (!searchQuery.value) return true
    
    const query = searchQuery.value.toLowerCase().trim()
    return (
      project.name?.toLowerCase().includes(query) ||
      project.description?.toLowerCase().includes(query)
    )
  })
  
  // Sort projects
  return result.sort((a, b) => {
    switch (sortBy.value) {
      case 'newest':
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      case 'oldest':
        return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      case 'name':
        return a.name.localeCompare(b.name)
      case 'name-desc':
        return b.name.localeCompare(a.name)
      default:
        return 0
    }
  })
})

// Methods
const navigateToNewProject = () => {
  router.push('/products/oasis/builder/new')
}

const confirmDelete = (project: Project) => {
  if (!project || !project.id || !project.name) return
  
  // Emit delete event with project ID and name
  if (project.id && project.name) {
    emit('delete', String(project.id), project.name)
  }
}

const openProject = (project: Project) => {
  if (!project || !project.id) return
  
  // Navigate to project workspace
  router.push({
    name: 'builder-workspace',
    params: { projectId: String(project.id) }
  })
}
</script>

<style scoped>
/* ProjectList styles */
</style> 