<template>
  <div class="flex flex-col h-full bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
    <!-- Confirmations render through the workspace-level ConfirmModal
         (useConfirm state is global; one host avoids duplicate modals). -->
    <!-- Header -->
    <div class="shrink-0 flex items-center gap-1 px-2 py-2 border-b border-blue-950/[0.08] dark:border-white/[0.14]">
      <!-- Back to the agent chat (desktop only; mobile uses the navbar view
           switcher). The robot marks it as the agent instance. -->
      <div class="relative group max-md:hidden">
        <button
          class="flex items-center justify-center w-7 h-7 rounded-md text-blue-950/60 dark:text-blue-100/70 hover:bg-blue-50 dark:hover:bg-white/[0.08] hover:text-blue-950 dark:hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
          @click="emit('collapse')"
        >
          <i class="fas fa-robot text-xs"></i>
        </button>
        <div
          class="pointer-events-none absolute left-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-blue-950 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-blue-950 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
        >
          Back to chat
        </div>
      </div>

      <!-- Panel title -->
      <div class="flex-1 min-w-0 flex items-center pl-0.5">
        <span class="text-xs font-semibold text-blue-950/80 dark:text-blue-100/85 truncate">Agent Manager</span>
      </div>

      <!-- Read-only view: work is dispatched by the agent in the main thread,
           not from here, so there is no "new task" control. -->
      <span
        class="shrink-0 inline-flex items-center gap-1 rounded-full px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wider bg-blue-950/[0.06] dark:bg-white/[0.08] text-blue-950/55 dark:text-white/55"
        title="Ask for work in your main thread — your agent dispatches it here"
      >
        <i class="fas fa-eye text-[8px]"></i>
        View only
      </span>
    </div>

    <!-- Team view -->
    <div class="flex-1 min-h-0 overflow-y-auto px-2 py-2 space-y-1">
      <!-- A refused delete (a task's run still holds its worktree) says why -->
      <div
        v-if="actionError"
        class="flex items-start gap-2 rounded-lg border border-red-200/70 dark:border-red-400/20 bg-red-50/70 dark:bg-red-500/[0.06] px-2.5 py-1.5"
      >
        <p class="flex-1 min-w-0 text-[11px] leading-snug text-red-700 dark:text-red-300 break-words">
          {{ actionError }}
        </p>
        <button
          type="button"
          aria-label="Dismiss error"
          class="shrink-0 text-red-400 hover:text-red-600 dark:text-red-300/60 dark:hover:text-red-300 transition-colors"
          @click="actionError = null"
        >
          <i class="fas fa-times text-[10px]"></i>
        </button>
      </div>

      <!-- Loading state -->
      <div
        v-if="store.instancesLoading && store.instances.length === 0"
        class="flex items-center justify-center gap-2 px-2 py-8 text-xs text-blue-950/40 dark:text-blue-100/45"
      >
        <i class="fas fa-circle-notch fa-spin text-[11px]"></i>
        <span>Loading agents…</span>
      </div>

      <template v-else>
        <!-- Lead thread: the one pinned conversation the user directs -->
        <template v-if="leadVisible && lead">
          <div class="section-label px-2 pt-1 pb-1.5">Main thread</div>
          <div
            :class="[
              'lead-card group rounded-lg border px-2.5 py-2 cursor-pointer transition-all duration-200',
              lead.id === store.activeInstanceId
                ? 'lead-card--active border-blue-300/80 dark:border-blue-400/40'
                : 'border-blue-950/[0.08] dark:border-white/[0.08] bg-blue-50/40 hover:bg-blue-50 hover:border-blue-200/90 dark:bg-white/[0.02] dark:hover:bg-white/[0.05] dark:hover:border-white/[0.14]'
            ]"
            @click="handleSelect(lead.id)"
          >
            <div class="flex items-center gap-2">
              <div class="agents-icon-chip flex items-center justify-center w-5 h-5 rounded-md shrink-0">
                <i class="fas fa-comments text-[9px] text-blue-950/80 dark:text-[#f3ede2]/90"></i>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-xs font-semibold text-blue-950/90 dark:text-white/90 truncate">
                  {{ lead.title || 'Main thread' }}
                </div>
                <div class="flex items-center gap-1.5 text-[10px] text-blue-950/40 dark:text-white/40">
                  <span class="truncate">{{ lead.lastMessagePreview || 'Direct the build from here' }}</span>
                  <span
                    v-if="store.checkIns.length > 0"
                    class="shrink-0 font-medium text-blue-950/60 dark:text-white/55"
                  >
                    · {{ store.checkIns.length }} waiting
                  </span>
                </div>
              </div>
              <span
                v-if="lead.isProcessing"
                class="shrink-0 flex items-center text-blue-600 dark:text-blue-300"
                title="Working"
              >
                <i class="fas fa-circle-notch fa-spin text-[10px]"></i>
              </span>
              <span
                v-else-if="lead.hasUnread"
                class="shrink-0 w-1.5 h-1.5 rounded-full bg-blue-950 dark:bg-[#f3ede2]"
                title="Agent finished while you were away"
              ></span>
            </div>
          </div>
        </template>

        <!-- Tasks: dispatched work running in the background, in parallel -->
        <div class="section-label px-2 pt-3 pb-1.5">Working in the background</div>
        <template v-if="taskFeed.length > 0">
          <InstanceCard
            v-for="instance in taskFeed"
            :key="instance.id"
            :instance="instance"
            :is-active="instance.id === store.activeInstanceId"
            @select="handleSelect(instance.id)"
            @delete="handleDelete(instance.id)"
          />
        </template>
        <div v-else class="px-2 pb-1 text-[11px] text-blue-950/35 dark:text-white/30">
          Nothing running. Ask for work in your main thread — your agent hands
          off anything worth doing in parallel.
        </div>

        <!-- Waiting on you: finished work, and subagents parked on a
             question. Read-only here — every decision is made in the main
             thread's queue, so the user only ever acts in one place. -->
        <template v-if="waitingInstances.length > 0">
          <div class="section-label px-2 pt-3 pb-1.5">Waiting on you</div>
          <div
            v-for="instance in waitingInstances"
            :key="instance.id"
            class="review-card rounded-lg border border-blue-100 dark:border-white/[0.06] bg-blue-50/40 dark:bg-white/[0.02] px-2.5 py-2 mb-1 cursor-pointer hover:bg-blue-50 dark:hover:bg-white/[0.05] transition-colors"
            @click="handleSelect(instance.id)"
          >
            <div class="flex items-start gap-2">
              <div class="flex-1 min-w-0">
                <div class="text-xs font-medium text-blue-950/85 dark:text-white/85 truncate">
                  {{ instance.title || 'Untitled task' }}
                </div>
                <p class="text-[10px] text-blue-950/45 dark:text-white/40 line-clamp-2 mt-0.5 break-words">
                  {{ reviewPreview(instance) }}
                </p>
              </div>
              <span
                v-if="instance.hasUnread"
                class="shrink-0 w-1.5 h-1.5 mt-1 rounded-full bg-blue-950 dark:bg-[#f3ede2]"
                title="Finished while you were away"
              ></span>
            </div>
            <div class="flex items-center gap-1.5 mt-1.5 text-[10px] text-blue-950/45 dark:text-white/40">
              <i :class="[
                'text-[8px]',
                instance.reviewStatus === 'input' ? 'fas fa-circle-question' : 'fas fa-check'
              ]"></i>
              <span>
                {{ instance.reviewStatus === 'input'
                  ? 'Asked a question — answer it in your main thread'
                  : 'Finished — review it in your main thread' }}
              </span>
            </div>
          </div>
        </template>

        <!-- History: archived threads, legacy chats, resolved tasks -->
        <template v-if="history.length > 0">
          <button
            class="w-full flex items-center justify-between rounded-md px-2 py-2 mt-3 text-[10px] font-semibold uppercase tracking-wider text-blue-950/40 dark:text-white/40 hover:text-blue-950/70 dark:hover:text-white/70 hover:bg-blue-50/60 dark:hover:bg-white/[0.04] transition-colors"
            @click="showHistory = !showHistory"
          >
            <span>History ({{ history.length }})</span>
            <i :class="['fas text-[9px]', showHistory ? 'fa-chevron-down' : 'fa-chevron-right']"></i>
          </button>
          <template v-if="showHistory">
            <InstanceCard
              v-for="instance in history"
              :key="instance.id"
              :instance="instance"
              :is-active="instance.id === store.activeInstanceId"
              :is-archived="!!instance.archivedAt"
              @select="handleSelect(instance.id)"
              @delete="handleDelete(instance.id)"
            />
          </template>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { AgentInstance } from '../../../types/services'
import { useAgentStore } from '../../../stores/agentStore'
import { useConfirm } from '../../../composables/useConfirm'
import InstanceCard from '../../molecules/sidebar/AgentInstanceCard.vue'

const emit = defineEmits<{
  (e: 'collapse'): void
  /** An instance was clicked — the workspace flips the sidebar to chat. */
  (e: 'select', instanceId: string): void
}>()

const store = useAgentStore()
const showHistory = ref(false)
const { confirm } = useConfirm()

const lead = computed(() => store.leadInstance)
const leadVisible = computed(() => !!lead.value)
// taskFeedInstances is already newest-first
const taskFeed = computed(() => store.taskFeedInstances)
const history = computed(() => store.historyInstances)

/** Subagents that have come back to the user: finished work awaiting review,
 *  and tasks parked on a question. Each has a card in the main thread's queue
 *  — this list is the read-only mirror of it. */
const waitingInstances = computed<AgentInstance[]>(() =>
  store.instances.filter(
    i => i.kind === 'task' && !i.archivedAt && !i.isProcessing &&
      (i.reviewStatus === 'ready' || i.reviewStatus === 'input')
  )
)

function reviewPreview(instance: AgentInstance): string {
  return instance.lastMessagePreview || instance.title || 'Finished task'
}

// --- Shared instance actions --------------------------------------------

const actionError = ref<string | null>(null)

function describeActionError(e: unknown): string {
  const response = (e as any)?.response
  if (response?.status === 409) {
    return 'This agent is still working — wait for it to finish or stop it.'
  }
  return e instanceof Error && e.message ? e.message : 'Something went wrong — try again.'
}

async function handleSelect(id: string) {
  emit('select', id)
  await store.switchInstance(id)
}

async function handleDelete(id: string) {
  const instance = store.instances.find(i => i.id === id)
  const name = instance?.title || 'this agent'
  const isRunning = !!instance?.isProcessing
  const confirmed = await confirm({
    title: 'Delete Agent',
    message: isRunning
      ? `"${name}" is still running. Deleting it disconnects the run (any work already in flight may still land) and permanently removes all its messages. This action cannot be undone.`
      : `Are you sure you want to delete "${name}" and all its messages? This action cannot be undone.`,
    confirmText: 'Delete',
    cancelText: 'Cancel',
    type: 'danger'
  })
  if (!confirmed) return
  // Cancel any in-flight stream before the instance disappears (no-op when idle).
  store.abortInstanceRun(id)
  try {
    await store.deleteInstance(id)
  } catch (e) {
    // The backend refuses to delete a task whose run is still live (409
    // agent_busy — its worktree is in use). The instance stays; say why.
    actionError.value = describeActionError(e)
  }
}
</script>

<style scoped>
/* Section labels share the workspace's uppercase micro-label convention */
.section-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgba(23, 37, 84, 0.4);
}

.dark .section-label {
  color: rgba(255, 255, 255, 0.4);
}

/* Panel title chip - subtle navy ink tint (a solid pill would compete with the + button) */
.agents-icon-chip {
  background: rgba(23, 37, 84, 0.08);
  box-shadow: inset 0 0 0 1px rgba(23, 37, 84, 0.06);
}

.dark .agents-icon-chip {
  background: rgba(243, 237, 226, 0.12);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

/* Selected lead card - same baby-blue wash as the active instance card */
.lead-card--active {
  background: linear-gradient(155deg, rgba(219, 238, 255, 0.9) 0%, rgba(183, 221, 247, 0.45) 100%);
  box-shadow:
    0 1px 2px rgba(30, 58, 138, 0.08),
    0 3px 8px -3px rgba(30, 58, 138, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.dark .lead-card--active {
  background: linear-gradient(155deg, rgba(96, 165, 250, 0.14) 0%, rgba(96, 165, 250, 0.05) 100%);
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* Navy ink buttons - matching the chat's send button */
.btn-new,
.btn-accept,
.btn-task-submit--active {
  background: theme('colors.blue.950');
  box-shadow:
    0 1px 2px rgba(23, 37, 84, 0.2),
    0 3px 8px -2px rgba(23, 37, 84, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.btn-new:hover,
.btn-accept:hover:not(:disabled),
.btn-task-submit--active:hover:not(:disabled) {
  background: theme('colors.blue.900');
  box-shadow:
    0 2px 3px rgba(23, 37, 84, 0.22),
    0 5px 12px -2px rgba(23, 37, 84, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.dark .btn-new,
.dark .btn-accept,
.dark .btn-task-submit--active {
  background: #f3ede2;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 3px 8px -2px rgba(0, 0, 0, 0.45);
}

.dark .btn-new:hover,
.dark .btn-accept:hover:not(:disabled),
.dark .btn-task-submit--active:hover:not(:disabled) {
  background: #ffffff;
  box-shadow:
    0 2px 3px rgba(0, 0, 0, 0.4),
    0 5px 12px -2px rgba(0, 0, 0, 0.5);
}

/* Ghost dismiss button - quiet outline that only tints on hover */
.btn-ghost {
  border: 1px solid rgba(191, 219, 254, 0.7);
  color: rgba(23, 37, 84, 0.7);
  background: transparent;
}

.btn-ghost:hover:not(:disabled) {
  background: rgba(239, 246, 255, 0.9);
  color: rgb(23, 37, 84);
}

.dark .btn-ghost {
  border-color: rgba(255, 255, 255, 0.12);
  color: rgba(255, 255, 255, 0.7);
}

.dark .btn-ghost:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.95);
}

/* New-task shell - same focus treatment as the chat input shell */
.task-shell {
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.task-shell:focus-within {
  border-color: rgba(59, 130, 246, 0.55);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.dark .task-shell:focus-within {
  border-color: rgba(147, 197, 253, 0.5);
  box-shadow: 0 0 0 3px rgba(147, 197, 253, 0.18);
}

.task-textarea,
.task-textarea:hover,
.task-textarea:focus,
.task-textarea:focus-visible,
.task-textarea:active {
  outline: none !important;
  box-shadow: none !important;
  border: none !important;
}

/* Ghost dropdown (draft count) - same recipe as the chat composer's
   .dropdown-wrapper selects */
.dropdown-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.dropdown-icon {
  position: absolute;
  left: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.6875rem;
  color: rgba(107, 114, 128, 0.8);
  pointer-events: none;
  transition: color 0.2s ease;
  z-index: 1;
}

.dark .dropdown-icon {
  color: rgba(255, 255, 255, 0.55);
}

.dropdown-wrapper:hover .dropdown-icon {
  color: rgb(55, 65, 81);
}

.dark .dropdown-wrapper:hover .dropdown-icon {
  color: rgba(255, 255, 255, 0.85);
}

.dropdown-select {
  background-image: url('data:image/svg+xml;charset=UTF-8,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27rgba(107,114,128,0.8)%27 stroke-width=%272.5%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3e%3cpolyline points=%276 9 12 15 18 9%27%3e%3c/polyline%3e%3c/svg%3e');
  background-repeat: no-repeat;
  background-position: right 0.55rem center;
  background-size: 0.85em;
  background-color: transparent;
  border: 1px solid transparent;
  color: rgba(23, 37, 84, 0.75);
  font-weight: 500;
  letter-spacing: 0.01em;
  padding: 0.3rem 1.5rem 0.3rem 0.6rem;
  border-radius: 0.5rem;
  cursor: pointer;
  text-overflow: ellipsis;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  transition: background-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
  outline: none;
}

.dropdown-select--with-icon {
  padding-left: 1.5rem;
}

.dark .dropdown-select {
  background-image: url('data:image/svg+xml;charset=UTF-8,%3csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27rgba(255,255,255,0.6)%27 stroke-width=%272.5%27 stroke-linecap=%27round%27 stroke-linejoin=%27round%27%3e%3cpolyline points=%276 9 12 15 18 9%27%3e%3c/polyline%3e%3c/svg%3e');
  color: rgba(255, 255, 255, 0.65);
}

.dropdown-select:hover {
  background-color: rgba(219, 234, 254, 0.5);
  color: rgb(23, 37, 84);
}

.dark .dropdown-select:hover {
  background-color: rgba(255, 255, 255, 0.07);
  color: rgba(255, 255, 255, 0.95);
}

.dropdown-select:focus-visible {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.35);
  outline: none;
}

.dark .dropdown-select:focus-visible {
  box-shadow: 0 0 0 2px rgba(147, 197, 253, 0.35);
}

.dropdown-select option {
  background-color: white;
  color: #374151;
  font-size: 0.75rem;
  font-weight: 500;
}

.dark .dropdown-select option {
  background-color: #0a0a0a;
  color: rgba(255, 255, 255, 0.7);
}
</style>
