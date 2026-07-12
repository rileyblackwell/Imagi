<template>
  <div
    :class="[
      'group relative rounded-lg border px-2.5 py-2 cursor-pointer transition-all duration-200',
      isActive
        ? 'border-indigo-400 dark:border-indigo-500/60 bg-indigo-50/70 dark:bg-indigo-500/[0.08] shadow-sm'
        : 'border-gray-200 dark:border-white/[0.06] bg-gray-50/50 hover:bg-gray-100 dark:bg-white/[0.02] dark:hover:bg-white/[0.05]',
      isArchived ? 'opacity-75' : ''
    ]"
    @click="emit('select')"
  >
    <!-- Title row -->
    <div class="flex items-start gap-2">
      <div class="flex-1 min-w-0">
        <input
          v-if="isEditing"
          ref="titleInput"
          v-model="draftTitle"
          type="text"
          class="w-full bg-transparent text-xs font-semibold text-gray-900 dark:text-white/90 border-b border-indigo-400 outline-none"
          @click.stop
          @keydown.enter.prevent="commitRename"
          @keydown.escape="cancelRename"
          @blur="commitRename"
        />
        <div
          v-else
          class="text-xs font-semibold text-gray-900 dark:text-white/90 truncate"
        >
          {{ instance.title || 'Untitled instance' }}
        </div>
        <div class="flex items-center gap-1.5 mt-1 text-[10px] text-gray-400 dark:text-white/40">
          <span>{{ relativeTime(instance.updatedAt) }}</span>
          <span v-if="instance.isProcessing" class="ml-1 flex items-center gap-1 text-indigo-500 dark:text-indigo-300">
            <i class="fas fa-circle-notch fa-spin text-[9px]"></i>
            <span>running</span>
          </span>
        </div>
      </div>

      <!-- Actions -->
      <div ref="menuRef" class="relative shrink-0" @click.stop>
        <button
          :class="[
            'w-6 h-6 flex items-center justify-center rounded transition-opacity hover:bg-gray-200 dark:hover:bg-white/[0.08] text-gray-500 dark:text-white/60',
            menuOpen ? 'opacity-100 bg-gray-200 dark:bg-white/[0.08]' : 'opacity-0 group-hover:opacity-100 focus:opacity-100'
          ]"
          title="Options"
          @click.stop="toggleMenu"
        >
          <i class="fas fa-ellipsis-h text-[10px]"></i>
        </button>
        <div
          v-if="menuOpen"
          class="absolute right-0 top-full mt-1 z-50 min-w-[130px] rounded-md border border-gray-200 dark:border-white/[0.08] bg-white dark:bg-[#161616] shadow-lg py-1"
        >
          <button class="menu-item" @click.stop="onRename">
            <i class="fas fa-pen menu-item-icon"></i>
            <span>Rename</span>
          </button>
          <button v-if="!isArchived" class="menu-item" @click.stop="onArchive">
            <i class="fas fa-archive menu-item-icon"></i>
            <span>Archive</span>
          </button>
          <button v-else class="menu-item" @click.stop="onUnarchive">
            <i class="fas fa-box-open menu-item-icon"></i>
            <span>Unarchive</span>
          </button>
          <button class="menu-item menu-item--danger" @click.stop="onDelete">
            <i class="fas fa-trash menu-item-icon"></i>
            <span>Delete</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onBeforeUnmount } from 'vue'
import type { AgentInstance } from '../../../types/services'

const props = defineProps<{
  instance: AgentInstance
  isActive: boolean
  isArchived?: boolean
}>()

const emit = defineEmits<{
  (e: 'select'): void
  (e: 'archive'): void
  (e: 'unarchive'): void
  (e: 'delete'): void
  (e: 'rename', title: string): void
}>()

const isEditing = ref(false)
const draftTitle = ref('')
const titleInput = ref<HTMLInputElement | null>(null)

const menuOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function closeMenu() {
  menuOpen.value = false
}

function onRename() {
  closeMenu()
  startRename()
}

function onArchive() {
  closeMenu()
  emit('archive')
}

function onUnarchive() {
  closeMenu()
  emit('unarchive')
}

function onDelete() {
  closeMenu()
  emit('delete')
}

function handleDocumentClick(event: MouseEvent) {
  if (menuOpen.value && menuRef.value && !menuRef.value.contains(event.target as Node)) {
    closeMenu()
  }
}

onMounted(() => document.addEventListener('mousedown', handleDocumentClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', handleDocumentClick))

async function startRename() {
  draftTitle.value = props.instance.title || ''
  isEditing.value = true
  await nextTick()
  titleInput.value?.focus()
  titleInput.value?.select()
}

function commitRename() {
  if (!isEditing.value) return
  const newTitle = draftTitle.value.trim()
  isEditing.value = false
  if (newTitle && newTitle !== props.instance.title) {
    emit('rename', newTitle)
  }
}

function cancelRename() {
  isEditing.value = false
}

function relativeTime(iso: string): string {
  if (!iso) return ''
  const date = new Date(iso)
  const diff = Date.now() - date.getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'now'
  if (mins < 60) return `${mins}m ago`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h ago`
  const days = Math.floor(hrs / 24)
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}
</script>

<style scoped>
.menu-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.375rem 0.625rem;
  font-size: 0.6875rem;
  font-weight: 500;
  text-align: left;
  color: rgb(55, 65, 81);
  transition: background-color 0.15s ease;
}

.menu-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.dark .menu-item {
  color: rgba(255, 255, 255, 0.8);
}

.dark .menu-item:hover {
  background-color: rgba(255, 255, 255, 0.06);
}

.menu-item--danger {
  color: rgb(220, 38, 38);
}

.dark .menu-item--danger {
  color: rgb(248, 113, 113);
}

.menu-item--danger:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

.dark .menu-item--danger:hover {
  background-color: rgba(239, 68, 68, 0.15);
}

.menu-item-icon {
  width: 0.875rem;
  font-size: 0.625rem;
  text-align: center;
  color: rgba(107, 114, 128, 0.9);
}

.menu-item--danger .menu-item-icon {
  color: inherit;
}

.dark .menu-item-icon {
  color: rgba(255, 255, 255, 0.45);
}
</style>
