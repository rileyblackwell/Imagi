<template>
  <div class="group relative transform transition-all duration-300">
    <!-- New Project Card -->
    <div v-if="isNew" class="relative">
      <!-- Modern glassmorphism container matching dashboard style -->
      <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden h-full flex flex-col">
        <!-- Sleek gradient header -->
        <div class="h-1 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-80"></div>
        
        <!-- Subtle background effects -->
        <div class="absolute -top-32 -right-32 w-64 h-64 bg-gradient-to-br from-indigo-400/4 to-violet-400/4 rounded-full blur-3xl opacity-50"></div>
        
        <!-- Content with reduced padding for slender look -->
        <div class="flex-1 p-5">
          <!-- Sleek Header Section -->
          <div class="relative z-10 mb-5">
            <!-- Modern pill badge -->
            <div class="inline-flex items-center px-3 py-1 bg-gradient-to-r from-indigo-500/15 to-violet-500/15 border border-indigo-400/20 rounded-full mb-3 backdrop-blur-sm">
              <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full mr-2 animate-pulse"></div>
              <span class="text-indigo-300 font-medium text-xs tracking-wide uppercase">New Project</span>
            </div>
            
            <!-- Elegant title section -->
            <div class="relative mb-4 text-center">
              <h3 class="text-lg font-semibold text-white leading-tight">Create Project</h3>
              <p class="text-gray-400 text-xs mt-1 leading-relaxed">Build with AI assistance</p>
            </div>
          </div>
          
          <!-- Sleek Create Form -->
          <div class="relative z-10 space-y-3">
            <!-- Modern Project Name Input -->
            <div class="relative group/input w-full">
              <div class="absolute inset-0 bg-gradient-to-r from-violet-500/12 to-indigo-500/12 rounded-xl blur-sm opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
              
              <label class="block text-xs font-medium text-gray-400 mb-1.5 ml-0.5 uppercase tracking-wider relative z-10">Project Name</label>
              <input
                :value="modelValue"
                @input="(e) => $emit('update:modelValue', (e.target as HTMLInputElement).value)"
                type="text"
                placeholder="Enter project name..."
                class="relative z-10 w-full px-4 py-2.5 bg-white/5 border border-white/10 focus:border-violet-400/50 hover:border-white/15 rounded-xl text-white placeholder-gray-400 transition-all duration-300 backdrop-blur-sm hover:bg-white/8 focus:bg-white/8 focus:shadow-lg focus:shadow-violet-500/20 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                style="outline: none !important; box-shadow: none !important;"
                :disabled="isLoading"
              >
            </div>
            
            <!-- Modern Project Description Input -->
            <div class="relative group/input w-full">
              <div class="absolute inset-0 bg-gradient-to-r from-violet-500/12 to-indigo-500/12 rounded-xl blur-sm opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
              
              <label class="block text-xs font-medium text-gray-400 mb-1.5 ml-0.5 uppercase tracking-wider relative z-10">Description <span class="text-gray-500 normal-case">(optional)</span></label>
              <textarea
                :value="description"
                @input="(e) => $emit('update:description', (e.target as HTMLTextAreaElement).value)"
                placeholder="Brief description..."
                class="relative z-10 w-full px-4 py-2.5 bg-white/5 border border-white/10 focus:border-violet-400/50 hover:border-white/15 rounded-xl text-white placeholder-gray-400 transition-all duration-300 resize-none backdrop-blur-sm hover:bg-white/8 focus:bg-white/8 focus:shadow-lg focus:shadow-violet-500/20 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                style="outline: none !important; box-shadow: none !important;"
                :disabled="isLoading"
                rows="2"
              ></textarea>
            </div>
            
            <!-- Sleek Create Button -->
            <div class="pt-1">
              <button
                @click="$emit('submit')"
                :disabled="!modelValue?.trim() || isLoading"
                class="w-full px-4 py-2.5 bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 text-white font-medium rounded-xl shadow-lg shadow-indigo-500/25 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                <span class="relative flex items-center justify-center">
                  <template v-if="isLoading">
                    <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2"></div>
                    Creating...
                  </template>
                  <template v-else>
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                    </svg>
                    Create Project
                  </template>
                </span>
              </button>
              
              <p class="text-xs text-gray-500 mt-2 text-center leading-relaxed">
                <svg class="w-3 h-3 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                </svg>
                Created with starter template
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Existing Project Card -->
    <div v-else-if="project && !isNew" class="relative group">
      <!-- Modern glassmorphism container matching dashboard style -->
      <div class="relative rounded-2xl border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-2xl shadow-black/25 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40 transform hover:-translate-y-1">
        <!-- Sleek gradient header -->
        <div class="h-1 w-full bg-gradient-to-r from-violet-400 via-indigo-400 to-violet-400 opacity-80"></div>
        
        <!-- Subtle background effects -->
        <div class="absolute -top-32 -left-32 w-64 h-64 bg-gradient-to-br from-violet-400/4 to-indigo-400/4 rounded-full blur-3xl opacity-50 group-hover:opacity-60 transition-opacity duration-500"></div>
        
        <!-- Content with reduced padding for slender look -->
        <div class="relative z-10 p-5">
          <!-- Modern project header -->
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center gap-3 flex-1 min-w-0">
              <!-- Modern icon with subtle gradient -->
              <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-400/20 to-indigo-400/20 flex items-center justify-center border border-violet-400/20 flex-shrink-0">
                <svg class="w-4 h-4 text-violet-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
                </svg>
              </div>
              
              <!-- Project name with improved typography -->
              <div class="flex-1 min-w-0">
                <h3 class="text-base font-semibold text-white truncate leading-tight">{{ project.name }}</h3>
                <div class="flex items-center text-xs text-gray-400 mt-1">
                  <svg class="w-3 h-3 mr-1.5 opacity-70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  {{ formatDate(project.updated_at) }}
                </div>
              </div>
            </div>
            
            <!-- Sleek Delete button -->
            <button
              @click.stop="confirmDelete"
              class="p-2 text-gray-400 hover:text-red-400 transition-all duration-200 rounded-lg hover:bg-white/5 border border-white/10 hover:border-red-400/30 flex items-center justify-center w-8 h-8 flex-shrink-0"
              title="Delete project"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
          
          <!-- Modern separator -->
          <div class="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-4"></div>
          
          <!-- Project description -->
          <div class="mb-4">
            <p v-if="project.description" class="text-gray-300 text-sm line-clamp-2 leading-relaxed">
              {{ project.description }}
            </p>
            <p v-else class="text-gray-500 text-sm italic">No description provided</p>
          </div>
          
          <!-- Sleek Open button -->
          <router-link
            :to="{ name: 'builder-workspace', params: { projectId: project.id.toString() }}"
            class="w-full inline-flex items-center justify-center px-4 py-2.5 bg-white/5 hover:bg-white/8 border border-white/10 hover:border-violet-400/30 text-white rounded-xl transition-all duration-300 text-sm font-medium group/button"
            title="Open project workspace"
          >
            <svg class="w-4 h-4 mr-2 group-hover/button:text-violet-400 transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
            </svg>
            Open Project
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
