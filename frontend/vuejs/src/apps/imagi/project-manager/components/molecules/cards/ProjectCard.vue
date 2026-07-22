<template>
  <router-link
    v-if="project"
    :to="{ name: 'project-hub', params: { projectName: toSlug(project.name) }}"
    class="crisp-card group relative block px-5 py-4 rounded-2xl bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm border transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
    :class="isOrange
      ? 'border-orange-200/70 dark:border-orange-300/[0.14] hover:border-orange-300 dark:hover:border-orange-300/30'
      : 'border-blue-200/70 dark:border-blue-300/[0.14] hover:border-blue-300 dark:hover:border-blue-300/30'"
    :title="`Open ${project.name}`"
  >
    <div class="flex items-center gap-3 sm:gap-4">
      <!-- Name + description -->
      <div class="flex-1 min-w-0">
        <h3 class="text-base font-semibold tracking-tight text-blue-950 dark:text-white truncate leading-tight transition-colors duration-300">
          {{ project.name }}
        </h3>
        <p v-if="project.description" class="text-xs text-blue-950/65 dark:text-blue-100/65 truncate leading-snug mt-1 transition-colors duration-300">
          {{ project.description }}
        </p>
      </div>

      <!-- Delete + open arrow -->
      <div class="flex items-center gap-1.5 flex-shrink-0">
        <button
          @click.stop.prevent="confirmDelete"
          class="w-8 h-8 rounded-lg flex items-center justify-center text-blue-950/40 dark:text-blue-100/40 hover:text-red-600 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-500/10 transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
          aria-label="Delete project"
        >
          <i class="fas fa-trash-alt text-xs"></i>
        </button>
        <svg
          class="hidden sm:block w-5 h-5 transition-transform duration-300 group-hover:translate-x-1"
          :class="isOrange ? 'text-orange-500 dark:text-orange-300' : 'text-blue-500 dark:text-blue-300'"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
        </svg>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Project } from '@/apps/imagi/build/types/components'
import { toSlug } from '@/apps/imagi/build/utils/slug'

const props = defineProps<{
  project?: Project;
  accent?: 'blue' | 'orange';
}>();

const emit = defineEmits<{
  (e: 'delete', project: Project): void;
}>();

const isOrange = computed(() => props.accent === 'orange')

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

/* Gentle lift on hover, matching the home value pills */
.crisp-card:hover {
  transform: translateY(-2px);
  box-shadow:
    0 0 0 1px rgba(15, 23, 42, 0.04),
    0 2px 4px rgba(15, 23, 42, 0.06),
    0 8px 18px -4px rgba(15, 23, 42, 0.09),
    0 20px 40px -12px rgba(15, 23, 42, 0.14);
}

:global(.dark) .crisp-card {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.04),
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 4px 10px -2px rgba(0, 0, 0, 0.45),
    0 12px 28px -10px rgba(0, 0, 0, 0.55);
}

:global(.dark) .crisp-card:hover {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.06),
    0 2px 4px rgba(0, 0, 0, 0.55),
    0 8px 18px -4px rgba(0, 0, 0, 0.5),
    0 20px 40px -12px rgba(0, 0, 0, 0.6);
}

@media (prefers-reduced-motion: reduce) {
  .crisp-card:hover {
    transform: none;
  }
}
</style>
