<!--
  AgentComposer.vue — the one text box for talking to an agent.

  The coordinator and every thread are typed to through this same composer:
  the box, the microphone button that turns into a send arrow once there are
  words, the model and reasoning chip, and the usage meter. What differs is
  where the words go, which the pane decides through `submit`: the
  coordinator's next message, or a thread's next turn (steering it).

  Model and effort are the instance's own, so changing them on a thread
  changes that thread only.
-->
<template>
<!-- Chat Input Section (fixed at bottom). Relative so the usage panel
     can anchor to the full section width — the sidebar clips overflow,
     so a panel anchored to its narrow button couldn't fit. -->
<div class="shrink-0 relative bg-canvas transition-colors duration-300">
  <!-- Model + reasoning menu (opens upward above the composer). The
       model is a short list — three tiers, each with what it is for and
       a check on the one in use — and reasoning effort is a four-bar
       meter under it, both running faster → smarter. Each is a radio
       group: one tab stop, arrows move the choice, and every change is
       one idempotent write to the workspace.

       The panels share one popover treatment: a translucent material
       that grows out of the chip that opened it (transform-origin sits
       at the bottom edge), so opening reads as the control unfolding
       rather than a card being dealt onto the pane. -->
  <Transition name="popover">
  <div
    v-if="tuneOpen"
    id="tune-panel"
    ref="tunePanel"
    role="group"
    aria-label="Model and reasoning"
    class="popover absolute bottom-full left-2 right-2 mb-1.5 z-50 overflow-hidden"
    @keydown.escape.stop.prevent="closeTune"
  >
    <!-- Body scrolls on short viewports so the panel never grows past the
         top of the sidebar (the usage panel's recipe). -->
    <div class="iw-scroll max-h-[min(26rem,calc(100vh-19rem))] overflow-y-auto">
      <div class="popover__head flex items-center justify-between gap-2 px-3 py-2">
        <span id="tune-model-heading" class="text-[11px] font-semibold uppercase tracking-wider text-ink/50 dark:text-white/50">
          Model
        </span>
      </div>
      <div
        role="radiogroup"
        aria-labelledby="tune-model-heading"
        class="p-1"
        @keydown="onModelKeydown"
      >
        <button
          v-for="(m, i) in orderedModels"
          :key="m.id"
          ref="modelRows"
          type="button"
          role="radio"
          :aria-checked="i === modelIndex"
          :tabindex="i === modelIndex ? 0 : -1"
          :disabled="!instance"
          class="model-row"
          :class="{ 'model-row--on': i === modelIndex }"
          @click="pickModel(m.id)"
        >
          <span class="min-w-0 flex-1">
            <span class="model-row__name">
              {{ modelShortName(m.id) }}
              <span class="model-row__tier">{{ modelTier(m.id) }}</span>
            </span>
            <span class="model-row__blurb">{{ modelBlurb(m.id) }}</span>
          </span>
          <i
            class="fas fa-check model-row__check"
            :class="{ 'opacity-0': i !== modelIndex }"
            aria-hidden="true"
          ></i>
        </button>
      </div>

      <div class="popover__head popover__head--mid flex items-center justify-between gap-2 px-3 py-2">
        <span id="tune-effort-heading" class="text-[11px] font-semibold uppercase tracking-wider text-ink/50 dark:text-white/50">
          Reasoning effort
        </span>
      </div>
      <div class="flex items-center gap-3 px-3 pt-3 pb-2">
        <!-- Bars rise with the rung and fill up to the chosen one, so the
             row reads as a meter. Hovering a bar previews its rung in
             the text beside it. -->
        <div
          role="radiogroup"
          aria-labelledby="tune-effort-heading"
          aria-describedby="tune-effort-note"
          class="effort-bars"
          @mouseleave="effortPreview = null"
          @keydown="onEffortKeydown"
        >
          <button
            v-for="(o, i) in effortOptions"
            :key="o.id"
            ref="effortBars"
            type="button"
            role="radio"
            :aria-checked="i === effortIndex"
            :aria-label="`${o.name}: ${o.description}`"
            :tabindex="i === effortIndex ? 0 : -1"
            :disabled="!instance"
            class="effort-bar"
            :class="{
              'effort-bar--on': i <= (effortPreview ?? effortIndex),
              'effort-bar--preview': effortPreview !== null && i <= effortPreview && i > effortIndex,
            }"
            :style="{ '--rung': i }"
            @mouseenter="effortPreview = i"
            @click="pickEffort(o.id)"
          ><span class="effort-bar__fill" aria-hidden="true"></span></button>
        </div>
        <div class="min-w-0 flex-1" aria-hidden="true">
          <p class="effort-readout__name">{{ shownEffort?.name }}</p>
          <p class="effort-readout__desc">{{ shownEffort?.description }}</p>
        </div>
      </div>
      <p id="tune-effort-note" class="tune-note px-3 pt-1 pb-3">
        More reasoning helps with difficult problems but uses more of your plan's usage. Medium is the default.
      </p>
    </div>
  </div>
  </Transition>

  <!-- Usage limits panel (opens upward above the composer) -->
  <Transition name="popover">
  <div
    v-if="usageOpen"
    ref="usagePanel"
    class="popover absolute bottom-full left-2 right-2 mb-1.5 z-50 overflow-hidden"
  >
    <div class="popover__head flex items-center justify-between gap-2 px-3 py-2">
      <span class="text-[11px] font-semibold uppercase tracking-wider text-ink/50 dark:text-white/50">
        Usage
      </span>
      <span class="text-[11px] font-medium text-ink/70 dark:text-white/70 truncate">
        {{ planSummary }}
      </span>
    </div>
    <!-- Body scrolls on short viewports (like the version-history list)
         so the panel never grows past the top of the sidebar; the calc
         budget covers the navbar + composer + panel header. -->
    <div class="iw-scroll max-h-[min(20rem,calc(100vh-19rem))] overflow-y-auto">
      <div class="px-3 py-2.5 space-y-3">
        <div v-for="meter in usageMeters" :key="meter.key">
          <div class="flex items-baseline justify-between gap-2">
            <span class="text-[10px] font-semibold uppercase tracking-wider text-ink/40 dark:text-white/40">
              {{ meter.label }}
            </span>
            <!-- Unknown usage shows an em-dash and no bar — never 0% -->
            <span class="text-[11px] font-medium tabular-nums text-ink/70 dark:text-white/70">
              {{ meter.usedText }}
            </span>
          </div>
          <div v-if="meter.percent !== null" class="usage-meter mt-1.5">
            <div class="usage-meter-fill" :style="{ width: `${meter.percent}%` }"></div>
          </div>
          <p v-if="meter.resetsAt" class="mt-1 text-[10px] text-ink/40 dark:text-white/35">
            Resets {{ meter.resetsAt }}
          </p>
        </div>
      </div>
    </div>
  </div>
  </Transition>

  <!-- Microphone picker (opens upward above the composer). The computer's
       own mic is the default; a headset is a choice, never a surprise. -->
  <Transition name="popover">
  <div
    v-if="micOpen"
    ref="micPanel"
    class="popover mic-panel absolute bottom-full left-2 right-2 mb-1.5 z-50 overflow-hidden"
  >
    <div class="popover__head flex items-center justify-between gap-2 px-3 py-2">
      <span class="text-[11px] font-semibold uppercase tracking-wider text-ink/50 dark:text-white/50">
        Microphone
      </span>
      <span class="text-[11px] font-medium text-ink/70 dark:text-white/70 truncate">
        {{ micActive?.label || (micLabelsHidden ? 'Not allowed yet' : 'System default') }}
      </span>
    </div>
    <div v-if="micLabelsHidden || micInputs.length === 0" class="px-3 py-3">
      <p class="text-[11px] leading-snug text-ink/60 dark:text-white/55">
        Allow microphone access to see and choose your microphones. Until
        then, dictation records from your computer's default input.
      </p>
      <button
        type="button"
        class="mic-allow iw-press mt-2 w-full rounded-full px-3 py-1.5 text-[11px] font-semibold text-paper dark:text-ink"
        @click="unlockMicInputs"
      >
        Allow microphone access
      </button>
    </div>
    <div v-else class="py-1" role="group" aria-label="Microphone">
      <button
        v-for="input in micInputs"
        :key="input.id"
        type="button"
        role="menuitemradio"
        :aria-checked="input.id === micActive?.id"
        class="mic-option iw-press"
        :class="{ 'mic-option--active': input.id === micActive?.id }"
        @click="chooseMicInput(input.id)"
      >
        <i class="fas fa-check mic-option-mark" :class="{ 'mic-option-mark--on': input.id === micActive?.id }"></i>
        <span class="truncate">{{ input.label || 'Microphone' }}</span>
        <span v-if="isBuiltInInput(input)" class="mic-option-tag">Built-in</span>
      </button>
      <p class="px-3 pb-2 pt-1.5 text-[10px] leading-snug text-ink/45 dark:text-white/40">
        Your computer's built-in microphone is used unless you pick another.
      </p>
    </div>
  </div>
  </Transition>

  <div class="px-2 pt-1 pb-3">
    <!-- What the pane puts above the box: the coordinator's check-in
         queue, or a stopped thread's way to try again. -->
    <slot />

    <!-- Queued prompt: one message held while the agent works. It slides
         in above the composer and slides back out when it fires, so the
         hand-off from "held" to "sent" is something you watch happen. -->
    <Transition name="queued">
    <div
      v-if="instance?.queuedPrompt"
      class="queued-row flex items-center gap-2 rounded-xl border border-blue-100 dark:border-white/[0.08] bg-ink/[0.03] dark:bg-white/[0.04] px-2.5 py-1.5 mb-1.5"
    >
      <i class="fas fa-hourglass-half text-[10px] text-ink/40 dark:text-white/40 shrink-0"></i>
      <div class="flex-1 min-w-0">
        <p class="text-[11px] font-medium text-ink/75 dark:text-white/70 truncate" :title="instance.queuedPrompt">
          {{ instance.queuedPrompt }}
        </p>
        <p class="text-[10px] text-ink/40 dark:text-white/35">{{ queuedNote }}</p>
      </div>
      <button
        type="button"
        title="Cancel queued message"
        aria-label="Cancel queued message"
        class="queued-cancel iw-press shrink-0 inline-flex items-center justify-center w-6 h-6 rounded-full text-ink/40 dark:text-white/40 hover:bg-blue-100/70 dark:hover:bg-white/[0.08] hover:text-ink/70 dark:hover:text-white/70"
        @click="cancelQueuedPrompt"
      >
        <i class="fas fa-times text-[10px]"></i>
      </button>
    </div>
    </Transition>

    <!-- Input shell: textarea on top, controls toolbar below -->
    <div class="chat-input-shell rounded-2xl bg-ink/[0.03] dark:bg-white/[0.03] border border-ink/[0.08] dark:border-white/[0.14] shadow-sm">
      <textarea
        ref="promptTextarea"
        v-model="prompt"
        :placeholder="promptPlaceholder"
        @keydown.enter.exact.prevent="handlePrompt"
        @keydown.enter.shift.exact="() => {}"
        @input="autoResizeTextarea"
        :disabled="!instance"
        rows="4"
        class="chat-textarea w-full bg-transparent text-ink dark:text-white/90 placeholder-ink/40 dark:placeholder-bone/40 text-sm px-3 pt-3 pb-1 resize-none leading-relaxed"
        style="min-height: 92px; max-height: 240px;"
      ></textarea>

      <!-- What went wrong with the last dictation, for a few seconds -->
      <p
        v-if="dictationError"
        role="status"
        class="dictation-error px-3 pb-1 text-[11px] leading-snug text-red-700/90 dark:text-red-300/90"
      >
        {{ dictationError }}
      </p>

      <!-- Controls toolbar: model + reasoning as one chip and usage on the left, send pinned right -->
      <div class="flex items-center justify-between gap-2 px-2 pb-2 pt-1">
        <!-- min-w-0 + overflow-hidden lets the chips truncate rather than
             shove the send button off the edge on a narrow sidebar. -->
        <div class="flex flex-nowrap items-center gap-1 min-w-0 flex-1 overflow-hidden">
          <!-- Model + reasoning: one chip naming both ("Opus 5.5 · Medium"),
               opening the model list and the effort meter together. -->
          <div ref="tuneRoot" class="min-w-0">
            <button
              type="button"
              title="Model and reasoning"
              aria-label="Model and reasoning"
              aria-controls="tune-panel"
              :aria-expanded="tuneOpen"
              :disabled="!instance"
              class="control-chip iw-press"
              :class="{ 'control-chip--active': tuneOpen }"
              @click="toggleTune"
            >
              <i class="fas fa-microchip control-chip-icon"></i>
              <span class="control-chip-label">{{ tuneLabel }}</span>
              <i class="fas fa-chevron-down control-chip-caret" :class="{ 'rotate-180': tuneOpen }"></i>
            </button>
          </div>

          <!-- Usage limits (button + anchored panel above) -->
          <div ref="usageRoot" class="shrink-0">
            <button
              type="button"
              title="Plan usage limits"
              aria-label="Usage limits"
              :aria-expanded="usageOpen"
              class="control-chip iw-press"
              :class="{ 'control-chip--active': usageOpen }"
              @click="toggleUsage"
            >
              <i class="fas fa-gauge-high control-chip-icon"></i>
              <span class="control-chip-label">Usage</span>
            </button>
          </div>
        </div>

        <!-- The one button, and it is the microphone first: hold to
             dictate, click to send (or to stop a run in flight). Once
             the box has words in it, typed or dictated, it turns into
             the red record button with a send arrow on it, so the tap
             that sends is obvious; a hold still records more onto the
             end, which is why it stays red rather than turning into a
             plain send button. Emptying the box (sending, or deleting
             the text) turns it back into the quiet mic. A run in flight
             makes it navy with the stop glyph, since a click stops the
             agent. Recording turns it red with a ring that swells with
             the voice; the click the browser fires when a hold lets go
             is swallowed, so letting go never sends. Which microphone it
             listens on lives behind the same button: a right-click (or
             the keyboard's menu key) opens the picker, so there is no
             second mic control beside it. Where the browser cannot
             record at all it is a plain send arrow. -->
        <button
          ref="sendButton"
          type="button"
          :title="sendTitle"
          :aria-label="sendTitle"
          :aria-pressed="isRecording"
          :aria-expanded="dictationSupported ? micOpen : undefined"
          :disabled="!instance || isTranscribing"
          class="btn-send iw-press relative flex shrink-0 items-center justify-center w-9 h-9 rounded-full"
          :class="sendClass"
          :style="isRecording ? micRingStyle : undefined"
          @pointerdown="onSendPointerDown"
          @pointerup="onSendPointerUp"
          @pointercancel="onSendPointerUp"
          @contextmenu.prevent="toggleMic"
          @click="onSendClick"
        >
          <!-- One glyph at a time; a change cross-fades the old one out
               as the new one turns in, rather than snapping. -->
          <Transition name="send-glyph">
            <i :key="sendGlyph" :class="sendGlyphClass" aria-hidden="true"></i>
          </Transition>
        </button>
      </div>
    </div>
  </div>
</div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onBeforeUnmount, onActivated, onDeactivated, watch, toRef } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
// The workspace's shared motion + material vocabulary (curves, durations,
// radii, elevation, focus ring). A var(--iw-*) with no token behind it
// resolves to nothing, which would leave the popovers transparent.
import '../../../styles/workspace.css'
import { useUsageStore, formatResetTime } from '@/shared/stores/usage'
import { isBuiltInInput, useDictation } from '../../../composables/useDictation'
import type { AIModel } from '../../../types/index'
import type { AgentInstance, ReasoningEffort, ReasoningEffortOption } from '../../../types/services'
import { reasoningEffortsForModel } from '../../../types/services'

const props = withDefaults(
  defineProps<{
    /** The coordinator or thread being typed to */
    instance: AgentInstance | null
    /** Where a message goes: the coordinator's next message, or a thread's
     *  next turn. Called mid-run too; the pane holds it behind the run. */
    submit: (text: string) => void | Promise<void>
    /** What the empty box says */
    placeholder?: string
    /** Under a message held behind a live run */
    queuedNote?: string
  }>(),
  {
    placeholder: 'Ask me to build, edit, or explain anything in your project...',
    queuedNote: 'Queued — sends when the agent finishes',
  }
)

const emit = defineEmits<{ (e: 'stop'): void }>()

const store = useAgentStore()
const instance = toRef(props, 'instance')
const prompt = ref('')
const promptTextarea = ref<HTMLTextAreaElement | null>(null)

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
    tuneOpen.value &&
    !tuneRoot.value?.contains(target) &&
    !tunePanel.value?.contains(target)
  ) {
    tuneOpen.value = false
  }
  if (
    micOpen.value &&
    !sendButton.value?.contains(target) &&
    !micPanel.value?.contains(target)
  ) {
    micOpen.value = false
  }
}

// Escape closes the model menu from anywhere, not only while focus is
// inside it — a keyboard user who Tabs past the last control would otherwise
// have no way back to dismiss it. Inside the panel its own handler fires
// first and stops the event, so this never runs twice.
function onDocKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && tuneOpen.value) closeTune()
}

onMounted(() => {
  document.addEventListener('mousedown', onDocMousedown)
  document.addEventListener('keydown', onDocKeydown)
})
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onDocMousedown)
  document.removeEventListener('keydown', onDocKeydown)
})

// --- Usage limits dropdown (plan + rolling windows) ---

const usageStore = useUsageStore()
const usageOpen = ref(false)
const usageRoot = ref<HTMLElement | null>(null)
const usagePanel = ref<HTMLElement | null>(null)

// --- Model + reasoning menu (the model list and the effort meter share one panel) ---

const tuneOpen = ref(false)
const tuneRoot = ref<HTMLElement | null>(null)
const tunePanel = ref<HTMLElement | null>(null)
// The microphone picker hangs off the send button (right-click) rather than
// off a handle of its own.
const micOpen = ref(false)
const sendButton = ref<HTMLElement | null>(null)
const micPanel = ref<HTMLElement | null>(null)

// The three controls share the space above the composer, so only one panel
// opens at a time.
function closeControlPanels() {
  usageOpen.value = false
  tuneOpen.value = false
  micOpen.value = false
}

function toggleUsage() {
  const next = !usageOpen.value
  closeControlPanels()
  usageOpen.value = next
  // Windows drift as older activity ages out; refresh on open.
  if (usageOpen.value) void usageStore.fetchUsage()
}

function toggleTune() {
  const next = !tuneOpen.value
  closeControlPanels()
  tuneOpen.value = next
}

/** "Pro plan" — em-dash while the plan is unknown. The allowances belong to
 *  the weekly meter below, not here. */
const planSummary = computed(() =>
  usageStore.plan ? `${usageStore.plan.name} plan` : '—'
)

/** The rolling-window meter. A list of one: the weekly allowance is the only
 *  window, but the panel renders rows, so keeping the shape costs nothing.
 *  Missing data renders as unknown (em-dash, no bar) — never as 0%. */
const usageMeters = computed(() => {
  const rows = [
    { key: 'week', label: 'Weekly limit', win: usageStore.weekly, percent: usageStore.weeklyPercent },
  ]
  return rows.map(({ key, label, win, percent }) => ({
    key,
    label,
    percent,
    // How much of the window's allowance is gone, on a 0-100 scale — the
    // dollar figures behind it stay out of the workspace. Unknown usage
    // stays an em-dash, never 0%.
    usedText: percent !== null ? `${percent}% used` : '—',
    resetsAt: formatResetTime(win?.resetsAt ?? null),
  }))
})

// The models offered in the composer, one per tier. SELECTABLE_MODEL_PATTERN
// admits whole families (GPT and Claude), so a new model the catalog adds
// shows up without another edit here.
const SELECTABLE_MODEL_PATTERN = /^(gpt|claude)-/
const modelOptions = computed<AIModel[]>(() => {
  const available = (store.availableModels || []).filter(model =>
    SELECTABLE_MODEL_PATTERN.test(model.id)
  )
  if (available.length > 0) {
    return available
  }
  return [
    { id: 'gpt-6-luna', name: 'GPT 6 Luna', provider: 'openai' } as AIModel,
    { id: 'claude-opus-5-5', name: 'Claude Opus 5.5', provider: 'anthropic', default: true } as AIModel,
    { id: 'gpt-6-astra', name: 'GPT 6 Astra', provider: 'openai' } as AIModel
  ]
})

const effortOptions = computed<ReasoningEffortOption[]>(() =>
  reasoningEffortsForModel(instance.value?.selectedModelId)
)

// The tiers ranked faster → smarter, the order the model menu lists them
// in. Unknown ids sort last but still appear, so the menu degrades
// gracefully if the lineup changes before this table does.
const MODEL_RANK: Record<string, number> = {
  'gpt-6-luna': 0,
  'claude-opus-5-5': 1,
  'gpt-6-astra': 2,
}
const orderedModels = computed<AIModel[]>(() =>
  [...modelOptions.value].sort(
    (a, b) => (MODEL_RANK[a.id] ?? 99) - (MODEL_RANK[b.id] ?? 99)
  )
)
// A conversation on a model the menu does not offer shows the default
// rather than an arbitrary end of the lineup.
const modelIndex = computed(() => {
  const models = orderedModels.value
  const idx = models.findIndex(m => m.id === instance.value?.selectedModelId)
  if (idx >= 0) return idx
  const fallback = models.findIndex(m => m.default)
  return fallback >= 0 ? fallback : 0
})
const currentModel = computed<AIModel | null>(() => orderedModels.value[modelIndex.value] ?? null)

/** The distinctive part of the model name for the chip
 *  ("Luna", "Opus 5.5", "Astra"), dropping the "GPT <version>" or "Claude"
 *  prefix. */
function modelShortName(id?: string | null): string {
  const model = orderedModels.value.find(m => m.id === id) ?? currentModel.value
  if (!model) return 'Model'
  return model.name.replace(/^(?:GPT\s*\d+(?:\.\d+)?|Claude)\s*/i, '').trim() || model.name
}

// What each tier is for, shown under its name in the menu. Static: the models endpoint
// sends no copy, and the composer's fallback list has none either.
const MODEL_BLURBS: Record<string, string> = {
  'gpt-6-luna': 'Fast and inexpensive, yet capable at most tasks — turn up reasoning for harder ones.',
  'claude-opus-5-5': 'Thoughtful and dependable, with strong judgment on code and design. The default.',
  'gpt-6-astra': 'Frontier intelligence for the hardest, most complex work.',
}
const modelBlurb = (id: string) =>
  MODEL_BLURBS[id] ?? orderedModels.value.find(m => m.id === id)?.description ?? ''

// effortOptions is the one ladder every model shares, ordered faster →
// smarter. The store re-seats a legacy selectedEffort onto it when the model
// changes, so the meter can't point at a rung the next request would reject —
// and changing model never moves it.
const effortIndex = computed(() => {
  const idx = effortOptions.value.findIndex(
    o => o.id === (instance.value?.selectedEffort ?? 'medium')
  )
  return idx >= 0 ? idx : 0
})

// The tier tag beside each model's name in the menu.
const MODEL_TIERS: Record<string, string> = {
  'gpt-6-luna': 'Fast',
  'claude-opus-5-5': 'Balanced',
  'gpt-6-astra': 'Frontier',
}
const modelTier = (id: string) => MODEL_TIERS[id] ?? ''

/** The chip reads "Opus 5.5 · Medium": the model's short name and the
 *  reasoning rung, so both settings are legible without opening anything. */
const tuneLabel = computed(
  () => `${modelShortName(currentModel.value?.id)} · ${effortOptions.value[effortIndex.value]?.name ?? 'Reasoning'}`
)

function pickModel(id: string) {
  if (id !== instance.value?.selectedModelId) void handleModelSelect(id)
}

function pickEffort(id: ReasoningEffort) {
  if (id !== instance.value?.selectedEffort) void handleEffortSelect(id)
}

// The bar under the pointer, whose rung the readout previews; null when the
// pointer is elsewhere and the readout shows the rung in use.
const effortPreview = ref<number | null>(null)
const shownEffort = computed<ReasoningEffortOption | null>(
  () => effortOptions.value[effortPreview.value ?? effortIndex.value] ?? null
)

const modelRows = ref<HTMLButtonElement[]>([])
const effortBars = ref<HTMLButtonElement[]>([])

/** Radio-group keys: arrows step one option (clamped at the ends rather than
 *  wrapping — both groups run faster → smarter, so they have a top), Home/End
 *  jump to them. `upIsMore` says which way ArrowUp goes: toward the top of
 *  the model list is faster, while the effort bars stand left to right, so
 *  there Up means more. Returns the index to move to, or null to ignore. */
function radioStep(key: string, current: number, count: number, upIsMore: boolean): number | null {
  const steps: Record<string, number> = {
    ArrowRight: current + 1,
    ArrowLeft: current - 1,
    ArrowDown: upIsMore ? current - 1 : current + 1,
    ArrowUp: upIsMore ? current + 1 : current - 1,
    Home: 0,
    End: count - 1,
  }
  if (!(key in steps) || count === 0) return null
  return Math.min(Math.max(steps[key]!, 0), count - 1)
}

// Focus follows the choice, since the chosen option is its group's one tab
// stop.
function onModelKeydown(e: KeyboardEvent) {
  const target = radioStep(e.key, modelIndex.value, orderedModels.value.length, false)
  if (target === null || !instance.value) return
  e.preventDefault()
  pickModel(orderedModels.value[target]!.id)
  void nextTick(() => modelRows.value[target]?.focus())
}

function onEffortKeydown(e: KeyboardEvent) {
  const target = radioStep(e.key, effortIndex.value, effortOptions.value.length, true)
  if (target === null || !instance.value) return
  e.preventDefault()
  effortPreview.value = null
  pickEffort(effortOptions.value[target]!.id)
  void nextTick(() => effortBars.value[target]?.focus())
}

/** Escape: the panel goes and focus returns to the chip that opened it, so a
 *  keyboard user is not dropped on the page body. */
function closeTune() {
  tuneOpen.value = false
  effortPreview.value = null
  void nextTick(() => tuneRoot.value?.querySelector<HTMLButtonElement>('button')?.focus())
}

watch(tuneOpen, open => {
  // Focus lands on the model in use, so the arrows work straight away.
  if (open) void nextTick(() => modelRows.value[modelIndex.value]?.focus())
  else effortPreview.value = null
})

// --- Dictation (holding the send button, or holding ⌘D) ---

// ⌘ on Apple hardware, Ctrl elsewhere: the modifier the rest of the OS
// already puts its shortcuts on.
const isApplePlatform =
  typeof navigator !== 'undefined' &&
  /Mac|iPhone|iPad|iPod/i.test(navigator.platform || navigator.userAgent || '')
const dictationShortcut = isApplePlatform ? '⌘D' : 'Ctrl+D'

const {
  state: dictationState,
  error: dictationError,
  supported: dictationSupported,
  level: dictationLevel,
  inputs: micInputs,
  activeInput: micActive,
  labelsHidden: micLabelsHidden,
  start: startDictation,
  stop: stopDictation,
  cancel: cancelDictation,
  selectInput: selectMicInput,
  unlockInputs: unlockMicInputs,
  refreshInputs: refreshMicInputs,
} = useDictation({ onTranscript: insertDictation })

const isRecording = computed(() => dictationState.value === 'recording')
const isTranscribing = computed(() => dictationState.value === 'transcribing')

/** What is being held to keep the mic open — the button, or the shortcut.
 *  Written by whichever hold opened it, and read only while recording, so
 *  the composer can say which one to let go of. */
const heldBy = ref<'button' | 'key' | null>(null)

/** How a live recording ends, in the words of whatever opened it. Both are
 *  holds: nothing stops dictation by being pressed a second time. */
const releaseHint = computed(() => {
  if (heldBy.value === 'key') return `let go of ${dictationShortcut}`
  if (heldBy.value === 'button') return 'let go of the button'
  return 'let go'
})

/** The red ring around a live mic widens with the voice it hears, so "is it
 *  picking me up?" is answered by looking rather than by sending a clip. */
const micRingStyle = computed(() => ({
  '--dictate-ring': `${2 + Math.round(dictationLevel.value * 10)}px`,
}))

function toggleMic() {
  // Nothing to pick from where the browser cannot record, and a right-click
  // on a disabled button is still a right-click.
  if (!dictationSupported || !instance.value) return
  const next = !micOpen.value
  closeControlPanels()
  micOpen.value = next
  // A headset may have connected since the list was last read.
  if (micOpen.value) void refreshMicInputs()
}

function chooseMicInput(id: string) {
  selectMicInput(id)
  micOpen.value = false
}

/** What a hold, a click, and a right-click each do, in that order: the
 *  button is the microphone first, and a click is how the words leave. */
const sendTitle = computed(() => {
  if (isTranscribing.value) return 'Transcribing…'
  if (isRecording.value) return `Listening — ${releaseHint.value} when you're done`
  const running = !!instance.value?.isProcessing
  if (!dictationSupported) return running ? 'Stop agent' : 'Send (Enter)'
  const click = running ? 'click to stop the agent' : 'click to send (Enter)'
  return `Hold to dictate, or hold ${dictationShortcut} · ${click} · right-click to choose microphone`
})

/** There is something a click would send. */
const hasPromptText = computed(() => !!instance.value && !!prompt.value.trim())

/** Words in the box and nothing running: the button is the red record
 *  button with a send arrow on it. A tap sends; a hold still records more. */
const isReadyToSend = computed(
  () => dictationSupported && hasPromptText.value && !instance.value?.isProcessing
)

/** Which glyph the button wears. Keyed, so a change animates. */
const sendGlyph = computed(() => {
  if (isTranscribing.value) return 'transcribing'
  if (isRecording.value) return 'mic'
  if (instance.value?.isProcessing) return 'stop'
  if (!dictationSupported || isReadyToSend.value) return 'arrow'
  return 'mic'
})

const sendGlyphClass = computed(() => {
  switch (sendGlyph.value) {
    case 'transcribing':
      return 'send-glyph fas fa-circle-notch fa-spin text-[13px]'
    case 'stop':
      return 'send-glyph fas fa-stop text-sm'
    case 'arrow':
      return 'send-glyph fas fa-arrow-up text-sm'
    default:
      return 'send-glyph fas fa-microphone text-[13px]'
  }
})

/** Red while the mic is live, and red with an arrow once there are words to
 *  send (still the record button, since a hold adds to them); navy ink when
 *  a click stops a run, or sends where the browser cannot record; a ghost
 *  otherwise — still pressable, because a hold records into an empty box. */
const sendClass = computed(() => {
  if (isRecording.value) return 'btn-send--recording'
  if (isReadyToSend.value) return 'btn-send--ready'
  if (instance.value && (hasPromptText.value || instance.value.isProcessing)) {
    return 'btn-send--active text-paper dark:text-ink'
  }
  return 'btn-send--idle'
})

// --- Tap versus hold on the send button ---
//
// A press that lasts HOLD_TO_TALK_MS becomes a hold: the mic opens, and
// letting go closes it and transcribes. A shorter press is a tap, and the
// click the browser fires on release does the tap's work (send, or stop the
// run) — that way a keyboard Enter or Space on the focused button sends too.
// A hold's release also fires a click, which is swallowed.

/** How long a press must last before it is a hold. Shorter reads as a click. */
const HOLD_TO_TALK_MS = 250

let holdTimer: ReturnType<typeof setTimeout> | null = null
let pointerHeld = false
// Set once a press has become a hold: the click on release is not a tap.
let holdConsumedClick = false
// The mic is still opening (permission prompt, device negotiation).
let holdOpening = false

function clearHoldTimer() {
  if (holdTimer) clearTimeout(holdTimer)
  holdTimer = null
}

function onSendPointerDown(e: PointerEvent) {
  // Only the primary button: a right-click is the context menu, not a hold.
  if (e.button !== undefined && e.button !== 0) return
  if (!instance.value || isTranscribing.value) return
  // Keep the caret (and any selection) in the textarea — a click sends what
  // is typed there, and a hold puts words there, at that caret.
  e.preventDefault()
  // A press on the button is a send or a hold, never a browse of the
  // picker it also opens: put the picker away first.
  micOpen.value = false
  pointerHeld = true
  holdConsumedClick = false
  // Follow the pointer off the button: a thumb that drifts mid-sentence
  // must still end the recording when it lifts.
  const el = e.currentTarget as HTMLElement | null
  if (el && typeof el.setPointerCapture === 'function') {
    try {
      el.setPointerCapture(e.pointerId)
    } catch {
      // jsdom, or a pointer that is already gone.
    }
  }
  clearHoldTimer()
  holdTimer = setTimeout(() => {
    holdTimer = null
    if (!pointerHeld) return
    holdConsumedClick = true
    // Already live from a ⌘D hold: the button simply takes over, and its
    // release is what stops the recording now.
    heldBy.value = 'button'
    if (isRecording.value) return
    holdOpening = true
    void startDictation().finally(() => {
      holdOpening = false
    })
  }, HOLD_TO_TALK_MS)
}

function onSendPointerUp() {
  if (!pointerHeld) return
  pointerHeld = false
  if (holdTimer) {
    // Let go before it became a hold: a tap. The click that follows does it.
    clearHoldTimer()
    return
  }
  if (isRecording.value) {
    stopDictation()
  } else if (holdOpening) {
    // Let go while the microphone was still opening (the permission prompt
    // was up): nothing was heard, so there is nothing to transcribe.
    cancelDictation()
  }
}

function onSendClick() {
  if (holdConsumedClick) {
    holdConsumedClick = false
    return
  }
  // Something else has the mic open — a ⌘D hold whose keys are still down.
  // A tap closes it rather than sending, and the next tap sends the words.
  if (isRecording.value) {
    stopDictation()
    return
  }
  if (instance.value?.isProcessing) {
    handleStopClick()
    return
  }
  void handlePrompt()
}

onBeforeUnmount(clearHoldTimer)

/** Dictated text lands where the caret is — in place of a selection, or
 *  between what is on either side, with a space added wherever it would
 *  otherwise run into a word — and the caret lands after it, so the next
 *  thing typed or dictated follows on. With the caret at the end, where
 *  each transcript leaves it, that is a plain append. Once the box has lost
 *  focus the words go on the end: a caret nobody can see is not a place to
 *  put them. Typing, selecting, and deleting are the textarea's own; nothing
 *  here takes them away, so the words can be edited between holds. The
 *  transcript is never sent by itself: the user reads it over, then clicks
 *  the button or presses Enter. */
function insertDictation(text: string) {
  const el = promptTextarea.value
  const current = prompt.value
  const caret = el && document.activeElement === el ? [el.selectionStart, el.selectionEnd] : null
  const [start, end] = caret ?? [current.length, current.length]
  const before = current.slice(0, start)
  const after = current.slice(end)
  const lead = before && !/\s$/.test(before) ? ' ' : ''
  const trail = after && !/^\s/.test(after) ? ' ' : ''
  prompt.value = `${before}${lead}${text}${trail}${after}`
  const landing = before.length + lead.length + text.length
  nextTick(() => {
    autoResizeTextarea()
    if (el) {
      el.focus()
      el.setSelectionRange(landing, landing)
    }
  })
}

// --- Holding ⌘D ---
//
// The shortcut is the button without the mouse: it is held, not pressed. The
// mic opens on the way down and closes when the keys come up, so a hold is a
// hold whichever of the two the hand is on, and nothing has to be pressed a
// second time to stop.
//
// Which key comes up first is not ours to choose — and macOS withholds a
// letter's keyup entirely while Command is still down — so the release is
// taken from the D, from the modifier, or from the window losing focus
// mid-hold (⌘-Tab), whichever arrives.
let keyHeld = false
// The mic is still opening (permission prompt, device negotiation).
let keyOpening = false

function isDictationChord(e: KeyboardEvent): boolean {
  const modifier = isApplePlatform ? e.metaKey : e.ctrlKey
  return !!modifier && !e.altKey && !e.shiftKey && (e.key || '').toLowerCase() === 'd'
}

/** ⌘D from anywhere in the workspace — the point of a shortcut is not having
 *  to find the button first. Left alone when the preview has already taken
 *  the keystroke for the app it is showing (it calls preventDefault), on a
 *  read-only task thread (no composer), and where the browser cannot record. */
function onDictationKeyDown(e: KeyboardEvent) {
  if (e.defaultPrevented) return
  if (!isDictationChord(e)) return
  if (!dictationSupported || !instance.value) return
  // The browser's own ⌘D (bookmark this page) must not fire, on the repeats
  // a held key sends as much as on the first one.
  e.preventDefault()
  if (e.repeat || keyHeld) return
  keyHeld = true
  heldBy.value = 'key'
  // Already live from a hold of the button: the keys take over, and their
  // release stops the recording.
  if (isRecording.value) return
  keyOpening = true
  void startDictation().finally(() => {
    keyOpening = false
  })
}

function onDictationKeyUp(e: KeyboardEvent) {
  const key = (e.key || '').toLowerCase()
  if (key === 'd' || key === 'meta' || key === 'control') releaseDictationKey()
}

/** The end of a ⌘D hold, however it ended. */
function releaseDictationKey() {
  if (!keyHeld) return
  keyHeld = false
  if (isRecording.value) {
    stopDictation()
  } else if (keyOpening) {
    // Let go while the microphone was still opening (the permission prompt
    // was up): nothing was heard, so there is nothing to transcribe.
    cancelDictation()
  }
}

// The shortcut belongs to the composer on screen. The workspace keeps the
// hidden pane alive (KeepAlive), and the coordinator's composer and a
// thread's must not both start recording on one ⌘D.
function listenForDictationKey() {
  document.addEventListener('keydown', onDictationKeyDown)
  document.addEventListener('keyup', onDictationKeyUp)
  window.addEventListener('blur', releaseDictationKey)
}
function stopListeningForDictationKey() {
  document.removeEventListener('keydown', onDictationKeyDown)
  document.removeEventListener('keyup', onDictationKeyUp)
  window.removeEventListener('blur', releaseDictationKey)
  releaseDictationKey()
}
onMounted(listenForDictationKey)
onActivated(listenForDictationKey)
onDeactivated(stopListeningForDictationKey)
onBeforeUnmount(stopListeningForDictationKey)


const promptPlaceholder = computed(() => {
  if (isRecording.value) {
    const mic = micActive.value?.label || 'the default microphone'
    return `Listening on ${mic}… ${releaseHint.value} when you're done.`
  }
  if (isTranscribing.value) return 'Transcribing…'
  return props.placeholder
})

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
  if (!prompt.value.trim() || !instance.value) return

  const promptText = prompt.value
  prompt.value = '' // Clear immediately

  // Reset textarea height
  if (promptTextarea.value) {
    promptTextarea.value.style.height = '92px'
  }

  // Mid-run, the pane's submit holds the message behind the run (one per
  // instance — a second submit replaces it) rather than racing a second run.
  await props.submit(promptText)
}

function cancelQueuedPrompt() {
  if (instance.value) store.clearQueuedPrompt(instance.value.id)
}

function handleStopClick() {
  const current = instance.value
  // Stop means stop: a queued prompt must not fire into the aborted run's
  // wake, but it shouldn't silently vanish either — hand it back to the
  // input for the user to send or discard.
  if (current?.queuedPrompt) {
    if (!prompt.value.trim()) prompt.value = current.queuedPrompt
    store.clearQueuedPrompt(current.id)
  }
  emit('stop')
}

// Model and effort belong to the instance being typed to: a thread keeps its
// own, apart from the coordinator's and every other thread's.
function handleModelSelect(modelId: string) {
  if (instance.value) store.setInstanceModel(instance.value.id, modelId)
}

function handleEffortSelect(effort: ReasoningEffort) {
  if (instance.value) store.setInstanceEffort(instance.value.id, effort)
}
</script>

<style scoped>
/* ── Popovers ───────────────────────────────────────────────────────────── */

/* Model, reasoning and usage share one surface: a translucent material lifted
   off the composer, so the transcript behind it stays present as colour. */
.popover {
  border-radius: var(--iw-r-lg);
  border: 1px solid var(--iw-material-border);
  background: var(--iw-material-bg);
  -webkit-backdrop-filter: var(--iw-material-filter);
  backdrop-filter: var(--iw-material-filter);
  box-shadow: var(--iw-shadow-3);
}

@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .popover {
    background: #ffffff;
  }

  .dark .popover {
    background: #0f0f0f;
  }
}

.popover__head {
  border-bottom: 1px solid var(--iw-hairline);
}

/* A second head partway down a panel rules itself off from the section
   above as well as the one below. */
.popover__head--mid {
  border-top: 1px solid var(--iw-hairline);
}

/* Grows from its bottom edge — the edge nearest the chip that opened it — so
   the panel reads as unfolding out of the control rather than arriving from
   somewhere off-screen. Closing is faster than opening: dismissals should
   feel immediate, arrivals deliberate. */
.popover-enter-active {
  transition:
    opacity var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-3) var(--iw-ease-spring);
  transform-origin: bottom center;
}

.popover-leave-active {
  transition:
    opacity var(--iw-dur-1) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
  transform-origin: bottom center;
}

.popover-enter-from {
  opacity: 0;
  transform: translateY(8px) scale(0.96);
}

.popover-leave-to {
  opacity: 0;
  transform: translateY(4px) scale(0.98);
}

/* ── Composer ───────────────────────────────────────────────────────────── */

/* Input shell wraps the textarea + controls toolbar as one field. Focus adds
   a soft halo outside the existing edge rather than thickening the border,
   so the field never changes size as you click into it. */
.chat-input-shell {
  transition:
    border-color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out);
}

.chat-input-shell:focus-within {
  border-color: rgba(19, 26, 44, 0.4);
  box-shadow: 0 0 0 3px rgba(var(--iw-accent), 0.13);
}

.dark .chat-input-shell:focus-within {
  border-color: rgba(255, 255, 255, 0.4);
}

/* ── Queued prompt ──────────────────────────────────────────────────────── */

/* Held above the composer while the agent works. It opens and closes its own
   space (grid rows) so the composer glides down and back rather than jumping
   when a message is queued or fires. */
.queued-enter-active,
.queued-leave-active {
  transition:
    opacity var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-3) var(--iw-ease-out),
    margin-bottom var(--iw-dur-3) var(--iw-ease-out);
}

.queued-enter-from,
.queued-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
  margin-bottom: -2.25rem;
}

.queued-cancel {
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.queued-cancel:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

/* Control chip: the compact model / reasoning / usage buttons. Ghost until
   hovered or open, so the input shell stays the focal point. */
.control-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  max-width: 100%;
  padding: 0.3rem 0.55rem;
  border-radius: var(--iw-r-sm);
  border: 1px solid transparent;
  background-color: transparent;
  color: rgba(19, 26, 44, 0.75);
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
  outline: none;
}

.control-chip:hover:not(:disabled) {
  background-color: rgba(219, 234, 254, 0.5);
  color: rgb(19, 26, 44);
}

.control-chip--active {
  background-color: rgba(219, 234, 254, 0.7);
  color: rgb(19, 26, 44);
}

.control-chip:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-chip:focus-visible {
  box-shadow: var(--iw-focus-ring);
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
  transition: transform var(--iw-dur-3) var(--iw-ease-inout);
}

/* Model menu rows: name, tier tag and what the tier is for, with a check on
   the model in use. Ghost rows that tint on hover, like the chip. */
.model-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.5rem 0.625rem;
  border: 0;
  border-radius: var(--iw-r-sm);
  background: transparent;
  text-align: left;
  cursor: pointer;
  outline: none;
  transition: background-color var(--iw-dur-2) var(--iw-ease-out);
}

.model-row:hover:not(:disabled) {
  background-color: rgba(219, 234, 254, 0.5);
}

.model-row--on {
  background-color: rgba(219, 234, 254, 0.35);
}

.model-row:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.model-row:focus-visible {
  box-shadow: var(--iw-focus-ring);
}

.dark .model-row:hover:not(:disabled) {
  background-color: rgba(255, 255, 255, 0.07);
}

.dark .model-row--on {
  background-color: rgba(255, 255, 255, 0.05);
}

.model-row__name {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
  font-size: 0.8125rem;
  font-weight: 500;
  line-height: 1.25rem;
  color: rgb(19, 26, 44);
}

.dark .model-row__name {
  color: rgba(255, 255, 255, 0.92);
}

.model-row__tier {
  font-size: 0.6875rem;
  font-weight: 500;
  color: rgba(19, 26, 44, 0.55);
}

.dark .model-row__tier {
  color: rgba(255, 255, 255, 0.45);
}

.model-row__blurb {
  display: block;
  font-size: 0.6875rem;
  line-height: 1rem;
  color: rgba(19, 26, 44, 0.7);
}

.dark .model-row__blurb {
  color: rgba(255, 255, 255, 0.55);
}

.model-row__check {
  flex-shrink: 0;
  font-size: 0.6875rem;
  color: rgb(19, 26, 44);
}

.dark .model-row__check {
  color: #f3ede2;
}

/* Reasoning effort meter: bars that rise with the rung, filled up to the
   chosen one in the send button's navy (cream in dark); the rest are hairline
   outlines. A hovered rung above the chosen one previews at half strength.
   Each bar's hit target is the full column, not just the ink. */
.effort-bars {
  display: flex;
  align-items: flex-end;
  gap: 0.1875rem;
  flex-shrink: 0;
}

.effort-bar {
  display: flex;
  align-items: flex-end;
  width: 1rem;
  height: 1.75rem;
  padding: 0 0.125rem;
  border: 0;
  border-radius: 0.25rem;
  background: transparent;
  cursor: pointer;
  outline: none;
}

.effort-bar:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.effort-bar:focus-visible {
  box-shadow: var(--iw-focus-ring);
}

.effort-bar__fill {
  display: block;
  width: 100%;
  height: calc(0.5rem + var(--rung) * 0.375rem);
  border-radius: 0.1875rem;
  box-shadow: inset 0 0 0 1px rgba(19, 26, 44, 0.25);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out);
}

.effort-bar--on .effort-bar__fill {
  background-color: rgb(19, 26, 44);
  box-shadow: none;
}

.effort-bar--preview .effort-bar__fill {
  background-color: rgba(19, 26, 44, 0.35);
}

.dark .effort-bar__fill {
  box-shadow: inset 0 0 0 1px rgba(243, 237, 226, 0.3);
}

.dark .effort-bar--on .effort-bar__fill {
  background-color: #f3ede2;
}

.dark .effort-bar--preview .effort-bar__fill {
  background-color: rgba(243, 237, 226, 0.4);
}

.effort-readout__name {
  font-size: 0.8125rem;
  font-weight: 500;
  line-height: 1.25rem;
  color: rgb(19, 26, 44);
}

.dark .effort-readout__name {
  color: rgba(255, 255, 255, 0.92);
}

.effort-readout__desc {
  font-size: 0.6875rem;
  line-height: 1rem;
  color: rgba(19, 26, 44, 0.7);
}

.dark .effort-readout__desc {
  color: rgba(255, 255, 255, 0.55);
}

/* What more reasoning costs. The opacities here clear 4.5:1 for 10px text
   over the glass. */
.tune-note {
  font-size: 0.625rem;
  line-height: 0.875rem;
  color: rgba(19, 26, 44, 0.55);
}

.dark .tune-note {
  color: rgba(255, 255, 255, 0.5);
}

@media (prefers-reduced-motion: reduce) {
  .model-row,
  .effort-bar__fill {
    transition: none;
  }
}

/* Usage-window meter: quiet navy ink bar (cream in dark mode, matching the
   primary button system) */
.usage-meter {
  position: relative;
  height: 0.25rem;
  border-radius: 9999px;
  background: rgba(19, 26, 44, 0.1);
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
  transition: width var(--iw-dur-4) var(--iw-ease-out);
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

/* Navy ink send button - matching the site's primary "Start Building" button.
   Send, stop, and the mic are the same button in different states, so the
   swap between them is a colour and shadow change on one shape rather than
   controls trading places. Hold-to-talk on touch means no text selection,
   callout, or scroll may start from a long press on it. */
.btn-send {
  border: 1px solid transparent;
  transform: translateZ(0);
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
  touch-action: none;
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    border-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.btn-send:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.btn-send:disabled {
  cursor: not-allowed;
}

/* Nothing to send yet: a quiet shape in the control chips' ghost register.
   Still pressable, because a hold records into an empty box. */
.btn-send--idle {
  background-color: rgba(219, 234, 254, 0.6);
  border-color: rgba(191, 219, 254, 0.7);
  color: rgba(19, 26, 44, 0.45);
  box-shadow: var(--iw-shadow-1);
}

.btn-send--idle:hover:not(:disabled) {
  background-color: rgba(219, 234, 254, 0.9);
  color: rgba(19, 26, 44, 0.7);
}

.btn-send--idle:disabled {
  opacity: 0.6;
}

.btn-send--active {
  background: theme('colors.blue.950');
  box-shadow: var(--iw-shadow-2), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.btn-send--active:hover {
  background: theme('colors.blue.900');
  box-shadow: var(--iw-shadow-3), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

/* Live: red, with a ring whose width is the voice level (set inline as
   --dictate-ring). It sits still on silence and swells as you speak, which
   is the whole point — a mic that hears nothing looks like one. */
.btn-send--recording,
.btn-send--recording:hover:not(:disabled) {
  background-color: #dc2626;
  color: #ffffff;
  box-shadow: 0 0 0 var(--dictate-ring, 2px) rgba(220, 38, 38, 0.35);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow 80ms linear;
}

/* Words to send: the record button, red, wearing a send arrow. Calmer than
   live recording — no ring — so the two never read as the same state. */
.btn-send--ready {
  background-color: #dc2626;
  color: #ffffff;
  box-shadow: var(--iw-shadow-2), inset 0 1px 0 rgba(255, 255, 255, 0.18);
}

.btn-send--ready:hover:not(:disabled) {
  background-color: #b91c1c;
  box-shadow: var(--iw-shadow-3), inset 0 1px 0 rgba(255, 255, 255, 0.18);
}

/* The glyph swap: the old one fades and shrinks out on the spot while the
   new one turns up into place. The leaving glyph is taken out of flow so the
   two overlap in the middle of the button instead of sitting side by side. */
.send-glyph-enter-active,
.send-glyph-leave-active {
  transition:
    opacity var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-3) var(--iw-ease-spring);
}

.send-glyph-leave-active {
  position: absolute;
}

.send-glyph-enter-from {
  opacity: 0;
  transform: translateY(6px) scale(0.6);
}

.send-glyph-leave-to {
  opacity: 0;
  transform: scale(0.6);
}

@media (prefers-reduced-motion: reduce) {
  .send-glyph-enter-active,
  .send-glyph-leave-active {
    transition: opacity var(--iw-dur-1) linear;
  }

  .send-glyph-enter-from,
  .send-glyph-leave-to {
    transform: none;
  }
}

.dark .btn-send--ready {
  background-color: #ef4444;
  color: #ffffff;
}

.dark .btn-send--ready:hover:not(:disabled) {
  background-color: #f87171;
}

.dark .btn-send--idle {
  background-color: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.12);
  color: rgba(219, 234, 254, 0.5);
}

.dark .btn-send--idle:hover:not(:disabled) {
  background-color: rgba(255, 255, 255, 0.09);
  color: rgba(255, 255, 255, 0.85);
}

.dark .btn-send--active {
  background: #f3ede2;
}

.dark .btn-send--active:hover {
  background: #ffffff;
}

.dark .btn-send--recording,
.dark .btn-send--recording:hover:not(:disabled) {
  background-color: #ef4444;
  color: #ffffff;
}

/* One microphone per row; the chosen one carries a check. */
.mic-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.45rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-align: left;
  color: rgba(19, 26, 44, 0.75);
  background-color: transparent;
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out);
  outline: none;
}

.mic-option:hover,
.mic-option:focus-visible {
  background-color: rgba(219, 234, 254, 0.5);
  color: rgb(19, 26, 44);
}

.mic-option--active {
  color: rgb(19, 26, 44);
}

.mic-option-mark {
  flex-shrink: 0;
  width: 0.75rem;
  font-size: 0.625rem;
  opacity: 0;
}

.mic-option-mark--on {
  opacity: 0.85;
}

.mic-option-tag {
  flex-shrink: 0;
  margin-left: auto;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  font-size: 0.5625rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(19, 26, 44, 0.6);
  background-color: rgba(219, 234, 254, 0.7);
}

.dark .mic-option {
  color: rgba(219, 234, 254, 0.7);
}

.dark .mic-option:hover,
.dark .mic-option:focus-visible,
.dark .mic-option--active {
  color: rgba(255, 255, 255, 0.95);
}

.dark .mic-option:hover,
.dark .mic-option:focus-visible {
  background-color: rgba(255, 255, 255, 0.07);
}

.dark .mic-option-tag {
  color: rgba(255, 255, 255, 0.7);
  background-color: rgba(255, 255, 255, 0.1);
}

/* "Allow microphone access" — the same navy ink as the composer's send button */
.mic-allow {
  background: theme('colors.blue.950');
  box-shadow: var(--iw-shadow-2), inset 0 1px 0 rgba(255, 255, 255, 0.12);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.mic-allow:hover {
  background: theme('colors.blue.900');
}

.mic-allow:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.dark .mic-allow {
  background: #f3ede2;
}

.dark .mic-allow:hover {
  background: #ffffff;
}
</style>
