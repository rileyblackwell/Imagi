<template>
  <div ref="rootRef" class="lp-root" @keydown="onRootKeydown">
    <!-- Toolbar: one 40px row. Navigation, the address, the servers' health,
         then the tools. Everything else is the app. -->
    <div class="lp-bar" role="toolbar" aria-label="Preview controls">
      <button
        v-if="canReturnToChat"
        type="button"
        class="lp-switch"
        aria-label="Back to the coordinator"
        @click="emit('return-to-chat')"
      >
        <i class="fas fa-chevron-left lp-switch-chevron"></i>
        <i class="fas fa-comments"></i>
        <span v-if="returnCount" class="lp-switch-count">{{ returnCount }}</span>
      </button>

      <div class="lp-nav">
        <button type="button" class="lp-btn" :disabled="!canGoBack || !appReady" title="Back" aria-label="Back" @click="goBack">
          <i class="fas fa-arrow-left"></i>
        </button>
        <button type="button" class="lp-btn" :disabled="!canGoForward || !appReady" title="Forward" aria-label="Forward" @click="goForward">
          <i class="fas fa-arrow-right"></i>
        </button>
        <button
          type="button"
          class="lp-btn"
          :disabled="!session"
          title="Reload (Shift-click for a hard reload)"
          aria-label="Reload"
          aria-keyshortcuts="Control+R Meta+R"
          @click="onReloadClick"
        >
          <i class="fas fa-rotate-right" :class="{ 'lp-spin': loadingPage }"></i>
        </button>
        <button type="button" class="lp-btn lp-btn--home" :disabled="!session" title="Home page" aria-label="Home page" @click="navigateTo('/')">
          <i class="fas fa-house"></i>
        </button>
      </div>

      <!-- The address: the app's path, editable; pages to jump to below. -->
      <div ref="addressRoot" class="lp-address" :class="{ 'is-focused': addressFocused }">
        <i class="fas fa-lock lp-address-lock" aria-hidden="true"></i>
        <input
          ref="addressInput"
          v-model="addressText"
          class="lp-address-input"
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
        <ul v-if="suggestionsOpen" id="lp-suggestions" class="lp-suggest" role="listbox" @mousedown.prevent>
          <template v-for="group in suggestionGroups" :key="group.name">
            <li class="lp-suggest-head" role="presentation">{{ group.name }}</li>
            <li
              v-for="item in group.items"
              :id="`lp-sugg-${item.index}`"
              :key="item.path"
              role="option"
              :aria-selected="item.index === activeSuggestion"
              :class="['lp-suggest-item', item.index === activeSuggestion && 'is-active', item.path === currentPath && 'is-current']"
              @click="chooseSuggestion(item.path)"
            >
              <span class="lp-suggest-title">{{ item.title }}</span>
              <span class="lp-suggest-path">{{ item.path }}</span>
            </li>
          </template>
        </ul>
      </div>

      <!-- Health of the two dev servers; details and actions on click. -->
      <div ref="statusRoot" class="lp-status-wrap">
        <button
          type="button"
          :class="['lp-status', `is-${overall.tone}`]"
          :aria-expanded="statusOpen"
          aria-haspopup="dialog"
          :title="overall.title"
          @click="statusOpen = !statusOpen"
        >
          <span class="lp-dot" aria-hidden="true"></span>
          <span class="lp-status-label">{{ overall.label }}</span>
        </button>
        <div v-if="statusOpen" class="lp-pop" role="dialog" aria-label="Your app's servers">
          <p class="lp-pop-head">Your app's servers</p>
          <div v-for="row in serverRows" :key="row.key" class="lp-pop-row">
            <span :class="['lp-dot', `is-${row.tone}`]" aria-hidden="true"></span>
            <span class="lp-pop-name">{{ row.name }}</span>
            <span class="lp-pop-state">{{ row.label }}</span>
          </div>
          <p v-if="lastReload" class="lp-pop-note">Last reloaded {{ lastReload }}</p>
          <div class="lp-pop-actions">
            <button type="button" class="lp-pop-action" :disabled="!!actionBusy" @click="runAction('restart_frontend')">Restart frontend</button>
            <button type="button" class="lp-pop-action" :disabled="!!actionBusy" @click="runAction('restart_backend')">Restart backend</button>
            <button type="button" class="lp-pop-action" :disabled="!!actionBusy" @click="runAction('migrate')">Update the database</button>
            <button type="button" class="lp-pop-action is-danger" :disabled="!!actionBusy" @click="runAction('reset_database')">Reset test data</button>
          </div>
          <p v-if="actionNote" class="lp-pop-note" aria-live="polite">{{ actionNote }}</p>
        </div>
      </div>

      <div class="lp-tools">
        <button
          type="button"
          :class="['lp-btn', picking && 'is-on']"
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
          :class="['lp-btn', drawerOpen && 'is-on']"
          title="Console, network and server logs (Ctrl+J)"
          aria-label="Console, network and server logs"
          :aria-pressed="drawerOpen"
          aria-keyshortcuts="Control+J Meta+J"
          @click="drawerOpen = !drawerOpen"
        >
          <i class="fas fa-terminal"></i>
          <span v-if="errorCount" class="lp-badge">{{ errorCount > 99 ? '99+' : errorCount }}</span>
        </button>
        <button type="button" class="lp-btn lp-btn--newtab" :disabled="!session" title="Open in a new tab" aria-label="Open in a new tab" @click="openInNewTab">
          <i class="fas fa-arrow-up-right-from-square"></i>
        </button>
      </div>

      <div v-if="loadingPage" class="lp-progress" aria-hidden="true"></div>
    </div>

    <div class="lp-stage">
      <!-- The app itself, rendered by this browser. Sandboxed on its own
           origin: it can run, post forms and open popups, never navigate
           Imagi or read anything of Imagi's. Remounted only by a hard reload
           or a server restart (iframeKey). -->
      <iframe
        v-if="iframeSrc"
        ref="frameRef"
        :key="iframeKey"
        :src="iframeSrc"
        class="lp-frame"
        title="Your app"
        sandbox="allow-scripts allow-forms allow-same-origin allow-popups allow-popups-to-escape-sandbox allow-modals allow-downloads"
        allow="clipboard-write"
        referrerpolicy="same-origin"
        @load="onFrameLoad"
      ></iframe>

      <!-- Edit awareness: a quiet note when an edit lands. -->
      <transition name="lp-fade">
        <p v-if="editNote" class="lp-edit-note" role="status">{{ editNote }}</p>
      </transition>

      <!-- An agent using the app in its own browser: the frame follows it
           to its page, and this says who it is and what it is doing. -->
      <transition name="lp-fade">
        <p v-if="agentNote && !editNote" class="lp-edit-note lp-edit-note--agent" role="status" data-testid="agent-note">
          <span class="lp-dot is-work" aria-hidden="true"></span>
          {{ agentNote }}
        </p>
      </transition>

      <!-- Picking: say how to get out of it. -->
      <p v-if="picking" class="lp-edit-note lp-edit-note--pick" role="status">Click anything in your app to ask the agent about it. Esc cancels.</p>

      <!-- The newest error, with a way to hand it to the agent. -->
      <div v-if="bannerVisible && latestError" class="lp-alert" role="alert">
        <span class="lp-alert-mark" aria-hidden="true"><i class="fas fa-exclamation"></i></span>
        <div class="lp-alert-body">
          <p class="lp-alert-title">{{ errorRouting ? 'Imagi is fixing something in your app' : 'Something broke in your app' }}</p>
          <p class="lp-alert-detail">{{ latestError.text }}</p>
          <p v-if="errorRoutingNote" class="lp-alert-detail" data-testid="error-routing-note">{{ errorRoutingNote }}</p>
        </div>
        <button v-if="!errorRouting" type="button" class="lp-cta" @click="fixError(latestError.text)">
          <i class="fas fa-wand-magic-sparkles"></i>
          Fix it
        </button>
        <button type="button" class="lp-alert-close" title="Dismiss" aria-label="Dismiss" @click="dismissBanner">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <!-- A new project's first build: the app opens here the moment its
           home page lands. The servers start underneath meanwhile. -->
      <div v-if="buildVeil" class="lp-veil" data-testid="building-veil">
        <div class="lp-notice">
          <h3 class="lp-notice-title">Building your home page</h3>
          <p class="lp-notice-body">Your app opens here as soon as it's ready. The other pages keep building after that.</p>
          <ol class="lp-stages" aria-live="polite">
            <li :class="['lp-stage-row', building ? 'is-running' : 'is-done']">
              <span class="lp-stage-mark" aria-hidden="true">
                <i v-if="!building" class="fas fa-check"></i>
                <span v-else class="lp-dot is-work"></span>
              </span>
              <span class="lp-stage-label">Writing your home page</span>
            </li>
            <li :class="['lp-stage-row', appStarted ? 'is-done' : phase === 'error' ? 'is-failed' : 'is-running']">
              <span class="lp-stage-mark" aria-hidden="true">
                <i v-if="appStarted" class="fas fa-check"></i>
                <span v-else class="lp-dot is-work"></span>
              </span>
              <span class="lp-stage-label">Starting your app</span>
            </li>
          </ol>
          <p class="lp-clock">{{ buildElapsedLabel }}</p>
        </div>
      </div>

      <!-- Starting: the real stages, as they happen. -->
      <div v-else-if="phase === 'starting' || (phase === 'ready' && !appReady && !iframeSrc)" class="lp-veil">
        <div class="lp-notice">
          <h3 class="lp-notice-title">Starting your app</h3>
          <ol class="lp-stages" aria-live="polite">
            <li v-for="stage in stages" :key="stage.key" :class="['lp-stage-row', `is-${stage.state}`]">
              <span class="lp-stage-mark" aria-hidden="true">
                <i v-if="stage.state === 'done'" class="fas fa-check"></i>
                <i v-else-if="stage.state === 'failed'" class="fas fa-xmark"></i>
                <span v-else class="lp-dot" :class="stage.state === 'running' ? 'is-work' : 'is-idle'"></span>
              </span>
              <span class="lp-stage-label">{{ stage.label }}</span>
              <span v-if="stage.ms !== undefined" class="lp-stage-ms">{{ seconds(stage.ms) }}</span>
            </li>
          </ol>
          <p class="lp-clock">{{ elapsedLabel }}</p>
        </div>
      </div>

      <!-- Loading the app's page after the servers are up. -->
      <div v-else-if="phase === 'ready' && !appReady" class="lp-veil lp-veil--soft" aria-hidden="true">
        <div class="lp-loader"><span class="lp-dot is-work"></span></div>
      </div>

      <div v-if="phase === 'error'" class="lp-veil lp-veil--solid">
        <div class="lp-notice">
          <h3 class="lp-notice-title">Your app couldn't start</h3>
          <p class="lp-notice-body">{{ failedStage ? `It stopped at "${failedStage.label}".` : 'The preview server reported a problem.' }}</p>
          <pre class="lp-code">{{ failureText }}</pre>
          <div class="lp-notice-actions">
            <button type="button" class="lp-cta" @click="fixError(failureText)">
              <i class="fas fa-wand-magic-sparkles"></i>
              Fix it
            </button>
            <button type="button" class="lp-ghost" @click="startPreview">Try again</button>
          </div>
        </div>
      </div>

      <div v-if="phase === 'stopped'" class="lp-veil">
        <div class="lp-notice">
          <h3 class="lp-notice-title">Your preview went to sleep</h3>
          <p class="lp-notice-body">It stops after a quiet spell to keep costs down. Everything you built is safe.</p>
          <div class="lp-notice-actions">
            <button type="button" class="lp-cta" @click="startPreview">Wake it up</button>
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
      @fix="fixError"
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
  (e: 'fix-error', text: string): void
  (e: 'return-to-chat'): void
  /** An element picked in the app, as a line of context for the agent. */
  (e: 'pick-element', text: string): void
}>()

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
    if (result.error_routing) errorRouting.value = result.error_routing
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
    : errorRouting.value?.to === 'new_thread'
      ? 'A new thread is fixing it.'
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

function fixError(text: string) {
  if (!text) return
  emit('fix-error', text)
  dismissedError.value = text
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
/* ---------------------------------------------------------------------------
   Live preview. A slim browser toolbar over the user's own app, which gets
   every other pixel. Colours come from the --sl-* tokens
   (shared/styles/spotlight.css); motion uses the one Spotlight curve.
   --------------------------------------------------------------------------- */

.lp-root {
  --lp-ease: cubic-bezier(0.22, 1, 0.36, 1);
  position: relative;
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  min-height: 0;
  background: var(--sl-bg, #f8f7f4);
  color: var(--sl-text, #14151c);
}

/* --- Toolbar ------------------------------------------------------------ */

.lp-bar {
  position: relative;
  z-index: 5;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  height: 2.5rem;
  flex-shrink: 0;
  padding: 0 0.5rem;
  border-bottom: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
  background: var(--sl-surface, #ffffff);
}
.dark .lp-bar { background: var(--sl-surface-2, #1a1d28); }

.lp-nav,
.lp-tools {
  display: flex;
  align-items: center;
  gap: 0.0625rem;
  flex-shrink: 0;
}

.lp-btn {
  position: relative;
  display: inline-grid;
  place-items: center;
  width: 1.875rem;
  height: 1.875rem;
  border-radius: 9999px;
  color: var(--sl-muted, #5c6172);
  font-size: 0.75rem;
  transition: color 0.2s var(--lp-ease), background-color 0.2s var(--lp-ease);
}
.lp-btn:hover:not(:disabled) {
  color: var(--sl-text, #14151c);
  background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065));
}
.lp-btn.is-on {
  color: var(--sl-text, #14151c);
  background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065));
}
.lp-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.lp-btn:focus-visible,
.lp-status:focus-visible,
.lp-switch:focus-visible,
.lp-pop-action:focus-visible,
.lp-cta:focus-visible,
.lp-ghost:focus-visible,
.lp-alert-close:focus-visible {
  outline: 2px solid var(--sl-focus, #d9730d);
  outline-offset: 3px;
}

.lp-badge {
  position: absolute;
  top: 0.0625rem;
  right: -0.0625rem;
  min-width: 0.9375rem;
  height: 0.9375rem;
  padding: 0 0.1875rem;
  border-radius: 9999px;
  background: var(--sl-bad, #d7334a);
  color: #fff;
  font-size: 0.5625rem;
  font-weight: 600;
  line-height: 0.9375rem;
  font-variant-numeric: tabular-nums;
}

/* The address: one field with a border that deepens, never a ring. */
.lp-address {
  position: relative;
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  height: 1.875rem;
  padding: 0 0.75rem 0 0.6875rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
  background: var(--sl-chip-bg, rgba(20, 21, 30, 0.035));
  transition: border-color 0.2s var(--lp-ease), background-color 0.2s var(--lp-ease);
}
.lp-address:hover { border-color: var(--sl-line-strong, rgba(20, 21, 30, 0.15)); }
.lp-address.is-focused {
  border-color: var(--sl-muted, #5c6172);
  background: var(--sl-surface, #ffffff);
}
.dark .lp-address.is-focused { background: var(--sl-bg-deep, #0b0b0d); }
/* The focus ring goes around the whole pill, not the bare input inside it. */
.lp-address-input:focus-visible { outline: none; }
.lp-address:has(.lp-address-input:focus-visible) {
  outline: 2px solid var(--sl-focus, #4f8cff);
  outline-offset: 2px;
}

.lp-address-lock {
  flex-shrink: 0;
  margin-right: 0.5rem;
  font-size: 0.5625rem;
  color: var(--sl-faint, #8a8fa0);
}

.lp-address-input {
  flex: 1;
  min-width: 0;
  height: 100%;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--sl-text, #14151c);
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.75rem;
}

.lp-suggest {
  position: absolute;
  top: calc(100% + 0.375rem);
  left: 0;
  right: 0;
  z-index: 20;
  max-height: 60vh;
  overflow-y: auto;
  padding: 0.375rem;
  border-radius: 1rem;
  border: 1px solid var(--sl-line-strong, rgba(20, 21, 30, 0.15));
  background: var(--sl-surface, #ffffff);
  box-shadow: var(--sl-card-shadow), 0 24px 60px -24px rgba(0, 0, 0, 0.35);
}
.dark .lp-suggest { background: var(--sl-surface-2, #1a1d28); box-shadow: 0 24px 60px -20px rgba(0, 0, 0, 0.85); }

.lp-suggest-head {
  padding: 0.5rem 0.625rem 0.25rem;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted, #5c6172);
}

.lp-suggest-item {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  padding: 0.4375rem 0.625rem;
  border-radius: 0.625rem;
  cursor: pointer;
  font-size: 0.8125rem;
  color: var(--sl-text, #14151c);
}
.lp-suggest-item:hover,
.lp-suggest-item.is-active { background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065)); }
.lp-suggest-item.is-current .lp-suggest-title { font-weight: 600; }
.lp-suggest-title { flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.lp-suggest-path {
  flex-shrink: 0;
  max-width: 45%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.6875rem;
  color: var(--sl-muted, #5c6172);
}

/* Status pill: a dot with a soft halo, and the word. */
.lp-status-wrap { position: relative; flex-shrink: 0; }

.lp-status {
  display: inline-flex;
  align-items: center;
  gap: 0.4375rem;
  height: 1.875rem;
  padding: 0 0.75rem 0 0.625rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--sl-text, #14151c);
  white-space: nowrap;
  transition: border-color 0.2s var(--lp-ease);
}
.lp-status:hover { border-color: var(--sl-line-strong, rgba(20, 21, 30, 0.15)); }

.lp-dot {
  position: relative;
  display: inline-block;
  flex-shrink: 0;
  width: 0.4375rem;
  height: 0.4375rem;
  border-radius: 9999px;
  background: var(--sl-faint, #8a8fa0);
}
.is-ok > .lp-dot,
.lp-dot.is-ok { background: var(--sl-ok, #139a55); box-shadow: 0 0 0 3px color-mix(in srgb, var(--sl-ok, #139a55) 20%, transparent); }
.is-bad > .lp-dot,
.lp-dot.is-bad { background: var(--sl-bad, #d7334a); box-shadow: 0 0 0 3px color-mix(in srgb, var(--sl-bad, #d7334a) 20%, transparent); }
.is-work > .lp-dot,
.lp-dot.is-work { background: var(--sl-work, #3a5fd0); animation: lp-breathe 1.8s var(--lp-ease) infinite; }
.lp-dot.is-idle { background: var(--sl-line-strong, rgba(20, 21, 30, 0.15)); }

@keyframes lp-breathe {
  0%, 100% { box-shadow: 0 0 0 2px color-mix(in srgb, var(--sl-work, #3a5fd0) 25%, transparent); }
  50% { box-shadow: 0 0 0 5px color-mix(in srgb, var(--sl-work, #3a5fd0) 8%, transparent); }
}

.lp-pop {
  position: absolute;
  top: calc(100% + 0.375rem);
  right: 0;
  z-index: 20;
  width: 16rem;
  padding: 0.75rem;
  border-radius: 1rem;
  border: 1px solid var(--sl-line-strong, rgba(20, 21, 30, 0.15));
  background: var(--sl-surface, #ffffff);
  box-shadow: var(--sl-card-shadow), 0 24px 60px -24px rgba(0, 0, 0, 0.35);
}
.dark .lp-pop { background: var(--sl-surface-2, #1a1d28); box-shadow: 0 24px 60px -20px rgba(0, 0, 0, 0.85); }

.lp-pop-head {
  margin-bottom: 0.5rem;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--sl-muted, #5c6172);
}
.lp-pop-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.3125rem 0;
  font-size: 0.8125rem;
}
.lp-pop-name { flex: 1; }
.lp-pop-state { color: var(--sl-muted, #5c6172); font-size: 0.75rem; }
.lp-pop-note { margin-top: 0.375rem; font-size: 0.75rem; color: var(--sl-muted, #5c6172); }
.lp-pop-actions {
  display: grid;
  gap: 0.25rem;
  margin-top: 0.625rem;
  padding-top: 0.625rem;
  border-top: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
}
.lp-pop-action {
  height: 1.875rem;
  padding: 0 0.75rem;
  border-radius: 9999px;
  text-align: left;
  font-size: 0.8125rem;
  color: var(--sl-text, #14151c);
  transition: background-color 0.2s var(--lp-ease);
}
.lp-pop-action:hover:not(:disabled) { background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065)); }
.lp-pop-action.is-danger { color: var(--sl-bad, #d7334a); }
.lp-pop-action:disabled { opacity: 0.5; cursor: not-allowed; }

.lp-switch {
  display: inline-flex;
  align-items: center;
  gap: 0.3125rem;
  height: 1.875rem;
  padding: 0 0.625rem;
  border-radius: 9999px;
  background: var(--sl-chip-bg, rgba(20, 21, 30, 0.035));
  color: var(--sl-muted, #5c6172);
  font-size: 0.6875rem;
  flex-shrink: 0;
}
.lp-switch-chevron { font-size: 0.5rem; opacity: 0.6; }
.lp-switch-count {
  min-width: 1rem;
  padding: 0 0.25rem;
  border-radius: 9999px;
  background: var(--sl-grad);
  color: var(--sl-on-accent, #1a0e08);
  font-size: 0.625rem;
  font-weight: 600;
}

/* Loading ribbon along the toolbar's lower edge. */
.lp-progress {
  position: absolute;
  left: 0;
  right: 0;
  bottom: -1px;
  height: 2px;
  overflow: hidden;
  pointer-events: none;
}
.lp-progress::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 30%;
  background: var(--sl-work, #3a5fd0);
  animation: lp-slide 1.1s var(--lp-ease) infinite;
}
@keyframes lp-slide {
  0% { transform: translateX(-110%); }
  100% { transform: translateX(400%); }
}
.lp-spin { animation: lp-rotate 0.9s linear infinite; }
@keyframes lp-rotate { to { transform: rotate(360deg); } }

/* --- Stage ------------------------------------------------------------- */

.lp-stage {
  position: relative;
  flex: 1;
  min-height: 0;
  background: var(--sl-bg-deep, #f0eee9);
}

.lp-frame {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
  background: #fff;
}

.lp-edit-note {
  position: absolute;
  top: 0.75rem;
  left: 50%;
  z-index: 6;
  transform: translateX(-50%);
  padding: 0.375rem 0.875rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
  background: color-mix(in srgb, var(--sl-surface, #ffffff) 94%, transparent);
  box-shadow: var(--sl-card-shadow, 0 14px 34px -20px rgba(20, 21, 30, 0.2));
  font-size: 0.75rem;
  color: var(--sl-muted, #5c6172);
  pointer-events: none;
}
.dark .lp-edit-note { background: color-mix(in srgb, var(--sl-surface-2, #1a1d28) 94%, transparent); }
.lp-edit-note--pick { color: var(--sl-text, #14151c); }
.lp-edit-note--agent {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--sl-text, #14151c);
}

.lp-fade-enter-active,
.lp-fade-leave-active { transition: opacity 0.2s var(--lp-ease), transform 0.2s var(--lp-ease); }
.lp-fade-enter-from,
.lp-fade-leave-to { opacity: 0; transform: translate(-50%, -4px); }

/* Error banner */
.lp-alert {
  position: absolute;
  left: 0.75rem;
  right: 0.75rem;
  bottom: 0.75rem;
  z-index: 6;
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.625rem 0.5rem 0.75rem;
  border-radius: 1rem;
  border: 1px solid var(--sl-line-strong, rgba(20, 21, 30, 0.15));
  background: var(--sl-surface, #ffffff);
  box-shadow: var(--sl-card-shadow), 0 16px 36px -16px rgba(20, 21, 30, 0.35);
}
.dark .lp-alert { background: var(--sl-surface-2, #1a1d28); }
.lp-alert-mark {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 9999px;
  background: color-mix(in srgb, var(--sl-bad, #d7334a) 14%, transparent);
  color: var(--sl-bad, #d7334a);
  font-size: 0.6875rem;
}
.lp-alert-body { flex: 1; min-width: 0; }
.lp-alert-title { font-size: 0.8125rem; font-weight: 600; }
.lp-alert-detail {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.6875rem;
  color: var(--sl-muted, #5c6172);
}
.lp-alert-close {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 1.625rem;
  height: 1.625rem;
  border-radius: 9999px;
  color: var(--sl-muted, #5c6172);
  font-size: 0.6875rem;
}
.lp-alert-close:hover { background: var(--sl-chip-bg-hover, rgba(20, 21, 30, 0.065)); color: var(--sl-text, #14151c); }

/* The lit button: the one action that matters on each notice. */
.lp-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  flex-shrink: 0;
  height: 1.875rem;
  padding: 0 0.875rem;
  border-radius: 9999px;
  background: var(--sl-grad);
  color: var(--sl-on-accent, #1a0e08);
  font-size: 0.75rem;
  font-weight: 600;
  box-shadow: var(--sl-btn-shadow, none);
  transition: transform 0.2s var(--lp-ease), box-shadow 0.2s var(--lp-ease);
}
.lp-cta:hover { transform: translateY(-1px); box-shadow: var(--sl-btn-shadow-hover, none); }
.lp-cta i { font-size: 0.625rem; }

.lp-ghost {
  height: 1.875rem;
  padding: 0 0.875rem;
  border-radius: 9999px;
  border: 1px solid var(--sl-line-strong, rgba(20, 21, 30, 0.15));
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--sl-text, #14151c);
  transition: border-color 0.2s var(--lp-ease);
}
.lp-ghost:hover { border-color: var(--sl-muted, #5c6172); }

/* Notices: starting, failed, asleep */
.lp-veil {
  position: absolute;
  inset: 0;
  z-index: 4;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: var(--sl-bg, #f8f7f4);
  background-image: radial-gradient(70% 320px at 50% -80px, var(--sl-spot-core, rgba(255, 170, 110, 0.3)), transparent 70%);
}
.lp-veil--solid { background-image: none; }
.lp-veil--soft { background: transparent; background-image: none; pointer-events: none; }

.lp-loader {
  display: grid;
  place-items: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  background: var(--sl-surface, #ffffff);
  box-shadow: var(--sl-card-shadow, 0 14px 34px -20px rgba(20, 21, 30, 0.2));
}

.lp-notice {
  width: 100%;
  max-width: 24rem;
  padding: 1.5rem;
  border-radius: 1.25rem;
  border: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
  background: var(--sl-surface, #ffffff);
  box-shadow: var(--sl-card-shadow, 0 14px 34px -20px rgba(20, 21, 30, 0.2));
}
.dark .lp-notice { background: var(--sl-surface-2, #1a1d28); }

.lp-notice-title {
  font-family: var(--sl-font-display, inherit);
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: -0.015em;
  color: var(--sl-text, #14151c);
}
.lp-notice-body {
  margin-top: 0.375rem;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: var(--sl-muted, #5c6172);
}
.lp-notice-actions { display: flex; gap: 0.5rem; margin-top: 1rem; }

.lp-stages {
  display: grid;
  gap: 0.125rem;
  margin-top: 0.875rem;
  padding: 0;
  list-style: none;
}
.lp-stage-row {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  height: 1.75rem;
  font-size: 0.8125rem;
  color: var(--sl-muted, #5c6172);
}
.lp-stage-row.is-running,
.lp-stage-row.is-done { color: var(--sl-text, #14151c); }
.lp-stage-row.is-failed { color: var(--sl-bad, #d7334a); }
.lp-stage-mark {
  display: grid;
  place-items: center;
  width: 1rem;
  flex-shrink: 0;
  font-size: 0.6875rem;
}
.lp-stage-row.is-done .lp-stage-mark { color: var(--sl-ok, #139a55); }
.lp-stage-label { flex: 1; }
.lp-stage-ms {
  font-size: 0.6875rem;
  font-variant-numeric: tabular-nums;
  color: var(--sl-muted, #5c6172);
}
.lp-clock {
  margin-top: 0.75rem;
  font-size: 0.6875rem;
  font-variant-numeric: tabular-nums;
  color: var(--sl-muted, #5c6172);
}

.lp-code {
  max-height: 9rem;
  overflow: auto;
  margin-top: 0.75rem;
  padding: 0.5rem 0.625rem;
  border-radius: 0.625rem;
  border: 1px solid var(--sl-line, rgba(20, 21, 30, 0.09));
  background: var(--sl-chip-bg, rgba(20, 21, 30, 0.035));
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.6875rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--sl-muted, #5c6172);
}

/* Phones: fewer controls, same row. */
@media (max-width: 640px) {
  .lp-btn--home,
  .lp-btn--newtab,
  .lp-status-label { display: none; }
  .lp-status { padding: 0 0.5625rem; }
}

@media (prefers-reduced-motion: reduce) {
  .lp-dot.is-work,
  .is-work > .lp-dot,
  .lp-progress::after,
  .lp-spin { animation: none; }
  .lp-btn, .lp-address, .lp-status, .lp-cta, .lp-ghost, .lp-pop-action { transition: none; }
}
</style>
