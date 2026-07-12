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
    <div class="shrink-0 px-2 py-2 border-b border-gray-200 dark:border-white/[0.08] flex items-center justify-between">
      <div class="flex items-center gap-0.5">
        <!-- Collapse -->
        <div class="relative group">
          <button
            class="flex items-center justify-center w-7 h-7 rounded-md text-gray-600 dark:text-white/70 hover:bg-gray-100 dark:hover:bg-white/[0.08] hover:text-gray-900 dark:hover:text-white transition-colors"
            @click="emit('collapse')"
          >
            <i class="fas fa-chevron-left text-xs"></i>
          </button>
          <div
            class="pointer-events-none absolute left-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-gray-900 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-gray-900 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
          >
            Collapse
          </div>
        </div>
        <!-- Search -->
        <div class="relative group">
          <button
            :class="[
              'flex items-center justify-center w-7 h-7 rounded-md transition-colors',
              showSearch
                ? 'bg-gray-100 dark:bg-white/[0.08] text-gray-900 dark:text-white'
                : 'text-gray-600 dark:text-white/70 hover:bg-gray-100 dark:hover:bg-white/[0.08] hover:text-gray-900 dark:hover:text-white'
            ]"
            @click="toggleSearch"
          >
            <i class="fas fa-search text-xs"></i>
          </button>
          <div
            class="pointer-events-none absolute left-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-gray-900 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-gray-900 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
          >
            Search chats
          </div>
        </div>
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

    <!-- Search input -->
    <div v-if="showSearch" class="shrink-0 px-2 py-2 border-b border-gray-200 dark:border-white/[0.08]">
      <div class="flex items-center gap-2 rounded-md bg-gray-100 dark:bg-white/[0.05] px-2 py-1.5">
        <i class="fas fa-search text-[11px] text-gray-400 dark:text-white/40 shrink-0"></i>
        <input
          ref="searchInput"
          v-model="searchQuery"
          type="text"
          placeholder="Search chats"
          class="flex-1 min-w-0 bg-transparent text-xs text-gray-900 dark:text-white/90 placeholder-gray-400 dark:placeholder-white/30 outline-none"
          @keydown.escape="closeSearch"
        />
        <button
          v-if="searchQuery"
          class="shrink-0 text-gray-400 hover:text-gray-600 dark:text-white/40 dark:hover:text-white/70 transition-colors"
          @click="searchQuery = ''"
        >
          <i class="fas fa-times text-[11px]"></i>
        </button>
      </div>
    </div>

    <!-- Instances list -->
    <div class="flex-1 min-h-0 overflow-y-auto px-2 py-2 space-y-1">
      <!-- Loading state -->
      <div v-if="store.instancesLoading && store.instances.length === 0" class="text-xs text-gray-400 dark:text-white/40 px-2 py-4 text-center">
        Loading...
      </div>

      <!-- No search results -->
      <div
        v-else-if="showSearch && searchQuery.trim() && !hasResults"
        class="text-xs text-gray-400 dark:text-white/40 px-2 py-4 text-center"
      >
        No chats match "{{ searchQuery.trim() }}"
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
import { computed, ref, nextTick } from 'vue'
import type { AgentInstance } from '../../../types/services'
import { useAgentStore } from '../../../stores/agentStore'
import { useConfirm } from '../../../composables/useConfirm'
import InstanceCard from '../../molecules/sidebar/AgentInstanceCard.vue'
import ConfirmModal from '../modals/ConfirmModal.vue'

const emit = defineEmits<{
  (e: 'collapse'): void
}>()

const store = useAgentStore()
const showArchived = ref(false)
const confirmModal = useConfirm()
const { confirm } = confirmModal

const showSearch = ref(false)
const searchQuery = ref('')
const searchInput = ref<HTMLInputElement | null>(null)

function filterBySearch(list: AgentInstance[]): AgentInstance[] {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return list
  return list.filter(
    i =>
      (i.title || '').toLowerCase().includes(q) ||
      (i.lastMessagePreview || '').toLowerCase().includes(q)
  )
}

const activeInstances = computed(() => filterBySearch(store.activeInstances))
const archivedInstances = computed(() => filterBySearch(store.archivedInstances))
const hasResults = computed(() => activeInstances.value.length > 0 || archivedInstances.value.length > 0)

async function toggleSearch() {
  showSearch.value = !showSearch.value
  if (showSearch.value) {
    await nextTick()
    searchInput.value?.focus()
  } else {
    searchQuery.value = ''
  }
}

function closeSearch() {
  showSearch.value = false
  searchQuery.value = ''
}

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
