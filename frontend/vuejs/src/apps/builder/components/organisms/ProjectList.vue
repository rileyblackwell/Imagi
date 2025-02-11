<template>
  <div class="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700 hover:border-primary-500/50 transition-all duration-300">
    <div class="w-14 h-14 bg-gradient-to-br from-indigo-500 to-violet-500 rounded-xl flex items-center justify-center mb-6">
      <i class="fas fa-folder-open text-2xl text-white"></i>
    </div>
    
    <h2 class="text-2xl font-bold text-white mb-4">Your Projects</h2>
    <p class="text-gray-400 mb-8">Continue working on your existing web projects and bring your ideas to life.</p>

    <div class="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
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

      <template v-else-if="projects && projects.length > 0">
        <ProjectCard
          v-for="project in projects"
          :key="project.id"
          :project="project"
          @delete="$emit('delete', project)"
        />
      </template>

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
import { ProjectCard, ActionButton } from '@/apps/builder/components';

defineProps({
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
