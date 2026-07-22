<template>
  <div v-if="!isCollapsed" class="flex flex-col h-full bg-white dark:bg-[#0a0a0a] border-r border-blue-950/[0.08] dark:border-white/[0.14] transition-colors duration-300">
    <!-- Header: manager toggle + instance title. Relative so the version
         dropdown can anchor to the full header width — the sidebar clips
         overflow, so a narrow panel can't fit it anchored to the button. -->
    <div class="shrink-0 relative flex items-center gap-2 px-3 py-2 border-b border-blue-950/[0.08] dark:border-white/[0.14]">
      <div class="relative group max-md:hidden">
        <button
          class="flex items-center justify-center w-8 h-8 rounded-md text-blue-950/60 dark:text-blue-100/65 hover:bg-blue-50 dark:hover:bg-white/[0.08] hover:text-blue-950 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
          @click="$emit('toggleManager')"
        >
          <i class="fas fa-layer-group text-sm"></i>
        </button>
        <div
          class="pointer-events-none absolute left-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-blue-950 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-blue-950 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
        >
          Show agent manager
        </div>
      </div>
      <div class="flex-1 min-w-0 text-xs font-semibold text-blue-950/80 dark:text-blue-100/85 truncate">
        {{ activeInstance?.title || 'New instance' }}
      </div>

      <!-- Version history toggle -->
      <div ref="historyRoot" class="relative group shrink-0">
        <button
          :class="[
            'flex items-center justify-center w-8 h-8 rounded-md transition-colors duration-200',
            historyOpen
              ? 'bg-blue-50 dark:bg-white/[0.08] text-blue-950 dark:text-white'
              : 'text-blue-950/60 dark:text-white/60 hover:bg-blue-50 dark:hover:bg-white/[0.08] hover:text-blue-950 dark:hover:text-white'
          ]"
          @click="toggleHistory"
        >
          <i class="fas fa-clock-rotate-left text-sm"></i>
        </button>
        <div
          v-if="!historyOpen"
          class="pointer-events-none absolute right-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-blue-950 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-blue-950 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
        >
          Version history
        </div>
      </div>

      <!-- Version history dropdown (anchored to the header, not the button:
           the sidebar clips overflow, so it must fit the panel's width) -->
      <div
        v-if="historyOpen"
        ref="historyDropdown"
        class="absolute right-2 top-full mt-1 z-50 w-72 max-w-[calc(100%-1rem)] rounded-xl border border-blue-100 dark:border-white/[0.08] bg-white dark:bg-[#0f0f0f] shadow-xl overflow-hidden"
      >
        <div class="px-3 py-2 border-b border-blue-100 dark:border-white/[0.08] text-[11px] font-semibold uppercase tracking-wider text-blue-950/50 dark:text-white/50">
          Version history
        </div>
        <div class="max-h-72 overflow-y-auto py-1">
          <div
            v-if="versionsLoading && !(versionHistory && versionHistory.length)"
            class="flex items-center gap-2 px-3 py-4 text-xs text-blue-950/40 dark:text-white/40"
          >
            <i class="fas fa-circle-notch fa-spin text-[11px]"></i>
            <span>Loading versions…</span>
          </div>
          <div
            v-else-if="!(versionHistory && versionHistory.length)"
            class="px-3 py-4 text-xs text-blue-950/40 dark:text-white/40"
          >
            No versions yet — they appear as your app changes.
          </div>
          <div
            v-for="version in versionHistory"
            :key="version.hash"
            class="flex items-center gap-2 px-3 py-2 hover:bg-blue-50/60 dark:hover:bg-white/[0.04] transition-colors"
          >
            <div class="flex-1 min-w-0">
              <p class="text-xs font-medium text-blue-950/85 dark:text-white/85 truncate" :title="version.message">
                {{ version.message || 'Project update' }}
              </p>
              <p class="text-[10px] text-blue-950/40 dark:text-white/35 truncate">
                {{ version.relative_date || version.date || '' }}
              </p>
            </div>
            <button
              type="button"
              :disabled="anyRunActive"
              :title="anyRunActive ? 'Wait for the agent to finish (or stop it) before restoring' : undefined"
              class="shrink-0 rounded-full border border-blue-200/70 dark:border-white/[0.12] px-2.5 py-1 text-[11px] font-medium text-blue-950/70 dark:text-white/70 hover:bg-blue-950 hover:border-blue-950 hover:text-[#fdf9f2] dark:hover:bg-[#f3ede2] dark:hover:border-[#f3ede2] dark:hover:text-blue-950 transition-colors disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-transparent disabled:hover:border-blue-200/70 dark:disabled:hover:border-white/[0.12] disabled:hover:text-blue-950/70 dark:disabled:hover:text-white/70"
              @click="onRestoreVersion(version)"
            >
              Restore
            </button>
          </div>
        </div>
      </div>

      <div v-if="onCollapseSidebar" class="relative group shrink-0 max-md:hidden">
        <button
          class="flex items-center justify-center w-8 h-8 rounded-md text-blue-950/60 dark:text-blue-100/65 hover:bg-blue-50 dark:hover:bg-white/[0.08] hover:text-blue-950 dark:hover:text-white transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
          @click="onCollapseSidebar()"
        >
          <i class="fas fa-chevron-left text-sm"></i>
        </button>
        <div
          class="pointer-events-none absolute right-0 top-full mt-1.5 z-50 whitespace-nowrap rounded-md bg-blue-950 dark:bg-white/95 px-2 py-1 text-[11px] font-medium text-white dark:text-blue-950 shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-150"
        >
          Collapse sidebar
        </div>
      </div>
    </div>

    <!-- Conversation Area (scrollable) -->
    <div class="flex-1 min-h-0 overflow-hidden flex flex-col">
      <!-- Keyed by instance so switching remounts the conversation: scroll
           position and the pinned-to-bottom state belong to one transcript
           and must not leak into another (a fresh mount lands at the latest
           message). -->
      <ChatConversation
        :key="activeInstance?.id || 'none'"
        :messages="ensureValidMessages(activeInstance?.conversation || [])"
        :is-processing="!!activeInstance?.isProcessing"
        :status-text="activeInstance?.statusText || ''"
        :examples="promptExamples"
        :can-restore="canRestoreCheckpoints"
        @use-example="handleExamplePrompt"
        @restore-checkpoint="emit('restore-checkpoint', $event)"
        class="flex-1"
      />
    </div>

    <!-- Chat Input Section (fixed at bottom). Relative so the usage panel
         can anchor to the full section width — the sidebar clips overflow,
         so a panel anchored to its narrow button couldn't fit. -->
    <div class="shrink-0 relative bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
      <!-- Model slider panel (opens upward above the composer): one slider
           across the three models, faster → smarter -->
      <div
        v-if="modelOpen"
        ref="modelPanel"
        class="absolute bottom-full left-2 right-2 mb-1 z-50 rounded-xl border border-blue-100 dark:border-white/[0.08] bg-white dark:bg-[#0f0f0f] shadow-xl overflow-hidden"
      >
        <div class="flex items-center justify-between gap-2 px-3 py-2 border-b border-blue-100 dark:border-white/[0.08]">
          <span class="text-[11px] font-semibold uppercase tracking-wider text-blue-950/50 dark:text-white/50">
            Model
          </span>
          <span class="text-[11px] font-medium text-blue-950/70 dark:text-white/70 truncate">
            {{ currentModel?.name || '—' }}
          </span>
        </div>
        <div class="px-3 py-3">
          <input
            type="range"
            class="control-slider"
            min="0"
            :max="Math.max(orderedModels.length - 1, 0)"
            step="1"
            :value="modelIndex"
            :disabled="!activeInstance || orderedModels.length < 2"
            aria-label="Model — faster to smarter"
            @input="onModelSlider"
          />
          <div class="flex items-center justify-between mt-1.5 text-[10px] font-semibold uppercase tracking-wider text-blue-950/45 dark:text-white/40">
            <span>Faster</span>
            <span>Smarter</span>
          </div>
          <p class="mt-2 text-[11px] leading-snug text-blue-950/50 dark:text-white/45">
            Smarter models consume your usage faster.
          </p>
        </div>
      </div>

      <!-- Reasoning effort slider panel (opens upward above the composer) -->
      <div
        v-if="effortOpen"
        ref="effortPanel"
        class="absolute bottom-full left-2 right-2 mb-1 z-50 rounded-xl border border-blue-100 dark:border-white/[0.08] bg-white dark:bg-[#0f0f0f] shadow-xl overflow-hidden"
      >
        <div class="flex items-center justify-between gap-2 px-3 py-2 border-b border-blue-100 dark:border-white/[0.08]">
          <span class="text-[11px] font-semibold uppercase tracking-wider text-blue-950/50 dark:text-white/50">
            Reasoning
          </span>
          <span class="text-[11px] font-medium text-blue-950/70 dark:text-white/70 truncate">
            {{ currentEffort?.name || '—' }}
          </span>
        </div>
        <div class="px-3 py-3">
          <input
            type="range"
            class="control-slider"
            min="0"
            :max="Math.max(effortOptions.length - 1, 0)"
            step="1"
            :value="effortIndex"
            :disabled="!activeInstance || effortOptions.length < 2"
            aria-label="Reasoning effort — faster to smarter"
            @input="onEffortSlider"
          />
          <div class="flex items-center justify-between mt-1.5 text-[10px] font-semibold uppercase tracking-wider text-blue-950/45 dark:text-white/40">
            <span>Faster</span>
            <span>Smarter</span>
          </div>
          <p class="mt-2 text-[11px] leading-snug text-blue-950/50 dark:text-white/45">
            More reasoning consumes your usage faster.
          </p>
        </div>
      </div>

      <!-- Usage limits panel (opens upward above the composer) -->
      <div
        v-if="usageOpen"
        ref="usagePanel"
        class="absolute bottom-full left-2 right-2 mb-1 z-50 rounded-xl border border-blue-100 dark:border-white/[0.08] bg-white dark:bg-[#0f0f0f] shadow-xl overflow-hidden"
      >
        <div class="flex items-center justify-between gap-2 px-3 py-2 border-b border-blue-100 dark:border-white/[0.08]">
          <span class="text-[11px] font-semibold uppercase tracking-wider text-blue-950/50 dark:text-white/50">
            Usage
          </span>
          <span class="text-[11px] font-medium text-blue-950/70 dark:text-white/70 truncate">
            {{ usageStore.plan ? `${usageStore.plan.name} plan` : '—' }}
          </span>
        </div>
        <!-- Body scrolls on short viewports (like the version-history list)
             so the panel never grows past the top of the sidebar; the calc
             budget covers the navbar + composer + panel header. -->
        <div class="max-h-[min(20rem,calc(100vh-19rem))] overflow-y-auto">
          <div class="px-3 py-2.5 space-y-3">
            <div v-for="meter in usageMeters" :key="meter.key">
              <div class="flex items-baseline justify-between gap-2">
                <span class="text-[10px] font-semibold uppercase tracking-wider text-blue-950/40 dark:text-white/40">
                  {{ meter.label }}
                </span>
                <!-- Unknown usage shows an em-dash and no bar — never 0% -->
                <span class="text-[11px] font-medium tabular-nums text-blue-950/70 dark:text-white/70">
                  {{ meter.usedText }}
                </span>
              </div>
              <div v-if="meter.percent !== null" class="usage-meter mt-1.5">
                <div class="usage-meter-fill" :style="{ width: `${meter.percent}%` }"></div>
              </div>
              <p v-if="meter.resetsAt" class="mt-1 text-[10px] text-blue-950/40 dark:text-white/35">
                Resets {{ meter.resetsAt }}
              </p>
            </div>
          </div>
          <div v-if="otherPlans.length" class="border-t border-blue-100 dark:border-white/[0.08] px-3 py-2">
            <div class="text-[10px] font-semibold uppercase tracking-wider text-blue-950/40 dark:text-white/40 pb-1.5">
              Other plans
            </div>
            <div
              v-for="plan in otherPlans"
              :key="plan.id"
              class="flex items-center justify-between gap-2 py-0.5"
            >
              <span class="text-[11px] font-medium text-blue-950/75 dark:text-white/70">{{ plan.name }}</span>
              <span class="text-[10px] tabular-nums text-blue-950/45 dark:text-white/40">{{ plan.limits }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="px-2 pt-1 pb-3">
        <!-- Queued prompt: one message held while the agent works -->
        <div
          v-if="activeInstance?.queuedPrompt"
          class="flex items-center gap-2 rounded-xl border border-blue-100 dark:border-white/[0.08] bg-blue-50/60 dark:bg-white/[0.04] px-2.5 py-1.5 mb-1.5"
        >
          <i class="fas fa-hourglass-half text-[10px] text-blue-950/40 dark:text-white/40 shrink-0"></i>
          <div class="flex-1 min-w-0">
            <p class="text-[11px] font-medium text-blue-950/75 dark:text-white/70 truncate" :title="activeInstance.queuedPrompt">
              {{ activeInstance.queuedPrompt }}
            </p>
            <p class="text-[10px] text-blue-950/40 dark:text-white/35">Queued — sends when the agent finishes</p>
          </div>
          <button
            type="button"
            title="Cancel queued message"
            aria-label="Cancel queued message"
            class="shrink-0 inline-flex items-center justify-center w-6 h-6 rounded-full text-blue-950/40 dark:text-white/40 hover:bg-blue-100/70 dark:hover:bg-white/[0.08] hover:text-blue-950/70 dark:hover:text-white/70 transition-colors"
            @click="cancelQueuedPrompt"
          >
            <i class="fas fa-times text-[10px]"></i>
          </button>
        </div>

        <!-- Input shell: textarea on top, controls toolbar below -->
        <div class="chat-input-shell rounded-2xl bg-blue-50/40 dark:bg-white/[0.03] border border-blue-950/[0.08] dark:border-white/[0.14] shadow-sm">
          <textarea
            ref="promptTextarea"
            v-model="prompt"
            :placeholder="promptPlaceholder"
            @keydown.enter.exact.prevent="handlePrompt"
            @keydown.enter.shift.exact="() => {}"
            @input="autoResizeTextarea"
            :disabled="!activeInstance"
            rows="4"
            class="chat-textarea w-full bg-transparent text-blue-950 dark:text-white/90 placeholder-blue-950/40 dark:placeholder-blue-100/40 text-sm px-3 pt-3 pb-1 resize-none leading-relaxed"
            style="min-height: 92px; max-height: 240px;"
          ></textarea>

          <!-- Controls toolbar: model + reasoning side by side on the left, send pinned right -->
          <div class="flex items-center justify-between gap-2 px-2 pb-2 pt-1">
            <!-- min-w-0 + overflow-hidden lets the chips truncate rather than
                 shove the send button off the edge on a narrow sidebar. -->
            <div class="flex flex-nowrap items-center gap-1 min-w-0 flex-1 overflow-hidden">
              <!-- Model: opens a slider from faster → smarter across the three models -->
              <div ref="modelRoot" class="min-w-0">
                <button
                  type="button"
                  title="Model — slide from faster to smarter"
                  aria-label="Model"
                  :aria-expanded="modelOpen"
                  :disabled="!activeInstance"
                  class="control-chip"
                  :class="{ 'control-chip--active': modelOpen }"
                  @click="toggleModel"
                >
                  <i class="fas fa-microchip control-chip-icon"></i>
                  <span class="control-chip-label">{{ modelShortName(activeInstance?.selectedModelId) }}</span>
                  <i class="fas fa-chevron-down control-chip-caret" :class="{ 'rotate-180': modelOpen }"></i>
                </button>
              </div>

              <!-- Reasoning effort: same faster → smarter slider -->
              <div ref="effortRoot" class="min-w-0">
                <button
                  type="button"
                  title="Reasoning effort — slide from faster to smarter"
                  aria-label="Reasoning effort"
                  :aria-expanded="effortOpen"
                  :disabled="!activeInstance"
                  class="control-chip"
                  :class="{ 'control-chip--active': effortOpen }"
                  @click="toggleEffort"
                >
                  <i class="fas fa-brain control-chip-icon"></i>
                  <span class="control-chip-label">{{ effortLabel(activeInstance?.selectedEffort) }}</span>
                  <i class="fas fa-chevron-down control-chip-caret" :class="{ 'rotate-180': effortOpen }"></i>
                </button>
              </div>

              <!-- Usage limits (button + anchored panel above) -->
              <div ref="usageRoot" class="shrink-0">
                <button
                  type="button"
                  title="Plan usage limits"
                  aria-label="Usage limits"
                  :aria-expanded="usageOpen"
                  class="control-chip"
                  :class="{ 'control-chip--active': usageOpen }"
                  @click="toggleUsage"
                >
                  <i class="fas fa-gauge-high control-chip-icon"></i>
                  <span class="control-chip-label">Usage</span>
                </button>
              </div>
            </div>

            <!-- Stop Button (replaces send while a run is in flight) -->
            <button
              v-if="activeInstance?.isProcessing"
              @click="handleStopClick"
              aria-label="Stop agent"
              title="Stop agent"
              class="btn-send btn-send--active flex shrink-0 items-center justify-center w-9 h-9 rounded-full transition-all duration-300 text-[#fdf9f2] dark:text-blue-950"
            >
              <i class="fas fa-stop text-sm"></i>
            </button>

            <!-- Send Button -->
            <button
              v-else
              @click="handlePrompt"
              :disabled="!prompt.trim() || !activeInstance"
              aria-label="Send message"
              class="btn-send flex shrink-0 items-center justify-center w-9 h-9 rounded-full transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
              :class="prompt.trim() && activeInstance
                ? 'btn-send--active text-[#fdf9f2] dark:text-blue-950'
                : 'bg-blue-100/60 dark:bg-white/[0.05] text-blue-950/40 dark:text-blue-100/40 cursor-not-allowed border border-blue-200/70 dark:border-white/[0.12] shadow-sm'"
            >
              <i class="fas fa-arrow-up text-sm"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
import { useUsageStore, formatCompactTokens, formatResetTime } from '@/shared/stores/usage'
import { useConfirm } from '../../../composables/useConfirm'
import { ChatConversation } from '../../organisms/chat'
import type { AIMessage, AIModel } from '../../../types/index'
import type { ReasoningEffort, ReasoningEffortOption } from '../../../types/services'
import { REASONING_EFFORTS } from '../../../types/services'

/** One commit from the project's version history (backend versions shape). */
interface VersionEntry {
  hash: string
  message?: string
  author?: string
  date?: string
  relative_date?: string
}

// Props
const props = defineProps<{
  selectedApp: any
  onPromptSubmit: (prompt: string) => Promise<void>
  onModelSelect: (modelId: string) => Promise<void>
  onEffortSelect: (effort: ReasoningEffort) => Promise<void>
  onExamplePrompt: (example: string) => void
  onCollapseSidebar?: () => void
  isCollapsed?: boolean
  versionHistory?: VersionEntry[]
  versionsLoading?: boolean
  promptExamples?: string[]
}>()

const emit = defineEmits<{
  (e: 'toggleManager'): void
  (e: 'stop'): void
  (e: 'load-versions'): void
  (e: 'restore-version', hash: string): void
  (e: 'restore-checkpoint', message: AIMessage): void
}>()

const store = useAgentStore()
const activeInstance = computed(() => store.activeInstance)
const prompt = ref('')
const promptTextarea = ref<HTMLTextAreaElement | null>(null)

// --- Version history dropdown ---

const { confirm } = useConfirm()
const historyOpen = ref(false)
const historyRoot = ref<HTMLElement | null>(null)
const historyDropdown = ref<HTMLElement | null>(null)

// Restores git-reset the canonical working tree. Only canonical-tree
// (chat/lead) runs write to it — kind='task' runs edit their own git
// worktrees — so restores stay enabled while tasks run in parallel and are
// blocked only by a live canonical run (the workspace and backend enforce
// the same rule as backstops).
const anyRunActive = computed(() =>
  store.instances.some(i => i.kind !== 'task' && i.isProcessing)
)

// Restore chips belong to canonical-tree threads: a task's edits live in its
// worktree and land (or not) through the review inbox, so its transcript
// never offers canonical-timeline restores.
const canRestoreCheckpoints = computed(() =>
  activeInstance.value?.kind !== 'task' && !anyRunActive.value
)

function toggleHistory() {
  historyOpen.value = !historyOpen.value
  // The list may be stale (the agent commits as it works); refresh on open.
  if (historyOpen.value) emit('load-versions')
}

async function onRestoreVersion(version: VersionEntry) {
  const confirmed = await confirm({
    title: 'Restore This Version',
    message: 'Restore your app to this version? Current work stays in history.',
    confirmText: 'Restore',
    cancelText: 'Cancel',
    type: 'warning'
  })
  if (!confirmed) return
  historyOpen.value = false
  emit('restore-version', version.hash)
}

function onDocMousedown(e: MouseEvent) {
  const target = e.target as Node
  // The toggle buttons count as "inside": closing on their mousedown would
  // make the follow-up click toggle the menu straight back open.
  if (
    historyOpen.value &&
    !historyRoot.value?.contains(target) &&
    !historyDropdown.value?.contains(target)
  ) {
    historyOpen.value = false
  }
  if (
    usageOpen.value &&
    !usageRoot.value?.contains(target) &&
    !usagePanel.value?.contains(target)
  ) {
    usageOpen.value = false
  }
  if (
    modelOpen.value &&
    !modelRoot.value?.contains(target) &&
    !modelPanel.value?.contains(target)
  ) {
    modelOpen.value = false
  }
  if (
    effortOpen.value &&
    !effortRoot.value?.contains(target) &&
    !effortPanel.value?.contains(target)
  ) {
    effortOpen.value = false
  }
}

onMounted(() => document.addEventListener('mousedown', onDocMousedown))
onBeforeUnmount(() => document.removeEventListener('mousedown', onDocMousedown))

// --- Usage limits dropdown (plan + rolling windows) ---

const usageStore = useUsageStore()
const usageOpen = ref(false)
const usageRoot = ref<HTMLElement | null>(null)
const usagePanel = ref<HTMLElement | null>(null)

// --- Model + reasoning slider popovers ---

const modelOpen = ref(false)
const modelRoot = ref<HTMLElement | null>(null)
const modelPanel = ref<HTMLElement | null>(null)
const effortOpen = ref(false)
const effortRoot = ref<HTMLElement | null>(null)
const effortPanel = ref<HTMLElement | null>(null)

// The three controls share the space above the composer, so only one panel
// opens at a time.
function closeControlPanels() {
  usageOpen.value = false
  modelOpen.value = false
  effortOpen.value = false
}

function toggleUsage() {
  const next = !usageOpen.value
  closeControlPanels()
  usageOpen.value = next
  // Windows drift as older activity ages out; refresh on open.
  if (usageOpen.value) void usageStore.fetchUsage()
}

function toggleModel() {
  const next = !modelOpen.value
  closeControlPanels()
  modelOpen.value = next
}

function toggleEffort() {
  const next = !effortOpen.value
  closeControlPanels()
  effortOpen.value = next
}

/** The two rolling-window meters. Missing data renders as unknown (em-dash,
 *  no bar) — never as 0%. */
const usageMeters = computed(() => {
  const rows = [
    { key: '5h', label: '5-hour window', win: usageStore.fiveHour, percent: usageStore.fiveHourPercent },
    { key: 'week', label: 'Weekly window', win: usageStore.weekly, percent: usageStore.weeklyPercent },
  ]
  return rows.map(({ key, label, win, percent }) => ({
    key,
    label,
    percent,
    usedText: win && win.used !== null && win.limit !== null
      ? `${formatCompactTokens(win.used)} / ${formatCompactTokens(win.limit)}${percent !== null ? ` · ${percent}%` : ''}`
      : '—',
    resetsAt: formatResetTime(win?.resetsAt ?? null),
  }))
})

/** The plan registry minus the user's own plan, for comparing limits. */
const otherPlans = computed(() =>
  usageStore.plans
    .filter(p => p.id && p.id !== usageStore.plan?.id)
    .map(p => ({
      id: p.id,
      name: p.name,
      limits: p.fiveHourTokens !== null && p.weeklyTokens !== null
        ? `${formatCompactTokens(p.fiveHourTokens)} / 5h · ${formatCompactTokens(p.weeklyTokens)} / wk`
        : '—',
    }))
)

const modelOptions = computed<AIModel[]>(() => {
  const available = (store.availableModels || []).filter(model => model.id.startsWith('gpt-5.6'))
  if (available.length > 0) {
    return available
  }
  return [
    { id: 'gpt-5.6-terra', name: 'GPT 5.6 Terra', provider: 'openai' } as AIModel,
    { id: 'gpt-5.6-sol', name: 'GPT 5.6 Sol', provider: 'openai' } as AIModel,
    { id: 'gpt-5.6-luna', name: 'GPT 5.6 Luna', provider: 'openai' } as AIModel
  ]
})

const effortOptions = computed<ReasoningEffortOption[]>(() => REASONING_EFFORTS)

// Models ranked faster → smarter (Luna is light/fast, Sol is the flagship) so
// the slider reads left = faster, right = smarter. Unknown ids sort last but
// still appear, so the slider degrades gracefully if the suite changes.
const MODEL_RANK: Record<string, number> = {
  'gpt-5.6-luna': 0,
  'gpt-5.6-terra': 1,
  'gpt-5.6-sol': 2,
}
const orderedModels = computed<AIModel[]>(() =>
  [...modelOptions.value].sort(
    (a, b) => (MODEL_RANK[a.id] ?? 99) - (MODEL_RANK[b.id] ?? 99)
  )
)
const modelIndex = computed(() => {
  const idx = orderedModels.value.findIndex(m => m.id === activeInstance.value?.selectedModelId)
  return idx >= 0 ? idx : 0
})
const currentModel = computed<AIModel | null>(() => orderedModels.value[modelIndex.value] ?? null)

/** The distinctive part of the model name for the compact chip ("Terra"),
 *  dropping the shared "GPT 5.6" prefix. */
function modelShortName(id?: string | null): string {
  const model = orderedModels.value.find(m => m.id === id) ?? currentModel.value
  if (!model) return 'Model'
  return model.name.replace(/^GPT\s*5\.6\s*/i, '').trim() || model.name
}

function onModelSlider(e: Event) {
  const idx = Number((e.target as HTMLInputElement).value)
  const model = orderedModels.value[idx]
  if (model && model.id !== activeInstance.value?.selectedModelId) {
    void handleModelSelect(model.id)
  }
}

// REASONING_EFFORTS is already ordered minimal → xhigh = faster → smarter.
const effortIndex = computed(() => {
  const idx = effortOptions.value.findIndex(
    o => o.id === (activeInstance.value?.selectedEffort ?? 'medium')
  )
  return idx >= 0 ? idx : 0
})
const currentEffort = computed<ReasoningEffortOption | null>(() => effortOptions.value[effortIndex.value] ?? null)

function effortLabel(id?: string | null): string {
  const option = effortOptions.value.find(o => o.id === id) ?? currentEffort.value
  return option?.name ?? 'Reasoning'
}

function onEffortSlider(e: Event) {
  const idx = Number((e.target as HTMLInputElement).value)
  const option = effortOptions.value[idx]
  if (option && option.id !== activeInstance.value?.selectedEffort) {
    void handleEffortSelect(option.id)
  }
}

// Helper to get friendly display name from file path
function getDisplayName(path: string): string {
  if (!path) return ''
  const parts = path.split('/')
  const filename = parts[parts.length - 1] ?? ''
  return filename.replace(/\.(vue|ts|js|tsx|jsx)$/, '')
}

// Helper to determine item kind from path
function getItemKind(path: string): string {
  if (!path) return 'item'
  if (/\/views\//i.test(path)) return 'page'
  if (/\/components\//i.test(path)) return 'block'
  if (/\/stores\//i.test(path)) return 'data store'
  return 'item'
}

const promptPlaceholder = computed(() => 'Ask me to build, edit, or explain anything in your project...')

// Methods
function ensureValidMessages(messages: any[]): AIMessage[] {
  if (!messages || !Array.isArray(messages)) {
    return []
  }
  
  const filteredMessages = messages.filter(m => {
    if (m && m.role === 'system') {
      if (m.content && (
        m.content.includes('Switched to file:') || 
        m.content.includes('Switched to build mode') ||
        m.content.includes('previously selected file')
      )) {
        return false
      }
    }
    return true
  })
  
  const validMessages = filteredMessages
    .filter(m => m && typeof m === 'object' && m.role)
    .map(m => {
      const content = m.content || ''
      const messageId = m.id || `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`
      
      return {
        role: m.role,
        content: content,
        code: m.code || '',
        timestamp: m.timestamp || new Date().toISOString(),
        id: messageId,
        // Run telemetry rides along or the transcript loses its activity
        // feed, plan, files-changed chip and cost caption.
        plan: m.plan,
        activity: m.activity,
        filesChanged: m.filesChanged,
        usage: m.usage,
        dbId: m.dbId,
        checkpoint: m.checkpoint
      }
    }) as AIMessage[]
  
  return validMessages
}

function autoResizeTextarea() {
  if (!promptTextarea.value) return
  promptTextarea.value.style.height = 'auto'
  const scrollHeight = promptTextarea.value.scrollHeight
  const maxHeight = 240
  promptTextarea.value.style.height = `${Math.min(scrollHeight, maxHeight)}px`
}

// After a checkpoint restore, the removed prompt comes back here so the
// user can edit and resend it (the Cursor rewind flow).
function setPromptText(text: string) {
  prompt.value = text
  nextTick(() => {
    autoResizeTextarea()
    promptTextarea.value?.focus()
  })
}

defineExpose({ setPromptText })

async function handlePrompt() {
  if (!prompt.value.trim() || !activeInstance.value) return

  const promptText = prompt.value
  prompt.value = '' // Clear immediately

  // Reset textarea height
  if (promptTextarea.value) {
    promptTextarea.value.style.height = '92px'
  }

  if (activeInstance.value.isProcessing) {
    // Mid-run: hold the message (one per instance — a second submit
    // replaces it) and auto-send when the run finishes.
    store.queuePrompt(activeInstance.value.id, promptText)
    return
  }

  await props.onPromptSubmit(promptText)
}

function cancelQueuedPrompt() {
  if (activeInstance.value) store.clearQueuedPrompt(activeInstance.value.id)
}

function handleStopClick() {
  const instance = activeInstance.value
  // Stop means stop: a queued prompt must not fire into the aborted run's
  // wake, but it shouldn't silently vanish either — hand it back to the
  // input for the user to send or discard.
  if (instance?.queuedPrompt) {
    if (!prompt.value.trim()) prompt.value = instance.queuedPrompt
    store.clearQueuedPrompt(instance.id)
  }
  emit('stop')
}

function handleExamplePrompt(exampleText: string) {
  prompt.value = exampleText
  handlePrompt()
}

async function handleModelSelect(modelId: string) {
  await props.onModelSelect(modelId)
}

async function handleEffortSelect(effort: ReasoningEffort) {
  await props.onEffortSelect(effort)
}
</script>

<style scoped>
/* Input shell wraps the textarea + controls toolbar as one field */
.chat-input-shell {
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.chat-input-shell:focus-within {
  border-color: rgba(59, 130, 246, 0.55);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
}

.dark .chat-input-shell:focus-within {
  border-color: rgba(147, 197, 253, 0.5);
  box-shadow: 0 0 0 3px rgba(147, 197, 253, 0.18);
}

/* Control chip: the compact model / reasoning / usage buttons. Ghost until
   hovered or open, so the input shell stays the focal point. */
.control-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  max-width: 100%;
  padding: 0.3rem 0.55rem;
  border-radius: 0.5rem;
  border: 1px solid transparent;
  background-color: transparent;
  color: rgba(23, 37, 84, 0.75);
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition: background-color 0.18s ease, color 0.18s ease, box-shadow 0.18s ease;
  outline: none;
}

.control-chip:hover:not(:disabled) {
  background-color: rgba(219, 234, 254, 0.5);
  color: rgb(23, 37, 84);
}

.control-chip--active {
  background-color: rgba(219, 234, 254, 0.7);
  color: rgb(23, 37, 84);
}

.control-chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-chip:focus-visible {
  box-shadow: 0 0 0 2px #ffffff, 0 0 0 4px rgba(59, 130, 246, 0.4);
}

.dark .control-chip {
  color: rgba(219, 234, 254, 0.7);
}

.dark .control-chip:hover:not(:disabled) {
  background-color: rgba(255, 255, 255, 0.07);
  color: rgba(255, 255, 255, 0.95);
}

.dark .control-chip--active {
  background-color: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.dark .control-chip:focus-visible {
  box-shadow: 0 0 0 2px #0a0a0a, 0 0 0 4px rgba(147, 197, 253, 0.5);
}

.control-chip-icon {
  font-size: 0.6875rem;
  opacity: 0.75;
  flex-shrink: 0;
}

.control-chip-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.control-chip-caret {
  font-size: 0.5rem;
  opacity: 0.6;
  flex-shrink: 0;
  transition: transform 0.18s ease;
}

/* Faster ↔ smarter slider: navy ink track + thumb (cream in dark), matching
   the primary button system. */
.control-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  border-radius: 9999px;
  background: rgba(23, 37, 84, 0.15);
  outline: none;
  cursor: pointer;
}

.dark .control-slider {
  background: rgba(255, 255, 255, 0.14);
}

.control-slider:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 9999px;
  background: theme('colors.blue.950');
  border: 2px solid #ffffff;
  box-shadow: 0 1px 3px rgba(23, 37, 84, 0.35);
  cursor: pointer;
  transition: transform 0.15s ease;
}

.control-slider::-webkit-slider-thumb:hover {
  transform: scale(1.12);
}

.control-slider::-moz-range-thumb {
  width: 16px;
  height: 16px;
  border-radius: 9999px;
  background: theme('colors.blue.950');
  border: 2px solid #ffffff;
  box-shadow: 0 1px 3px rgba(23, 37, 84, 0.35);
  cursor: pointer;
}

.control-slider:focus-visible::-webkit-slider-thumb {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.35);
}

.control-slider:focus-visible::-moz-range-thumb {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.35);
}

.dark .control-slider::-webkit-slider-thumb {
  background: #f3ede2;
  border-color: #0f0f0f;
}

.dark .control-slider::-moz-range-thumb {
  background: #f3ede2;
  border-color: #0f0f0f;
}

/* Usage-window meter: quiet navy ink bar (cream in dark mode, matching the
   primary button system) */
.usage-meter {
  position: relative;
  height: 0.25rem;
  border-radius: 9999px;
  background: rgba(23, 37, 84, 0.1);
  overflow: hidden;
}

.dark .usage-meter {
  background: rgba(255, 255, 255, 0.12);
}

.usage-meter-fill {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  border-radius: 9999px;
  background: theme('colors.blue.950');
  transition: width 0.3s ease;
}

.dark .usage-meter-fill {
  background: #f3ede2;
}

/* Textarea sits inside the input shell, which owns the border/focus ring */
textarea,
textarea:hover,
textarea:focus,
textarea:focus-visible,
textarea:active {
  outline: 0 !important;
  outline-width: 0 !important;
  outline-style: none !important;
  outline-offset: 0 !important;
  outline-color: transparent !important;
  box-shadow: none !important;
  -webkit-box-shadow: none !important;
  -webkit-tap-highlight-color: transparent !important;
  border: none !important;
  transition: none !important;
}

/* Navy ink send button - matching the site's primary "Start Building" button */
.btn-send {
  transform: translateY(0) translateZ(0);
}

.btn-send--active {
  background: theme('colors.blue.950');
  box-shadow:
    0 1px 2px rgba(23, 37, 84, 0.2),
    0 3px 8px -2px rgba(23, 37, 84, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.btn-send--active:hover {
  background: theme('colors.blue.900');
  box-shadow:
    0 2px 3px rgba(23, 37, 84, 0.22),
    0 5px 12px -2px rgba(23, 37, 84, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.dark .btn-send--active {
  background: #f3ede2;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 3px 8px -2px rgba(0, 0, 0, 0.45);
}

.dark .btn-send--active:hover {
  background: #ffffff;
  box-shadow:
    0 2px 3px rgba(0, 0, 0, 0.4),
    0 5px 12px -2px rgba(0, 0, 0, 0.5);
}

/* Refined minimal scrollbar - matching homepage */
:deep(::-webkit-scrollbar) {
  width: 8px;
}

:deep(::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(::-webkit-scrollbar-thumb) {
  background: rgba(0, 0, 0, 0.12);
  border-radius: 4px;
  transition: background 0.2s ease;
}

:deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(0, 0, 0, 0.2);
}

:root.dark :deep(::-webkit-scrollbar-thumb) {
  background: rgba(255, 255, 255, 0.12);
}

:root.dark :deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(255, 255, 255, 0.2);
}
</style>
