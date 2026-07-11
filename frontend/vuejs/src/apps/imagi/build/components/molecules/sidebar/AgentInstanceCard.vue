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
      <i
        :class="[
          'text-[10px] mt-0.5 shrink-0',
          instance.mode === 'agent'
            ? 'fas fa-robot text-purple-500 dark:text-purple-400'
            : 'fas fa-comment-dots text-indigo-500 dark:text-indigo-400'
        ]"
      ></i>
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
        <div
          class="text-[11px] text-gray-500 dark:text-white/50 mt-0.5 line-clamp-2 leading-snug"
          :title="instance.lastMessagePreview"
        >
          {{ instance.lastMessagePreview || 'No messages yet' }}
        </div>
        <div class="flex items-center gap-1.5 mt-1.5 text-[10px] text-gray-400 dark:text-white/40">
          <span>{{ instance.selectedModelId || '—' }}</span>
          <span aria-hidden="true">·</span>
          <span>{{ relativeTime(instance.updatedAt) }}</span>
          <span v-if="instance.isProcessing" class="ml-1 flex items-center gap-1 text-indigo-500 dark:text-indigo-300">
            <i class="fas fa-circle-notch fa-spin text-[9px]"></i>
            <span>running</span>
          </span>
        </div>
      </div>

      <!-- Actions -->
      <div
        class="shrink-0 opacity-0 group-hover:opacity-100 focus-within:opacity-100 transition-opacity flex items-center gap-0.5"
        @click.stop
      >
        <button
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-200 dark:hover:bg-white/[0.08] text-gray-500 dark:text-white/60"
          title="Rename"
          @click.stop="startRename"
        >
          <i class="fas fa-pen text-[9px]"></i>
        </button>
        <button
          v-if="!isArchived"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-200 dark:hover:bg-white/[0.08] text-gray-500 dark:text-white/60"
          title="Archive"
          @click.stop="emit('archive')"
        >
          <i class="fas fa-archive text-[9px]"></i>
        </button>
        <button
          v-else
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-200 dark:hover:bg-white/[0.08] text-gray-500 dark:text-white/60"
          title="Unarchive"
          @click.stop="emit('unarchive')"
        >
          <i class="fas fa-box-open text-[9px]"></i>
        </button>
        <button
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-red-100 dark:hover:bg-red-500/20 text-gray-500 dark:text-white/60 hover:text-red-600 dark:hover:text-red-400"
          title="Delete"
          @click.stop="emit('delete')"
        >
          <i class="fas fa-trash text-[9px]"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
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
  if (mins < 60) return `${mins}m`
  const hrs = Math.floor(mins / 60)
  if (hrs < 24) return `${hrs}h`
  const days = Math.floor(hrs / 24)
  if (days < 7) return `${days}d`
  return date.toLocaleDateString()
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
