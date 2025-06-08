<template>
  <div class="group relative transform transition-all duration-300">
    <!-- Card Container with removed hover effects -->  
    <!-- New Project Card -->
    <div v-if="isNew" class="relative">
      
      <!-- Card content with sleeker styling - matching project library container -->
      <div class="relative bg-dark-900/80 backdrop-blur-lg rounded-2xl overflow-hidden h-full border border-dark-800/60 shadow-lg shadow-dark-900/20 transition-all duration-300">
        <!-- Card header with gradient -->
        <div class="h-2 w-full bg-gradient-to-r from-indigo-500 to-violet-500"></div>
        
        <!-- Subtle glowing orb effect -->
        <div class="absolute -bottom-20 -right-20 w-40 h-40 rounded-full opacity-5 blur-3xl transition-opacity duration-500 group-hover:opacity-10 bg-indigo-500"></div>
        
        <div class="p-6 relative z-10">
          <!-- Enhanced New Project Card Layout -->
          <div class="flex flex-col space-y-6">
            <!-- Enhanced header with badge -->
            <div class="flex items-center justify-between">
              <div class="inline-block px-4 py-1.5 bg-indigo-500/10 rounded-full">
                <span class="text-indigo-400 font-semibold text-sm tracking-wider">NEW PROJECT</span>
              </div>
              
              <!-- Icon with animation -->
              <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/20 to-violet-500/20 flex items-center justify-center hover:scale-110 transition-all duration-300 border border-indigo-500/20 shadow-lg shadow-indigo-500/5">
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
                class="relative z-10 w-full px-5 py-3 bg-dark-900/90 border border-dark-600 focus:border-transparent rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-200"
                :disabled="isLoading"
              >
            </div>
            
            <!-- Project Description Input -->
            <div class="relative group/input w-full">
              <label class="block text-sm font-medium text-gray-300 mb-2 ml-1">Project Description <span class="text-gray-500">(optional)</span></label>
              <div class="absolute inset-0 mt-7 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-lg blur-[2px] opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
              <textarea
                :value="description"
                @input="(e) => $emit('update:description', (e.target as HTMLTextAreaElement).value)"
                placeholder="Brief description of your project..."
                class="relative z-10 w-full px-5 py-3 bg-dark-900/90 border border-dark-600 focus:border-transparent rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-200 resize-none"
                :disabled="isLoading"
                rows="3"
              ></textarea>
            </div>
            
            <!-- Create Button -->
            <div class="pt-2">
              <button
                @click="$emit('submit')"
                :disabled="!modelValue?.trim() || isLoading"
                class="w-full flex justify-center items-center px-6 py-3.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-semibold rounded-lg shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30 transform hover:scale-[1.02] transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none"
              >
                <span class="relative flex items-center">
                  <template v-if="isLoading">
                    <i class="fas fa-circle-notch fa-spin mr-2.5"></i>
                    Creating...
                  </template>
                  <template v-else>
                    <i class="fas fa-magic mr-2.5"></i>
                    Create Project
                  </template>
                </span>
              </button>
              
              <p class="text-xs text-gray-400 mt-4 text-center">
                <i class="fas fa-info-circle mr-1"></i>
                Your project will be created with our recommended starter template
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Existing Project Card -->
    <div v-else-if="project && !isNew">
      
      <router-link :to="{ name: 'builder-workspace', params: { projectId: project.id.toString() }}" class="block">
        <div 
          class="relative bg-dark-900/80 backdrop-blur-lg rounded-2xl overflow-hidden border border-dark-800/60 shadow-lg shadow-dark-900/20 transition-all duration-300 hover:translate-y-[-2px]"
          >
          <!-- Card header with gradient - made slightly taller for consistency -->
          <div class="h-2 w-full bg-gradient-to-r from-indigo-500 to-violet-500"></div>

          <!-- Subtle glowing orb effect -->
          <div class="absolute -top-20 -right-20 w-40 h-40 rounded-full opacity-5 blur-3xl transition-opacity duration-500 group-hover:opacity-10 bg-violet-500"></div>
      
          <div class="relative z-10 p-6">
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
                class="relative z-10 w-full px-5 py-3 bg-dark-900/90 border border-dark-600 focus:border-transparent rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-200"
                :disabled="isLoading"
              >
            </div>
            
            <!-- Project Description Input -->
            <div class="relative group/input w-full">
              <label class="block text-sm font-medium text-gray-300 mb-2 ml-1">Project Description <span class="text-gray-500">(optional)</span></label>
              <div class="absolute inset-0 mt-7 bg-gradient-to-r from-indigo-500/10 to-violet-500/10 rounded-lg blur-[2px] opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
              <textarea
                :value="description"
                @input="(e) => $emit('update:description', (e.target as HTMLTextAreaElement).value)"
                placeholder="Brief description of your project..."
                class="relative z-10 w-full px-5 py-3 bg-dark-900/90 border border-dark-600 focus:border-transparent rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all duration-200 min-h-[80px] resize-y"
                :disabled="isLoading"
                rows="3"
              ></textarea>
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
                <!-- Modernized Project Card Layout with enhanced design -->
              <div class="flex flex-col space-y-4">
                <!-- Modern project header with subtle badges -->
                <div class="flex items-center mb-2">
                  <div class="flex items-center gap-3 w-full">
                    <!-- Modern icon with subtle effect -->
                    <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500/15 to-violet-500/15 flex items-center justify-center transition-all duration-300 border border-indigo-500/10 shadow-md">
                      <i class="fas fa-cube text-indigo-300 text-base"></i>
                    </div>
                    
                    <!-- Project name with improved typography -->
                    <h3 class="text-lg font-semibold text-white truncate">{{ project.name }}</h3>
                  </div>
                  
                  <!-- Project status indicator removed -->
                </div>
                
                <!-- Last modified date with improved design -->
                <div class="flex items-center text-xs text-gray-400">
                  <i class="fas fa-history text-xs opacity-70 mr-1.5"></i>
                  Updated {{ formatDate(project.updated_at) }}
                </div>
            
                <!-- Project metadata with modern design -->
                <div class="my-3 w-full">
                  <!-- Modern separator -->
                  <div class="w-full h-px bg-dark-700/50 my-3"></div>
                  
                  <!-- Project description with improved visibility and full width -->
                  <p v-if="project.description" class="text-gray-300 text-sm line-clamp-2 w-full">
                    {{ project.description }}
                  </p>
                  <p v-else class="text-gray-500 text-sm italic w-full">No description provided</p>
                </div>

                <!-- Modern action buttons with improved layout -->
                <div class="flex items-center gap-2 mt-2 justify-between">
                  <!-- Professional Open project button -->
                  <router-link
                    :to="{ name: 'builder-workspace', params: { projectId: project.id.toString() }}"
                    class="py-2 px-4 text-white text-xs font-medium transition-all duration-200 rounded-md bg-indigo-600 hover:bg-indigo-500 shadow-sm text-center flex items-center justify-center flex-1"
                    title="Open project workspace"
                  >
                    <i class="fas fa-code mr-1.5"></i>
                    Open Project
                  </router-link>
                  
                  <!-- Sleek Delete button with better styling -->
                  <button
                    @click.stop="confirmDelete"
                    class="p-2 text-gray-400 hover:text-red-400 transition-all duration-200 rounded-md hover:bg-dark-800 border border-dark-700 flex items-center justify-center h-9 w-9"
                    title="Delete this project"
                  >
                    <i class="fas fa-trash-alt text-xs"></i>
                  </button>
                </div>
              </div>
            </template>
          </div>
        </div>
      </router-link>
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
