<template>
  <div class="group relative transform transition-all duration-300 hover:translate-y-[-3px]">
    <!-- Enhanced hover glow effect -->
    <div class="absolute -inset-[1px] rounded-xl bg-gradient-to-r from-primary-500/30 via-violet-500/30 to-indigo-500/30 opacity-0 group-hover:opacity-100 blur-[2px] transition-all duration-300"></div>
    
    <!-- Card content with enhanced styling -->
    <div class="relative bg-dark-800/80 backdrop-blur-md rounded-xl p-7 border border-dark-700/80 group-hover:border-primary-500/30 transition-all duration-300 shadow-lg shadow-dark-950/30 group-hover:shadow-xl group-hover:shadow-primary-500/10">
      <div class="flex items-center justify-between">
        <!-- Project info -->
        <div class="flex-1">
          <div class="flex items-center gap-4" :class="{ 'mb-2': !isNew, 'mb-5': isNew }">
            <!-- Enhanced icon container with animation -->
            <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500/15 to-violet-500/15 flex items-center justify-center group-hover:scale-110 transition-all duration-300 border border-primary-500/20 shadow-md shadow-primary-500/5">
              <i :class="[isNew ? 'fas fa-plus' : 'fas fa-cube', 'text-primary-400 text-lg']"></i>
            </div>
            <template v-if="isNew">
              <h3 class="text-xl font-semibold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent">Create New Project</h3>
            </template>
            <template v-else-if="project">
              <h3 class="text-xl font-semibold text-white truncate group-hover:text-primary-400/90 transition-colors">{{ project.name }}</h3>
            </template>
          </div>
          
          <template v-if="isNew">
            <!-- Enhanced Project Name Input with animated focus state -->
            <div class="relative group/input w-full">
              <div class="absolute inset-0 bg-gradient-to-r from-primary-500/10 to-violet-500/10 rounded-lg blur-[2px] opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
              <input
                :value="modelValue"
                @input="(e) => $emit('update:modelValue', (e.target as HTMLInputElement).value)"
                type="text"
                placeholder="Enter project name..."
                class="relative z-10 w-full px-5 py-3 bg-dark-900/90 border border-dark-600 focus:border-primary-500/50 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500/30 transition-all duration-200"
                :disabled="isLoading"
              >
            </div>
          </template>
          <template v-else-if="project">
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
          </template>
        </div>

        <!-- Actions with enhanced styling -->
        <div class="flex items-center gap-3">
          <template v-if="isNew">
            <button
              @click="$emit('submit')"
              :disabled="!modelValue?.trim() || isLoading"
              class="px-5 py-3 bg-gradient-to-r from-primary-500 to-violet-500 hover:from-primary-600 hover:to-violet-600 disabled:from-dark-700 disabled:to-dark-700 disabled:text-gray-500 text-white rounded-lg flex items-center gap-2.5 shadow-lg shadow-primary-500/10 group-hover:shadow-xl group-hover:shadow-primary-500/20 transition-all duration-300 font-medium"
            >
              <i class="fas fa-spinner fa-spin" v-if="isLoading"></i>
              <span>Create Project</span>
            </button>
          </template>
          <template v-else-if="project">
            <!-- Open project button with enhanced hover effect -->
            <router-link
              :to="{ name: 'builder-workspace', params: { projectId: project.id.toString() }}"
              class="p-3 text-primary-400 hover:text-white transition-all duration-200 rounded-lg bg-primary-500/10 hover:bg-primary-500 hover:scale-105 shadow-md shadow-primary-500/5 hover:shadow-lg hover:shadow-primary-500/20"
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
          </template>
        </div>
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
