<template>
  <BuilderPageTemplate>
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-white">Create New Project</h1>
        <p class="mt-2 text-gray-400">
          Start building your next application with Imagi
        </p>
      </div>

      <!-- Project Form -->
      <ProjectForm
        v-model:name="formData.name"
        v-model:description="formData.description"
        :loading="isLoading"
        @submit="handleSubmit"
        @cancel="handleCancel"
      />
    </div>
  </BuilderPageTemplate>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '@/apps/products/oasis/builder/stores/projectStore'
import { useNotification } from '@/shared/composables/useNotification'
import { BuilderPageTemplate } from '@/apps/products/oasis/builder/components/templates'
import { ProjectForm } from '@/apps/products/oasis/builder/components/molecules'
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
      description: formData.value.description || ''
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
