<template>
  <!-- Colours come from the --sl-* tokens; motion uses the one Spotlight curve
       (--lp-ease). The toolbar fits the pane, not the screen, so it is sized
       by a container query: beside the chat on a tablet the pane is
       phone-narrow even though the screen isn't. -->
  <div
    ref="rootRef"
    class="[--lp-ease:cubic-bezier(0.22,1,0.36,1)] relative flex flex-col w-full h-full min-h-0 bg-sl-bg text-sl-text [container-name:lp] [container-type:inline-size]"
    @keydown="onRootKeydown"
  >
    <!-- Toolbar: one 40px row. Navigation, the address, the servers' health,
         then the tools. Everything else is the app. -->
    <div
      class="relative z-[5] flex items-center gap-1.5 h-10 shrink-0 px-2 border-b border-b-sl-line bg-sl-surface dark:bg-sl-surface-2"
      role="toolbar"
      aria-label="Preview controls"
    >
      <button
        v-if="canReturnToChat"
        type="button"
        class="inline-flex items-center gap-[0.3125rem] h-[1.875rem] px-2.5 rounded-full bg-sl-chip-bg text-sl-muted text-[0.6875rem] shrink-0"
        aria-label="Back to the coordinator"
        @click="emit('return-to-chat')"
      >
        <i class="fas fa-chevron-left text-[0.5rem] opacity-60"></i>
        <i class="fas fa-comments"></i>
        <span
          v-if="returnCount"
          class="min-w-[1rem] px-1 rounded-full bg-sl-grad text-sl-on-accent text-[0.625rem] font-semibold"
        >{{ returnCount }}</span>
      </button>

      <div class="flex items-center gap-px shrink-0">
        <button type="button" :class="btnClass()" :disabled="!canGoBack || !appReady" title="Back" aria-label="Back" @click="goBack">
          <i class="fas fa-arrow-left"></i>
        </button>
        <button type="button" :class="btnClass()" :disabled="!canGoForward || !appReady" title="Forward" aria-label="Forward" @click="goForward">
          <i class="fas fa-arrow-right"></i>
        </button>
        <button
          type="button"
          :class="btnClass()"
          :disabled="!session"
          title="Reload (Shift-click for a hard reload)"
          aria-label="Reload"
          aria-keyshortcuts="Control+R Meta+R"
          @click="onReloadClick"
        >
          <i class="fas fa-rotate-right" :class="{ 'lp-spin': loadingPage }"></i>
        </button>
        <button
          type="button"
          :class="[btnClass(), '[@container_lp_(max-width:560px)]:hidden']"
          :disabled="!session"
          title="Home page"
          aria-label="Home page"
          @click="navigateTo('/')"
        >
          <i class="fas fa-house"></i>
        </button>
      </div>

      <!-- The address: the app's path, editable; pages to jump to below. One
           field with a border that deepens, never a ring; the focus ring goes
           around the whole pill, not the bare input inside it. -->
      <div
        ref="addressRoot"
        class="relative flex-1 min-w-0 flex items-center h-[1.875rem] pl-[0.6875rem] pr-3 rounded-full border
          [transition:border-color_0.2s_var(--lp-ease),background-color_0.2s_var(--lp-ease)] motion-reduce:[transition:none]
          has-[.lp-address-input:focus-visible]:outline has-[.lp-address-input:focus-visible]:outline-2
          has-[.lp-address-input:focus-visible]:outline-sl-focus has-[.lp-address-input:focus-visible]:outline-offset-2"
        :class="addressFocused
          ? 'border-sl-muted bg-sl-surface dark:bg-sl-bg-deep'
          : 'border-sl-line bg-sl-chip-bg hover:border-sl-line-strong'"
      >
        <i class="fas fa-lock shrink-0 mr-2 text-[0.5625rem] text-sl-faint" aria-hidden="true"></i>
        <input
          ref="addressInput"
          v-model="addressText"
          class="lp-address-input flex-1 min-w-0 h-full [border:0] ![outline:none] bg-transparent text-sl-text text-[0.75rem] [font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace]"
          type="text"
          spellcheck="false"
          autocomplete="off"
          role="combobox"
          aria-label="Address"
          aria-autocomplete="list"
          :aria-expanded="suggestionsOpen"
          aria-controls="lp-suggestions"
          aria-keyshortcuts="Control+L Meta+L"
          :aria-activedescendant="activeSuggestion >= 0 ? `lp-sugg-${activeSuggestion}` : undefined"
          :disabled="!session"
          @focus="onAddressFocus"
          @blur="onAddressBlur"
          @keydown="onAddressKeydown"
        />
        <ul
          v-if="suggestionsOpen"
          id="lp-suggestions"
          :class="['top-[calc(100%+0.375rem)] left-0 right-0 max-h-[60vh] overflow-y-auto p-1.5', POPOVER]"
          role="listbox"
          @mousedown.prevent
        >
          <template v-for="group in suggestionGroups" :key="group.name">
            <li class="pt-2 px-2.5 pb-1 text-[0.6875rem] font-semibold tracking-[0.14em] uppercase text-sl-muted" role="presentation">{{ group.name }}</li>
            <li
              v-for="item in group.items"
              :id="`lp-sugg-${item.index}`"
              :key="item.path"
              role="option"
              :aria-selected="item.index === activeSuggestion"
              class="flex items-baseline gap-3 py-[0.4375rem] px-2.5 rounded-[0.625rem] cursor-pointer text-[0.8125rem] text-sl-text"
              :class="item.index === activeSuggestion ? 'bg-sl-chip-bg-hover' : 'hover:bg-sl-chip-bg-hover'"
              @click="chooseSuggestion(item.path)"
            >
              <span class="flex-1 min-w-0 truncate" :class="item.path === currentPath && 'font-semibold'">{{ item.title }}</span>
              <span class="shrink-0 max-w-[45%] truncate [font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace] text-[0.6875rem] text-sl-muted">{{ item.path }}</span>
            </li>
          </template>
        </ul>
      </div>

      <!-- Health of the two dev servers; details and actions on click. A dot
           with a soft halo, and the word. -->
      <div ref="statusRoot" class="relative shrink-0">
        <button
          type="button"
          class="inline-flex items-center gap-[0.4375rem] h-[1.875rem] pl-2.5 pr-3 rounded-full border border-sl-line
            text-[0.6875rem] font-semibold text-sl-text whitespace-nowrap
            transition-[border-color] duration-200 ease-[var(--lp-ease)] motion-reduce:[transition:none] hover:border-sl-line-strong
            [@container_lp_(max-width:560px)]:px-[0.5625rem]"
          :aria-expanded="statusOpen"
          aria-haspopup="dialog"
          :title="overall.title"
          @click="statusOpen = !statusOpen"
        >
          <span :class="[DOT, overall.tone === 'idle' ? 'bg-sl-faint' : DOT_TONE[overall.tone]]" aria-hidden="true"></span>
          <span class="[@container_lp_(max-width:560px)]:hidden">{{ overall.label }}</span>
        </button>
        <div
          v-if="statusOpen"
          :class="['top-[calc(100%+0.375rem)] right-0 w-64 p-3', POPOVER]"
          role="dialog"
          aria-label="Your app's servers"
        >
          <p class="mb-2 text-[0.6875rem] font-semibold tracking-[0.14em] uppercase text-sl-muted">Your app's servers</p>
          <div v-for="row in serverRows" :key="row.key" class="flex items-center gap-2 py-[0.3125rem] text-[0.8125rem]">
            <span :class="[DOT, DOT_TONE[row.tone]]" aria-hidden="true"></span>
            <span class="flex-1">{{ row.name }}</span>
            <span class="text-sl-muted text-[0.75rem]">{{ row.label }}</span>
          </div>
          <p v-if="lastReload" class="mt-1.5 text-[0.75rem] text-sl-muted">Last reloaded {{ lastReload }}</p>
          <div class="grid gap-1 mt-2.5 pt-2.5 border-t border-t-sl-line">
            <button type="button" :class="[POP_ACTION, 'text-sl-text']" :disabled="!!actionBusy" @click="runAction('restart_frontend')">Restart frontend</button>
            <button type="button" :class="[POP_ACTION, 'text-sl-text']" :disabled="!!actionBusy" @click="runAction('restart_backend')">Restart backend</button>
            <button type="button" :class="[POP_ACTION, 'text-sl-text']" :disabled="!!actionBusy" @click="runAction('migrate')">Update the database</button>
            <button type="button" :class="[POP_ACTION, 'text-sl-bad']" :disabled="!!actionBusy" @click="runAction('reset_database')">Reset test data</button>
          </div>
          <p v-if="actionNote" class="mt-1.5 text-[0.75rem] text-sl-muted" aria-live="polite">{{ actionNote }}</p>
        </div>
      </div>

      <div class="flex items-center gap-px shrink-0">
        <button
          type="button"
          :class="btnClass(picking)"
          :disabled="!appReady"
          title="Pick an element to ask the agent about (Ctrl+Shift+C)"
          aria-label="Pick an element"
          :aria-pressed="picking"
          aria-keyshortcuts="Control+Shift+C Meta+Shift+C"
          @click="togglePicker"
        >
          <i class="fas fa-crosshairs"></i>
        </button>
        <button
          type="button"
          :class="btnClass(drawerOpen)"
          title="Console, network and server logs (Ctrl+J)"
          aria-label="Console, network and server logs"
          :aria-pressed="drawerOpen"
          aria-keyshortcuts="Control+J Meta+J"
          @click="drawerOpen = !drawerOpen"
        >
          <i class="fas fa-terminal"></i>
          <span
            v-if="errorCount"
            class="absolute top-px -right-px min-w-[0.9375rem] h-[0.9375rem] px-[0.1875rem] rounded-full bg-sl-bad text-white
              text-[0.5625rem] font-semibold leading-[0.9375rem] tabular-nums"
          >{{ errorCount > 99 ? '99+' : errorCount }}</span>
        </button>
        <button
          type="button"
          :class="[btnClass(), '[@container_lp_(max-width:560px)]:hidden']"
          :disabled="!session"
          title="Open in a new tab"
          aria-label="Open in a new tab"
          @click="openInNewTab"
        >
          <i class="fas fa-arrow-up-right-from-square"></i>
        </button>
      </div>

      <!-- Loading ribbon along the toolbar's lower edge. -->
      <div
        v-if="loadingPage"
        class="lp-slide absolute left-0 right-0 -bottom-px h-0.5 overflow-hidden pointer-events-none
          after:content-[''] after:absolute after:top-0 after:bottom-0 after:w-[30%] after:bg-sl-work"
        aria-hidden="true"
      ></div>
    </div>

    <!-- The stage: clipped, so nothing the app or its notes do can widen the pane. -->
    <div class="relative flex-1 min-h-0 overflow-hidden bg-sl-bg-deep">
      <!-- The app itself, rendered by this browser. Sandboxed on its own
           origin: it can run, post forms and open popups, never navigate
           Imagi or read anything of Imagi's. Remounted only by a hard reload
           or a server restart (iframeKey).
           width 1px + min-width 100%, not width 100%: iOS Safari grows an
           iframe to its page's width, so an app wider than the pane pushed the
           frame past it and the page slid sideways under a finger. -->
      <iframe
        v-if="iframeSrc"
        ref="frameRef"
        :key="iframeKey"
        :src="iframeSrc"
        class="block w-px min-w-full h-full [border:0] bg-white"
        title="Your app"
        sandbox="allow-scripts allow-forms allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-modals allow-downloads"
        allow="clipboard-write"
        referrerpolicy="same-origin"
        @load="onFrameLoad"
      ></iframe>

      <!-- Edit awareness: a quiet note when an edit lands. -->
      <transition v-bind="FADE">
        <p v-if="editNote" :class="[NOTE, 'text-sl-muted']" role="status">{{ editNote }}</p>
      </transition>

      <!-- An agent using the app in its own browser: the frame follows it
           to its page, and this says who it is and what it is doing. -->
      <transition v-bind="FADE">
        <p v-if="agentNote && !editNote" :class="[NOTE, 'inline-flex items-center gap-2 text-sl-text']" role="status" data-testid="agent-note">
          <span :class="[DOT, DOT_TONE.work]" aria-hidden="true"></span>
          {{ agentNote }}
        </p>
      </transition>

      <!-- Picking: say how to get out of it. -->
      <p v-if="picking" :class="[NOTE, 'text-sl-text']" role="status">Click anything in your app to ask the agent about it. Esc cancels.</p>

      <!-- The newest error. It has already gone to the agents (the status
           poll carries it to the coordinator, or to the thread that just
           changed that part of the app), so this only says so. -->
      <div
        v-if="bannerVisible && latestError"
        class="absolute left-3 right-3 bottom-3 z-[6] flex items-center gap-2.5 py-2 pr-2.5 pl-3 rounded-2xl border border-sl-line-strong
          bg-sl-surface dark:bg-sl-surface-2 [box-shadow:var(--sl-card-shadow),0_16px_36px_-16px_rgba(20,21,30,0.35)]"
        role="alert"
      >
        <span
          class="grid place-items-center shrink-0 w-6 h-6 rounded-full bg-[color:color-mix(in_srgb,var(--sl-bad)_14%,transparent)] text-sl-bad text-[0.6875rem]"
          aria-hidden="true"
        ><i class="fas fa-exclamation"></i></span>
        <div class="flex-1 min-w-0">
          <p class="text-[0.8125rem] font-semibold">{{ errorRouting ? 'Imagi is fixing something in your app' : 'Something broke in your app' }}</p>
          <p :class="ALERT_DETAIL">{{ latestError.text }}</p>
          <p v-if="errorRoutingNote" :class="ALERT_DETAIL" data-testid="error-routing-note">{{ errorRoutingNote }}</p>
        </div>
        <button
          type="button"
          class="grid place-items-center shrink-0 w-[1.625rem] h-[1.625rem] rounded-full text-sl-muted text-[0.6875rem] hover:bg-sl-chip-bg-hover hover:text-sl-text"
          title="Dismiss"
          aria-label="Dismiss"
          @click="dismissBanner"
        >
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- Notices: building, starting, failed, asleep. -->
      <!-- A new project's first build: the app opens here the moment its
           home page lands. The servers start underneath meanwhile. -->
      <div v-if="buildVeil" :class="[VEIL, VEIL_LIT]" data-testid="building-veil">
        <div :class="NOTICE">
          <h3 :class="NOTICE_TITLE">Building your home page</h3>
          <p :class="NOTICE_BODY">Your app opens here as soon as it's ready. The other pages keep building after that.</p>
          <ol :class="STAGES" aria-live="polite">
            <li :class="stageRowClass(building ? 'running' : 'done')">
              <span :class="stageMarkClass(building ? 'running' : 'done')" aria-hidden="true">
                <i v-if="!building" class="fas fa-check"></i>
                <span v-else :class="[DOT, DOT_TONE.work]"></span>
              </span>
              <span class="flex-1">Writing your home page</span>
            </li>
            <li :class="stageRowClass(appStarted ? 'done' : phase === 'error' ? 'failed' : 'running')">
              <span :class="stageMarkClass(appStarted ? 'done' : phase === 'error' ? 'failed' : 'running')" aria-hidden="true">
                <i v-if="appStarted" class="fas fa-check"></i>
                <span v-else :class="[DOT, DOT_TONE.work]"></span>
              </span>
              <span class="flex-1">Starting your app</span>
            </li>
          </ol>
          <p :class="CLOCK">{{ buildElapsedLabel }}</p>
        </div>
      </div>

      <!-- Starting: the real stages, as they happen. -->
      <div v-else-if="phase === 'starting' || (phase === 'ready' && !appReady && !iframeSrc)" :class="[VEIL, VEIL_LIT]">
        <div :class="NOTICE">
          <h3 :class="NOTICE_TITLE">Starting your app</h3>
          <ol :class="STAGES" aria-live="polite">
            <li v-for="stage in stages" :key="stage.key" :class="stageRowClass(stage.state)">
              <span :class="stageMarkClass(stage.state)" aria-hidden="true">
                <i v-if="stage.state === 'done'" class="fas fa-check"></i>
                <i v-else-if="stage.state === 'failed'" class="fas fa-xmark"></i>
                <span v-else :class="[DOT, stage.state === 'running' ? DOT_TONE.work : DOT_TONE.idle]"></span>
              </span>
              <span class="flex-1">{{ stage.label }}</span>
              <span v-if="stage.ms !== undefined" class="text-[0.6875rem] tabular-nums text-sl-muted">{{ seconds(stage.ms) }}</span>
            </li>
          </ol>
          <p :class="CLOCK">{{ elapsedLabel }}</p>
        </div>
      </div>

      <!-- Loading the app's page after the servers are up. -->
      <div v-else-if="phase === 'ready' && !appReady" :class="[VEIL, 'bg-transparent pointer-events-none']" aria-hidden="true">
        <div class="grid place-items-center w-9 h-9 rounded-full bg-sl-surface shadow-sl-card">
          <span :class="[DOT, DOT_TONE.work]"></span>
        </div>
      </div>

      <div v-if="phase === 'error'" :class="[VEIL, 'bg-sl-bg']">
        <div :class="NOTICE">
          <h3 :class="NOTICE_TITLE">Your app couldn't start</h3>
          <p :class="NOTICE_BODY">{{ failedStage ? `It stopped at "${failedStage.label}".` : 'The preview server reported a problem.' }}</p>
          <pre
            class="max-h-36 overflow-auto mt-3 py-2 px-2.5 rounded-[0.625rem] border border-sl-line bg-sl-chip-bg
              [font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace] text-[0.6875rem] leading-[1.5]
              whitespace-pre-wrap [word-break:break-word] text-sl-muted"
          >{{ failureText }}</pre>
          <div :class="NOTICE_ACTIONS">
            <button type="button" :class="CTA" @click="startPreview">Try again</button>
          </div>
        </div>
      </div>

      <div v-if="phase === 'stopped'" :class="[VEIL, VEIL_LIT]">
        <div :class="NOTICE">
          <h3 :class="NOTICE_TITLE">Your preview went to sleep</h3>
          <p :class="NOTICE_BODY">It stops after a quiet spell to keep costs down. Everything you built is safe.</p>
          <div :class="NOTICE_ACTIONS">
            <button type="button" :class="CTA" @click="startPreview">Wake it up</button>
          </div>
        </div>
      </div>
    </div>

    <PreviewDrawer
      v-if="drawerOpen"
      v-model:tab="drawerTab"
      :height="drawerHeight"
      :console="consoleEntries"
      :network="networkEntries"
      :logs="logLines"
      @update:height="setDrawerHeight"
      @clear="clearDrawer"
      @close="drawerOpen = false"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import PreviewDrawer, { type DrawerTab, type LogLine } from './PreviewDrawer.vue'
import { PreviewService, type PreviewApp } from '../../../services/previewService'
import {
  LivePreviewService,
  describeAgentAction,
  normalizeAddress,
  parseBridgeMessage,
  type BridgeCommand,
  type BridgeMessage,
  type ConsoleEntry,
  type LiveStartResult,
  type LiveStatus,
  type NetworkEntry,
  type PickedElement,
  type ServerAction,
  type StartStage,
} from '../../../services/livePreviewService'

const props = defineProps<{
  projectId: string
  /** Pane is hidden (phone, sidebar open): keep the session, poll less. */
  paused?: boolean
  /** Phones: the preview replaced the chat, so offer the way back. */
  canReturnToChat?: boolean
  returnCount?: number
  /** The project's first build is still writing its home page. */
  building?: boolean
}>()

const emit = defineEmits<{
  /** Errors the app reported went to an agent: which one. */
  (e: 'errors-routed', routing: NonNullable<LiveStatus['error_routing']>): void
  (e: 'return-to-chat'): void
  /** An element picked in the app, as a line of context for the agent. */
  (e: 'pick-element', text: string): void
}>()

// ---------------------------------------------------------------------------
// Class lists shared by several elements. Focus rings come from the
// Spotlight default (`.spotlight :focus-visible`: 2px --sl-focus, 3px out).
// ---------------------------------------------------------------------------

/** A toolbar button; `on` while its tool (picker, drawer) is engaged. */
function btnClass(on = false): string[] {
  return [
    'relative inline-grid place-items-center w-[1.875rem] h-[1.875rem] rounded-full text-[0.75rem] [transition:color_0.2s_var(--lp-ease),background-color_0.2s_var(--lp-ease)] motion-reduce:[transition:none] disabled:opacity-50 disabled:cursor-not-allowed',
    on ? 'text-sl-text bg-sl-chip-bg-hover' : 'text-sl-muted enabled:hover:text-sl-text enabled:hover:bg-sl-chip-bg-hover',
  ]
}

/** The suggestions list and the servers popover. */
const POPOVER =
  'absolute z-20 rounded-2xl border border-sl-line-strong bg-sl-surface [box-shadow:var(--sl-card-shadow),0_24px_60px_-24px_rgba(0,0,0,0.35)] dark:bg-sl-surface-2 dark:[box-shadow:0_24px_60px_-20px_rgba(0,0,0,0.85)]'
const POP_ACTION =
  'h-[1.875rem] px-3 rounded-full text-left text-[0.8125rem] transition-[background-color] duration-200 ease-[var(--lp-ease)] motion-reduce:[transition:none] enabled:hover:bg-sl-chip-bg-hover disabled:opacity-50 disabled:cursor-not-allowed'

/** Status dots. The working one breathes (.lp-breathe, below). */
const DOT = 'relative inline-block shrink-0 w-[0.4375rem] h-[0.4375rem] rounded-full'
const DOT_TONE = {
  ok: 'bg-sl-ok [box-shadow:0_0_0_3px_color-mix(in_srgb,var(--sl-ok)_20%,transparent)]',
  bad: 'bg-sl-bad [box-shadow:0_0_0_3px_color-mix(in_srgb,var(--sl-bad)_20%,transparent)]',
  work: 'bg-sl-work lp-breathe',
  idle: 'bg-sl-line-strong',
} as const

/** The quiet notes at the top of the stage (edit, agent, picking). */
const NOTE =
  'absolute top-3 left-1/2 z-[6] -translate-x-1/2 py-1.5 px-3.5 rounded-full border border-sl-line bg-[color:color-mix(in_srgb,var(--sl-surface)_94%,transparent)] dark:bg-[color:color-mix(in_srgb,var(--sl-surface-2)_94%,transparent)] shadow-sl-card text-[0.75rem] pointer-events-none'
const FADE = {
  enterActiveClass: '[transition:opacity_0.2s_var(--lp-ease),transform_0.2s_var(--lp-ease)]',
  leaveActiveClass: '[transition:opacity_0.2s_var(--lp-ease),transform_0.2s_var(--lp-ease)]',
  enterFromClass: 'opacity-0 -translate-y-1',
  leaveToClass: 'opacity-0 -translate-y-1',
}
const ALERT_DETAIL =
  'truncate [font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace] text-[0.6875rem] text-sl-muted'

/** Notices: building, starting, failed, asleep. */
const VEIL = 'absolute inset-0 z-[4] flex items-center justify-center p-6'
const VEIL_LIT = 'bg-sl-bg bg-[radial-gradient(70%_320px_at_50%_-80px,var(--sl-spot-core),transparent_70%)]'
const NOTICE = 'w-full max-w-sm p-6 rounded-[1.25rem] border border-sl-line bg-sl-surface dark:bg-sl-surface-2 shadow-sl-card'
const NOTICE_TITLE = 'font-sl-display text-[1.125rem] font-bold tracking-[-0.015em] text-sl-text'
const NOTICE_BODY = 'mt-1.5 text-[0.8125rem] leading-[1.5] text-sl-muted'
const NOTICE_ACTIONS = 'flex gap-2 mt-4'
const STAGES = 'grid gap-0.5 mt-3.5 p-0 list-none'
const CLOCK = 'mt-3 text-[0.6875rem] tabular-nums text-sl-muted'
/** The lit button: the one action that matters on each notice. */
const CTA =
  'inline-flex items-center gap-1.5 shrink-0 h-[1.875rem] px-3.5 rounded-full bg-sl-grad text-sl-on-accent text-[0.75rem] font-semibold shadow-sl-btn [transition:transform_0.2s_var(--lp-ease),box-shadow_0.2s_var(--lp-ease)] motion-reduce:[transition:none] hover:-translate-y-px hover:shadow-sl-btn-hover'

const STAGE_TONE: Record<string, string> = {
  running: 'text-sl-text',
  done: 'text-sl-text',
  failed: 'text-sl-bad',
}
/** A start stage's row; lp-stage-row / is-<state> are kept as hooks. */
function stageRowClass(state: string): string[] {
  return [
    'lp-stage-row',
    `is-${state}`,
    'flex items-center gap-2.5 h-7 text-[0.8125rem]',
    STAGE_TONE[state] ?? 'text-sl-muted',
  ]
}
function stageMarkClass(state: string): string[] {
  return ['grid place-items-center w-4 shrink-0 text-[0.6875rem]', state === 'done' ? 'text-sl-ok' : '']
}

type Phase = 'idle' | 'starting' | 'ready' | 'stopped' | 'error'

const STATUS_ACTIVE_MS = 2000
const STATUS_IDLE_MS = 15000
const LOGS_MS = 1500
const MAX_CONSOLE = 500
const MAX_NETWORK = 300
const MAX_LOG_LINES = 2000

const rootRef = ref<HTMLElement | null>(null)
const frameRef = ref<HTMLIFrameElement | null>(null)
const addressInput = ref<HTMLInputElement | null>(null)
const addressRoot = ref<HTMLElement | null>(null)
const statusRoot = ref<HTMLElement | null>(null)

const phase = ref<Phase>('idle')
const session = ref<LiveStartResult | null>(null)
const startError = ref('')
const iframeSrc = ref('')
const iframeKey = ref(0)
const appReady = ref(false)
const loadingPage = ref(false)
const currentPath = ref('/')
const canGoBack = ref(false)
const canGoForward = ref(false)
const status = ref<LiveStatus | null>(null)
const stages = ref<StartStage[]>([])
let disposed = false

// ---------------------------------------------------------------------------
// The bridge: messages from the app, commands to it
// ---------------------------------------------------------------------------

function send(command: BridgeCommand): boolean {
  const win = frameRef.value?.contentWindow
  if (!win || !session.value) return false
  win.postMessage({ target: 'imagi-preview', ...command }, session.value.origin)
  return true
}

let helloTimer: number | null = null
function stopHello() {
  if (helloTimer) window.clearInterval(helloTimer)
  helloTimer = null
}
/** Say hello until the bridge answers; it talks only after that. */
function greet() {
  stopHello()
  send({ cmd: 'hello' })
  let tries = 0
  helloTimer = window.setInterval(() => {
    if (bridgeReady || ++tries > 60) return stopHello()
    send({ cmd: 'hello' })
  }, 150)
}

let bridgeReady = false

function onMessage(e: MessageEvent) {
  // Only the preview's own window, from the preview origin.
  if (!session.value || e.origin !== session.value.origin) return
  if (!frameRef.value || e.source !== frameRef.value.contentWindow) return
  const msg = parseBridgeMessage(e.data)
  if (msg) handleBridge(msg)
}

function handleBridge(msg: BridgeMessage) {
  switch (msg.type) {
    case 'ready':
      bridgeReady = true
      stopHello()
      appReady.value = true
      loadingPage.value = false
      setPath(msg.path)
      break
    case 'loading':
      loadingPage.value = true
      break
    case 'nav':
      setPath(msg.path)
      canGoBack.value = msg.canGoBack
      canGoForward.value = msg.canGoForward
      loadingPage.value = false
      break
    case 'console':
      addConsole({ level: msg.level, text: msg.text, ts: msg.ts })
      break
    case 'net':
      networkEntries.value.push({ id: msg.id, method: msg.method, url: msg.url, status: msg.status, ms: msg.ms })
      if (networkEntries.value.length > MAX_NETWORK) networkEntries.value.splice(0, networkEntries.value.length - MAX_NETWORK)
      break
    case 'hmr':
      noteEdit(msg.files)
      homeArrived(msg.files)
      break
    case 'full-reload':
      noteEdit([])
      loadingPage.value = true
      break
    case 'picked':
      picking.value = false
      if (msg.element) emit('pick-element', describePick(msg.element, msg.path || currentPath.value))
      break
    case 'shortcut':
      runShortcut(msg.key, msg.shift)
      break
  }
}

function onFrameLoad() {
  // A new document in the frame (first load, reload, HMR full reload): its
  // bridge waits for a hello before it says anything.
  bridgeReady = false
  greet()
  // No bridge after a while (the page failed before its first script):
  // show what loaded anyway.
  window.setTimeout(() => {
    if (!disposed && !bridgeReady) {
      appReady.value = true
      loadingPage.value = false
    }
  }, 4000)
}

function setPath(path: string) {
  currentPath.value = path || '/'
  if (!addressFocused.value) addressText.value = currentPath.value
}

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------

function frameUrl(path: string): string {
  if (!session.value) return ''
  const base = session.value.base.replace(/\/$/, '')
  return `${session.value.origin}${base}${path === '/' ? '/' : path}`
}

function navigateTo(input: string) {
  const path = normalizeAddress(input)
  setPath(path)
  if (bridgeReady && send({ cmd: 'navigate', path })) return
  // No bridge to ask: load the address directly.
  loadingPage.value = true
  iframeSrc.value = frameUrl(path)
}

function goBack() {
  send({ cmd: 'back' })
}

function goForward() {
  send({ cmd: 'forward' })
}

/** Soft reload keeps the frame; hard reload remounts it from scratch. */
function reload(hard = false) {
  if (!session.value) return
  loadingPage.value = true
  if (!hard && bridgeReady && send({ cmd: 'reload' })) return
  appReady.value = false
  bridgeReady = false
  iframeSrc.value = frameUrl(currentPath.value)
  iframeKey.value += 1
}

function onReloadClick(e: MouseEvent) {
  reload(e.shiftKey)
}

function openInNewTab() {
  if (session.value) window.open(frameUrl(currentPath.value), '_blank', 'noopener,noreferrer')
}

// ---------------------------------------------------------------------------
// The address bar
// ---------------------------------------------------------------------------

const addressText = ref('/')
const addressFocused = ref(false)
const activeSuggestion = ref(-1)
const apps = ref<PreviewApp[]>([])

async function refreshPages() {
  try {
    apps.value = await PreviewService.pages(props.projectId)
  } catch {
    // The address bar still works without suggestions.
  }
}

const suggestionGroups = computed(() => {
  const q = addressText.value.trim().toLowerCase()
  // While the field still shows where you are, list every page.
  const showAll = !q || q === currentPath.value.toLowerCase()
  let index = 0
  const groups: Array<{ name: string; items: Array<{ title: string; path: string; index: number }> }> = []
  for (const app of apps.value) {
    const items = app.pages
      .filter((p) => showAll || p.title.toLowerCase().includes(q) || p.path.toLowerCase().includes(q))
      .map((p) => ({ title: p.title, path: p.path, index: index++ }))
    if (items.length) groups.push({ name: app.title || app.name, items })
  }
  return groups
})
const flatSuggestions = computed(() => suggestionGroups.value.flatMap((g) => g.items))
const suggestionsOpen = computed(() => addressFocused.value && flatSuggestions.value.length > 0)

function onAddressFocus() {
  addressFocused.value = true
  activeSuggestion.value = -1
  void refreshPages()
  requestAnimationFrame(() => addressInput.value?.select())
}

function onAddressBlur() {
  addressFocused.value = false
  addressText.value = currentPath.value
}

function chooseSuggestion(path: string) {
  navigateTo(path)
  addressInput.value?.blur()
}

function onAddressKeydown(e: KeyboardEvent) {
  const items = flatSuggestions.value
  if (e.key === 'ArrowDown' && items.length) {
    e.preventDefault()
    activeSuggestion.value = (activeSuggestion.value + 1) % items.length
  } else if (e.key === 'ArrowUp' && items.length) {
    e.preventDefault()
    activeSuggestion.value = activeSuggestion.value <= 0 ? items.length - 1 : activeSuggestion.value - 1
  } else if (e.key === 'Enter') {
    e.preventDefault()
    const chosen = items[activeSuggestion.value]
    navigateTo(chosen ? chosen.path : addressText.value)
    addressInput.value?.blur()
  } else if (e.key === 'Escape') {
    e.preventDefault()
    addressInput.value?.blur()
  }
}

// ---------------------------------------------------------------------------
// Server health, start progress and actions
// ---------------------------------------------------------------------------

type Tone = 'ok' | 'work' | 'bad' | 'idle'

const SERVER_STOPPED: [string, Tone] = ['Stopped', 'bad']
const SERVER_LABELS: Record<string, [string, Tone]> = {
  ready: ['Running', 'ok'],
  reloading: ['Reloading', 'work'],
  starting: ['Starting', 'work'],
  crashed: ['Crashed', 'bad'],
  stopped: ['Stopped', 'bad'],
}

const serverRows = computed(() =>
  (['frontend', 'backend'] as const).map((key) => {
    const state = status.value?.[key]?.state || (phase.value === 'starting' ? 'starting' : 'stopped')
    const [label, tone] = SERVER_LABELS[state] ?? SERVER_STOPPED
    return { key, name: key === 'frontend' ? 'Frontend' : 'Backend', label, tone }
  })
)

const overall = computed<{ label: string; tone: Tone; title: string }>(() => {
  if (phase.value === 'starting') return { label: 'Starting', tone: 'work', title: 'Your app is starting' }
  if (phase.value === 'error') return { label: 'Failed', tone: 'bad', title: 'Your app could not start' }
  if (phase.value !== 'ready') return { label: 'Stopped', tone: 'idle', title: 'Your app is not running' }
  const states = serverRows.value.map((r) => status.value?.[r.key]?.state)
  if (states.some((s) => s === 'crashed' || s === 'stopped')) {
    return { label: 'Crashed', tone: 'bad', title: 'A server stopped. Open for details.' }
  }
  if (states.some((s) => s === 'reloading')) {
    const which = serverRows.value.find((r) => status.value?.[r.key]?.state === 'reloading')
    return { label: `${which?.name || 'App'} reloading`, tone: 'work', title: 'Picking up an edit' }
  }
  return { label: 'Live', tone: 'ok', title: 'Your app is running' }
})

const lastReload = computed(() => {
  const times = [status.value?.backend?.log_changed_at, status.value?.frontend?.log_changed_at].filter(
    (t): t is number => typeof t === 'number'
  )
  if (!times.length) return ''
  void nowTick.value
  return ago(Math.max(...times) * 1000)
})

const nowTick = ref(Date.now())

function ago(ms: number): string {
  const s = Math.max(0, Math.round((nowTick.value - ms) / 1000))
  if (s < 10) return 'just now'
  if (s < 60) return `${s}s ago`
  const m = Math.round(s / 60)
  return m < 60 ? `${m} min ago` : `${Math.round(m / 60)} h ago`
}

const statusOpen = ref(false)
const actionBusy = ref<ServerAction | null>(null)
const actionNote = ref('')

const ACTION_DONE: Record<ServerAction, string> = {
  restart_frontend: 'Frontend restarted.',
  restart_backend: 'Backend restarted.',
  restart: 'Restarted.',
  migrate: 'Database is up to date.',
  reset_database: 'Test data cleared. The database starts empty.',
}

async function runAction(action: ServerAction) {
  if (action === 'reset_database' && !window.confirm('Clear all the data your app has saved while previewing? Accounts and records made here will be gone.')) {
    return
  }
  actionBusy.value = action
  actionNote.value = 'Working…'
  try {
    const result = await LivePreviewService.action(props.projectId, action)
    actionNote.value = result.ok === false ? `That didn't work: ${result.error || 'unknown error'}` : ACTION_DONE[action]
    if (action === 'restart_frontend' || action === 'reset_database' || action === 'restart') reload(true)
    void pollStatus()
  } catch (e) {
    actionNote.value = e instanceof Error ? e.message : 'That didn\'t work.'
  } finally {
    actionBusy.value = null
  }
}

const failedStage = computed(() => stages.value.find((s) => s.state === 'failed') || null)
const failureText = computed(() => (failedStage.value?.detail || startError.value || '').trim())

let statusTimer: number | null = null
let statusInFlight = false

function scheduleStatus(ms?: number) {
  if (statusTimer) window.clearTimeout(statusTimer)
  if (disposed) return
  const delay = ms ?? (props.paused || document.hidden ? STATUS_IDLE_MS : STATUS_ACTIVE_MS)
  statusTimer = window.setTimeout(() => void pollStatus(), delay)
}

async function pollStatus() {
  if (disposed || statusInFlight) return
  statusInFlight = true
  const outgoing = pendingErrors.splice(0, pendingErrors.length)
  // A poll sent while the servers were still starting can answer after the
  // start has: its "not running" is stale and must not stop the new session.
  const sentFor = session.value
  try {
    const visible = !props.paused && !document.hidden
    const result = await LivePreviewService.status(props.projectId, outgoing, visible)
    if (disposed) return
    status.value = result
    if (result.progress?.stages) stages.value = result.progress.stages
    if (result.error_routing) {
      errorRouting.value = result.error_routing
      if (result.error_routing.new) emit('errors-routed', result.error_routing)
    }
    followAgent(result.agent)
    if (phase.value === 'ready' && result.running === false && sentFor === session.value) {
      // The servers went away (idle shutdown, a deploy).
      phase.value = 'stopped'
      iframeSrc.value = ''
      session.value = null
    }
  } catch {
    // Errors that didn't make it go out with the next poll.
    pendingErrors.unshift(...outgoing)
  } finally {
    statusInFlight = false
    if (phase.value === 'ready' || phase.value === 'starting') scheduleStatus(phase.value === 'starting' ? 400 : undefined)
  }
}

// ---------------------------------------------------------------------------
// Agents using the app
// ---------------------------------------------------------------------------

// Agents act in a browser of their own on the server, so runs carry on with
// this tab closed. While one is active, this frame goes where it goes.
const agentNote = ref('')
let agentSeenAt = 0

function followAgent(activity: LiveStatus['agent']) {
  if (!activity) {
    agentNote.value = ''
    return
  }
  agentNote.value = `${activity.label} is ${describeAgentAction(activity.action)}`
  if (activity.at === agentSeenAt) return
  agentSeenAt = activity.at
  const path = normalizeAddress(activity.path || '/')
  if (path !== currentPath.value && phase.value === 'ready') navigateTo(path)
}

// ---------------------------------------------------------------------------
// Start
// ---------------------------------------------------------------------------

const elapsed = ref(0)
let elapsedTimer: number | null = null
const elapsedLabel = computed(() => `${Math.floor(elapsed.value / 60)}:${String(elapsed.value % 60).padStart(2, '0')}`)

function seconds(ms: number): string {
  return ms < 1000 ? `${ms} ms` : `${(ms / 1000).toFixed(1)} s`
}

async function startPreview() {
  if (phase.value === 'starting') return
  phase.value = 'starting'
  startError.value = ''
  appReady.value = false
  bridgeReady = false
  stages.value = []
  elapsed.value = 0
  const startedAt = Date.now()
  if (elapsedTimer) window.clearInterval(elapsedTimer)
  elapsedTimer = window.setInterval(() => {
    elapsed.value = Math.floor((Date.now() - startedAt) / 1000)
  }, 1000)
  // Progress arrives on the status poll while the start request runs.
  scheduleStatus(300)
  try {
    const result = await LivePreviewService.start(props.projectId)
    if (disposed) return
    session.value = result
    phase.value = 'ready'
    iframeSrc.value = frameUrl(currentPath.value)
    void refreshPages()
  } catch (e) {
    if (disposed) return
    phase.value = 'error'
    startError.value = e instanceof Error ? e.message : 'The preview could not start.'
    // Goes to the agents like any error the app reports.
    if (failureText.value) pendingErrors.push({ level: 'error', text: failureText.value, ts: Date.now() })
    void pollStatus()
  } finally {
    if (elapsedTimer) window.clearInterval(elapsedTimer)
    elapsedTimer = null
  }
}

// ---------------------------------------------------------------------------
// Console, network, logs, errors
// ---------------------------------------------------------------------------

const consoleEntries = ref<ConsoleEntry[]>([])
const networkEntries = ref<NetworkEntry[]>([])
const logLines = ref<LogLine[]>([])
const logOffsets: { backend?: number; frontend?: number } = {}
const pendingErrors: ConsoleEntry[] = []
let errorFlushTimer: number | null = null

const errorCount = computed(() => consoleEntries.value.filter((e) => e.level === 'error').length)

// Vite's own live-reload socket failing (a proxy or network that drops
// WebSocket upgrades) isn't the app breaking: keep it in the console as a
// warning, out of the banner and the error routing.
const DEV_SERVER_NOISE = /^\[vite\] (failed to connect to websocket|server connection lost)|^WebSocket connection to .* failed/i

function addConsole(entry: ConsoleEntry) {
  if (entry.level === 'error' && DEV_SERVER_NOISE.test(entry.text)) entry = { ...entry, level: 'warn' }
  consoleEntries.value.push(entry)
  if (consoleEntries.value.length > MAX_CONSOLE) consoleEntries.value.splice(0, consoleEntries.value.length - MAX_CONSOLE)
  if (entry.level !== 'error') return
  pendingErrors.push(entry)
  // Errors go out promptly: an agent's edit reads back what broke within a
  // second or two of making it.
  if (errorFlushTimer) window.clearTimeout(errorFlushTimer)
  errorFlushTimer = window.setTimeout(() => void pollStatus(), 300)
}

const errorRouting = ref<LiveStatus['error_routing']>(null)
const errorRoutingNote = computed(() =>
  errorRouting.value?.to === 'thread'
    ? 'Sent to the thread that just changed this part of your app.'
    : errorRouting.value?.to === 'coordinator'
      ? 'Sent to the coordinator, which is getting it fixed.'
      : ''
)
const dismissedError = ref<string | null>(null)
const latestError = computed(() => {
  for (let i = consoleEntries.value.length - 1; i >= 0; i--) {
    const entry = consoleEntries.value[i]
    if (entry?.level === 'error') return entry
  }
  return null
})
const bannerVisible = computed(
  () => phase.value === 'ready' && !drawerOpen.value && !!latestError.value && latestError.value.text !== dismissedError.value
)

function dismissBanner() {
  if (latestError.value) dismissedError.value = latestError.value.text
}

const drawerOpen = ref(false)
const drawerTab = ref<DrawerTab>('console')
const drawerHeight = ref(loadDrawerHeight())

function loadDrawerHeight(): number {
  try {
    const saved = Number(localStorage.getItem('imagi_preview_drawer_h'))
    if (saved > 0) return saved
  } catch {
    // storage may be unavailable
  }
  return 260
}

function setDrawerHeight(h: number) {
  const max = Math.max(160, (rootRef.value?.clientHeight || 600) - 120)
  drawerHeight.value = Math.round(Math.min(max, Math.max(112, h)))
  try {
    localStorage.setItem('imagi_preview_drawer_h', String(drawerHeight.value))
  } catch {
    // storage may be unavailable
  }
}

function clearDrawer(tab: DrawerTab) {
  if (tab === 'console') consoleEntries.value = []
  else if (tab === 'network') networkEntries.value = []
  else logLines.value = []
}

let logsTimer: number | null = null
async function pollLogs() {
  if (logsTimer) window.clearTimeout(logsTimer)
  logsTimer = null
  if (disposed || !drawerOpen.value || drawerTab.value !== 'logs' || phase.value !== 'ready') return
  try {
    const result = await LivePreviewService.logs(props.projectId, logOffsets)
    for (const source of ['backend', 'frontend'] as const) {
      const chunk = result[source]
      if (!chunk) continue
      if (chunk.reset) logLines.value = logLines.value.filter((l) => l.source !== source)
      logOffsets[source] = chunk.offset
      for (const text of chunk.lines) if (text.trim()) logLines.value.push({ source, text })
    }
    if (logLines.value.length > MAX_LOG_LINES) logLines.value.splice(0, logLines.value.length - MAX_LOG_LINES)
  } catch {
    // try again on the next tick
  }
  if (!disposed) logsTimer = window.setTimeout(() => void pollLogs(), LOGS_MS)
}

watch([drawerOpen, drawerTab], () => void pollLogs())

// ---------------------------------------------------------------------------
// Edit awareness and the element picker
// ---------------------------------------------------------------------------

const editNote = ref('')
const editFiles = new Set<string>()
let editTimer: number | null = null
let editHide: number | null = null

// Vite reports one update per module part, plus the stylesheet Tailwind
// regenerates after any template change, so the note names the edited
// source file, or counts them, and falls back to styles alone.
function editSummary(files: Set<string>): string {
  const sources = [...files].filter((f) => !/\.(css|scss|sass|less|postcss)$/i.test(f))
  if (sources.length === 1) return `Updated ${sources[0]!.split('/').pop()}`
  if (sources.length > 1) return `Updated ${sources.length} files`
  return files.size ? 'Updated styles' : 'Reloaded after an edit'
}

function noteEdit(files: string[]) {
  for (const f of files) editFiles.add(f.split('?')[0] ?? f)
  if (editTimer) window.clearTimeout(editTimer)
  editTimer = window.setTimeout(() => {
    editNote.value = editSummary(editFiles)
    editFiles.clear()
    if (editHide) window.clearTimeout(editHide)
    editHide = window.setTimeout(() => {
      editNote.value = ''
    }, 2600)
  }, 400)
}

const picking = ref(false)

function togglePicker() {
  if (!appReady.value) return
  picking.value = !picking.value
  send({ cmd: picking.value ? 'pick' : 'cancel-pick' })
  if (picking.value) frameRef.value?.focus()
}

function describePick(el: PickedElement, path: string): string {
  const what = `<${el.tag}>${el.text ? ` "${el.text.slice(0, 80)}"` : ''}`
  const where = el.component ? ` in ${el.component}${el.file ? ` (${el.file})` : ''}` : ''
  return `On the ${path} page of the preview, this element: ${what}${where}.`
}

// ---------------------------------------------------------------------------
// Keyboard
// ---------------------------------------------------------------------------

function runShortcut(key: string, shift: boolean) {
  if (key === 'l') {
    addressInput.value?.focus()
  } else if (key === 'j') {
    drawerOpen.value = !drawerOpen.value
  } else if (key === 'r') {
    reload(shift)
  } else if (key === 'c' && shift) {
    togglePicker()
  }
}

function onRootKeydown(e: KeyboardEvent) {
  if (!(e.metaKey || e.ctrlKey) || e.altKey) return
  const key = e.key.toLowerCase()
  if (key === 'l' || key === 'j' || key === 'r' || (key === 'c' && e.shiftKey)) {
    e.preventDefault()
    runShortcut(key, e.shiftKey)
  }
}

function onDocMouseDown(e: MouseEvent) {
  if (statusOpen.value && statusRoot.value && !statusRoot.value.contains(e.target as Node)) {
    statusOpen.value = false
  }
}

function onVisibility() {
  if (!document.hidden && (phase.value === 'ready' || phase.value === 'starting')) void pollStatus()
}

// ---------------------------------------------------------------------------
// First build
// ---------------------------------------------------------------------------

// Shown from when the workspace opens on a project still building its home
// page until the app has loaded the finished page.
const buildVeil = ref(!!props.building)
const buildElapsed = ref(0)
let buildTimer: number | null = null
const buildElapsedLabel = computed(
  () => `${Math.floor(buildElapsed.value / 60)}:${String(buildElapsed.value % 60).padStart(2, '0')}`
)
const appStarted = computed(() => phase.value === 'ready' && appReady.value)

function stopBuildClock() {
  if (buildTimer) window.clearInterval(buildTimer)
  buildTimer = null
}

watch(
  () => props.building,
  (building) => {
    if (building) {
      buildVeil.value = true
      const startedAt = Date.now()
      buildElapsed.value = 0
      stopBuildClock()
      buildTimer = window.setInterval(() => {
        buildElapsed.value = Math.floor((Date.now() - startedAt) / 1000)
      }, 1000)
      return
    }
    stopBuildClock()
    if (!buildVeil.value) {
      // Already open: the home page was hot-swapped in (homeArrived).
      if (session.value) void refreshPages()
      return
    }
    void refreshPages()
    if (session.value && iframeSrc.value) {
      // Load the finished home page fresh; the veil lifts once it has.
      currentPath.value = '/'
      addressText.value = '/'
      reload(true)
    } else if (phase.value === 'error' || phase.value === 'stopped') {
      buildVeil.value = false
    }
    // Otherwise the app is still starting; the veil stays until it loads.
  },
  { immediate: true }
)

watch(appReady, (ready) => {
  if (ready && !props.building) buildVeil.value = false
})

// The home page landing in a frame that's already open: Vite hot-swaps it in
// place, which is quicker than the build's status catching up and the frame
// reloading. With the veil down, that status change has nothing left to do.
const HOME_VIEW = '/src/apps/home/views/HomeView.vue'
function homeArrived(files: unknown) {
  if (!buildVeil.value || !Array.isArray(files)) return
  if (files.some((f) => typeof f === 'string' && (f.split('?')[0] ?? '').endsWith(HOME_VIEW))) {
    buildVeil.value = false
  }
}

// A preview that fails to start, or stops, shows its own notice once the
// build is done.
watch(phase, (p) => {
  if ((p === 'error' || p === 'stopped') && !props.building) buildVeil.value = false
})

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------

let tickTimer: number | null = null

function resetForProject() {
  stopHello()
  session.value = null
  iframeSrc.value = ''
  appReady.value = false
  bridgeReady = false
  status.value = null
  stages.value = []
  currentPath.value = '/'
  addressText.value = '/'
  agentNote.value = ''
  agentSeenAt = 0
  consoleEntries.value = []
  networkEntries.value = []
  logLines.value = []
  delete logOffsets.backend
  delete logOffsets.frontend
  errorRouting.value = null
  dismissedError.value = null
  apps.value = []
  phase.value = 'idle'
}

onMounted(() => {
  window.addEventListener('message', onMessage)
  document.addEventListener('mousedown', onDocMouseDown)
  document.addEventListener('visibilitychange', onVisibility)
  tickTimer = window.setInterval(() => {
    nowTick.value = Date.now()
  }, 15000)
  void refreshPages()
  void startPreview()
})

onBeforeUnmount(() => {
  disposed = true
  window.removeEventListener('message', onMessage)
  document.removeEventListener('mousedown', onDocMouseDown)
  document.removeEventListener('visibilitychange', onVisibility)
  for (const t of [statusTimer, logsTimer, errorFlushTimer, editTimer, editHide]) if (t) window.clearTimeout(t)
  if (elapsedTimer) window.clearInterval(elapsedTimer)
  if (tickTimer) window.clearInterval(tickTimer)
  stopBuildClock()
  stopHello()
})

watch(
  () => props.projectId,
  (next, prev) => {
    if (next && next !== prev) {
      resetForProject()
      void refreshPages()
      void startPreview()
    }
  }
)

watch(
  () => props.paused,
  (paused) => {
    if (!paused) void pollStatus()
    else scheduleStatus()
  }
)

defineExpose({ reload: () => reload(false) })
</script>

<style scoped>
/* Keyframe animations stay here: scoped keyframe names are hashed, so a
   utility can't reference them. */
.lp-breathe { animation: lp-breathe 1.8s var(--lp-ease) infinite; }
@keyframes lp-breathe {
  0%, 100% { box-shadow: 0 0 0 2px color-mix(in srgb, var(--sl-work, #3a5fd0) 25%, transparent); }
  50% { box-shadow: 0 0 0 5px color-mix(in srgb, var(--sl-work, #3a5fd0) 8%, transparent); }
}

.lp-slide::after { animation: lp-slide 1.1s var(--lp-ease) infinite; }
@keyframes lp-slide {
  0% { transform: translateX(-110%); }
  100% { transform: translateX(400%); }
}

.lp-spin { animation: lp-rotate 0.9s linear infinite; }
@keyframes lp-rotate { to { transform: rotate(360deg); } }

@media (prefers-reduced-motion: reduce) {
  .lp-breathe,
  .lp-slide::after,
  .lp-spin { animation: none; }
}
</style>
