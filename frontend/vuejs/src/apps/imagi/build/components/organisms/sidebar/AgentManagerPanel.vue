<template>
  <div class="flex flex-col h-full bg-white dark:bg-[#0a0a0a] border-r border-blue-100 dark:border-white/[0.08] transition-colors duration-300">
    <!-- Confirm Modal (uses Teleport to body) -->
    <ConfirmModal
      :is-open="confirmModal.isModalOpen.value"
      :options="confirmModal.modalOptions.value"
      @confirm="confirmModal.handleConfirm"
      @cancel="confirmModal.handleCancel"
    />
    <!-- Header -->
    <div class="shrink-0 flex items-center gap-1 px-2 py-2 border-b border-blue-100 dark:border-white/[0.08]">
      <!-- Collapse (desktop only; mobile uses the navbar view switcher) -->
      <div class="relative group max-md:hidden">
        <button
          class="flex items-center justify-center w-7 h-7 rounded-md text-blue-950/60 dark:text-white/70 hover:bg-blue-50 dark:hover:bg-white/[0.08] hover:text-blue-950 dark:hover:text-white transition-colors"
          @click="emit('collapse')"
        >
          <i class="fas fa-chevron-left text-xs"></i>
        </button>
        <div
          class="pointer-events-none absolute left-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-blue-950 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-blue-950 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
        >
          Collapse
        </div>
      </div>

      <!-- Panel title -->
      <div class="flex-1 min-w-0 flex items-center gap-2 pl-0.5">
        <div class="agents-icon-chip flex items-center justify-center w-5 h-5 rounded-md shrink-0">
          <i class="fas fa-layer-group text-[9px] text-blue-700 dark:text-blue-300"></i>
        </div>
        <span class="text-xs font-semibold text-blue-950/80 dark:text-white/80 truncate">Agents</span>
      </div>

      <!-- Search -->
      <div class="relative group">
        <button
          :class="[
            'flex items-center justify-center w-7 h-7 rounded-md transition-colors',
            showSearch
              ? 'bg-blue-50 dark:bg-white/[0.08] text-blue-950 dark:text-white'
              : 'text-blue-950/60 dark:text-white/70 hover:bg-blue-50 dark:hover:bg-white/[0.08] hover:text-blue-950 dark:hover:text-white'
          ]"
          @click="toggleSearch"
        >
          <i class="fas fa-search text-xs"></i>
        </button>
        <div
          class="pointer-events-none absolute right-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-blue-950 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-blue-950 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
        >
          Search chats
        </div>
      </div>

      <!-- New agent instance -->
      <div class="relative group">
        <button
          class="btn-new flex items-center justify-center w-7 h-7 rounded-md text-blue-950 border border-white/60 dark:border-white/30 transition-all duration-200"
          @click="handleCreate"
        >
          <i class="fas fa-plus text-xs"></i>
        </button>
        <div
          class="pointer-events-none absolute right-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-blue-950 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-blue-950 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
        >
          New agent instance
        </div>
      </div>
    </div>

    <!-- Search input -->
    <div v-if="showSearch" class="shrink-0 px-2 py-2 border-b border-blue-100 dark:border-white/[0.08]">
      <div class="search-shell flex items-center gap-2 rounded-lg bg-blue-50/50 dark:bg-white/[0.03] border border-blue-200/70 dark:border-white/[0.08] px-2.5 py-1.5">
        <i class="fas fa-search text-[11px] text-blue-950/40 dark:text-white/40 shrink-0"></i>
        <input
          ref="searchInput"
          v-model="searchQuery"
          type="text"
          placeholder="Search chats"
          class="flex-1 min-w-0 bg-transparent text-xs text-blue-950 dark:text-white/90 placeholder-blue-950/40 dark:placeholder-white/30 outline-none"
          @keydown.escape="closeSearch"
        />
        <button
          v-if="searchQuery"
          class="shrink-0 text-blue-950/40 hover:text-blue-950/70 dark:text-white/40 dark:hover:text-white/70 transition-colors"
          @click="searchQuery = ''"
        >
          <i class="fas fa-times text-[11px]"></i>
        </button>
      </div>
    </div>

    <!-- Instances list -->
    <div class="flex-1 min-h-0 overflow-y-auto px-2 py-2 space-y-1">
      <!-- Loading state -->
      <div
        v-if="store.instancesLoading && store.instances.length === 0"
        class="flex items-center justify-center gap-2 px-2 py-8 text-xs text-blue-950/40 dark:text-white/40"
      >
        <i class="fas fa-circle-notch fa-spin text-[11px]"></i>
        <span>Loading agents…</span>
      </div>

      <!-- No search results -->
      <div
        v-else-if="showSearch && searchQuery.trim() && !hasResults"
        class="flex flex-col items-center px-4 py-8 text-center"
      >
        <div class="flex items-center justify-center w-9 h-9 rounded-full bg-blue-50 dark:bg-white/[0.05] border border-blue-100 dark:border-white/[0.08] mb-2.5">
          <i class="fas fa-search text-xs text-blue-400 dark:text-white/40"></i>
        </div>
        <div class="text-xs font-medium text-blue-950/60 dark:text-white/50">No matching chats</div>
        <div class="text-[11px] text-blue-950/40 dark:text-white/30 mt-1 break-all">
          Nothing matches "{{ searchQuery.trim() }}"
        </div>
      </div>

      <!-- Empty state -->
      <div
        v-else-if="!hasResults"
        class="flex flex-col items-center px-4 py-8 text-center"
      >
        <div class="flex items-center justify-center w-9 h-9 rounded-full bg-blue-50 dark:bg-white/[0.05] border border-blue-100 dark:border-white/[0.08] mb-2.5">
          <i class="fas fa-layer-group text-xs text-blue-400 dark:text-white/40"></i>
        </div>
        <div class="text-xs font-medium text-blue-950/60 dark:text-white/50">No agents yet</div>
        <div class="text-[11px] text-blue-950/40 dark:text-white/30 mt-1">Create one with the + button above</div>
      </div>

      <!-- Active instances -->
      <template v-if="activeInstances.length > 0">
        <div class="text-[10px] font-semibold uppercase tracking-wider text-blue-950/40 dark:text-white/40 px-2 pt-1 pb-1.5">
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
          class="w-full flex items-center justify-between rounded-md px-2 py-2 mt-3 text-[10px] font-semibold uppercase tracking-wider text-blue-950/40 dark:text-white/40 hover:text-blue-950/70 dark:hover:text-white/70 hover:bg-blue-50/60 dark:hover:bg-white/[0.04] transition-colors"
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

<style scoped>
/* Panel title chip - baby-blue accent matching the site's primary buttons */
.agents-icon-chip {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.1),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.7);
}

.dark .agents-icon-chip {
  background: rgba(96, 165, 250, 0.12);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

/* Baby-blue "new agent" button - matching the chat's send button */
.btn-new {
  background: linear-gradient(155deg, #dbeeff 0%, #b7ddf7 55%, #9ecdf3 100%);
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.14),
    0 3px 8px -2px rgba(30, 58, 138, 0.16),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.12);
}

.btn-new:hover {
  filter: brightness(1.04);
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.16),
    0 5px 12px -2px rgba(30, 58, 138, 0.22),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.12);
}

.dark .btn-new {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.5),
    0 3px 8px -2px rgba(0, 0, 0, 0.45),
    inset 0 1px 1px 0 rgba(255, 255, 255, 0.75),
    inset 0 -2px 4px -1px rgba(30, 58, 138, 0.18);
}

/* Search field focus ring - matching the chat input shell */
.search-shell {
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.search-shell:focus-within {
  border-color: rgba(59, 130, 246, 0.55);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.dark .search-shell:focus-within {
  border-color: rgba(147, 197, 253, 0.5);
  box-shadow: 0 0 0 3px rgba(147, 197, 253, 0.18);
}
</style>
