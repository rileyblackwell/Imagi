<template>
  <div class="crisp-card relative rounded-2xl bg-white/85 dark:bg-white/[0.045] backdrop-blur-sm border border-orange-200/70 dark:border-orange-300/[0.14] transition-colors duration-300 overflow-hidden p-8">
    <!-- Header -->
    <div class="relative mb-8">
      <div class="flex items-center justify-between mb-4">
        <p class="inline-flex items-center px-3.5 py-1.5 rounded-full border border-orange-200/70 dark:border-orange-400/25 bg-orange-50/80 dark:bg-orange-400/10 text-xs font-semibold text-orange-700 dark:text-orange-300 uppercase tracking-[0.18em] transition-colors duration-300">YOUR PROJECTS</p>
      </div>

      <!-- Title section -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-2xl font-semibold tracking-tight text-blue-950 dark:text-white transition-colors duration-300">Project Library</h2>

          <!-- Project count -->
          <div class="flex items-center gap-3 px-4 py-2 rounded-xl bg-white/85 dark:bg-white/[0.04] border border-blue-200/70 dark:border-white/[0.14] transition-colors duration-300">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-1 ring-blue-900/[0.08] dark:ring-blue-300/[0.18] flex items-center justify-center">
              <i class="fas fa-folder-open text-blue-600 dark:text-blue-300 text-lg"></i>
            </div>
            <div>
              <p class="text-xs font-medium uppercase tracking-[0.14em] text-blue-950/70 dark:text-blue-100/55 transition-colors duration-300">Total</p>
              <p class="text-xl font-semibold tabular-nums text-blue-950 dark:text-white transition-colors duration-300">{{ projects.length || 0 }}</p>
            </div>
          </div>
        </div>

        <p class="text-blue-950/65 dark:text-blue-100/65 transition-colors duration-300">Continue working on your existing web applications</p>

        <!-- Hairline accent divider -->
        <div class="mt-4 h-px w-16 bg-gradient-to-r from-transparent via-orange-300/70 dark:via-orange-300/30 to-transparent" aria-hidden="true"></div>
      </div>
    </div>

    <template v-if="!isLoading && !error && projects?.length">
      <!-- Recent Projects -->
      <div v-if="recentProjects.length" class="mb-10">
        <div class="flex items-center gap-2.5 mb-5">
          <i class="fas fa-clock text-blue-600 dark:text-blue-300 text-sm"></i>
          <h3 class="text-xs font-semibold text-blue-950/70 dark:text-blue-100/55 uppercase tracking-[0.18em] transition-colors duration-300">Recently Opened</h3>
          <span class="flex-1 h-px bg-blue-950/[0.08] dark:bg-white/[0.14]" aria-hidden="true"></span>
        </div>

        <div class="space-y-4">
          <ProjectCard
            v-for="(project, index) in recentProjects"
            :key="project.id"
            :project="project"
            :accent="index % 2 === 1 ? 'orange' : 'blue'"
            @delete="$emit('delete', project.id, project.name)"
          />
        </div>
      </div>

      <!-- All Projects Section -->
      <div class="space-y-5">
        <div class="flex items-center gap-2.5 mb-4">
          <i class="fas fa-folder text-orange-600 dark:text-orange-300 text-sm"></i>
          <h3 class="text-xs font-semibold text-blue-950/70 dark:text-blue-100/55 uppercase tracking-[0.18em] transition-colors duration-300">All Projects</h3>
          <span class="flex-1 h-px bg-blue-950/[0.08] dark:bg-white/[0.14]" aria-hidden="true"></span>
        </div>

        <!-- Projects List -->
        <div class="space-y-4 max-h-[350px] overflow-y-auto pr-2 pl-0.5 pt-1 pb-2 custom-scrollbar">
          <template v-if="props.projects.length > 3">
            <ProjectCard
              v-for="(project, index) in otherProjects"
              :key="project.id"
              :project="project"
              :accent="index % 2 === 1 ? 'orange' : 'blue'"
              @delete="$emit('delete', project.id, project.name)"
            />
          </template>
          <div v-else-if="recentProjects.length === 0" class="flex flex-col items-center justify-center py-12">
            <i class="fas fa-folder-open text-3xl text-blue-950/30 dark:text-blue-100/30 mb-3"></i>
            <p class="text-blue-950/65 dark:text-blue-100/65 transition-colors duration-300">No additional projects</p>
          </div>
        </div>
      </div>
    </template>

    <!-- Loading, Error, Empty States -->
    <div v-else>
      <div v-if="isLoading" class="flex flex-col items-center justify-center py-16">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#dbeeff] to-[#9ecdf3] dark:from-blue-400/[0.18] dark:to-blue-500/[0.22] ring-1 ring-blue-900/[0.08] dark:ring-blue-300/[0.18] flex items-center justify-center mb-5">
          <div class="w-7 h-7 border-2 border-blue-200 dark:border-blue-300/30 border-t-blue-600 dark:border-t-blue-300 rounded-full animate-spin"></div>
        </div>
        <p class="text-blue-950/65 dark:text-blue-100/65 text-lg transition-colors duration-300">Loading your projects...</p>
      </div>

      <div v-else-if="error" class="flex flex-col items-center justify-center py-16">
        <div class="w-16 h-16 rounded-2xl bg-red-50 dark:bg-red-500/10 ring-1 ring-red-900/[0.08] dark:ring-red-400/30 flex items-center justify-center mb-5">
          <i class="fas fa-exclamation-circle text-2xl text-red-500 dark:text-red-300"></i>
        </div>
        <p class="text-blue-950/65 dark:text-blue-100/65 mb-6 text-center max-w-md transition-colors duration-300">{{ error }}</p>
        <button
          type="button"
          @click="$emit('retry')"
          class="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-full font-medium text-sm bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white transition-colors duration-200 shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
        >
          <i class="fas fa-sync-alt"></i>
          <span>Try Again</span>
        </button>
      </div>

      <div v-else class="flex flex-col items-center justify-center py-16">
        <div class="w-16 h-16 rounded-2xl bg-orange-100 dark:bg-orange-400/[0.14] ring-1 ring-orange-900/[0.08] dark:ring-orange-300/[0.18] flex items-center justify-center mb-5">
          <i class="fas fa-folder-open text-2xl text-orange-600 dark:text-orange-300"></i>
        </div>
        <h3 class="text-xl font-semibold tracking-tight text-blue-950 dark:text-white mb-2 transition-colors duration-300">No projects yet</h3>
        <p class="text-blue-950/65 dark:text-blue-100/65 text-center max-w-md mb-6 transition-colors duration-300">Create your first project to start building with Imagi</p>

        <!-- Directional hint -->
        <div class="flex items-center text-blue-700 dark:text-blue-300 transition-colors duration-300">
          <i class="fas fa-long-arrow-alt-left text-lg mr-2"></i>
          <span>Get started with a new project</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import ProjectCard from '../../molecules/cards/ProjectCard.vue'
import type { Project } from '@/apps/imagi/build/types/components'
import type { ProjectListProps } from '@/apps/imagi/build/types/components'

const props = defineProps<ProjectListProps>()

// Get 3 most recently updated projects for display
const recentProjects = computed(() => {
  if (!props.projects?.length) return []

  return [...props.projects]
    .sort((a, b) => {
      // Handle cases where updated_at might be undefined
      if (!a.updated_at) return 1;  // If a's date is missing, b comes first
      if (!b.updated_at) return -1; // If b's date is missing, a comes first

      const dateA = new Date(a.updated_at).getTime()
      const dateB = new Date(b.updated_at).getTime()
      return dateB - dateA
    })
    .slice(0, 3)
})

// Get all projects except the recent ones
const otherProjects = computed(() => {
  if (!props.projects?.length) return []

  const recentIds = new Set(recentProjects.value.map(p => p.id))

  return [...props.projects]
    .filter(project => !recentIds.has(project.id))
    .sort((a, b) => {
      // Handle cases where updated_at might be undefined
      if (!a.updated_at) return 1;  // If a's date is missing, b comes first
      if (!b.updated_at) return -1; // If b's date is missing, a comes first

      const dateA = new Date(a.updated_at).getTime()
      const dateB = new Date(b.updated_at).getTime()
      return dateB - dateA
    })
})
</script>

<style scoped>
/* Crisp, sharply-defined panel matching Home/About - hairline edge + tight layered shadow */
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

/* Refined minimal scrollbar */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.12) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 8px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.2);
}

:global(.dark) .custom-scrollbar {
  scrollbar-color: rgba(255, 255, 255, 0.12) transparent;
}

:global(.dark) .custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
}

:global(.dark) .custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
