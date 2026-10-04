<!--
  OperateWorkspace.vue - Shell for the per-project Operate workspace, the
  central hub for running the business.

  Resolves the project from the URL slug (like ProjectHub), points the
  operate store at it, and renders the tab navigation with a child
  router-view for Dashboard / Finance / Invoices / Tasks.

  Route: /imagi/project/:projectName/operations
-->
<template>
  <ToolWorkspaceShell
    :project-name="projectName"
    :project="project"
    :is-loading="isLoading"
    title="Operate"
    description="The central hub for running your business — money in and out, invoices, and the day-to-day work, all in one place."
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
  { name: 'operate-finance', label: 'Finance', icon: 'fa-file-invoice-dollar' },
  { name: 'operate-invoices', label: 'Invoices', icon: 'fa-receipt' },
  { name: 'operate-tasks', label: 'Tasks', icon: 'fa-list-check' },
]

// Point the operate store at the resolved project so tab views can load data.
watch(project, (resolved) => {
  if (resolved?.id != null) {
    operateStore.setProject(Number(resolved.id))
  }
}, { immediate: true })

</script>
