<template>
  <div class="group relative transform transition-all duration-300 hover:-translate-y-2">
    <!-- Card content with styling matching home components -->
    <div class="relative h-full rounded-2xl border border-gray-800/60 bg-dark-900/40 backdrop-blur-sm transition-all duration-500 hover:shadow-[0_0_25px_-5px_rgba(99,102,241,0.5)] overflow-hidden">
      <!-- Background gradient -->
      <div class="absolute inset-0 bg-gradient-to-br opacity-10 -z-10 transition-opacity duration-300 group-hover:opacity-20 from-indigo-900 to-violet-900"></div>
      
      <!-- Glowing orb effect -->
      <div class="absolute -bottom-20 -right-20 w-40 h-40 rounded-full opacity-10 blur-3xl transition-opacity duration-500 group-hover:opacity-20 bg-indigo-500"></div>
      
      <div class="relative z-10 p-8">
        <template v-if="isNew">
          <!-- Enhanced New Project Card Layout -->
          <div class="flex flex-col space-y-6">
            <!-- Enhanced header with badge -->
            <div class="flex items-center justify-between">
              <div class="inline-block px-4 py-1.5 bg-indigo-500/10 rounded-full">
                <span class="text-indigo-400 font-semibold text-sm tracking-wider">NEW PROJECT</span>
              </div>
              
              <!-- Icon with animation -->
              <div class="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center hover:scale-110 transition-all duration-300 border border-indigo-500/20 shadow-md shadow-indigo-500/5">
                <i class="fas fa-plus text-indigo-400 text-lg"></i>
              </div>
            </div>
            
            <!-- Enhanced title section -->
            <div class="text-center">
              <h3 class="text-2xl font-bold text-white mb-2">Create New Project</h3>
              <p class="text-gray-300 text-sm mb-4">Build a new web application with AI assistance</p>
              
              <!-- Decorative element matching home sections -->
              <div class="w-16 h-1 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full mx-auto"></div>
            </div>
            
            <!-- Enhanced Project Name Input with animated focus state -->
            <div class="relative group/input w-full">
              <label class="block text-sm font-medium text-gray-300 mb-2 ml-1">Project Name</label>
              <div class="absolute inset-0 mt-7 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-lg blur-[2px] opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
              <input
                :value="modelValue"
                @input="(e) => $emit('update:modelValue', (e.target as HTMLInputElement).value)"
                type="text"
                placeholder="Enter project name..."
                class="relative z-10 w-full px-5 py-3 bg-dark-900/90 border border-dark-600 focus:border-indigo-500/50 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-indigo-500/30 transition-all duration-200"
                :disabled="isLoading"
              >
            </div>
            
            <!-- Create Button -->
            <div class="pt-2">
              <button
                @click="$emit('submit')"
                :disabled="!modelValue?.trim() || isLoading"
                class="w-full px-5 py-4 bg-indigo-600 hover:bg-indigo-500 border border-indigo-500/40 hover:border-indigo-400/50 disabled:bg-dark-700 disabled:border-dark-600 disabled:text-gray-500 text-white rounded-lg flex items-center justify-center gap-2.5 shadow-lg hover:shadow-indigo-500/20 transition-all duration-300 transform hover:-translate-y-1 font-medium"
              >
                <i class="fas fa-spinner fa-spin" v-if="isLoading"></i>
                <span v-else class="flex items-center">
                  <i class="fas fa-rocket mr-2"></i>
                  Start Building
                </span>
              </button>
              
              <!-- Helper text -->
              <p class="text-xs text-gray-400 mt-4 text-center">
                <i class="fas fa-info-circle mr-1"></i>
                Your project will be created with our recommended starter template
              </p>
            </div>
          </div>
        </template>
        
        <template v-else-if="project">
          <!-- Existing Project Card Layout -->
          <div class="flex items-center justify-between">
            <!-- Project info -->
            <div class="flex-1">
              <div class="flex items-center gap-4 mb-2">
                <!-- Icon container with animation -->
                <div class="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-indigo-500/20 shadow-md shadow-indigo-500/5">
                  <i class="fas fa-cube text-indigo-400 text-lg"></i>
                </div>
                <div>
                  <h3 class="text-xl font-semibold text-white truncate group-hover:text-indigo-400/90 transition-colors">{{ project.name }}</h3>
                  <div class="flex items-center gap-5 text-sm text-gray-400 mt-1">
                    <span class="flex items-center gap-2 group-hover:text-gray-300 transition-colors">
                      <i class="fas fa-clock text-xs opacity-70"></i>
                      {{ formatDate(project.updated_at) }}
                    </span>
                    <span class="flex items-center gap-2 group-hover:text-gray-300 transition-colors">
                      <i class="fas fa-code-branch text-xs opacity-70"></i>
                      v{{ project.version || '1.0' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center gap-3">
              <!-- Open project button with enhanced hover effect -->
              <router-link
                :to="{ name: 'builder-workspace', params: { projectId: project.id.toString() }}"
                class="p-3 text-indigo-400 hover:text-white transition-all duration-200 rounded-lg bg-indigo-500/10 hover:bg-indigo-500 hover:scale-105 shadow-md shadow-indigo-500/5 hover:shadow-lg hover:shadow-indigo-500/20"
                title="Open project"
              >
                <i class="fas fa-arrow-right"></i>
              </router-link>
              
              <!-- Delete button with enhanced hover effect -->
              <button
                @click.stop="confirmDelete"
                class="p-3 text-red-400 hover:text-white transition-all duration-200 rounded-lg bg-red-500/10 hover:bg-red-500 hover:scale-105 shadow-md shadow-red-500/5 hover:shadow-lg hover:shadow-red-500/20"
                title="Delete project"
              >
                <i class="fas fa-trash"></i>
              </button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Project {
  id: string | number;
  name: string;
  updated_at: string;
  version?: string;
}

const props = defineProps<{
  project?: Project;
  modelValue?: string;
  isLoading?: boolean;
  isNew?: boolean;
}>();

const emit = defineEmits<{
  (e: 'delete', project: Project): void;
  (e: 'update:modelValue', value: string): void;
  (e: 'submit'): void;
}>();

function formatDate(date: string) {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date));
}

function confirmDelete() {
  if (props.project) {
    emit('delete', props.project);
  }
}
</script>
