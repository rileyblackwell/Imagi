<template>
  <div class="group relative">
    <!-- Existing Project Card -->
    <div v-if="project && !isNew" class="relative h-full">
      <!-- Subtle background glow (matching main dashboard cards) -->
      <div class="absolute -inset-1 bg-gradient-to-r from-fuchsia-600/10 via-violet-600/10 to-fuchsia-600/10 rounded-2xl blur-lg opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      
      <!-- Main card container with premium glass effect matching dashboard -->
      <div class="relative rounded-xl border border-white/[0.08] bg-[#0a0a0f]/80 backdrop-blur-xl overflow-hidden h-full flex flex-col transition-all duration-300 hover:border-white/[0.12]">
        <!-- Gradient accent line at top (matching main dashboard cards) -->
        <div class="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-fuchsia-500/50 to-transparent"></div>
        
        <!-- Decorative background orbs (matching main dashboard cards) -->
        <div class="absolute -bottom-20 -right-20 w-32 h-32 bg-fuchsia-500/5 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute -top-20 -left-20 w-24 h-24 bg-violet-500/5 rounded-full blur-3xl pointer-events-none"></div>
        
        <!-- Card content -->
        <div class="relative z-10 p-4 flex-1 flex flex-col">
          <!-- Project header -->
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center gap-2.5 flex-1 min-w-0">
              <!-- Icon with matching style -->
              <div class="w-8 h-8 rounded-lg bg-white/[0.05] border border-white/[0.08] flex items-center justify-center flex-shrink-0">
                <i class="fas fa-folder text-xs text-fuchsia-400/80"></i>
              </div>
              
              <!-- Project name and metadata -->
              <div class="flex-1 min-w-0">
                <h3 class="text-sm font-semibold text-white/90 truncate leading-tight">{{ project.name }}</h3>
                <div class="flex items-center text-xs text-white/40 mt-0.5">
                  <i class="far fa-clock text-[10px] mr-1.5"></i>
                  {{ formatDate(project.updated_at) }}
                </div>
              </div>
            </div>
            
            <!-- Delete button with refined styling -->
            <button
              @click.stop="confirmDelete"
              class="p-1.5 text-white/30 hover:text-red-400 transition-all duration-200 rounded-lg hover:bg-white/[0.05] border border-transparent hover:border-red-400/20 flex items-center justify-center w-7 h-7 flex-shrink-0"
              title="Delete project"
            >
              <i class="fas fa-trash text-[10px]"></i>
            </button>
          </div>
          
          <!-- Subtle separator matching dashboard style -->
          <div class="w-full h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent mb-3"></div>
          
          <!-- Project description -->
          <div class="mb-4 flex-1">
            <p v-if="project.description" class="text-white/50 text-xs line-clamp-2 leading-relaxed">
              {{ project.description }}
            </p>
            <p v-else class="text-white/30 text-xs italic">No description provided</p>
          </div>
          
          <!-- Open button matching dashboard button style -->
          <router-link
            :to="{ name: 'builder-workspace', params: { projectId: project.id.toString() }}"
            class="w-full inline-flex items-center justify-center gap-2 px-4 py-2 bg-white/[0.05] border border-white/[0.1] hover:bg-white/[0.08] hover:border-white/[0.15] rounded-lg text-white/70 hover:text-white text-xs font-medium transition-all duration-300 group/btn"
            title="Open project workspace"
          >
            <i class="fas fa-folder-open text-[10px] text-fuchsia-400/80"></i>
            <span>Open Project</span>
            <i class="fas fa-arrow-right text-[10px] transform group-hover/btn:translate-x-1 transition-transform duration-300"></i>
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
