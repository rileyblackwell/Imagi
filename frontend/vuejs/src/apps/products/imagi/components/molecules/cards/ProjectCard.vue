<template>
  <router-link
    v-if="project"
    :to="{ name: 'builder-workspace', params: { projectName: toSlug(project.name) }}"
    class="crisp-card group relative block px-5 py-3 rounded-2xl bg-white dark:bg-white/[0.05] border border-blue-200/70 dark:border-blue-300/[0.16] hover:border-blue-300 dark:hover:border-blue-300/30 transition-colors duration-300"
    :title="`Open ${project.name}`"
  >
    <!-- Delete button -->
    <button
      @click.stop.prevent="confirmDelete"
      class="absolute top-3 right-3 w-8 h-8 rounded-lg flex items-center justify-center text-red-600 dark:text-red-300 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-400/30 hover:bg-red-100 dark:hover:bg-red-500/20 transition-all duration-200 z-10"
      aria-label="Delete project"
    >
      <i class="fas fa-trash-alt text-xs"></i>
    </button>

    <!-- Name + description + CTA -->
    <div class="min-w-0 pr-12">
      <h3 class="text-base font-semibold text-blue-950 dark:text-white truncate leading-tight text-center transition-colors duration-300">
        {{ project.name }}
      </h3>
      <p v-if="project.description" class="text-xs text-blue-950/70 dark:text-blue-100/70 truncate leading-snug mt-1.5 text-center transition-colors duration-300">
        {{ project.description }}
      </p>
      <div class="flex items-center justify-center gap-1.5 text-xs font-medium text-blue-700 dark:text-blue-300 group-hover:text-blue-800 dark:group-hover:text-blue-200 transition-colors duration-200 mt-2.5 pt-2.5 border-t border-blue-200/60 dark:border-white/[0.1]">
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

<style scoped>
/* Crisp, sharply-defined card matching Home/About - hairline edge + tight layered shadow */
.crisp-card {
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.03),
    0 1px 2px rgba(15, 23, 42, 0.06),
    0 4px 10px -2px rgba(15, 23, 42, 0.07),
    0 12px 28px -10px rgba(15, 23, 42, 0.10);
}

:global(.dark) .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}
</style>
