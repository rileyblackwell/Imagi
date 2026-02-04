<template>
  <div class="group relative transform transition-all duration-300 hover:-translate-y-0.5">
    <!-- Project Card -->
    <div v-if="project && !isNew" class="relative h-full">
      <!-- Main card container with clean style -->
      <div class="relative rounded-xl border border-gray-200 dark:border-gray-300 bg-gray-50 dark:bg-gray-50 overflow-hidden h-full flex flex-col transition-all duration-300 hover:border-gray-300 dark:hover:border-gray-400 hover:shadow-md">
        
        <!-- Card content -->
        <div class="relative z-10 p-4 flex-1 flex flex-col">
          <!-- Project header -->
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <!-- Icon -->
              <div class="w-9 h-9 rounded-lg bg-gray-200 dark:bg-gray-200 flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform duration-300">
                <i class="fas fa-folder text-sm text-gray-600 dark:text-gray-600"></i>
              </div>
              
              <!-- Project name and metadata -->
              <div class="flex-1 min-w-0">
                <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-900 truncate leading-tight">{{ project.name }}</h3>
                <div class="flex items-center text-xs text-gray-500 dark:text-gray-600 mt-1">
                  <svg class="w-3 h-3 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ formatDate(project.updated_at) }}
                </div>
              </div>
            </div>
            
            <!-- Delete button -->
            <button
              @click.stop="confirmDelete"
              class="p-2 text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-500 transition-all duration-200 rounded-lg hover:bg-red-50 dark:hover:bg-red-50 border border-transparent hover:border-red-200 dark:hover:border-red-200 flex items-center justify-center w-8 h-8 flex-shrink-0"
              title="Delete project"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
          
          <!-- Project description -->
          <div class="mb-3 flex-1">
            <p v-if="project.description" class="text-gray-600 dark:text-gray-700 text-xs line-clamp-2 leading-relaxed">
              {{ project.description }}
            </p>
            <p v-else class="text-gray-400 dark:text-gray-500 text-xs italic">No description provided</p>
          </div>
          
          <!-- Open button -->
          <router-link
            :to="{ name: 'builder-workspace', params: { projectId: project.id.toString() }}"
            class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-gray-900 dark:bg-gray-900 hover:bg-gray-800 dark:hover:bg-gray-800 text-white rounded-lg transition-all duration-300 text-xs font-medium group/btn"
            title="Open project workspace"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
            </svg>
            <span>Open Project</span>
            <i class="fas fa-arrow-right text-xs transform group-hover/btn:translate-x-1 transition-transform duration-200"></i>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Project } from '../../../types/components'

const props = defineProps<{
  project?: Project;
  modelValue?: string;
  description?: string;
  isLoading?: boolean;
  isNew?: boolean;
}>();

const emit = defineEmits<{
  (e: 'delete', project: Project): void;
  (e: 'update:modelValue', value: string): void;
  (e: 'update:description', value: string): void;
  (e: 'submit'): void;
}>();

function formatDate(date?: string) {
  if (!date) return 'No date available';
  
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(new Date(date));
}

function confirmDelete() {
  if (props.project) {
    emit('delete', props.project);
  }
}
</script>
