<template>
  <div class="group relative transform transition-all duration-300">
    <!-- Existing Project Card -->
    <div v-if="project && !isNew" class="relative h-full">
      <!-- Background glow -->
      <div class="absolute -inset-0.5 bg-gradient-to-r from-violet-600/20 via-fuchsia-600/20 to-violet-600/20 rounded-2xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      
      <!-- Main card container with premium glass effect -->
      <div class="relative rounded-2xl border border-white/[0.08] bg-[#0a0a0f]/90 backdrop-blur-xl overflow-hidden h-full flex flex-col transition-all duration-300 hover:border-white/[0.12] hover:-translate-y-1">
        <!-- Accent line -->
        <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-violet-500/50 to-transparent"></div>
        
        <!-- Decorative elements -->
        <div class="absolute -bottom-16 -right-16 w-32 h-32 bg-violet-500/5 rounded-full blur-2xl pointer-events-none group-hover:opacity-80 transition-opacity duration-500"></div>
        <div class="absolute -top-16 -left-16 w-24 h-24 bg-fuchsia-500/5 rounded-full blur-2xl pointer-events-none group-hover:opacity-80 transition-opacity duration-500"></div>
        
        <!-- Card content -->
        <div class="relative z-10 p-5 flex-1 flex flex-col">
          <!-- Project header -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <!-- Icon with gradient -->
              <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-500/20 to-fuchsia-500/20 border border-violet-500/20 flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform duration-300">
                <i class="fas fa-folder text-sm text-violet-300"></i>
              </div>
              
              <!-- Project name and metadata -->
              <div class="flex-1 min-w-0">
                <h3 class="text-sm font-semibold text-white/90 truncate leading-tight">{{ project.name }}</h3>
                <div class="flex items-center text-xs text-white/40 mt-1">
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
              class="p-2 text-white/40 hover:text-red-400 transition-all duration-200 rounded-lg hover:bg-red-500/10 border border-white/[0.08] hover:border-red-400/30 flex items-center justify-center w-8 h-8 flex-shrink-0"
              title="Delete project"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
          
          <!-- Separator -->
          <div class="w-full h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent mb-4"></div>
          
          <!-- Project description -->
          <div class="mb-4 flex-1">
            <p v-if="project.description" class="text-white/50 text-xs line-clamp-2 leading-relaxed">
              {{ project.description }}
            </p>
            <p v-else class="text-white/30 text-xs italic">No description provided</p>
          </div>
          
          <!-- Open button -->
          <router-link
            :to="{ name: 'builder-workspace', params: { projectId: project.id.toString() }}"
            class="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 bg-white/[0.05] hover:bg-white/[0.08] border border-white/[0.08] hover:border-violet-400/30 text-white/90 rounded-xl transition-all duration-300 text-xs font-medium group/btn"
            title="Open project workspace"
          >
            <svg class="w-4 h-4 group-hover/btn:text-violet-400 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
