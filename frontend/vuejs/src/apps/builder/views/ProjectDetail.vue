<template>
  <div class="min-h-screen bg-dark-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="project" class="space-y-8">
        <!-- Header -->
        <div class="flex justify-between items-start">
          <div>
            <h1 class="text-2xl font-bold text-white mb-2">{{ project.name }}</h1>
            <p class="text-gray-400">{{ project.description || 'No description' }}</p>
          </div>
          <div class="flex gap-4">
            <IconButton
              icon="fas fa-edit"
              variant="secondary"
              @click="editProject"
            >
              Edit
            </IconButton>
            <IconButton
              icon="fas fa-trash"
              variant="danger"
              @click="confirmDelete"
            >
              Delete
            </IconButton>
          </div>
        </div>

        <!-- Project Details -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <!-- Project Info -->
          <div class="bg-dark-800 rounded-lg p-6">
            <h2 class="text-lg font-semibold text-white mb-4">Project Information</h2>
            <dl class="space-y-4">
              <div>
                <dt class="text-gray-400">Created</dt>
                <dd class="text-white">{{ formatDateWithStyle(project.created_at, 'long') }}</dd>
              </div>
              <div>
                <dt class="text-gray-400">Last Updated</dt>
                <dd class="text-white">{{ formatDateWithStyle(project.updated_at, 'long') }}</dd>
              </div>
              <div>
                <dt class="text-gray-400">Status</dt>
                <dd class="text-white">{{ project.status || 'Active' }}</dd>
              </div>
            </dl>
          </div>

          <!-- Project Stats -->
          <div class="bg-dark-800 rounded-lg p-6">
            <h2 class="text-lg font-semibold text-white mb-4">Project Statistics</h2>
            <!-- Add project stats here -->
          </div>
        </div>
      </div>

      <EmptyState
        v-else
        icon="fas fa-folder-open"
        title="Project not found"
        description="The requested project could not be found"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projectStore'
import { formatDateWithStyle } from '@/shared/utils/date'
import { useNotification } from '@/shared/composables/useNotification'
import { IconButton } from '@/shared/components/atoms'
import { EmptyState } from '@/shared/components/molecules'
import type { Project } from '@/shared/types/project' 

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()
const { showNotification } = useNotification()

const project = computed<Project | undefined>(() => {
  return projectStore.getProjectById(route.params.id as string)
})

function editProject() {
  // TODO: Implement edit functionality
  showNotification({
    type: 'info',
    message: 'Edit functionality coming soon'
  })
}

async function confirmDelete() {
  if (!project.value?.id) return
  
  // TODO: Add confirmation dialog
  try {
    await projectStore.deleteProject(String(project.value.id))
    showNotification({
      type: 'success',
      message: 'Project deleted successfully'
    })
    router.push({ name: 'builder-projects' })
  } catch (error) {
    showNotification({
      type: 'error',
      message: 'Failed to delete project'
    })
  }
}

onMounted(async () => {
  if (!projectStore.initialized) {
    await projectStore.fetchProjects()
  }
})
</script>
