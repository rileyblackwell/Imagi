<template>
  <router-link
    v-if="project"
    :to="{ name: 'builder-workspace', params: { projectName: toSlug(project.name) }}"
    class="group relative block px-5 py-3 rounded-2xl bg-white dark:bg-white border border-gray-200 dark:border-gray-300 shadow-md"
    :title="`Open ${project.name}`"
  >
    <!-- Delete button -->
    <button
      @click.stop.prevent="confirmDelete"
      class="absolute top-3 right-3 w-8 h-8 rounded-lg flex items-center justify-center text-red-600 bg-red-50 border border-red-200 shadow-sm hover:bg-red-100 hover:shadow-md transition-all duration-200 z-10"
      aria-label="Delete project"
    >
      <i class="fas fa-trash-alt text-xs"></i>
    </button>

    <!-- Name + description + CTA -->
    <div class="min-w-0 pr-12">
      <h3 class="text-base font-semibold text-gray-900 dark:text-black truncate leading-tight text-center">
        {{ project.name }}
      </h3>
      <p v-if="project.description" class="text-xs text-gray-600 dark:text-black truncate leading-snug mt-1.5 text-center">
        {{ project.description }}
      </p>
      <div class="flex items-center justify-center gap-1.5 text-xs font-medium text-gray-600 dark:text-gray-700 group-hover:text-black dark:group-hover:text-black transition-colors duration-200 mt-2.5 pt-2.5 border-t border-gray-200 dark:border-gray-200">
        <span>Open workspace</span>
        <i class="fas fa-arrow-right text-xs group-hover:translate-x-1 transition-transform duration-200"></i>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import type { Project } from '../../../types/components'
import { toSlug } from '../../../utils/slug'

const props = defineProps<{
  project?: Project;
}>();

const emit = defineEmits<{
  (e: 'delete', project: Project): void;
}>();

function confirmDelete() {
  if (props.project) {
    emit('delete', props.project);
  }
}
</script>
