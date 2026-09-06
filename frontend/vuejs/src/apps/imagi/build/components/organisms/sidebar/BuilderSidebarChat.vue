<template>
  <div v-if="!isCollapsed" class="iw-surface flex flex-col h-full bg-canvas transition-colors duration-300">
    <!-- Header: the ways out of here, and — on a subagent's thread — whose
         thread it is. The main thread goes unnamed: it is the one the user
         drives and the one the workspace opens on, so "Main agent" was a
         caption on the thing you were already looking at. A subagent's
         read-only thread does keep its own name, which is now the whole way
         you tell the two apart at a glance: a name means you have stepped into
         somebody else's transcript. What the
         agent is doing right now is not here: it belongs under the message
         that set it going, so the transcript says it. Version restores live
         inline in the transcript (the
         per-message checkpoint chips), so the header carries no history
         controls.

         This is the workspace's junction: everything else in it is one hop
         from here, which is why the main thread is the only pane offering more
         than one destination. -->
    <WorkspacePaneHeader
      :title="headerTitle"
      :status="headerStatus"
      :state="headerState"
      :switches="paneSwitches"
      @switch="onPaneSwitch"
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
        :show-activity="!isLeadThread"
        @restore-checkpoint="emit('restore-checkpoint', $event)"
        @open-task="onOpenTask"
        class="flex-1"
      />
    </div>

    <!-- Chat Input Section (fixed at bottom). Relative so the usage panel
         can anchor to the full section width — the sidebar clips overflow,
         so a panel anchored to its narrow button couldn't fit. -->
    <div class="shrink-0 relative bg-canvas transition-colors duration-300">
      <!-- Model + reasoning panel (opens upward above the composer): a named
           list for which model thinks and a segmented dial for how hard it
           thinks, in one place — the two are one decision about the same
           trade-off, so they share a dropdown rather than trading places in
           two. Every option is visible, named and priced at once, so a
           trackpad user clicks once and a keyboard user arrows once.

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
        <div class="popover__head flex items-center justify-between gap-2 px-3 py-2">
          <span class="text-[11px] font-semibold uppercase tracking-wider text-blue-950/50 dark:text-white/50">
            Model
          </span>
          <span class="text-[11px] font-medium text-blue-950/70 dark:text-white/70 truncate">
            {{ currentModel?.name || '—' }}
          </span>
        </div>
        <!-- Body scrolls on short viewports so the panel never grows past the
             top of the sidebar (the usage panel's recipe). -->
        <div class="iw-scroll max-h-[min(24rem,calc(100vh-19rem))] overflow-y-auto">
          <!-- Roving-tabindex radiogroup: arrows move focus and select at
               once, as a native radio does. -->
          <div class="p-1.5" role="radiogroup" aria-label="Model, faster to smarter" @keydown="onModelKey">
            <button
              v-for="(m, i) in orderedModels"
              :key="m.id"
              :ref="el => (modelRowEls[i] = el as HTMLButtonElement | null)"
              type="button"
              role="radio"
              :aria-checked="m.id === currentModel?.id"
              :tabindex="m.id === currentModel?.id ? 0 : -1"
              :aria-labelledby="`tune-name-${m.id}`"
              :aria-describedby="`tune-desc-${m.id} tune-cost-${m.id}`"
              :disabled="!activeInstance"
              class="tune-row iw-press"
              :class="{ 'tune-row--on': m.id === currentModel?.id }"
              @click="pickModel(m.id)"
            >
              <i class="fas fa-check tune-row__mark" aria-hidden="true"></i>
              <!-- A radio names itself from its content, which would swallow
                   the blurb and the cost sentence and then read the blurb
                   again as the description; the name line and the two
                   descriptions are wired up by id instead. -->
              <span class="min-w-0">
                <span :id="`tune-name-${m.id}`" class="flex items-baseline gap-1.5 min-w-0">
                  <span class="tune-row__name">{{ modelShortName(m.id) }}</span>
                  <span class="tune-row__gen">{{ modelGeneration(m) }}</span>
                  <span v-if="m.id === defaultModelId" class="tune-row__tag">Default</span>
                </span>
                <span :id="`tune-desc-${m.id}`" class="tune-row__desc" :title="modelBlurb(m.id)">{{ modelBlurb(m.id) }}</span>
              </span>
              <!-- The multiple is information, not a warning: neutral ink,
                   spelled out for screen readers. -->
              <span class="tune-row__cost" aria-hidden="true">{{ modelCostLabel(m.id) }}</span>
              <span :id="`tune-cost-${m.id}`" class="sr-only">{{ modelCostText(m.id) }}</span>
            </button>
          </div>

          <div class="popover__head popover__head--mid flex items-center justify-between gap-2 px-3 py-2">
            <span class="text-[11px] font-semibold uppercase tracking-wider text-blue-950/50 dark:text-white/50">
              Reasoning
            </span>
            <span class="text-[11px] font-medium text-blue-950/70 dark:text-white/70 truncate">
              {{ currentEffort?.name || '—' }}
            </span>
          </div>

          <div class="px-3 pt-2.5 pb-2.5">
            <div
              class="tune-dial"
              role="radiogroup"
              aria-label="Reasoning effort, faster to smarter"
              aria-describedby="tune-effort-hint"
              @keydown="onEffortKey"
              @mouseleave="hintEffort = null"
            >
              <!-- The thumb slides under the chosen segment; its width is a
                   quarter of the track inside the 2px padding, so translateX
                   in whole multiples of itself lands on each segment. -->
              <span class="tune-dial__thumb" aria-hidden="true" :style="{ transform: `translateX(${effortIndex * 100}%)` }"></span>
              <button
                v-for="(o, i) in effortOptions"
                :key="o.id"
                :ref="el => (effortSegEls[i] = el as HTMLButtonElement | null)"
                type="button"
                role="radio"
                :aria-checked="o.id === currentEffort?.id"
                :tabindex="o.id === currentEffort?.id ? 0 : -1"
                :disabled="!activeInstance"
                class="tune-dial__seg iw-press"
                :class="{ 'tune-dial__seg--on': o.id === currentEffort?.id }"
                @mouseenter="hintEffort = o"
                @click="pickEffort(o.id)"
              >{{ o.name }}</button>
            </div>
            <!-- What the rung under the pointer (else the chosen one) means.
                 Only the mouse previews, so a screen reader hears selections,
                 not chatter; the min-height holds the line while it is empty. -->
            <p id="tune-effort-hint" class="tune-hint" aria-live="polite">
              <strong class="font-semibold">{{ hintOption?.name }}</strong><template v-if="hintOption"> — {{ hintOption.description }}</template>
            </p>
            <p class="tune-note">Smarter models and more reasoning use your plan's usage faster.</p>
          </div>
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
          <span class="text-[11px] font-semibold uppercase tracking-wider text-blue-950/50 dark:text-white/50">
            Usage
          </span>
          <span class="text-[11px] font-medium text-blue-950/70 dark:text-white/70 truncate">
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
          <span class="text-[11px] font-semibold uppercase tracking-wider text-blue-950/50 dark:text-white/50">
            Microphone
          </span>
          <span class="text-[11px] font-medium text-blue-950/70 dark:text-white/70 truncate">
            {{ micActive?.label || (micLabelsHidden ? 'Not allowed yet' : 'System default') }}
          </span>
        </div>
        <div v-if="micLabelsHidden || micInputs.length === 0" class="px-3 py-3">
          <p class="text-[11px] leading-snug text-blue-950/60 dark:text-white/55">
            Allow microphone access to see and choose your microphones. Until
            then, dictation records from your computer's default input.
          </p>
          <button
            type="button"
            class="mic-allow iw-press mt-2 w-full rounded-full px-3 py-1.5 text-[11px] font-semibold text-paper dark:text-blue-950"
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
          <p class="px-3 pb-2 pt-1.5 text-[10px] leading-snug text-blue-950/45 dark:text-white/40">
            Your computer's built-in microphone is used unless you pick another.
          </p>
        </div>
      </div>
      </Transition>

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
            class="btn-back-to-lead iw-press mt-2 w-full rounded-full px-3 py-1.5 text-[11px] font-semibold text-paper dark:text-blue-950"
            @click="goToLead"
          >
            Back to main thread
          </button>
        </div>
      </div>

      <div v-else class="px-2 pt-1 pb-3">
        <!-- Check-in queue: subagents reporting back, one card at a time —
             a question to answer, or the news that one finished -->
        <CheckInQueue
          v-if="isLeadThread"
          :queue="store.checkIns"
          :busy="resolvingCheckIn"
          @accept="emit('check-in-accept', $event)"
          @dismiss="emit('check-in-dismiss', $event)"
          @answer="onAnswerCheckIn"
          @skip="onSkipCheckIn"
          @view="onViewCheckIn"
          @retry="onRetryCheckIn"
        />

        <!-- Queued prompt: one message held while the agent works. It slides
             in above the composer and slides back out when it fires, so the
             hand-off from "held" to "sent" is something you watch happen. -->
        <Transition name="queued">
        <div
          v-if="activeInstance?.queuedPrompt"
          class="queued-row flex items-center gap-2 rounded-xl border border-blue-100 dark:border-white/[0.08] bg-blue-50/60 dark:bg-white/[0.04] px-2.5 py-1.5 mb-1.5"
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
            class="queued-cancel iw-press shrink-0 inline-flex items-center justify-center w-6 h-6 rounded-full text-blue-950/40 dark:text-white/40 hover:bg-blue-100/70 dark:hover:bg-white/[0.08] hover:text-blue-950/70 dark:hover:text-white/70"
            @click="cancelQueuedPrompt"
          >
            <i class="fas fa-times text-[10px]"></i>
          </button>
        </div>
        </Transition>

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
              <!-- Model + reasoning: one chip naming both ("Terra · Medium"),
                   opening the model list and the reasoning dial together. -->
              <div ref="tuneRoot" class="min-w-0">
                <button
                  type="button"
                  title="Model and reasoning"
                  aria-label="Model and reasoning"
                  aria-controls="tune-panel"
                  :aria-expanded="tuneOpen"
                  :disabled="!activeInstance"
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

            <!-- The one button, and it stays the microphone: hold to dictate,
                 click to send (or to stop a run in flight). The glyph never
                 turns into an arrow once there is text, because the words in
                 the box are as likely to be added to — record, read it over,
                 record some more — as sent, and a button that had become
                 "send" would say the mic was gone. What changes is the fill
                 (navy once a click has something to do) and the run-in-flight
                 state, where a click stops the agent and so wears the stop
                 glyph. Recording turns it red with a ring that swells with
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
              :disabled="!activeInstance || isTranscribing"
              class="btn-send iw-press flex shrink-0 items-center justify-center w-9 h-9 rounded-full"
              :class="sendClass"
              :style="isRecording ? micRingStyle : undefined"
              @pointerdown="onSendPointerDown"
              @pointerup="onSendPointerUp"
              @pointercancel="onSendPointerUp"
              @contextmenu.prevent="toggleMic"
              @click="onSendClick"
            >
              <i v-if="isTranscribing" class="fas fa-circle-notch fa-spin text-[13px]"></i>
              <i v-else-if="isRecording" class="fas fa-microphone text-[13px]"></i>
              <i v-else-if="activeInstance?.isProcessing" class="fas fa-stop text-sm"></i>
              <i v-else-if="!dictationSupported" class="fas fa-arrow-up text-sm"></i>
              <i v-else class="fas fa-microphone text-[13px]"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onBeforeUnmount, watch } from 'vue'
import { useAgentStore } from '../../../stores/agentStore'
// The workspace's shared motion + material vocabulary (curves, durations,
// radii, elevation, focus ring). Imported by each pane that spends it rather
// than by an ancestor layout: a var(--iw-*) with no token behind it resolves
// to nothing, which would leave this pane's popovers transparent.
import '../../../styles/workspace.css'
import { useUsageStore, formatResetTime } from '@/shared/stores/usage'
import { ChatConversation } from '../../organisms/chat'
import CheckInQueue from '../../molecules/sidebar/CheckInQueue.vue'
import { isBuiltInInput, useDictation } from '../../../composables/useDictation'
import WorkspacePaneHeader from '../../molecules/sidebar/WorkspacePaneHeader.vue'
import type { AIMessage, AIModel } from '../../../types/index'
import type { CheckInDto, ReasoningEffort, ReasoningEffortOption } from '../../../types/services'
import { reasoningEffortsForModel } from '../../../types/services'

// Props
const props = defineProps<{
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
  /** Look in on a subagent — it opens in the Subagents pane, never here */
  (e: 'open-task', conversationId: number): void
  /** Go and watch the app being built. Only reachable from here below the md
   *  breakpoint; on desktop the preview already sits beside this pane. */
  (e: 'open-preview'): void
}>()

const store = useAgentStore()
const activeInstance = computed(() => store.activeInstance)
const prompt = ref('')
const promptTextarea = ref<HTMLTextAreaElement | null>(null)

// The user drives everything from the lead thread; a task's thread is a
// read-only record of what a background subagent did.
const isTaskThread = computed(() => activeInstance.value?.kind === 'task')
const isLeadThread = computed(() => activeInstance.value?.kind === 'lead')

// The main thread wears no name at all. Its conversation name is never
// surfaced, and labelling it "Main agent" only told you what the pane you were
// already typing into was. Subagent threads do show their own name — that is
// what makes an unnamed masthead legible, because a name now means you are
// reading somebody else's thread rather than your own.
const headerTitle = computed(() =>
  isTaskThread.value ? (activeInstance.value?.title || 'Background agent') : ''
)

/** Where you can go from the main thread. Subagents first — it is the nearer
 *  room, and the one that reports back here. The preview is the outer wall of
 *  the workspace, so it sits outermost; on desktop it is already on screen
 *  beside this pane, which is what `mobileOnly` says. */
const paneSwitches = computed(() => [
  {
    id: 'manager',
    icon: 'fas fa-layer-group',
    label: 'Subagents',
    // Both read the same number, and that is the point rather than a
    // duplication: the dot on the icon says something is alive over there and
    // can be caught without looking, the badge says how much. Working right
    // now, not how many exist — see workingAgentCount for why.
    live: store.workingAgentCount > 0,
    count: store.workingAgentCount,
    direction: 'forward' as const,
  },
  {
    id: 'preview',
    icon: 'fas fa-globe',
    label: 'Preview',
    direction: 'forward' as const,
    mobileOnly: true,
  },
])

function onPaneSwitch(id: string) {
  if (id === 'manager') emit('toggleManager')
  else if (id === 'preview') emit('open-preview')
}

/** The header's second line: where this thread stands while nothing is
 *  running. A live run is narrated in the transcript instead, directly under
 *  the message that started it — that is where you are looking when you have
 *  just sent something, and it puts "Thinking…" next to the thing being
 *  thought about rather than in a corner of the masthead. So the plate goes
 *  quiet the moment a run starts and only speaks between them. */
const headerStatus = computed(() => {
  const instance = activeInstance.value
  if (instance?.isProcessing) return ''
  // No "background agent" prefix: the muted mark and the note above the
  // composer already say that, and the sidebar is too narrow to spend
  // characters twice. These match the manager's card labels word for word.
  if (isTaskThread.value) {
    switch (instance?.reviewStatus) {
      case 'input': return 'Asked you a question'
      case 'ready': return 'Subagent complete — one of your options'
      case 'failed': return 'Stopped before finishing'
      case 'accepted': return 'Subagent complete'
      case 'dismissed': return 'Discarded'
      default: return 'Read only'
    }
  }
  // Not everything in the queue is owed an answer: a subagent that finished
  // put its work in the app on its own, so its card is news to read. Saying
  // "1 agent is waiting on you" over a card with nothing to decide sends the
  // user looking for a decision that does not exist.
  const waiting = store.checkIns.filter(c => c.kind !== 'done').length
  if (waiting > 0) {
    return `${waiting} ${waiting === 1 ? 'agent is' : 'agents are'} waiting on you`
  }
  const finished = store.checkIns.length
  if (finished > 0) {
    return `${finished} ${finished === 1 ? 'subagent' : 'subagents'} finished`
  }
  // Nothing running and nothing waiting: the plate is just the thread's name.
  // "Ready when you are" was a line spent saying that no line was needed.
  return ''
})

/** The dot beside that line, in the crew ledger's three-token vocabulary.
 *  Never 'working' — a live run has no line here to mark. */
const headerState = computed<'waiting' | 'idle'>(() => {
  const instance = activeInstance.value
  if (isTaskThread.value) {
    const status = instance?.reviewStatus
    return status === 'input' || status === 'ready' || status === 'failed'
      ? 'waiting'
      : 'idle'
  }
  // Same split as the line above it: only a card that owes the user something
  // lights the dot.
  return store.checkIns.some(c => c.kind !== 'done') ? 'waiting' : 'idle'
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
function onViewCheckIn(checkIn: CheckInDto) {
  emit('open-task', checkIn.task.id)
}

/** Run a failed subagent again. The store drops this card as it goes: the
 *  run's start retires the error server-side, and the run end files whatever
 *  comes next. */
function onRetryCheckIn(checkIn: CheckInDto) {
  store.retryTask(checkIn.task.id)
}

/** A dispatch card in the transcript was clicked — open that subagent's
 *  thread over in the Subagents pane, so this thread keeps its place. */
function onOpenTask(conversationId: number) {
  emit('open-task', conversationId)
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

// Escape closes the tuning panel from anywhere, not only while focus is
// inside it — a keyboard user who Tabs past the last segment would otherwise
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

// --- Model + reasoning popover (the model list and the reasoning dial share one panel) ---

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

// The models offered in the composer. This used to filter on a 'gpt-5.6'
// prefix, which silently hid GPT 6 Astra; it matches the whole GPT family now,
// so a new generation shows up without another edit here.
const SELECTABLE_MODEL_PATTERN = /^gpt-/
const modelOptions = computed<AIModel[]>(() => {
  const available = (store.availableModels || []).filter(model =>
    SELECTABLE_MODEL_PATTERN.test(model.id)
  )
  if (available.length > 0) {
    return available
  }
  return [
    { id: 'gpt-5.6-terra', name: 'GPT 5.6 Terra', provider: 'openai' } as AIModel,
    { id: 'gpt-5.6-sol', name: 'GPT 5.6 Sol', provider: 'openai' } as AIModel,
    { id: 'gpt-5.6-luna', name: 'GPT 5.6 Luna', provider: 'openai' } as AIModel,
    { id: 'gpt-6-astra', name: 'GPT 6 Astra', provider: 'openai' } as AIModel
  ]
})

const effortOptions = computed<ReasoningEffortOption[]>(() =>
  reasoningEffortsForModel(activeInstance.value?.selectedModelId)
)

// Models ranked faster → smarter (Luna is light/fast, Astra is the frontier)
// so the list reads top = faster, bottom = smarter. Unknown ids sort last but
// still appear, so the list degrades gracefully if the suite changes.
const MODEL_RANK: Record<string, number> = {
  'gpt-5.6-luna': 0,
  'gpt-5.6-terra': 1,
  'gpt-5.6-sol': 2,
  'gpt-6-astra': 3,
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

/** The distinctive part of the model name for the compact chip ("Terra",
 *  "Astra"), dropping the "GPT <version>" prefix whichever generation it is. */
function modelShortName(id?: string | null): string {
  const model = orderedModels.value.find(m => m.id === id) ?? currentModel.value
  if (!model) return 'Model'
  return model.name.replace(/^GPT\s*\d+(?:\.\d+)?\s*/i, '').trim() || model.name
}

// effortOptions is the one ladder every model shares, ordered faster →
// smarter. The store re-seats a legacy selectedEffort onto it when the model
// changes, so the dial can't point at a rung the next request would reject —
// and changing model never moves the dial.
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

/** The chip reads "Terra · Medium": the model's short name and the reasoning
 *  rung, so both settings are legible without opening anything. */
const tuneLabel = computed(
  () => `${modelShortName(activeInstance.value?.selectedModelId)} · ${effortLabel(activeInstance.value?.selectedEffort)}`
)

const DEFAULT_MODEL_ID = 'gpt-5.6-terra'
// The catalog flags its default; the composer's fallback list carries no
// flag, so the tag settles on Terra rather than vanishing.
const defaultModelId = computed(
  () => orderedModels.value.find(m => m.default)?.id ?? DEFAULT_MODEL_ID
)

// Static: the models endpoint does not send prices, and the composer's
// fallback list has none — the ratios are input price relative to Luna.
const MODEL_META: Record<string, { blurb: string; cost: number }> = {
  'gpt-5.6-luna': { blurb: 'Light and fast for quick edits', cost: 1 },
  'gpt-5.6-terra': { blurb: 'Balanced for everyday building', cost: 3 },
  'gpt-5.6-sol': { blurb: 'Flagship for demanding work', cost: 6 },
  'gpt-6-astra': { blurb: 'Frontier — the hardest work, 1M context', cost: 20 },
}
const modelBlurb = (id: string) => MODEL_META[id]?.blurb ?? ''
const modelCostLabel = (id: string) => {
  const c = MODEL_META[id]?.cost
  return c ? `${c}×` : '—'
}
const modelCostText = (id: string) => {
  const c = MODEL_META[id]?.cost
  if (!c) return ''
  return c === 1 ? 'Uses the least usage per token' : `Uses about ${c} times Luna's usage per token`
}

/** "GPT 5.6" / "GPT 6" — the prefix modelShortName strips. */
function modelGeneration(m: AIModel): string {
  const g = m.name.match(/^GPT\s*\d+(?:\.\d+)?/i)
  return g ? g[0].replace(/\s+/, ' ') : ''
}

const modelRowEls = ref<(HTMLButtonElement | null)[]>([])
const effortSegEls = ref<(HTMLButtonElement | null)[]>([])
// The rung under the pointer, previewed in the hint line; the chosen rung
// otherwise.
const hintEffort = ref<ReasoningEffortOption | null>(null)
const hintOption = computed(() => hintEffort.value ?? currentEffort.value)

function pickModel(id: string) {
  if (id !== activeInstance.value?.selectedModelId) void handleModelSelect(id)
}

function pickEffort(id: ReasoningEffort) {
  // A pick ends the preview: an arrow key can land on a rung other than the
  // one the pointer happens to rest on, and the hint must follow the pick.
  hintEffort.value = null
  if (id !== activeInstance.value?.selectedEffort) void handleEffortSelect(id)
}

/** Roving radio keys: arrows wrap, Home/End jump; moving selects, as a
 *  native radio does. Each step is one idempotent write to the workspace. */
function roveKey(
  e: KeyboardEvent,
  count: number,
  index: number,
  els: (HTMLButtonElement | null)[],
  select: (i: number) => void
) {
  if (count === 0) return
  let next = index
  if (e.key === 'ArrowDown' || e.key === 'ArrowRight') next = (index + 1) % count
  else if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') next = (index - 1 + count) % count
  else if (e.key === 'Home') next = 0
  else if (e.key === 'End') next = count - 1
  else return
  e.preventDefault()
  els[next]?.focus()
  select(next)
}
const onModelKey = (e: KeyboardEvent) =>
  roveKey(e, orderedModels.value.length, modelIndex.value, modelRowEls.value, i =>
    pickModel(orderedModels.value[i]!.id)
  )
const onEffortKey = (e: KeyboardEvent) =>
  roveKey(e, effortOptions.value.length, effortIndex.value, effortSegEls.value, i =>
    pickEffort(effortOptions.value[i]!.id)
  )

/** Escape: the panel goes and focus returns to the chip that opened it, so a
 *  keyboard user is not dropped on the page body. */
function closeTune() {
  tuneOpen.value = false
  void nextTick(() => tuneRoot.value?.querySelector<HTMLButtonElement>('button')?.focus())
}

watch(tuneOpen, open => {
  hintEffort.value = null
  // Focus lands on the chosen model row, so the arrows work straight away.
  if (open) void nextTick(() => modelRowEls.value[modelIndex.value]?.focus())
})

// --- Dictation (holding the send button, and ⌘D) ---

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
  toggle: toggleDictation,
  start: startDictation,
  stop: stopDictation,
  cancel: cancelDictation,
  selectInput: selectMicInput,
  unlockInputs: unlockMicInputs,
  refreshInputs: refreshMicInputs,
} = useDictation({ onTranscript: insertDictation })

const isRecording = computed(() => dictationState.value === 'recording')
const isTranscribing = computed(() => dictationState.value === 'transcribing')

/** The red ring around a live mic widens with the voice it hears, so "is it
 *  picking me up?" is answered by looking rather than by sending a clip. */
const micRingStyle = computed(() => ({
  '--dictate-ring': `${2 + Math.round(dictationLevel.value * 10)}px`,
}))

function toggleMic() {
  // Nothing to pick from where the browser cannot record, and a right-click
  // on a disabled button is still a right-click.
  if (!dictationSupported || !activeInstance.value) return
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
  if (isRecording.value) return `Stop dictating (${dictationShortcut})`
  const running = !!activeInstance.value?.isProcessing
  if (!dictationSupported) return running ? 'Stop agent' : 'Send (Enter)'
  const click = running ? 'click to stop the agent' : 'click to send (Enter)'
  return `Hold to dictate (${dictationShortcut}) · ${click} · right-click to choose microphone`
})

/** Navy ink when a click does something (there is text to send, or a run to
 *  stop); red while the mic is live; a ghost otherwise — still pressable,
 *  because a hold records into an empty box. The fill is all that changes
 *  with the text: the glyph stays a microphone. */
const sendClass = computed(() => {
  if (isRecording.value) return 'btn-send--recording'
  if (activeInstance.value && (prompt.value.trim() || activeInstance.value.isProcessing)) {
    return 'btn-send--active text-paper dark:text-blue-950'
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
  if (!activeInstance.value || isTranscribing.value) return
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
    // Already live from ⌘D: the hold simply takes over, and its release stops.
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
  // The mic was opened with ⌘D: a tap closes it, and the next tap sends the
  // words it produced.
  if (isRecording.value) {
    stopDictation()
    return
  }
  if (activeInstance.value?.isProcessing) {
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

/** ⌘D from anywhere in the workspace — the point of a shortcut is not having
 *  to find the button first. Left alone when the preview has already taken
 *  the keystroke for the app it is showing (it calls preventDefault), on a
 *  read-only task thread (no composer), and where the browser cannot record. */
function onDictationKey(e: KeyboardEvent) {
  if (e.defaultPrevented) return
  const modifier = isApplePlatform ? e.metaKey : e.ctrlKey
  if (!modifier || e.altKey || e.shiftKey || (e.key || '').toLowerCase() !== 'd') return
  if (!dictationSupported || isTaskThread.value || !activeInstance.value) return
  e.preventDefault()
  toggleDictation()
}

onMounted(() => document.addEventListener('keydown', onDictationKey))
onBeforeUnmount(() => document.removeEventListener('keydown', onDictationKey))

// A task thread has no composer, so a mic left open there would have nowhere
// to put its words.
watch(isTaskThread, readOnly => {
  if (readOnly) cancelDictation()
})

const promptPlaceholder = computed(() => {
  if (isRecording.value) {
    const mic = micActive.value?.label || 'the default microphone'
    return `Listening on ${mic}… let go of the button, or press ${dictationShortcut}, when you're done.`
  }
  if (isTranscribing.value) return 'Transcribing…'
  return 'Ask me to build, edit, or explain anything in your project...'
})

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
  
  // Spread, never a field whitelist: everything a message carries beyond the
  // four fields defaulted here — activity feed, plan, files-changed chip, cost
  // caption, dispatch cards, checkpoint — is the transcript's content, and a
  // whitelist silently drops whatever it was not updated to know about.
  const validMessages = filteredMessages
    .filter(m => m && typeof m === 'object' && m.role)
    .map(m => ({
      ...m,
      content: m.content || '',
      code: m.code || '',
      timestamp: m.timestamp || new Date().toISOString(),
      id: m.id || `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
    })) as AIMessage[]

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
  border-color: rgba(23, 37, 84, 0.4);
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
  color: rgba(23, 37, 84, 0.75);
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

/* Model rows — the chip's ghost / hover / active tints, one per row, so the
   open chip and the chosen row wear the same colour. The 6px gutter around
   the group makes a selected row read as a pill inside the card. */
.tune-row {
  display: grid;
  grid-template-columns: 0.75rem minmax(0, 1fr) auto;
  column-gap: 0.5rem;
  align-items: center;
  width: 100%;
  /* Two text lines are 31px; 4px of padding lets min-height set the 40px. */
  min-height: 2.5rem;
  padding: 0.25rem 0.5rem;
  border-radius: var(--iw-r-sm);
  text-align: left;
  color: rgba(23, 37, 84, 0.75);
  background-color: transparent;
  cursor: pointer;
  outline: none;
  --iw-focus-base: rgb(var(--iw-surface));
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.tune-row:hover:not(:disabled):not(.tune-row--on) {
  background-color: rgba(219, 234, 254, 0.5);
  color: rgb(23, 37, 84);
}

.tune-row--on {
  background-color: rgba(219, 234, 254, 0.7);
  color: rgb(23, 37, 84);
}

.tune-row:focus-visible {
  position: relative;
  z-index: 1;
  box-shadow: var(--iw-focus-ring);
}

.tune-row:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dark .tune-row {
  color: rgba(219, 234, 254, 0.7);
}

.dark .tune-row:hover:not(:disabled):not(.tune-row--on) {
  background-color: rgba(255, 255, 255, 0.07);
  color: rgba(255, 255, 255, 0.95);
}

.dark .tune-row--on {
  background-color: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.tune-row__mark {
  font-size: 0.625rem;
  opacity: 0;
  transition: opacity var(--iw-dur-2) var(--iw-ease-out);
}

.tune-row--on .tune-row__mark {
  opacity: 0.85;
}

.tune-row__name {
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1rem;
}

.tune-row__gen {
  font-size: 0.625rem;
  font-weight: 500;
  font-variant-numeric: tabular-nums;
  opacity: 0.75;
}

/* Centred, not baseline-aligned: a padded pill hanging off the baseline
   would make the tagged row taller than its neighbours. */
.tune-row__tag {
  flex-shrink: 0;
  align-self: center;
  padding: 0.1rem 0.4rem;
  line-height: 0.75rem;
  border-radius: 999px;
  font-size: 0.5625rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: rgba(23, 37, 84, 0.6);
  background-color: rgba(219, 234, 254, 0.7);
}

/* On a hovered or selected row the pill would otherwise vanish into the
   row's own tint, so there it is cut from ink instead. */
.tune-row--on .tune-row__tag,
.tune-row:hover:not(:disabled) .tune-row__tag {
  background-color: rgba(23, 37, 84, 0.08);
}

.dark .tune-row__tag {
  color: rgba(255, 255, 255, 0.7);
  background-color: rgba(255, 255, 255, 0.1);
}

.dark .tune-row--on .tune-row__tag,
.dark .tune-row:hover:not(:disabled) .tune-row__tag {
  background-color: rgba(255, 255, 255, 0.14);
}

.tune-row__desc {
  display: block;
  font-size: 0.6875rem;
  line-height: 0.9375rem;
  opacity: 0.85;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tune-row__cost {
  font-size: 0.625rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  font-variant-numeric: tabular-nums;
  opacity: 0.75;
}

/* Reasoning dial: a track, a sliding thumb in the send button's navy (cream
   in dark), and four labels the thumb passes under. */
.tune-dial {
  position: relative;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  padding: 2px;
  border-radius: var(--iw-r-sm);
  background: rgba(var(--iw-ink), 0.06);
}

.dark .tune-dial {
  background: rgba(255, 255, 255, 0.06);
}

/* Width and offset must match the track's 2px padding and gap-less grid
   exactly, since translateX counts in multiples of the thumb's own width. */
.tune-dial__thumb {
  position: absolute;
  top: 2px;
  bottom: 2px;
  left: 2px;
  width: calc((100% - 4px) / 4);
  border-radius: var(--iw-r-xs);
  background: theme('colors.blue.950');
  box-shadow: var(--iw-shadow-1), inset 0 1px 0 rgba(255, 255, 255, 0.12);
  pointer-events: none;
  transition: transform var(--iw-dur-2) var(--iw-ease-out);
}

.dark .tune-dial__thumb {
  background: #f3ede2;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25);
}

.tune-dial__seg {
  position: relative;
  z-index: 1;
  height: 1.75rem;
  border-radius: var(--iw-r-xs);
  font-size: 0.6875rem;
  font-weight: 600;
  white-space: nowrap;
  color: rgba(23, 37, 84, 0.65);
  background: transparent;
  cursor: pointer;
  outline: none;
  --iw-focus-base: rgb(var(--iw-surface));
  transition:
    color var(--iw-dur-2) var(--iw-ease-out),
    background-color var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.tune-dial__seg:hover:not(:disabled):not(.tune-dial__seg--on) {
  color: rgb(23, 37, 84);
  background-color: rgba(23, 37, 84, 0.05);
}

.tune-dial__seg--on {
  color: #ffffff;
}

.tune-dial__seg:focus-visible {
  box-shadow: var(--iw-focus-ring);
}

.tune-dial__seg:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dark .tune-dial__seg {
  color: rgba(219, 234, 254, 0.65);
}

.dark .tune-dial__seg:hover:not(:disabled):not(.tune-dial__seg--on) {
  color: rgba(255, 255, 255, 0.95);
  background-color: rgba(255, 255, 255, 0.06);
}

.dark .tune-dial__seg--on {
  color: theme('colors.blue.950');
}

/* "Extra High" needs ~74px at 11px; on the narrowest sidebars it steps down
   rather than wrapping or abbreviating. */
@media (max-width: 360px) {
  .tune-dial__seg {
    font-size: 0.625rem;
  }
}

/* One line holds every rung's copy down to a 300px column, so the panel does
   not reserve a second. The opacities here and above clear 4.5:1 for 11px
   text over the glass; the 10px figures are backed by sr text. */
.tune-hint {
  margin-top: 0.5rem;
  min-height: 1rem;
  font-size: 0.6875rem;
  line-height: 1rem;
  color: rgba(23, 37, 84, 0.7);
}

.dark .tune-hint {
  color: rgba(255, 255, 255, 0.55);
}

.tune-note {
  margin-top: 0.5rem;
  font-size: 0.625rem;
  line-height: 0.875rem;
  color: rgba(23, 37, 84, 0.55);
}

.dark .tune-note {
  color: rgba(255, 255, 255, 0.5);
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

/* Back-to-main-thread button on a read-only task thread — same navy ink
   recipe as the composer's send button */
.btn-back-to-lead {
  background: theme('colors.blue.950');
  box-shadow: var(--iw-shadow-2), inset 0 1px 0 rgba(255, 255, 255, 0.12);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.btn-back-to-lead:hover {
  background: theme('colors.blue.900');
  box-shadow: var(--iw-shadow-3), inset 0 1px 0 rgba(255, 255, 255, 0.12);
}

.btn-back-to-lead:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.dark .btn-back-to-lead {
  background: #f3ede2;
}

.dark .btn-back-to-lead:hover {
  background: #ffffff;
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
  color: rgba(23, 37, 84, 0.45);
  box-shadow: var(--iw-shadow-1);
}

.btn-send--idle:hover:not(:disabled) {
  background-color: rgba(219, 234, 254, 0.9);
  color: rgba(23, 37, 84, 0.7);
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
  color: rgba(23, 37, 84, 0.75);
  background-color: transparent;
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out);
  outline: none;
}

.mic-option:hover,
.mic-option:focus-visible {
  background-color: rgba(219, 234, 254, 0.5);
  color: rgb(23, 37, 84);
}

.mic-option--active {
  color: rgb(23, 37, 84);
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
  color: rgba(23, 37, 84, 0.6);
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
