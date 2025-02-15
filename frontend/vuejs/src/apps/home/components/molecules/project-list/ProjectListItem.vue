<template>
  <div
    class="group p-4 rounded-lg bg-dark-800/50 hover:bg-dark-700/50 transition-all cursor-pointer border border-dark-700/50 hover:border-primary-500/50 hover:shadow-lg hover:shadow-primary-500/5"
    @click="$emit('click')"
  >
    <div class="flex items-start justify-between">
      <!-- Project Main Info -->
      <div class="flex items-start space-x-4">
        <!-- Framework Icon -->
        <div class="mt-1 w-10 h-10 flex items-center justify-center rounded-lg bg-dark-700 border border-dark-600">
          <i :class="[
            frameworkIcon,
            'text-lg',
            getFrameworkColor(project.framework)
          ]"></i>
        </div>

        <!-- Project Details -->
        <div class="space-y-1">
          <div class="flex items-center space-x-2">
            <h3 class="text-white font-medium group-hover:text-primary-400 transition-colors">
              {{ project.name }}
            </h3>
            <span 
              class="px-2 py-0.5 text-xs rounded-full"
              :class="getStatusClasses(project.status)"
            >
              {{ project.status }}
            </span>
          </div>
          <p class="text-sm text-gray-400 line-clamp-2">
            {{ project.description || 'No description' }}
          </p>
          
          <!-- Project Meta -->
          <div class="flex items-center space-x-4 text-xs text-gray-500">
            <span class="flex items-center space-x-1">
              <i class="fas fa-code"></i>
              <span>{{ project.framework || 'Unknown' }}</span>
            </span>
            <span class="flex items-center space-x-1">
              <i class="fas fa-clock"></i>
              <span>{{ formatDate(project.updatedAt) }}</span>
            </span>
          </div>
        </div>
      </div>

      <!-- Right Actions -->
      <div class="flex items-center space-x-2">
        <div v-if="project.progress !== undefined" class="text-right mr-4">
          <div class="flex items-center space-x-2">
            <div class="w-20 h-1.5 rounded-full bg-dark-600 overflow-hidden">
              <div
                class="h-full rounded-full bg-primary-500 transition-all duration-500"
                :style="{ width: `${project.progress}%` }"
              ></div>
            </div>
            <span class="text-xs text-gray-400">{{ project.progress }}%</span>
          </div>
        </div>
        <i class="fas fa-chevron-right text-gray-400 group-hover:text-primary-400 transition-colors"></i>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Project {
  id: string | number;
  name: string;
  description?: string;
  status: 'active' | 'pending' | 'failed' | 'inactive';
  updatedAt: string | Date;
  framework?: string;
  progress?: number;
}

const props = defineProps<{
  project: Project;
}>();

defineEmits<{
  (e: 'click'): void;
}>();

const formatDate = (date: string | Date): string => {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
};

const getStatusClasses = (status: string) => {
  const baseClasses = 'border';
  switch (status) {
    case 'active':
      return `${baseClasses} bg-success-500/10 border-success-500/20 text-success-400`;
    case 'pending':
      return `${baseClasses} bg-warning-500/10 border-warning-500/20 text-warning-400`;
    case 'failed':
      return `${baseClasses} bg-error-500/10 border-error-500/20 text-error-400`;
    default:
      return `${baseClasses} bg-gray-500/10 border-gray-500/20 text-gray-400`;
  }
};

const getFrameworkColor = (framework?: string) => {
  switch (framework?.toLowerCase()) {
    case 'vue':
      return 'text-emerald-400';
    case 'react':
      return 'text-blue-400';
    case 'angular':
      return 'text-red-400';
    default:
      return 'text-gray-400';
  }
};

const frameworkIcon = computed(() => {
  switch (props.project.framework?.toLowerCase()) {
    case 'vue':
      return 'fab fa-vuejs';
    case 'react':
      return 'fab fa-react';
    case 'angular':
      return 'fab fa-angular';
    default:
      return 'fas fa-code';
  }
});
</script>
