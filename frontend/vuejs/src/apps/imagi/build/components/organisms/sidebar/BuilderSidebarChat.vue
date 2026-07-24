<template>
  <div v-if="!isCollapsed" class="flex flex-col h-full bg-white dark:bg-[#0a0a0a] transition-colors duration-300">
    <!-- Header: who you're talking to, and a way over to the agents. There is
         only one thread the user drives, so it is simply "Main agent" — no
         conversation name to track. A subagent's read-only thread keeps its
         own name and a muted mark, which is how you tell the two apart at a
         glance. Version restores live inline in the transcript (the
         per-message checkpoint chips), so the header carries no history
         controls. -->
    <WorkspacePaneHeader
      :icon="isTaskThread ? 'fas fa-robot' : 'fas fa-comments'"
      :tone="isTaskThread ? 'muted' : 'primary'"
      :title="headerTitle"
      :status="headerStatus"
      :live="!!activeInstance?.isProcessing"
      switch-icon="fas fa-layer-group"
      switch-label="Agents"
      :switch-count="store.activeAgentInstances.length"
      switch-direction="forward"
      @switch="$emit('toggleManager')"
    />

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
        :can-restore="canRestoreCheckpoints"
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
        </div>
      </div>

      <!-- A background task's thread is read-only: it is driven by the main
           thread (dispatch, and answers relayed from the check-in queue), so
           there is no composer here — just a way back. -->
      <div v-if="isTaskThread" class="px-2 pt-1 pb-3">
        <div class="rounded-2xl border border-blue-950/[0.08] dark:border-white/[0.14] bg-blue-50/40 dark:bg-white/[0.03] px-3 py-2.5">
          <p class="text-[11px] leading-snug text-blue-950/60 dark:text-white/55">
            This agent is working in the background. You direct it from your main
            thread — its results and questions arrive there.
          </p>
          <button
            type="button"
            class="btn-back-to-lead mt-2 w-full rounded-full px-3 py-1.5 text-[11px] font-semibold text-[#fdf9f2] dark:text-blue-950 transition-all duration-200"
            @click="goToLead"
          >
            Back to main thread
          </button>
        </div>
      </div>

      <div v-else class="px-2 pt-1 pb-3">
        <!-- Check-in queue: background agents reporting back, one at a time -->
        <CheckInQueue
          v-if="isLeadThread"
          :queue="store.checkIns"
          :busy="resolvingCheckIn"
          @accept="emit('check-in-accept', $event)"
          @dismiss="emit('check-in-dismiss', $event)"
          @answer="onAnswerCheckIn"
          @skip="onSkipCheckIn"
          @view="onViewCheckIn"
        />

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
import { useUsageStore, formatResetTime } from '@/shared/stores/usage'
import { ChatConversation } from '../../organisms/chat'
import CheckInQueue from '../../molecules/sidebar/CheckInQueue.vue'
import WorkspacePaneHeader from '../../molecules/sidebar/WorkspacePaneHeader.vue'
import type { AIMessage, AIModel } from '../../../types/index'
import type { CheckInDto, ReasoningEffort, ReasoningEffortOption } from '../../../types/services'
import { REASONING_EFFORTS } from '../../../types/services'

// Props
const props = defineProps<{
  selectedApp: any
  onPromptSubmit: (prompt: string) => Promise<void>
  onModelSelect: (modelId: string) => Promise<void>
  onEffortSelect: (effort: ReasoningEffort) => Promise<void>
  isCollapsed?: boolean
  /** An accept/dismiss from the check-in queue is in flight */
  resolvingCheckIn?: boolean
}>()

const emit = defineEmits<{
  (e: 'toggleManager'): void
  (e: 'stop'): void
  (e: 'restore-checkpoint', message: AIMessage): void
  /** Merge a finished background task's work into the app */
  (e: 'check-in-accept', checkIn: CheckInDto): void
  /** Discard a finished background task's work */
  (e: 'check-in-dismiss', checkIn: CheckInDto): void
}>()

const store = useAgentStore()
const activeInstance = computed(() => store.activeInstance)
const prompt = ref('')
const promptTextarea = ref<HTMLTextAreaElement | null>(null)

// The user drives everything from the lead thread; a task's thread is a
// read-only record of what a background subagent did.
const isTaskThread = computed(() => activeInstance.value?.kind === 'task')
const isLeadThread = computed(() => activeInstance.value?.kind === 'lead')

// The main thread is always just "the main agent" — its conversation name is
// never surfaced, so there is nothing for the user to name or keep track of.
// Subagent threads show their own name so it is obvious which one is open.
const headerTitle = computed(() =>
  isTaskThread.value ? (activeInstance.value?.title || 'Background agent') : 'Main agent'
)

/** The header's second line: what this thread is doing right now. On the main
 *  thread the queue takes precedence — agents waiting on you is the thing you
 *  most need to know before typing. */
const headerStatus = computed(() => {
  const instance = activeInstance.value
  if (instance?.isProcessing) return instance.statusText || 'Working…'
  // No "background agent" prefix: the muted mark and the note above the
  // composer already say that, and the sidebar is too narrow to spend
  // characters twice. These match the manager's card labels word for word.
  if (isTaskThread.value) {
    switch (instance?.reviewStatus) {
      case 'input': return 'Asked you a question'
      case 'ready': return 'Finished — waiting on you'
      case 'accepted': return 'Added to your app'
      case 'dismissed': return 'Discarded'
      default: return 'Read only'
    }
  }
  const waiting = store.checkIns.length
  if (waiting > 0) {
    return `${waiting} ${waiting === 1 ? 'agent is' : 'agents are'} waiting on you`
  }
  return 'Ready when you are'
})

async function goToLead() {
  const lead = store.leadInstance
  if (lead) await store.switchInstance(lead.id)
}

/** The answer restarts the subagent in the background — the user stays here. */
function onAnswerCheckIn(checkIn: CheckInDto, answer: string) {
  store.answerCheckIn(checkIn, answer)
}

/** Clear an entry the user has dealt with (or wants out of the way). */
function onSkipCheckIn(checkIn: CheckInDto) {
  void store.resolveCheckIn(checkIn.id)
}

/** Open the task's read-only thread to see what it actually did. */
async function onViewCheckIn(checkIn: CheckInDto) {
  const instance = store.instances.find(i => i.conversationId === checkIn.task.id)
  if (instance) await store.switchInstance(instance.id)
}

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

function onDocMousedown(e: MouseEvent) {
  const target = e.target as Node
  // The toggle buttons count as "inside": closing on their mousedown would
  // make the follow-up click toggle the menu straight back open.
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
    { key: '5h', label: '5-hour limit', win: usageStore.fiveHour, percent: usageStore.fiveHourPercent },
    { key: 'week', label: 'Weekly limit', win: usageStore.weekly, percent: usageStore.weeklyPercent },
  ]
  return rows.map(({ key, label, win, percent }) => ({
    key,
    label,
    percent,
    // Just the percentage used — no raw token counts (matches Claude Code's
    // 5-hour / weekly session limits). Unknown usage stays an em-dash.
    usedText: percent !== null ? `${percent}% used` : '—',
    resetsAt: formatResetTime(win?.resetsAt ?? null),
  }))
})

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

/* Back-to-main-thread button on a read-only task thread — same navy ink
   recipe as the composer's send button */
.btn-back-to-lead {
  background: theme('colors.blue.950');
  box-shadow:
    0 1px 2px rgba(23, 37, 84, 0.2),
    0 3px 8px -2px rgba(23, 37, 84, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.btn-back-to-lead:hover {
  background: theme('colors.blue.900');
}

.dark .btn-back-to-lead {
  background: #f3ede2;
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 3px 8px -2px rgba(0, 0, 0, 0.45);
}

.dark .btn-back-to-lead:hover {
  background: #ffffff;
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
