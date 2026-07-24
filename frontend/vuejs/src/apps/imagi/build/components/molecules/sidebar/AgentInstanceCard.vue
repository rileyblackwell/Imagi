<template>
  <div
    :class="[
      'group relative rounded-lg border px-2.5 py-2 cursor-pointer transition-all duration-200',
      isActive
        ? 'instance-card--active border-blue-300/80 dark:border-blue-400/40'
        : 'border-blue-950/[0.08] dark:border-white/[0.1] bg-blue-50/40 hover:bg-blue-50 hover:border-blue-950/[0.16] dark:bg-white/[0.02] dark:hover:bg-white/[0.05] dark:hover:border-white/[0.18]',
      isArchived ? 'opacity-70 hover:opacity-100' : ''
    ]"
    @click="emit('select')"
  >
    <!-- Title row -->
    <div class="flex items-start gap-2">
      <div class="flex-1 min-w-0">
        <div
          :class="[
            'text-xs truncate transition-colors duration-200',
            isActive
              ? 'font-semibold text-blue-950 dark:text-white'
              : 'font-medium text-blue-950/80 dark:text-blue-100/75 group-hover:text-blue-950 dark:group-hover:text-white'
          ]"
        >
          {{ instance.title || 'Untitled agent' }}
        </div>
        <!-- What this agent is doing right now. Active agents share one list,
             so the status is what tells them apart. -->
        <div class="flex items-center gap-1 mt-1 text-[10px]" :class="status.tone">
          <i :class="[status.icon, 'text-[9px]']"></i>
          <span class="truncate">{{ status.label }}</span>
        </div>
        <div class="flex items-center gap-1.5 mt-0.5 text-[10px] text-blue-950/40 dark:text-blue-100/45">
          <span>{{ relativeTime(instance.updatedAt) }}</span>
          <!-- Conversation-wide token total; null means never captured, so
               nothing renders (unknown, not "0 tokens") -->
          <span
            v-if="typeof instance.totalTokens === 'number' && instance.totalTokens > 0"
            :title="`${instance.totalTokens.toLocaleString()} tokens used`"
          >
            · {{ formatTokens(instance.totalTokens) }} tokens
          </span>
        </div>
      </div>

      <!-- Unread dot: a run finished while this instance was off-screen -->
      <span
        v-if="instance.hasUnread"
        class="shrink-0 w-1.5 h-1.5 mt-1.5 rounded-full bg-blue-950 dark:bg-[#f3ede2]"
        title="Agent finished while you were away"
      ></span>

      <!-- Actions -->
      <div ref="menuRef" class="relative shrink-0" @click.stop>
        <button
          :class="[
            'w-6 h-6 flex items-center justify-center rounded-md transition-opacity hover:bg-blue-100 dark:hover:bg-white/[0.08] text-blue-950/50 dark:text-blue-100/60 hover:text-blue-950/80 dark:hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]',
            menuOpen ? 'opacity-100 bg-blue-100 dark:bg-white/[0.08]' : 'opacity-0 group-hover:opacity-100 focus:opacity-100'
          ]"
          title="Options"
          @click.stop="toggleMenu"
        >
          <i class="fas fa-ellipsis-h text-[10px]"></i>
        </button>
        <div
          v-if="menuOpen"
          class="absolute right-0 top-full mt-1 z-50 min-w-[140px] rounded-lg border border-blue-950/[0.08] dark:border-white/[0.14] bg-white/95 dark:bg-[#161616]/95 backdrop-blur-sm shadow-xl shadow-blue-950/10 dark:shadow-black/40 py-1"
        >
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
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import type { AgentInstance } from '../../../types/services'

const props = defineProps<{
  instance: AgentInstance
  isActive: boolean
  isArchived?: boolean
}>()

/**
 * One line describing where this agent stands. Running beats everything (a
 * re-prompted agent is working again whatever its last outcome was), then the
 * states that want the user, then the settled ones.
 */
const status = computed(() => {
  const instance = props.instance
  if (instance.isProcessing) {
    return {
      label: 'Working…',
      icon: 'fas fa-circle-notch fa-spin',
      tone: 'text-blue-600 dark:text-blue-300',
    }
  }
  if (instance.archivedAt) {
    return {
      label: 'Archived',
      icon: 'fas fa-box-archive',
      tone: 'text-blue-950/40 dark:text-blue-100/40',
    }
  }
  switch (instance.reviewStatus) {
    case 'input':
      return {
        label: 'Asked you a question',
        icon: 'fas fa-circle-question',
        tone: 'text-blue-950/60 dark:text-blue-100/60',
      }
    case 'ready':
      return {
        label: 'Finished — waiting on you',
        icon: 'fas fa-check',
        tone: 'text-blue-950/60 dark:text-blue-100/60',
      }
    case 'accepted':
      return {
        label: 'Added to your app',
        icon: 'fas fa-check-double',
        tone: 'text-blue-950/40 dark:text-blue-100/40',
      }
    case 'dismissed':
      return {
        label: 'Discarded',
        icon: 'fas fa-xmark',
        tone: 'text-blue-950/40 dark:text-blue-100/40',
      }
    case 'active':
      // A dispatched agent between creation and its run starting.
      return {
        label: 'Starting…',
        icon: 'fas fa-hourglass-start',
        tone: 'text-blue-950/45 dark:text-blue-100/45',
      }
    default:
      return {
        label: 'Idle',
        icon: 'fas fa-comments',
        tone: 'text-blue-950/40 dark:text-blue-100/40',
      }
  }
})

const emit = defineEmits<{
  (e: 'select'): void
  (e: 'delete'): void
}>()

const menuOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)

function toggleMenu() {
  menuOpen.value = !menuOpen.value
}

function closeMenu() {
  menuOpen.value = false
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

/** Compact token count for the meta row: 850, 12.3k, 2M. */
function formatTokens(total: number): string {
  if (total >= 1_000_000) {
    const millions = total / 1_000_000
    return `${millions >= 10 ? Math.round(millions) : Math.round(millions * 10) / 10}M`
  }
  if (total >= 1_000) {
    const thousands = total / 1_000
    return `${thousands >= 100 ? Math.round(thousands) : Math.round(thousands * 10) / 10}k`
  }
  return String(total)
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
/* Selected card - soft baby-blue wash matching the site's primary accent */
.instance-card--active {
  background: linear-gradient(155deg, rgba(219, 238, 255, 0.9) 0%, rgba(183, 221, 247, 0.45) 100%);
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.08),
    0 3px 8px -3px rgba(30, 58, 138, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.dark .instance-card--active {
  background: linear-gradient(155deg, rgba(96, 165, 250, 0.14) 0%, rgba(96, 165, 250, 0.05) 100%);
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.375rem 0.625rem;
  font-size: 0.6875rem;
  font-weight: 500;
  text-align: left;
  color: rgb(23, 37, 84);
  transition: background-color 0.15s ease;
}

.menu-item:hover {
  background-color: rgba(59, 130, 246, 0.08);
}

.dark .menu-item {
  color: rgba(219, 234, 254, 0.8);
}

.dark .menu-item:hover {
  background-color: rgba(255, 255, 255, 0.06);
}

/* Canonical focus ring, inset against the menu surface */
.menu-item:focus-visible {
  outline: none;
  box-shadow: inset 0 0 0 2px rgba(59, 130, 246, 0.4);
}

.dark .menu-item:focus-visible {
  box-shadow: inset 0 0 0 2px rgba(147, 197, 253, 0.5);
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
  color: rgba(37, 99, 235, 0.75);
}

.menu-item--danger .menu-item-icon {
  color: inherit;
}

.dark .menu-item-icon {
  color: rgba(219, 234, 254, 0.5);
}
</style>
