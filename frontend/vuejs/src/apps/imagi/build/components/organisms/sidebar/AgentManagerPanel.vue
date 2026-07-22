<template>
  <div class="flex flex-col h-full bg-white dark:bg-[#0a0a0a] border-r border-blue-950/[0.08] dark:border-white/[0.14] transition-colors duration-300">
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

      <!-- New task -->
      <div class="relative group">
        <button
          class="btn-new flex items-center justify-center w-7 h-7 rounded-md text-[#fdf9f2] dark:text-blue-950 transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
          @click="toggleNewTask"
        >
          <i class="fas fa-plus text-xs"></i>
        </button>
        <div
          class="pointer-events-none absolute right-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-blue-950 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-blue-950 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
        >
          New task
        </div>
      </div>
    </div>

    <!-- New task form: prompt + draft count. Each draft becomes its own task
         conversation running in its own worktree, so they build in parallel. -->
    <div v-if="showNewTask" class="shrink-0 px-2 py-2 border-b border-blue-100 dark:border-white/[0.08]">
      <!-- Dispatch failures (usage limit, network) surface here — the form
           stays open so the typed prompt is never silently discarded. -->
      <div
        v-if="taskError"
        class="flex items-start gap-2 rounded-lg border border-red-200/70 dark:border-red-400/20 bg-red-50/70 dark:bg-red-500/[0.06] px-2.5 py-1.5 mb-1.5"
      >
        <p class="flex-1 min-w-0 text-[11px] leading-snug text-red-700 dark:text-red-300 break-words">
          {{ taskError }}
        </p>
        <button
          type="button"
          aria-label="Dismiss error"
          class="shrink-0 text-red-400 hover:text-red-600 dark:text-red-300/60 dark:hover:text-red-300 transition-colors"
          @click="taskError = null"
        >
          <i class="fas fa-times text-[10px]"></i>
        </button>
      </div>
      <div class="task-shell rounded-xl bg-blue-50/40 dark:bg-white/[0.03] border border-blue-100 dark:border-white/[0.08]">
        <textarea
          ref="taskInput"
          v-model="taskPrompt"
          rows="3"
          placeholder="Describe a task for the team…"
          class="task-textarea w-full bg-transparent text-blue-950 dark:text-white/90 placeholder-blue-950/40 dark:placeholder-white/30 text-xs px-2.5 pt-2 pb-1 resize-none leading-relaxed"
          @keydown.enter.exact.prevent="submitNewTask"
          @keydown.escape="closeNewTask"
        ></textarea>
        <div class="flex items-center justify-between gap-2 px-1.5 pb-1.5">
          <div class="dropdown-wrapper" title="How many parallel drafts to build">
            <i class="fas fa-clone dropdown-icon"></i>
            <select
              v-model.number="taskVariants"
              aria-label="Number of drafts"
              class="dropdown-select dropdown-select--with-icon text-xs"
            >
              <option :value="1">1 draft</option>
              <option :value="2">2 drafts</option>
              <option :value="3">3 drafts</option>
            </select>
          </div>
          <button
            type="button"
            :disabled="!taskPrompt.trim() || creatingTasks"
            class="btn-task-submit inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[11px] font-semibold transition-all duration-200"
            :class="taskPrompt.trim() && !creatingTasks
              ? 'btn-task-submit--active text-[#fdf9f2] dark:text-blue-950'
              : 'bg-blue-100/60 dark:bg-white/[0.05] text-blue-950/40 dark:text-white/40 cursor-not-allowed border border-blue-200/70 dark:border-white/[0.12]'"
            @click="submitNewTask"
          >
            <i :class="['text-[10px] fas', creatingTasks ? 'fa-circle-notch fa-spin' : 'fa-play']"></i>
            Start
          </button>
        </div>
      </div>
    </div>

    <!-- Team view -->
    <div class="flex-1 min-h-0 overflow-y-auto px-2 py-2 space-y-1">
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
          <div class="section-label px-2 pt-1 pb-1.5">Lead thread</div>
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
                  {{ lead.title || 'Lead thread' }}
                </div>
                <div class="flex items-center gap-1.5 text-[10px] text-blue-950/40 dark:text-white/40">
                  <span>{{ lead.lastMessagePreview || 'Direct the build from here' }}</span>
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

        <!-- Tasks: dispatched work still in flight -->
        <div class="section-label px-2 pt-3 pb-1.5">Tasks</div>
        <template v-if="taskFeed.length > 0">
          <InstanceCard
            v-for="instance in taskFeed"
            :key="instance.id"
            :instance="instance"
            :is-active="instance.id === store.activeInstanceId"
            @select="handleSelect(instance.id)"
            @archive="handleArchive(instance.id)"
            @delete="handleDelete(instance.id)"
            @rename="handleRename(instance.id, $event)"
          />
        </template>
        <div v-else class="px-2 pb-1 text-[11px] text-blue-950/35 dark:text-white/30">
          No tasks running — dispatch one with the + button.
        </div>

        <!-- Review inbox: finished tasks whose drafts await accept/dismiss -->
        <template v-if="reviewGroups.length > 0 || reviewError">
          <div class="section-label px-2 pt-3 pb-1.5">Review inbox</div>
          <div
            v-if="reviewError"
            class="flex items-start gap-2 rounded-lg border border-red-200/70 dark:border-red-400/20 bg-red-50/70 dark:bg-red-500/[0.06] px-2.5 py-1.5 mb-1"
          >
            <p class="flex-1 min-w-0 text-[11px] leading-snug text-red-700 dark:text-red-300 break-words">
              {{ reviewError }}
            </p>
            <button
              type="button"
              aria-label="Dismiss error"
              class="shrink-0 text-red-400 hover:text-red-600 dark:text-red-300/60 dark:hover:text-red-300 transition-colors"
              @click="reviewError = null"
            >
              <i class="fas fa-times text-[10px]"></i>
            </button>
          </div>

          <template v-for="group in reviewGroups" :key="group[0]!.id">
            <!-- Best-of-N: sibling drafts compare side by side -->
            <div
              v-if="group.length > 1"
              class="grid gap-1.5 mb-1"
              :class="group.length >= 3 ? 'grid-cols-3' : 'grid-cols-2'"
            >
              <div
                v-for="(instance, i) in group"
                :key="instance.id"
                class="review-card rounded-lg border border-blue-100 dark:border-white/[0.06] bg-blue-50/40 dark:bg-white/[0.02] px-2 py-1.5 cursor-pointer hover:bg-blue-50 dark:hover:bg-white/[0.05] transition-colors"
                @click="handleSelect(instance.id)"
              >
                <div class="flex items-center justify-between gap-1">
                  <span class="text-[10px] font-semibold uppercase tracking-wider text-blue-950/50 dark:text-white/50">
                    Draft {{ draftLetter(i) }}
                  </span>
                  <span
                    v-if="instance.hasUnread"
                    class="shrink-0 w-1.5 h-1.5 rounded-full bg-blue-950 dark:bg-[#f3ede2]"
                    title="Finished while you were away"
                  ></span>
                </div>
                <div class="mt-1 text-[10px] text-blue-950/45 dark:text-white/40 space-y-0.5">
                  <div v-if="filesChangedCount(instance) !== null" class="truncate">
                    <i class="fas fa-file-pen text-[8px] mr-1"></i>{{ filesChangedCount(instance) }} {{ filesChangedCount(instance) === 1 ? 'file' : 'files' }}
                  </div>
                  <div v-else class="line-clamp-2 break-words">{{ reviewPreview(instance) }}</div>
                  <div v-if="typeof instance.totalTokens === 'number' && instance.totalTokens > 0">
                    {{ formatTokens(instance.totalTokens) }} tokens
                  </div>
                </div>
                <div class="flex flex-col gap-1 mt-1.5" @click.stop>
                  <button
                    type="button"
                    :disabled="resolvingId !== null"
                    class="btn-accept w-full rounded-full px-2 py-1 text-[10px] font-semibold text-[#fdf9f2] dark:text-blue-950 transition-all duration-200 disabled:opacity-50"
                    @click="handleAccept(instance)"
                  >
                    <i v-if="resolvingId === instance.id" class="fas fa-circle-notch fa-spin text-[9px]"></i>
                    <span v-else>Accept</span>
                  </button>
                  <button
                    type="button"
                    :disabled="resolvingId !== null"
                    class="btn-ghost w-full rounded-full px-2 py-1 text-[10px] font-medium transition-colors disabled:opacity-50"
                    @click="handleDismiss(instance)"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </div>

            <!-- Single-draft task -->
            <div
              v-else
              class="review-card rounded-lg border border-blue-100 dark:border-white/[0.06] bg-blue-50/40 dark:bg-white/[0.02] px-2.5 py-2 mb-1 cursor-pointer hover:bg-blue-50 dark:hover:bg-white/[0.05] transition-colors"
              @click="handleSelect(group[0]!.id)"
            >
              <div class="flex items-start gap-2">
                <div class="flex-1 min-w-0">
                  <div class="text-xs font-medium text-blue-950/85 dark:text-white/85 truncate">
                    {{ group[0]!.title || 'Untitled task' }}
                  </div>
                  <p class="text-[10px] text-blue-950/45 dark:text-white/40 line-clamp-2 mt-0.5 break-words">
                    {{ reviewPreview(group[0]!) }}
                  </p>
                </div>
                <span
                  v-if="group[0]!.hasUnread"
                  class="shrink-0 w-1.5 h-1.5 mt-1 rounded-full bg-blue-950 dark:bg-[#f3ede2]"
                  title="Finished while you were away"
                ></span>
              </div>
              <div class="flex items-center gap-1.5 mt-1 text-[10px] text-blue-950/40 dark:text-white/40">
                <span v-if="filesChangedCount(group[0]!) !== null">
                  <i class="fas fa-file-pen text-[8px] mr-1"></i>{{ filesChangedCount(group[0]!) }} {{ filesChangedCount(group[0]!) === 1 ? 'file' : 'files' }} changed
                </span>
                <span v-if="typeof group[0]!.totalTokens === 'number' && group[0]!.totalTokens > 0">
                  · {{ formatTokens(group[0]!.totalTokens) }} tokens
                </span>
              </div>
              <div class="flex items-center gap-1.5 mt-2" @click.stop>
                <button
                  type="button"
                  :disabled="resolvingId !== null"
                  class="btn-accept flex-1 rounded-full px-2.5 py-1 text-[11px] font-semibold text-[#fdf9f2] dark:text-blue-950 transition-all duration-200 disabled:opacity-50"
                  @click="handleAccept(group[0]!)"
                >
                  <i v-if="resolvingId === group[0]!.id" class="fas fa-circle-notch fa-spin text-[10px]"></i>
                  <span v-else>Accept</span>
                </button>
                <button
                  type="button"
                  :disabled="resolvingId !== null"
                  class="btn-ghost flex-1 rounded-full px-2.5 py-1 text-[11px] font-medium transition-colors disabled:opacity-50"
                  @click="handleDismiss(group[0]!)"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </template>
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
              @archive="handleArchive(instance.id)"
              @unarchive="handleUnarchive(instance.id)"
              @delete="handleDelete(instance.id)"
              @rename="handleRename(instance.id, $event)"
            />
          </template>
        </template>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'
import type { AgentInstance } from '../../../types/services'
import { useAgentStore } from '../../../stores/agentStore'
import { useUsageStore, formatResetTime } from '@/shared/stores/usage'
import { useConfirm } from '../../../composables/useConfirm'
import InstanceCard from '../../molecules/sidebar/AgentInstanceCard.vue'

const props = defineProps<{
  /** Workspace.handlePrompt — dispatches a prompt onto a specific instance
   *  through the queued-prompt-safe streaming path. */
  onDispatchTask?: (prompt: string, targetInstanceId: string) => void | Promise<void>
}>()

const emit = defineEmits<{
  (e: 'collapse'): void
  /** An instance was clicked — the workspace flips the sidebar to chat. */
  (e: 'select', instanceId: string): void
  /** A task merge landed — the workspace refreshes files/versions/preview. */
  (e: 'accepted'): void
}>()

const store = useAgentStore()
const showHistory = ref(false)
const { confirm } = useConfirm()

const lead = computed(() => store.leadInstance)
const leadVisible = computed(() => !!lead.value)
// taskFeedInstances is already newest-first
const taskFeed = computed(() => store.taskFeedInstances)
const history = computed(() => store.historyInstances)

/** Ready tasks grouped by variant_group: best-of-N siblings render as
 *  side-by-side draft columns, everything else as single cards. */
const reviewGroups = computed<AgentInstance[][]>(() => {
  const groups: AgentInstance[][] = []
  const byGroup = new Map<string, AgentInstance[]>()
  for (const instance of store.reviewInboxInstances) {
    if (instance.variantGroup) {
      let group = byGroup.get(instance.variantGroup)
      if (!group) {
        group = []
        byGroup.set(instance.variantGroup, group)
        groups.push(group)
      }
      group.push(instance)
    } else {
      groups.push([instance])
    }
  }
  return groups
})

function draftLetter(index: number): string {
  return String.fromCharCode(65 + index) // A, B, C
}

/** How many files a ready task changed, from its last assistant reply's
 *  metadata — null (unknown) when its messages were never loaded. */
function filesChangedCount(instance: AgentInstance): number | null {
  if (!instance.messagesLoaded) return null
  for (let i = instance.conversation.length - 1; i >= 0; i--) {
    const message = instance.conversation[i]
    if (message?.role === 'assistant' && message.filesChanged?.length) {
      return message.filesChanged.length
    }
  }
  return null
}

function reviewPreview(instance: AgentInstance): string {
  return instance.lastMessagePreview || instance.title || 'Finished task'
}

/** Compact token count: 850, 12.3k, 2M (same recipe as the instance card). */
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

// --- New task dispatch -------------------------------------------------

const showNewTask = ref(false)
const taskPrompt = ref('')
const taskVariants = ref(1)
const taskInput = ref<HTMLTextAreaElement | null>(null)
const creatingTasks = ref(false)
const taskError = ref<string | null>(null)
const usageStore = useUsageStore()

async function toggleNewTask() {
  showNewTask.value = !showNewTask.value
  if (showNewTask.value) {
    await nextTick()
    taskInput.value?.focus()
  }
}

function closeNewTask() {
  showNewTask.value = false
}

async function submitNewTask() {
  const promptText = taskPrompt.value.trim()
  if (!promptText || creatingTasks.value) return
  const parentId = lead.value?.conversationId ?? null
  // One uuid ties the N sibling drafts together for the review inbox.
  const variantGroup = crypto.randomUUID()
  const count = Math.min(3, Math.max(1, taskVariants.value))
  creatingTasks.value = true
  taskError.value = null
  try {
    // The runs would be refused 429 pre-stream anyway; checking first avoids
    // creating N task conversations that would sit idle in the feed forever.
    await usageStore.fetchUsage()
    if (usageStore.exceededWindow) {
      const window = usageStore.exceededWindow === '5h'
        ? usageStore.fiveHour
        : usageStore.weekly
      const resetsAt = formatResetTime(window?.resetsAt ?? null)
      taskError.value = resetsAt
        ? `Usage limit reached — resets ${resetsAt}. Upgrade your plan for a higher limit.`
        : 'Usage limit reached — usage frees up as older activity ages out of the window. Upgrade your plan for a higher limit.'
      return
    }
    for (let i = 0; i < count; i++) {
      const instance = await store.createInstance({
        kind: 'task',
        parentId,
        variantGroup,
        activate: false,
      })
      // Fire the run without awaiting completion: each task edits its own
      // worktree, so the runs parallelize server-side.
      if (instance && props.onDispatchTask) {
        void props.onDispatchTask(promptText, instance.id)
      }
    }
    taskPrompt.value = ''
    showNewTask.value = false
  } catch (e) {
    // Creation failed (network, backend error): keep the form open with the
    // typed prompt so the dispatch can be retried.
    taskError.value = e instanceof Error && e.message
      ? e.message
      : 'Could not start the task — try again.'
  } finally {
    creatingTasks.value = false
  }
}

// --- Review inbox (accept / dismiss) ------------------------------------

const resolvingId = ref<string | null>(null)
const reviewError = ref<string | null>(null)

/** Other still-ready drafts from the same variant group. */
function readySiblings(instance: AgentInstance): AgentInstance[] {
  if (!instance.variantGroup) return []
  return store.reviewInboxInstances.filter(
    i => i.id !== instance.id && i.variantGroup === instance.variantGroup
  )
}

function describeReviewError(e: unknown): string {
  const response = (e as any)?.response
  if (response?.status === 409 && response?.data?.error === 'merge_conflict') {
    const detail = response.data.detail
    return detail
      ? `Merge conflict — this draft no longer applies cleanly: ${detail}`
      : 'Merge conflict — this draft no longer applies cleanly to your app.'
  }
  if (response?.status === 409 && response?.data?.error === 'stale_base') {
    return 'Your project was restored to an earlier version after this draft was made, so accepting it would undo that restore. Dismiss it and dispatch a fresh task.'
  }
  if (response?.status === 409 && response?.data?.error === 'already_accepted') {
    return 'This draft was already accepted — its changes are part of your app.'
  }
  if (response?.status === 409) {
    return 'The agent is still working on this project — wait for it to finish or stop it.'
  }
  return e instanceof Error && e.message ? e.message : 'Something went wrong — try again.'
}

async function handleAccept(instance: AgentInstance) {
  if (resolvingId.value) return
  const name = instance.title || 'this draft'
  const siblings = readySiblings(instance)
  const confirmed = await confirm({
    title: 'Accept This Draft',
    message: siblings.length > 0
      ? `Merge "${name}" into your app? Its changes become part of your project — you'll then be asked whether to dismiss the ${siblings.length === 1 ? 'other draft' : 'other drafts'}.`
      : `Merge "${name}" into your app? Its changes become part of your project.`,
    confirmText: 'Accept',
    cancelText: 'Cancel',
    type: 'info'
  })
  if (!confirmed) return
  reviewError.value = null
  resolvingId.value = instance.id
  try {
    await store.acceptTaskInstance(instance.id)
    emit('accepted')
  } catch (e) {
    reviewError.value = describeReviewError(e)
    return
  } finally {
    resolvingId.value = null
  }

  // Best-of-N: the winner is in — offer to clear the losing drafts.
  if (siblings.length > 0) {
    const dismissSiblings = await confirm({
      title: 'Dismiss The Other Drafts?',
      message: `This task produced ${siblings.length + 1} drafts and you accepted one. Dismiss the ${siblings.length === 1 ? 'other draft' : `other ${siblings.length} drafts`}? Their changes are discarded.`,
      confirmText: 'Dismiss drafts',
      cancelText: 'Keep them',
      type: 'warning'
    })
    if (dismissSiblings) {
      for (const sibling of siblings) {
        try {
          await store.dismissTaskInstance(sibling.id)
        } catch (e) {
          reviewError.value = describeReviewError(e)
        }
      }
    }
  }
}

async function handleDismiss(instance: AgentInstance) {
  if (resolvingId.value) return
  const name = instance.title || 'this draft'
  const confirmed = await confirm({
    title: 'Dismiss This Draft',
    message: `Dismiss "${name}"? Its changes are discarded and never touch your app. The conversation stays in History.`,
    confirmText: 'Dismiss',
    cancelText: 'Cancel',
    type: 'warning'
  })
  if (!confirmed) return
  reviewError.value = null
  resolvingId.value = instance.id
  try {
    await store.dismissTaskInstance(instance.id)
  } catch (e) {
    reviewError.value = describeReviewError(e)
  } finally {
    resolvingId.value = null
  }
}

// --- Shared instance actions --------------------------------------------

async function handleSelect(id: string) {
  emit('select', id)
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
  const isRunning = !!instance?.isProcessing
  const confirmed = await confirm({
    title: 'Delete Agent Instance',
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
    reviewError.value = describeReviewError(e)
  }
}

async function handleRename(id: string, title: string) {
  await store.renameInstance(id, title)
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
