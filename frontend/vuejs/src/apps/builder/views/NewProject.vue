<template>
  <div class="min-h-screen bg-dark-900">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-white">Create New Project</h1>
        <p class="mt-2 text-gray-400">
          Start building your next application with Imagi
        </p>
      </div>

      <!-- Project Form -->
      <div class="bg-dark-800 rounded-lg p-6">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Project Name -->
          <div>
            <label for="name" class="block text-sm font-medium text-gray-200">
              Project Name
            </label>
            <input
              id="name"
              v-model="formData.name"
              type="text"
              required
              placeholder="My Awesome Project"
              class="mt-1 block w-full rounded-md bg-dark-700 border-dark-600 text-white placeholder-gray-400 focus:border-primary-500 focus:ring-primary-500"
            />
          </div>

          <!-- Project Description -->
          <div>
            <label for="description" class="block text-sm font-medium text-gray-200">
              Description
            </label>
            <textarea
              id="description"
              v-model="formData.description"
              rows="3"
              placeholder="Describe your project..."
              class="mt-1 block w-full rounded-md bg-dark-700 border-dark-600 text-white placeholder-gray-400 focus:border-primary-500 focus:ring-primary-500"
            ></textarea>
          </div>

          <!-- Submit Button -->
          <div class="flex justify-end space-x-4">
            <IconButton
              type="button"
              variant="secondary"
              @click="handleCancel"
            >
              Cancel
            </IconButton>
            <IconButton
              type="submit"
              variant="primary"
              :loading="isLoading"
            >
              Create Project
            </IconButton>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projectStore'
import { useNotification } from '@/shared/composables/useNotification'
import { IconButton } from '@/shared/components/atoms'
import type { ProjectCreateData } from '@/shared/types/project'

const router = useRouter()
const projectStore = useProjectStore()
const { showNotification } = useNotification()

const isLoading = ref(false)
const formData = ref<Required<ProjectCreateData>>({
  name: '',
  description: ''
})

function handleCancel() {
  router.push({ name: 'builder-projects' })
}

async function handleSubmit() {
  if (isLoading.value) return

  isLoading.value = true
  try {
    const newProject = await projectStore.createProject({
      name: formData.value.name,
      description: formData.value.description || '' // Ensure description is never undefined
    })
    
    showNotification({
      type: 'success',
      message: 'Project created successfully'
    })
    
    router.push({
      name: 'builder-project-detail',
      params: { id: newProject.id }
    })
  } catch (error) {
    showNotification({
      type: 'error',
      message: 'Failed to create project'
    })
  } finally {
    isLoading.value = false
  }
}
</script>
