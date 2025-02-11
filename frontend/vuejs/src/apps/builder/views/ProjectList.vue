<template>
  <div class="min-h-screen bg-dark-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-2xl font-bold text-white">Your Projects</h1>
        <IconButton
          icon="fas fa-plus"
          variant="primary"
          @click="createNewProject"
        >
          New Project
        </IconButton>
      </div>

      <div class="grid gap-6">
        <ProjectListItem
          v-for="project in projectStore.sortedProjects"
          :key="project.id"
          :project="project"
          @click="goToProject(project.id)"
        />
        <EmptyState
          v-if="!projectStore.hasProjects"
          icon="fas fa-folder-open"
          title="No projects yet"
          description="Start by creating your first project"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projectStore'
import { IconButton } from '@/shared/components/atoms'
import { ProjectListItem, EmptyState } from '@/shared/components/molecules'
import type { Project } from '@/shared/types/project'

const router = useRouter()
const projectStore = useProjectStore()

function goToProject(id: string | number) {
  router.push({
    name: 'builder-project-detail',
    params: { id: String(id) }
  })
}

function createNewProject() {
  router.push({ name: 'builder-new-project' })
}
</script>
