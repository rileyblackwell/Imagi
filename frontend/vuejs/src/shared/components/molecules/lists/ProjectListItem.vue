<template>
  <router-link
    :to="{ name: 'builder-project-detail', params: { id: project.id } }"
    class="block p-4 rounded-lg hover:bg-dark-700 transition-colors duration-200"
  >
    <div class="flex items-center">
      <div class="flex-grow">
        <h4 class="text-white font-medium mb-1">{{ project.name }}</h4>
        <p class="text-gray-400 text-sm">{{ project.description }}</p>
      </div>
      <div class="flex items-center">
        <span :class="[statusClass, 'px-2 py-1 rounded text-xs mr-4']">
          {{ project.status }}
        </span>
        <i class="fas fa-chevron-right text-gray-500"></i>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Project, StatusClasses } from '@/apps/builder/types/index'

const props = defineProps<{
  project: Project
}>()

const statusClasses: StatusClasses = {
  'active': 'bg-green-900/50 text-green-400',
  'draft': 'bg-gray-900/50 text-gray-400',
  'archived': 'bg-red-900/50 text-red-400'
}

const statusClass = computed(() => statusClasses[props.project.status])
</script>
