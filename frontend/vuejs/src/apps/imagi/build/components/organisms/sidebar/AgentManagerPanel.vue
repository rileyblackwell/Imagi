<template>
  <div class="flex flex-col h-full bg-white dark:bg-[#0a0a0a] border-r border-gray-200 dark:border-white/[0.08] transition-colors duration-300">
    <!-- Confirm Modal (uses Teleport to body) -->
    <ConfirmModal
      :is-open="confirmModal.isModalOpen.value"
      :options="confirmModal.modalOptions.value"
      @confirm="confirmModal.handleConfirm"
      @cancel="confirmModal.handleCancel"
    />
    <!-- Header -->
    <div class="shrink-0 px-3 py-3 border-b border-gray-200 dark:border-white/[0.08] flex items-center justify-between">
      <div class="flex items-center gap-2">
        <i class="fas fa-layer-group text-xs text-gray-500 dark:text-white/50"></i>
        <span class="text-xs font-semibold uppercase tracking-wider text-gray-600 dark:text-white/70">
          Agents
        </span>
      </div>
      <div class="relative group">
        <button
          class="flex items-center justify-center w-7 h-7 rounded-md bg-gray-100 hover:bg-gray-200 dark:bg-white/[0.05] dark:hover:bg-white/[0.1] text-gray-700 dark:text-white/80 transition-colors"
          @click="handleCreate"
        >
          <i class="fas fa-plus text-xs"></i>
        </button>
        <div
          class="pointer-events-none absolute right-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-gray-900 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-gray-900 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
        >
          New agent instance
        </div>
      </div>
    </div>

    <!-- Instances list -->
    <div class="flex-1 min-h-0 overflow-y-auto px-2 py-2 space-y-1">
      <!-- Loading state -->
      <div v-if="store.instancesLoading && store.instances.length === 0" class="text-xs text-gray-400 dark:text-white/40 px-2 py-4 text-center">
        Loading...
      </div>

      <!-- Active instances -->
      <template v-if="activeInstances.length > 0">
        <div class="text-[10px] font-semibold uppercase tracking-wider text-gray-400 dark:text-white/40 px-2 py-1">
          Active
        </div>
        <InstanceCard
          v-for="instance in activeInstances"
          :key="instance.id"
          :instance="instance"
          :is-active="instance.id === store.activeInstanceId"
          @select="handleSelect(instance.id)"
          @archive="handleArchive(instance.id)"
          @delete="handleDelete(instance.id)"
          @rename="handleRename(instance.id, $event)"
        />
      </template>

      <!-- Archived / past instances -->
      <template v-if="archivedInstances.length > 0">
        <button
          class="w-full flex items-center justify-between px-2 py-2 mt-3 text-[10px] font-semibold uppercase tracking-wider text-gray-400 dark:text-white/40 hover:text-gray-600 dark:hover:text-white/70 transition-colors"
          @click="showArchived = !showArchived"
        >
          <span>Past ({{ archivedInstances.length }})</span>
          <i :class="['fas text-[9px]', showArchived ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
        </button>
        <template v-if="showArchived">
          <InstanceCard
            v-for="instance in archivedInstances"
            :key="instance.id"
            :instance="instance"
            :is-active="instance.id === store.activeInstanceId"
            is-archived
            @select="handleSelect(instance.id)"
            @unarchive="handleUnarchive(instance.id)"
            @delete="handleDelete(instance.id)"
            @rename="handleRename(instance.id, $event)"
          />
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import { useConfirm } from '../../../composables/useConfirm'
import InstanceCard from '../../molecules/sidebar/AgentInstanceCard.vue'
import ConfirmModal from '../modals/ConfirmModal.vue'

const store = useAgentStore()
const showArchived = ref(false)
const confirmModal = useConfirm()
const { confirm } = confirmModal

const activeInstances = computed(() => store.activeInstances)
const archivedInstances = computed(() => store.archivedInstances)

async function handleCreate() {
  await store.createInstance()
}

async function handleSelect(id: string) {
  await store.switchInstance(id)
}

async function handleArchive(id: string) {
  await store.archiveInstance(id)
}

async function handleUnarchive(id: string) {
  await store.unarchiveInstance(id)
}

async function handleDelete(id: string) {
  const instance = store.instances.find(i => i.id === id)
  const name = instance?.title || 'this agent instance'
  const confirmed = await confirm({
    title: 'Delete Agent Instance',
    message: `Are you sure you want to delete "${name}" and all its messages? This action cannot be undone.`,
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'danger'
  })
  if (!confirmed) return
  await store.deleteInstance(id)
}

async function handleRename(id: string, title: string) {
  await store.renameInstance(id, title)
}
</script>
