<template>
  <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
    <!-- Header -->
    <div class="w-14 h-14 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-xl flex items-center justify-center mb-6">
      <i class="fas fa-folder-open text-2xl text-white"></i>
    </div>
    
    <h2 class="text-2xl font-bold text-white mb-4">Your Projects</h2>
    <p class="text-gray-400 mb-8">Continue working on your existing web projects and bring your ideas to life.</p>

    <template v-if="!isLoading && !error && projects?.length">
      <!-- Recent Projects -->
      <div v-if="recentProjects.length" class="mb-8">
        <h3 class="text-sm font-medium text-gray-400 mb-4">Recently Opened</h3>
        <div class="space-y-3">
          <ProjectCard
            v-for="project in recentProjects"
            :key="project.id"
            :project="project"
            @delete="$emit('delete', project)"
          />
        </div>
      </div>

      <!-- Search Section -->
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-medium text-gray-400">All Projects</h3>
          <div class="relative group w-96">
            <!-- Add pointer-events-none class -->
            <div class="absolute inset-0 bg-gradient-to-r from-primary-500/20 to-violet-500/20 rounded-xl blur opacity-0 group-focus-within:opacity-100 transition duration-300 pointer-events-none"></div>
            <input
              :value="searchQuery"
              @input="onSearchInput"
              type="text"
              placeholder="Search all projects..."
              class="relative z-10 w-full px-4 py-2 bg-dark-900/50 border border-dark-600 focus:border-primary-500/50 rounded-xl text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
            >
          </div>
        </div>

        <!-- Search Results -->
        <div 
          v-if="searchQuery"
          class="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar"
        >
          <template v-if="filteredProjects.length">
            <ProjectCard
              v-for="project in filteredProjects"
              :key="project.id"
              :project="project"
              @delete="$emit('delete', project)"
            />
          </template>
          
          <div v-else class="text-center py-8">
            <p class="text-gray-400">No projects match your search</p>
          </div>
        </div>
      </div>
    </template>

    <!-- Loading, Error, Empty States -->
    <div v-else>
      <div v-if="isLoading" class="flex flex-col items-center justify-center py-12">
        <div class="w-14 h-14 bg-primary-500/10 rounded-full flex items-center justify-center mb-4">
          <i class="fas fa-spinner fa-spin text-2xl text-primary-400"></i>
        </div>
        <p class="text-gray-400">Loading your projects...</p>
      </div>

      <div v-else-if="error" class="flex flex-col items-center justify-center py-12">
        <div class="w-14 h-14 bg-red-500/10 rounded-full flex items-center justify-center mb-4">
          <i class="fas fa-exclamation-circle text-2xl text-red-400"></i>
        </div>
        <p class="text-gray-400 mb-4">{{ error }}</p>
        <ActionButton variant="secondary" @click="$emit('retry')">
          Try Again
        </ActionButton>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-12">
        <div class="w-14 h-14 bg-dark-700 rounded-full flex items-center justify-center mb-4">
          <i class="fas fa-folder-open text-2xl text-gray-400"></i>
        </div>
        <p class="text-gray-400 text-center">No projects yet. Create your first project to get started!</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { ProjectCard, ActionButton } from '@/apps/builder/components';

const props = defineProps({
  projects: {
    type: Array,
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  }
});

defineEmits(['delete', 'retry']);

// Local state
const searchQuery = ref('');

// Get 3 most recently updated projects for display
const recentProjects = computed(() => {
  if (!props.projects?.length) return [];
  
  return [...props.projects]
    .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    .slice(0, 3);
});

// Filter all projects based on search query (including recent ones)
const filteredProjects = computed(() => {
  if (!props.projects?.length || !searchQuery.value.trim()) return [];

  const query = searchQuery.value.toLowerCase().trim();
  
  return [...props.projects]
    .filter(project => 
      project.name.toLowerCase().includes(query) ||
      project.description?.toLowerCase().includes(query)
    )
    .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
});

function onSearchInput(e) {
  searchQuery.value = e.target.value;
}
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
</style>
