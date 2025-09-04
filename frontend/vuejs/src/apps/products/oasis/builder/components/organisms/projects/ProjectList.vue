<template>
  <div class="relative rounded-2xl border border-gray-800/60 bg-dark-900/40 backdrop-blur-sm transition-all duration-500 hover:shadow-[0_0_25px_-5px_rgba(99,102,241,0.5)] overflow-hidden p-8">
    <!-- Background gradient -->
    <div class="absolute inset-0 bg-gradient-to-br opacity-10 -z-10 transition-opacity duration-300 group-hover:opacity-20 from-indigo-900 to-violet-900"></div>
    
    <!-- Glowing orb effect -->
    <div class="absolute -bottom-20 -right-20 w-40 h-40 rounded-full opacity-10 blur-3xl transition-opacity duration-500 group-hover:opacity-20 bg-indigo-500"></div>
    
    <!-- Enhanced Header with badge styling to match project card -->
    <div class="relative z-10 mb-8">
      <div class="flex items-center justify-between mb-4">
        <div class="inline-block px-4 py-1.5 bg-indigo-500/10 rounded-full">
          <span class="text-indigo-400 font-semibold text-sm tracking-wider">YOUR PROJECTS</span>
        </div>
      </div>
      
      <!-- Title section -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-2xl font-bold text-white">Project Library</h2>
          
          <!-- Enhanced combined project icon with count -->
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
        
        <p class="text-gray-300">Continue working on your existing web applications</p>
        
        <!-- Decorative element matching new project card -->
        <div class="w-16 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full mt-4"></div>
      </div>
    </div>

    <template v-if="!isLoading && !error && projects?.length">
      <!-- Recent Projects with Enhanced Styling -->
      <div v-if="recentProjects.length" class="mb-10">
        <div class="flex items-center bg-indigo-500/5 rounded-lg px-4 py-2 mb-5">
          <i class="fas fa-clock text-indigo-400 mr-3"></i>
          <h3 class="text-sm font-medium text-white uppercase tracking-wider">Recently Opened</h3>
        </div>
        
        <div class="space-y-4">
          <ProjectCard
            v-for="project in recentProjects"
            :key="project.id"
            :project="project"
            @delete="$emit('delete', project.id, project.name)"
          />
        </div>
      </div>

      <!-- All Projects Section -->
      <div class="space-y-5">
        <div class="flex items-center bg-indigo-500/5 rounded-lg px-4 py-2 mb-4">
          <i class="fas fa-folder text-indigo-400 mr-3"></i>
          <h3 class="text-sm font-medium text-white uppercase tracking-wider">All Projects</h3>
        </div>

        <!-- Projects List with Enhanced Scrollbar -->
        <div class="space-y-4 max-h-[350px] overflow-y-auto pr-2 custom-scrollbar">
          <template v-if="props.projects.length > 3">
            <ProjectCard
              v-for="project in otherProjects"
              :key="project.id"
              :project="project"
              @delete="$emit('delete', project.id, project.name)"
            />
          </template>
          <div v-else-if="recentProjects.length === 0" class="flex flex-col items-center justify-center py-12">
            <i class="fas fa-folder-open text-3xl text-indigo-400 mb-3 opacity-70"></i>
            <p class="text-gray-300">No additional projects</p>
          </div>
        </div>
      </div>
    </template>

    <!-- Enhanced Loading, Error, Empty States -->
    <div v-else>
      <div v-if="isLoading" class="flex flex-col items-center justify-center py-16">
        <div class="w-16 h-16 bg-indigo-500/10 rounded-full flex items-center justify-center mb-5 animate-pulse">
          <i class="fas fa-spinner fa-spin text-2xl text-indigo-400"></i>
        </div>
        <p class="text-gray-300 text-lg">Loading your projects...</p>
      </div>

      <div v-else-if="error" class="flex flex-col items-center justify-center py-16">
        <div class="w-16 h-16 bg-red-500/10 rounded-full flex items-center justify-center mb-5">
          <i class="fas fa-exclamation-circle text-2xl text-red-400"></i>
        </div>
        <p class="text-gray-300 mb-6 text-center max-w-md">{{ error }}</p>
        <GradientButton
          @click="$emit('retry')"
        >
          <i class="fas fa-sync-alt mr-2"></i>
          Try Again
        </GradientButton>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-16">
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
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ProjectCard from '../../molecules/cards/ProjectCard.vue'
import { GradientButton } from '@/shared/components/atoms'
import type { Project } from '../../../types/components'
import type { ProjectListProps } from '../../../types/components'

const props = defineProps<ProjectListProps>()

// Get 3 most recently updated projects for display
const recentProjects = computed(() => {
  if (!props.projects?.length) return []
  
  return [...props.projects]
    .sort((a, b) => {
      // Handle cases where updated_at might be undefined
      if (!a.updated_at) return 1;  // If a's date is missing, b comes first
      if (!b.updated_at) return -1; // If b's date is missing, a comes first
      
      const dateA = new Date(a.updated_at).getTime()
      const dateB = new Date(b.updated_at).getTime()
      return dateB - dateA
    })
    .slice(0, 3)
})

// Get all projects except the recent ones
const otherProjects = computed(() => {
  if (!props.projects?.length) return []
  
  const recentIds = new Set(recentProjects.value.map(p => p.id))
  
  return [...props.projects]
    .filter(project => !recentIds.has(project.id))
    .sort((a, b) => {
      // Handle cases where updated_at might be undefined
      if (!a.updated_at) return 1;  // If a's date is missing, b comes first
      if (!b.updated_at) return -1; // If b's date is missing, a comes first
      
      const dateA = new Date(a.updated_at).getTime()
      const dateB = new Date(b.updated_at).getTime()
      return dateB - dateA
    })
})
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
</style>
