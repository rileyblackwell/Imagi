<template>
  <div class="group relative">
    <!-- Refined hover effect -->
    <div class="absolute -inset-[1px] rounded-xl bg-gradient-to-r from-primary-500/20 via-violet-500/20 to-indigo-500/20 opacity-0 group-hover:opacity-100 blur-[1px] transition-all duration-300"></div>
    
    <!-- Card content with enhanced styling -->
    <div class="relative bg-dark-800/70 backdrop-blur-sm rounded-xl p-6 border border-dark-700/80 group-hover:border-primary-500/20 transition-all duration-300 group-hover:shadow-lg group-hover:shadow-primary-500/5">
      <div class="flex items-center justify-between">
        <!-- Project info -->
        <div class="flex-1">
          <div class="flex items-center gap-3" :class="{ 'mb-2': !isNew, 'mb-4': isNew }">
            <!-- Enhanced icon container -->
            <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-primary-500/10 to-violet-500/10 flex items-center justify-center group-hover:scale-105 transition-all duration-300 border border-primary-500/10">
              <i :class="[isNew ? 'fas fa-plus' : 'fas fa-cube', 'text-primary-400']"></i>
            </div>
            <template v-if="isNew">
              <h3 class="text-lg font-semibold bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent">Create New Project</h3>
            </template>
            <template v-else-if="project">
              <h3 class="text-lg font-semibold text-white truncate group-hover:text-primary-400/90 transition-colors">{{ project.name }}</h3>
            </template>
          </div>
          
          <template v-if="isNew">
            <!-- Enhanced Project Name Input -->
            <div class="relative group/input w-full">
              <div class="absolute inset-0 bg-gradient-to-r from-primary-500/5 to-violet-500/5 rounded-lg blur-[1px] opacity-0 group-focus-within/input:opacity-100 transition-all duration-300 pointer-events-none"></div>
              <input
                :value="modelValue"
                @input="(e) => $emit('update:modelValue', (e.target as HTMLInputElement).value)"
                type="text"
                placeholder="Enter project name..."
                class="relative z-10 w-full px-4 py-2.5 bg-dark-900/80 border border-dark-600 focus:border-primary-500/50 rounded-lg text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
                :disabled="isLoading"
              >
            </div>
          </template>
          <template v-else-if="project">
            <div class="flex items-center gap-4 text-sm text-gray-400">
              <span class="flex items-center gap-2 group-hover:text-gray-300 transition-colors">
                <i class="fas fa-clock text-xs"></i>
                {{ formatDate(project.updated_at) }}
              </span>
              <span class="flex items-center gap-2 group-hover:text-gray-300 transition-colors">
                <i class="fas fa-code-branch text-xs"></i>
                v{{ project.version || '1.0' }}
              </span>
            </div>
          </template>
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-2">
          <template v-if="isNew">
            <button
              @click="$emit('submit')"
              :disabled="!modelValue?.trim() || isLoading"
              class="ml-4 px-4 py-2.5 bg-primary-500 hover:bg-primary-600 disabled:bg-dark-700 disabled:text-gray-500 text-white rounded-lg flex items-center gap-2 group-hover:shadow-lg group-hover:shadow-primary-500/10 transition-all duration-300"
            >
              <i class="fas fa-spinner fa-spin" v-if="isLoading"></i>
              <span>Create</span>
            </button>
          </template>
          <template v-else-if="project">
            <router-link
              :to="{ name: 'builder-workspace', params: { projectId: project.id.toString() }}"
              class="p-2.5 text-primary-400 hover:text-primary-300 transition-all duration-200 rounded-lg hover:bg-primary-500/10 hover:scale-105"
              title="Open project"
            >
              <i class="fas fa-arrow-right"></i>
            </router-link>
            <button
              @click.stop="confirmDelete"
              class="p-2.5 text-red-400 hover:text-red-300 opacity-0 group-hover:opacity-100 transition-all duration-200 rounded-lg hover:bg-red-500/10 hover:scale-105"
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
