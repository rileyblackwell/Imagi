<!--
  OperateWorkspace.vue - Shell for the per-project Operate workspace: a
  dashboard for running the business, with the app on one side and the
  money on the other.

  Resolves the project from the URL slug (like ProjectHub), points the
  operate store at it, and renders the tab navigation with a child
  router-view for the Dashboard and the Ledger it reads expenses from.

  Route: /imagi/project/:projectName/operations
-->
<template>
  <ToolWorkspaceShell
    beta
    :project-name="projectName"
    :project="project"
    :is-loading="isLoading"
    title="Operate"
    description="How your app and your business are doing. Is the app up and fast, who is visiting, and what is coming in and going out."
    loading-label="Loading operate workspace…"
    :tabs="tabs"
  >
    <router-view v-if="operateStore.projectId" />
  </ToolWorkspaceShell>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useProjectFromSlug, ToolWorkspaceShell, type ToolTab } from '@/apps/imagi/shared'
import { useOperateStore } from '../stores/operate'

const props = defineProps<{
  projectName: string
}>()

const { project, isLoading } = useProjectFromSlug(() => props.projectName, 'the operate workspace')
const operateStore = useOperateStore()

const tabs: ToolTab[] = [
  { name: 'operate-dashboard', label: 'Dashboard', icon: 'fa-gauge-high' },
  { name: 'operate-finance', label: 'Ledger', icon: 'fa-file-invoice-dollar' },
]

// Point the operate store at the resolved project so tab views can load data.
watch(project, (resolved) => {
  if (resolved?.id != null) {
    operateStore.setProject(Number(resolved.id))
  }
}, { immediate: true })

</script>
