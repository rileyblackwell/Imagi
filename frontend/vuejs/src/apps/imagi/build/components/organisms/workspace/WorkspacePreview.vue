<template>
  <!-- Glass Dock. The preview pane is a Spotlight stage: the user's app sits on
       it as a lit card, and the controls float above it in one frosted pill.
       The chrome stays quiet so the app is the brightest thing here. Colours
       come from the --sl-* tokens, so the themes differ only there. -->
  <div
    class="relative w-full h-full flex flex-col bg-sl-bg bg-[radial-gradient(70%_320px_at_50%_-80px,var(--sl-spot-core),transparent_70%)]"
  >
    <!-- The dock: one frosted pill floating on the stage above the app —
         navigation, and where you are (also the page menu). It sits in its own band rather than over the app,
         because anything laid over the frame would hide the app's own header.
         Phones: the preview already fills a phone, so the band tightens. -->
    <div class="relative z-[3] flex shrink-0 justify-center pt-3 px-4 pb-2.5 max-[767px]:p-2">
      <div
        class="relative flex items-center gap-1 max-[767px]:gap-0.5 w-full max-w-[44rem] p-1 rounded-full border border-sl-line-strong
          bg-[color:color-mix(in_srgb,var(--sl-surface)_72%,transparent)] [backdrop-filter:blur(16px)_saturate(1.4)] shadow-sl-card"
      >
        <div class="flex items-center gap-px shrink-0">
          <button
            type="button"
            @click="goBack"
            :disabled="!canGoBack || phase !== 'ready'"
            title="Back"
            aria-label="Back"
            :class="NAV"
          >
            <i class="fas fa-arrow-left"></i>
          </button>

          <button
            type="button"
            @click="goForward"
            :disabled="!canGoForward || phase !== 'ready'"
            title="Forward"
            aria-label="Forward"
            :class="NAV"
          >
            <i class="fas fa-arrow-right"></i>
          </button>

          <button
            type="button"
            @click="reload"
            title="Refresh page"
            aria-label="Refresh page"
            :class="NAV"
          >
            <i class="fas fa-rotate-right" :class="{ 'fa-spin': busy }"></i>
          </button>

          <!-- Home has a second door (the home page is a row in the page
               menu), which is why it alone stands down on the narrowest phones. -->
          <button
            type="button"
            @click="goHome"
            title="Go to home page"
            aria-label="Go to home page"
            :class="[NAV, 'max-[359px]:hidden']"
          >
            <i class="fas fa-house"></i>
          </button>
        </div>

        <span class="shrink-0 w-px h-[1.125rem] mx-0.5 bg-sl-line-strong max-[359px]:hidden" aria-hidden="true"></span>

        <!-- The nameplate: the section of the app this page lives in, then the
             page itself ("home / About"). Also opens the page menu. Narrow
             panes drop the section before the page name ever truncates. -->
        <div class="relative flex-1 min-w-0" ref="menuRoot">
          <button
            type="button"
            @click="onMenuToggle"
            :disabled="apps.length === 0"
            :aria-expanded="menuOpen"
            aria-haspopup="true"
            class="pv-plate relative flex items-center gap-1.5 w-full h-8 pl-3.5 pr-8 rounded-full text-left bg-sl-chip-bg cursor-pointer
              transition-[background-color] duration-[160ms] ease-[ease] enabled:hover:bg-sl-chip-bg-hover
              disabled:opacity-[0.55] disabled:cursor-not-allowed
              focus-visible:![outline:none] focus-visible:[box-shadow:0_0_0_2px_var(--sl-focus)]"
          >
            <span
              v-if="location.dir"
              class="shrink-0 max-w-[10rem] truncate text-[0.8125rem] text-sl-faint max-[640px]:hidden"
            >{{ location.dir }}</span>
            <span
              v-if="location.dir"
              class="shrink-0 text-[0.8125rem] text-sl-faint opacity-60 max-[640px]:hidden"
              aria-hidden="true"
            >/</span>
            <span class="flex-1 min-w-0 truncate font-sl-display text-[0.875rem] font-semibold tracking-[-0.01em] text-sl-text">{{ location.page }}</span>
            <i
              class="fas fa-chevron-down absolute right-3.5 top-1/2 -translate-y-1/2 text-[0.5625rem] text-sl-faint pointer-events-none
                transition-transform duration-200 ease-[ease]"
              :class="{ 'rotate-180': menuOpen }"
            ></i>
          </button>

          <!-- Every page in the project, grouped by the section it belongs to:
               folders, then the pages inside them. Names only — the menu is a
               map of the app, not of its source tree. -->
          <div
            v-if="menuOpen && apps.length > 0"
            class="pv-menu absolute z-20 left-1/2 -translate-x-1/2 origin-top mt-2.5 w-80 max-w-[calc(100vw-1.5rem)] max-h-[60vh] overflow-y-auto p-1.5
              rounded-2xl border border-sl-line-strong bg-sl-surface [box-shadow:var(--sl-card-shadow),0_24px_60px_-24px_rgba(0,0,0,0.35)]
              dark:bg-sl-surface-2 dark:[box-shadow:0_24px_60px_-20px_rgba(0,0,0,0.85)]"
          >
            <p
              class="flex items-center justify-between pt-1.5 px-2.5 pb-2 mb-1 border-b border-b-sl-line
                text-[0.6875rem] font-semibold tracking-[0.08em] uppercase text-sl-faint"
            >
              Pages in your app
              <span :class="['pv-menu-count', COUNT]">{{ pageCount }}</span>
            </p>
            <div v-for="(app, i) in apps" :key="app.name" class="pv-row" :style="{ '--pv-i': i }">
              <button
                type="button"
                @click="toggleApp(app.name)"
                :aria-expanded="isExpanded(app.name)"
                class="flex items-center gap-2 w-full py-[0.4375rem] px-2.5 rounded-[0.625rem] text-[0.8125rem] font-semibold text-sl-text cursor-pointer
                  transition-[background-color] duration-[140ms] ease-[ease] hover:bg-sl-chip-bg
                  focus-visible:![outline:none] focus-visible:[box-shadow:inset_0_0_0_2px_var(--sl-focus)]"
              >
                <i
                  class="fas fa-chevron-right w-2.5 shrink-0 text-[0.5rem] text-sl-faint transition-transform duration-200 ease-[ease]"
                  :class="{ 'rotate-90': isExpanded(app.name) }"
                ></i>
                <i
                  class="fas shrink-0 w-3.5 text-[0.75rem] text-sl-amber"
                  :class="isExpanded(app.name) ? 'fa-folder-open' : 'fa-folder'"
                ></i>
                <span class="truncate flex-1 text-left">{{ app.name }}</span>
                <span :class="COUNT">{{ app.pages.length }}</span>
              </button>

              <div v-if="isExpanded(app.name)" class="mt-px mb-1 ml-[1.3125rem] pl-2 border-l border-l-sl-line">
                <p v-if="!app.pages.length" class="py-1.5 px-2.5 text-[0.75rem] italic text-sl-faint">No pages yet</p>
                <button
                  v-for="page in app.pages"
                  :key="page.path"
                  type="button"
                  @click="onSelectPage(page.path)"
                  :aria-current="page.path === currentPath ? 'page' : undefined"
                  class="pv-file flex items-center gap-2 w-full py-[0.4375rem] px-2.5 rounded-[0.625rem] text-[0.8125rem] text-left cursor-pointer
                    [transition:background-color_0.14s_ease,color_0.14s_ease] hover:bg-sl-chip-bg hover:text-sl-text
                    focus-visible:![outline:none] focus-visible:[box-shadow:inset_0_0_0_2px_var(--sl-focus)]"
                  :class="page.path === currentPath ? 'bg-sl-chip-bg-hover font-semibold text-sl-text' : 'text-sl-muted'"
                >
                  <i
                    class="fas fa-file-lines w-3.5 shrink-0 text-[0.6875rem]"
                    :class="page.path === currentPath ? 'text-sl-coral' : 'text-sl-faint'"
                  ></i>
                  <span class="truncate flex-1">{{ page.title }}</span>
                  <span v-if="page.path === currentPath" class="shrink-0 text-[0.6875rem] font-medium text-sl-coral">Viewing</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Back to the main agent: phones only, where the preview has
             replaced the chat (see canReturnToChat). On the narrowest phones
             it drops its chevron, so the page name keeps a readable share. -->
        <button
          v-if="canReturnToChat"
          type="button"
          @click="emit('return-to-chat')"
          class="shrink-0 inline-flex items-center gap-[0.3125rem] h-8 px-3 rounded-full bg-sl-chip-bg text-sl-muted text-[0.75rem] font-medium whitespace-nowrap cursor-pointer
            [transition:background-color_0.16s_ease,color_0.16s_ease] hover:bg-sl-chip-bg-hover hover:text-sl-text
            max-[767px]:h-7 max-[767px]:gap-1 max-[767px]:px-2
            focus-visible:![outline:none] focus-visible:[box-shadow:0_0_0_2px_var(--sl-focus)]"
          aria-label="Back to the coordinator"
        >
          <!-- !: Font Awesome's .fas sets display too. -->
          <i class="fas fa-chevron-left text-[0.5rem] opacity-[0.55] max-[359px]:!hidden"></i>
          <i class="fas fa-comments text-[0.625rem] opacity-75"></i>
          <span>Coordinator</span>
          <span
            v-if="returnCount"
            class="inline-flex items-center justify-center min-w-[1.0625rem] h-[1.0625rem] px-1 rounded-full bg-sl-grad text-sl-on-accent
              text-[0.625rem] font-semibold tabular-nums leading-none"
          >{{ returnCount }}</span>
        </button>

        <!-- Loading ribbon: a travelling sliver of the coral-to-amber light
             along the dock's lower edge while the session is starting or a
             navigation is in flight. -->
        <div
          v-if="busy"
          class="pv-progress absolute left-5 right-5 -bottom-px h-0.5 overflow-hidden rounded-sm pointer-events-none
            after:content-[''] after:absolute after:top-0 after:bottom-0 after:w-[34%] after:rounded-sm after:bg-sl-grad"
          aria-hidden="true"
        ></div>
      </div>
    </div>

    <!-- The frame: the app as a lit card on the stage — rounded, edged with a
         hairline, and set on the stage's light. Decoration lives here, never
         on .pv-stage (see the note on the screen element). Phones: no stage
         margins and no card, just a hairline on top. -->
    <div class="relative flex flex-1 min-h-0 justify-center px-4 pb-4 max-[767px]:p-0">
      <div
        class="relative flex flex-col flex-1 min-w-0 min-h-0 overflow-hidden rounded-2xl border border-sl-line-strong shadow-sl-win
          max-[767px]:rounded-none max-[767px]:shadow-none
          max-[767px]:[border-width:1px_0_0] max-[767px]:[border-style:solid_none_none] max-[767px]:[border-color:var(--sl-line)_currentcolor_currentcolor]"
      >

        <!-- Screen: frames from the remote browser, input forwarded back.
             NOTE for future edits: this element's box IS the remote viewport —
             paneSize() measures it and pageCoords() maps client coords through it
              1:1. Never give it padding, a border, or anything else that makes its
             rect disagree with the <img> inside; decoration goes on the background
             or in pointer-events-none overlays. Its matte (bg-sl-bg-deep) is
             what shows through when the frame and remote viewport briefly
             disagree, or an optimistic scroll opens a gap. -->
        <div
          ref="screenRef"
          tabindex="0"
          class="pv-stage group/stage relative flex-1 min-h-0 outline-none overflow-hidden touch-none bg-sl-bg-deep"
          :style="stageStyle"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @pointercancel="onPointerCancel"
          @wheel.prevent="onWheel"
          @keydown="onKeyDown"
          @keyup="onKeyUp"
          @contextmenu.prevent
        >
          <!-- Drawn at exactly the remote viewport's CSS size from the top-left
               corner, never stretched to the pane: with the browser rendering at
               this screen's pixel ratio, each frame pixel lands on one screen
               pixel, which is what keeps text as crisp as in a real browser.
               While a pane resize is in flight the frame overhangs or falls a
               few px short, like a real window mid-resize. The translate3d
               carries the optimistic local scroll (compositor-only, always
               present so the img keeps its own layer); gaps it opens show the
               container bg. -->
          <!-- The rest of the page, captured ahead of time (see Backdrop). It
               sits behind the frame and scrolls with the page, so a scroll
               shows real content straight away instead of an empty strip.
               Slices stack at their page offsets in one layer that the scroll
               moves; the frame on top hides while the backdrop carries a
               scroll, and the fixed-elements overlay pins over both. -->
          <div
            v-if="backdropUsable && backdrop"
            class="pv-backdrop absolute top-0 left-0 w-full pointer-events-none will-change-transform"
            :style="backdropStyle"
            aria-hidden="true"
          >
            <img
              v-for="slice in backdrop.slices"
              :key="slice.y"
              :src="slice.src"
              alt=""
              draggable="false"
              class="pv-backdrop-slice absolute left-0 max-w-none select-none"
              :style="sliceStyle(slice.y)"
            />
          </div>
          <!-- Sized inline to the remote viewport; max-w-none keeps the base
               img rule from squeezing it into a narrower pane (which would
               resample it). -->
          <img
            v-if="frameSrc"
            :src="frameSrc"
            alt=""
            draggable="false"
            decoding="async"
            class="pv-live absolute top-0 left-0 max-w-none select-none pointer-events-none"
            :class="{ 'is-covered invisible': backdropCarries }"
            :style="frameStyle"
          />
          <!-- While the backdrop carries a scroll, the page's fixed header (and
               anything else pinned to the view) stays put on top of it. -->
          <img
            v-if="backdropCarries && backdrop?.overlay"
            :src="backdrop.overlay"
            alt=""
            draggable="false"
            class="pv-backdrop-overlay absolute top-0 left-0 max-w-none pointer-events-none select-none"
            :style="viewportBox"
            aria-hidden="true"
          />

          <!-- The page's scrollbar, drawn here so it moves with the page the
               moment it scrolls (the remote page's own is hidden). Its pointer
               input stays here, never forwarded to the page underneath; wheel
               input passes through and scrolls the page as usual.
               A slim ink pill that shows while the page moves and on hover,
               then gets out of the way. It sits over whatever the previewed
               app draws, light or dark, so the pill carries a faint light rim
               to stay visible on both. Touch (hover: none): only while
               scrolling, and too slim to aim at, so it is a position
               indicator there, as on a phone's own browser. -->
          <div
            v-if="scrollbar && phase === 'ready'"
            ref="scrollbarRef"
            class="pv-scrollbar group/bar absolute top-1 right-0.5 bottom-1 z-[2] w-3.5 cursor-default touch-none
              transition-opacity duration-[260ms] ease-[ease] motion-reduce:[transition:none] [@media(hover:none)]:pointer-events-none"
            :class="scrollbarActive || thumbDragging
              ? 'opacity-100'
              : 'opacity-0 group-hover/stage:opacity-100 [@media(hover:none)]:group-hover/stage:opacity-0'"
            aria-hidden="true"
            @pointerdown.stop.prevent="onScrollbarPointerDown"
            @pointermove.stop="onScrollbarPointerMove"
            @pointerup.stop="onScrollbarPointerUp"
            @pointercancel.stop="onScrollbarPointerUp"
          >
            <div
              class="pv-scrollbar-thumb absolute right-[0.1875rem] rounded-full [box-shadow:0_0_0_1px_rgba(255,255,255,0.55)]
                h-[max(2rem,var(--pv-thumb-size,100%))] top-[calc((100%-max(2rem,var(--pv-thumb-size,100%)))*var(--pv-thumb-at,0))]
                [transition:width_160ms_ease,background-color_160ms_ease] motion-reduce:[transition:none]"
              :class="thumbDragging
                ? 'w-2 bg-[rgba(20,21,30,0.55)]'
                : 'w-1.5 bg-[rgba(20,21,30,0.38)] group-hover/bar:w-2 group-hover/bar:bg-[rgba(20,21,30,0.55)]'"
              :style="thumbStyle"
            ></div>
          </div>

          <!-- Console-error banner: recent JS errors reported by the previewed
               page itself. Pointer events must not leak through to the screen's
               input forwarding underneath. -->
          <div
            v-if="consoleBannerVisible && latestConsoleError"
            class="pv-alert absolute z-10 left-3 right-3 bottom-3 flex items-center gap-2.5 overflow-hidden py-2 pr-2.5 pl-3.5 rounded-[0.875rem]
              border border-ink/[0.08] bg-[rgba(253,249,242,0.96)] [backdrop-filter:blur(8px)]
              [box-shadow:inset_0_1px_0_rgba(255,255,255,0.8),0_16px_36px_-16px_rgba(19,26,44,0.4)]
              dark:border-white/10 dark:bg-[rgba(18,18,20,0.96)]
              dark:[box-shadow:inset_0_1px_0_rgba(255,255,255,0.04),0_16px_36px_-16px_rgba(0,0,0,0.9)]"
            @pointerdown.stop
            @pointermove.stop
            @pointerup.stop
            @wheel.stop
          >
            <!-- A stripe of alarm down the edge — enough to read as "wrong"
                 from the corner of the eye without turning the card red. -->
            <span class="absolute left-0 top-0 bottom-0 w-[3px] bg-[linear-gradient(180deg,#f87171,#dc2626)]" aria-hidden="true"></span>
            <div
              class="grid place-items-center shrink-0 w-6 h-6 rounded-full bg-red-500/10 text-red-600 text-[0.625rem]
                [box-shadow:inset_0_0_0_1px_rgba(239,68,68,0.2)] dark:bg-red-500/[0.14] dark:text-red-400"
            >
              <i class="fas fa-exclamation"></i>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-[0.8125rem] font-medium leading-tight text-blue-950 dark:text-white/[0.92]">
                {{ errorRouting ? 'Imagi is fixing something in your app' : 'Something broke in your app' }}
              </p>
              <p :class="ALERT_DETAIL">{{ latestConsoleError.text }}</p>
              <p v-if="errorRoutingNote" :class="ALERT_DETAIL" data-testid="error-routing-note">{{ errorRoutingNote }}</p>
            </div>
            <button
              type="button"
              @click="dismissConsoleBanner"
              title="Dismiss"
              aria-label="Dismiss"
              class="inline-flex items-center justify-center shrink-0 w-7 h-7 rounded-full text-[0.6875rem] cursor-pointer
                [transition:background-color_0.14s_ease,color_0.14s_ease]
                text-ink/40 hover:bg-ink/[0.06] hover:text-ink/70
                dark:text-white/40 dark:hover:bg-white/[0.07] dark:hover:text-white/75
                focus-visible:![outline:none] focus-visible:[box-shadow:0_0_0_2px_#fbfaf7,0_0_0_4px_rgba(194,65,12,0.4)]"
            >
              <i class="fas fa-times"></i>
            </button>
          </div>

          <!-- Starting: the wait is long enough (first start installs the whole
               dependency tree) that it gets a real progress story — an elapsed
               clock and copy that tracks which stage the wait is in. -->
          <div v-if="phase === 'starting'" :class="[VEIL, VEIL_GLASS]">
            <div :class="['pv-notice', NOTICE]">
              <!-- A ring of ink drawn once around, with a heartbeat at the centre. -->
              <div class="pv-orbit relative grid place-items-center w-[3.25rem] h-[3.25rem] mb-1.5" aria-hidden="true">
                <span class="pv-orbit-core w-2 h-2 rounded-full bg-blue-950 dark:bg-[#f3ede2]"></span>
              </div>
              <h3 :class="NOTICE_TITLE">Bringing your app to life</h3>
              <p :class="NOTICE_BODY" aria-live="polite">{{ startingStage }}</p>
              <!-- Elapsed clock: proof of life while a cold start installs a dependency tree -->
              <p
                class="mt-0.5 [font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace] text-[0.6875rem] tabular-nums tracking-[0.04em]
                  text-ink/[0.35] dark:text-blue-100/[0.35]"
              >{{ elapsedLabel }}</p>
            </div>
          </div>

          <!-- Error overlay -->
          <div v-else-if="phase === 'error'" :class="[VEIL, 'bg-sl-bg-deep']">
            <div :class="['pv-notice', NOTICE]">
              <div :class="[MARK, MARK_ALERT]" aria-hidden="true">
                <i class="fas fa-triangle-exclamation"></i>
              </div>
              <h3 :class="NOTICE_TITLE">The preview couldn't start</h3>
              <p :class="NOTICE_BODY">This is the preview server, not your app's code — a retry usually clears it.</p>
              <!-- Raw server text stays raw — mono, boxed, and scrollable
                   rather than dressed up as prose. -->
              <pre
                class="w-full max-h-28 overflow-auto mt-1.5 mb-1 py-2 px-2.5 rounded-[0.625rem] border border-ink/[0.08] bg-ink/[0.035]
                  [font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace] text-[0.6875rem] leading-[1.5] text-left
                  whitespace-pre-wrap [word-break:break-word] text-ink/[0.65]
                  dark:border-white/[0.08] dark:bg-white/[0.04] dark:text-blue-100/[0.65]"
              >{{ error }}</pre>
              <button @click="startPreview" :class="BTN">
                <i class="fas fa-sync-alt"></i>
                Try again
              </button>
            </div>
          </div>

          <!-- Stopped overlay (session ended, e.g. idle shutdown or restart) -->
          <div v-else-if="phase === 'stopped'" :class="[VEIL, VEIL_GLASS]">
            <div :class="['pv-notice', NOTICE]">
              <div :class="[MARK, MARK_QUIET]" aria-hidden="true">
                <i class="fas fa-moon"></i>
              </div>
              <h3 :class="NOTICE_TITLE">Your preview dozed off</h3>
              <p :class="NOTICE_BODY">The session shuts down after a quiet spell to save you money. Everything you built is safe.</p>
              <button @click="startPreview" :class="BTN">
                <i class="fas fa-play"></i>
                Wake it up
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, shallowRef, watch, computed, onMounted, onBeforeUnmount } from 'vue'
import {
  PreviewService,
  PreviewNotRunningError,
  type PreviewApp,
  type PreviewConsoleError,
  type PreviewFrame,
  type PreviewInputEvent,
  type PreviewScroll,
} from '../../../services/previewService'
import { rememberPreviewViewport } from '@/shared/services/previewPrewarm'

const props = defineProps<{
  projectId: string
  /** Pane is hidden/backgrounded: keep the session warm but stop active work. */
  paused?: boolean
  /**
   * The preview has replaced the panes rather than sitting beside them, and
   * nothing else on screen brings them back. True only on a phone showing the
   * preview: desktop collapses the sidebar from the top bar's toggle, which
   * stays put and is the way back there, so a second control would be a second
   * way to do one thing.
   */
  canReturnToChat?: boolean
  /** Badge on that return: how much has come back from the subagents and is
   *  sitting in the thread — questions to answer and work that just landed. */
  returnCount?: number
}>()

const emit = defineEmits<{
  /** Errors the page reported went to an agent: which one. */
  (e: 'errors-routed', routing: NonNullable<PreviewFrame['error_routing']>): void
  /** Take me back to the main agent (the toolbar's return pill). */
  (e: 'return-to-chat'): void
}>()

// ---------------------------------------------------------------------------
// Class lists shared by several elements of the template
// ---------------------------------------------------------------------------

/** A dock button (back, forward, refresh, home). Phones get a tighter one. */
const NAV =
  'inline-flex items-center justify-center w-8 h-8 max-[767px]:w-7 max-[767px]:h-7 rounded-full text-[0.75rem] text-sl-muted cursor-pointer [transition:color_0.15s_ease,background-color_0.15s_ease,transform_0.15s_ease] enabled:hover:text-sl-text enabled:hover:bg-sl-chip-bg-hover enabled:active:scale-[0.92] disabled:opacity-30 disabled:cursor-not-allowed focus-visible:![outline:none] focus-visible:[box-shadow:0_0_0_2px_var(--sl-focus)]'
/** Page counts in the page menu. */
const COUNT = 'text-[0.6875rem] font-medium tabular-nums tracking-[0] text-sl-faint'
const ALERT_DETAIL =
  'truncate [font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace] text-[0.6875rem] text-ink/50 dark:text-blue-100/[0.45]'

// Notices (starting / stopped / error): a veil over the stage holding one card.
const VEIL = 'absolute inset-0 flex items-center justify-center p-6 [backdrop-filter:blur(6px)]'
const VEIL_GLASS =
  'bg-[color:color-mix(in_srgb,var(--sl-bg-deep)_86%,transparent)] dark:bg-[color:color-mix(in_srgb,var(--sl-bg-deep)_88%,transparent)]'
const NOTICE =
  'flex flex-col items-center gap-2 w-full max-w-[23rem] pt-7 px-6 pb-6 rounded-[1.25rem] border border-ink/[0.08] bg-[#fbfaf7] text-center [box-shadow:inset_0_1px_0_rgba(255,255,255,0.8),0_24px_60px_-24px_rgba(19,26,44,0.3)] dark:border-white/10 dark:bg-[#121214] dark:[box-shadow:inset_0_1px_0_rgba(255,255,255,0.04),0_24px_60px_-24px_rgba(0,0,0,0.9)]'
const NOTICE_TITLE =
  "font-sl-display [font-variation-settings:'opsz'_24,'SOFT'_30,'WONK'_1] text-[1.0625rem] font-semibold tracking-[-0.012em] text-blue-950 dark:text-white/[0.94]"
const NOTICE_BODY = 'max-w-[19rem] text-[0.8125rem] leading-[1.5] text-ink/[0.55] dark:text-blue-100/[0.55]'
/** Notice marks: the same rounded plaque as the pane header's mark. */
const MARK = 'grid place-items-center w-11 h-11 mb-2 rounded-[0.875rem] text-[0.9375rem]'
const MARK_QUIET =
  'bg-ink/[0.06] text-ink/60 [box-shadow:inset_0_0_0_1px_rgba(19,26,44,0.06)] dark:bg-[rgba(243,237,226,0.09)] dark:text-[rgba(243,237,226,0.75)] dark:[box-shadow:inset_0_0_0_1px_rgba(255,255,255,0.07)]'
const MARK_ALERT =
  'bg-red-500/[0.08] text-red-600 [box-shadow:inset_0_0_0_1px_rgba(239,68,68,0.18)] dark:bg-red-500/[0.12] dark:text-red-400 dark:[box-shadow:inset_0_0_0_1px_rgba(239,68,68,0.25)]'
/** The notices' one button, in navy ink (bone in dark). In dark the hover
 *  keeps the resting shadow; the focus ring wins over both. */
const BTN =
  'inline-flex items-center gap-1.5 h-[2.125rem] mt-2.5 px-[1.125rem] rounded-full text-[0.8125rem] font-medium cursor-pointer [&_i]:text-[0.625rem] [transition:background-color_0.18s_ease,box-shadow_0.18s_ease,transform_0.18s_ease] bg-blue-950 text-[#fbfaf7] [box-shadow:0_1px_2px_rgba(19,26,44,0.2),0_3px_8px_-2px_rgba(19,26,44,0.25)] hover:bg-blue-900 hover:-translate-y-px hover:[box-shadow:0_2px_3px_rgba(19,26,44,0.2),0_6px_14px_-4px_rgba(19,26,44,0.3)] active:translate-y-0 motion-reduce:hover:[transform:none] focus-visible:![outline:none] focus-visible:[box-shadow:0_0_0_2px_#fbfaf7,0_0_0_4px_rgba(194,65,12,0.4)] dark:bg-[#f3ede2] dark:text-blue-950 dark:[box-shadow:0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)] dark:hover:bg-white dark:focus-visible:[box-shadow:0_0_0_2px_#121214,0_0_0_4px_rgba(251,191,36,0.5)]'

type Phase = 'idle' | 'starting' | 'ready' | 'stopped' | 'error'

const phase = ref<Phase>('idle')
const error = ref<string | null>(null)
const frameSrc = ref<string | null>(null)
const etag = ref<string | undefined>(undefined)
const currentPath = ref('/')
const canGoBack = ref(false)
const canGoForward = ref(false)
// Size of the remote browser viewport in CSS pixels; kept in sync with the
// pane so client coordinates map 1:1 onto page coordinates.
const viewport = ref<[number, number]>([1280, 800])

// A navigation (goto/back/forward/reload) is waiting on the server. Purely
// presentational: it drives the loading ribbon and the refresh icon's spin.
const navigating = ref(false)
const busy = computed(() => phase.value === 'starting' || navigating.value)

const menuOpen = ref(false)
// The folders (apps) currently open in the page menu. Opening the menu opens
// all of them (see onMenuToggle); a folder can still be folded away by hand.
const expandedApps = ref<string[]>([])
const menuRoot = ref<HTMLElement | null>(null)
const screenRef = ref<HTMLElement | null>(null)

// ---------------------------------------------------------------------------
// Session lifecycle + frame polling
// ---------------------------------------------------------------------------

let pollTimer: number | null = null
let resizeTimer: number | null = null
let observer: ResizeObserver | null = null
let lastActivityAt = 0
let disposed = false

// The remote browser renders at this screen's pixel ratio, so a frame maps
// 1:1 onto screen pixels. Read fresh each time: dragging the window to
// another display or zooming the page changes it. Capped at 2: a 3x phone
// screen would more than double every frame for little visible gain.
function deviceScaleFactor(): number {
  return Math.min(window.devicePixelRatio || 1, 2)
}
// The ratio the remote viewport was last set to (see ensureViewportMatchesPane).
let viewportDsf = deviceScaleFactor()

function paneSize(): { width: number; height: number } {
  const rect = screenRef.value?.getBoundingClientRect()
  return {
    width: Math.max(320, Math.round(rect?.width || 1280)),
    height: Math.max(320, Math.round(rect?.height || 800)),
  }
}

// Every frame request (poll, input batch, navigation, start) takes a number
// when it is sent, and a response only lands if it was sent after the one
// already applied. Responses race each other — a poll and an input batch can
// be served by different workers — so arrival order means nothing; without
// this an older poll could replace a newer frame mid-scroll and the page would
// jump back.
let requestSeq = 0
let appliedSeq = 0
let shownFrameSeq = 0

// Frames are decoded off-screen before being shown, so the JPEG decode never
// blocks the paint that displays it (decoding on the visible <img> stutters
// scrolling). The frame's scroll offset goes on screen in the same tick as its
// pixels, so the transform that places it (see frameStyle) never lags them.
function showFrame(src: string, seq: number, scroll: PreviewScroll | null | undefined) {
  const img = new Image()
  img.src = src
  const show = () => {
    if (disposed || seq <= shownFrameSeq) return
    shownFrameSeq = seq
    frameSrc.value = src
    // A frame that couldn't report its offset keeps the last one: the best
    // guess, and right whenever the page didn't move.
    if (scroll) shownScrollY.value = scroll.y
  }
  img.decode().then(show, show)
}

// Apply one response. Returns false (and changes nothing) when a response
// sent later has already been applied.
function applyFrame(f: PreviewFrame, seq: number): boolean {
  if (seq <= appliedSeq) return false
  appliedSeq = seq
  // Kept when a payload has none: the page failed to report it this once
  // (typically mid-navigation), which says nothing about its height.
  if (f.scroll) scrollInfo.value = f.scroll
  if (f.frame_skipped) {
    // Asked for no bitmap (a scroll the backdrop carries): what's on screen
    // stays, and the scroll above is all this reply says.
  } else if (f.frame) {
    showFrame(`data:image/${f.frame_type === 'png' ? 'png' : 'jpeg'};base64,${f.frame}`, seq, f.scroll)
  } else if (seq > shownFrameSeq) {
    // No bitmap: it matched the etag, so the pixels on screen are this frame.
    shownFrameSeq = seq
    if (f.scroll) shownScrollY.value = f.scroll.y
  }
  if (f.etag) etag.value = f.etag
  if (typeof f.path === 'string') currentPath.value = f.path
  canGoBack.value = !!f.can_go_back
  canGoForward.value = !!f.can_go_forward
  if (f.viewport) viewport.value = f.viewport
  // A full replacement list on every payload (empty array clears); guarded so
  // a payload from an older backend without the field keeps the current list.
  if (Array.isArray(f.console_errors)) {
    consoleErrors.value = f.console_errors
    errorRouting.value = f.console_errors.length ? (f.error_routing ?? errorRouting.value) : null
    if (f.error_routing?.new) emit('errors-routed', f.error_routing)
  }
  return true
}

// For responses that aren't input batches (start, poll, navigate): apply it,
// and if no input was sent while it was out, it is the server's word on where
// the page is scrolled.
function applyStatus(f: PreviewFrame, seq: number) {
  if (applyFrame(f, seq) && inputInFlight === 0 && lastInputSeq < seq) reconcileScroll(f)
}

// ---------------------------------------------------------------------------
// Console errors from the previewed page (backend contract: frame/status
// payloads carry the last ~5 uncaught errors, deduped, cleared on navigation)
// ---------------------------------------------------------------------------

const consoleErrors = ref<PreviewConsoleError[]>([])
// Set once the server has sent the current errors on to be fixed (to the
// thread that just changed that part of the app, or to the coordinator); the
// banner then says so.
const errorRouting = ref<PreviewFrame['error_routing']>(null)
const errorRoutingNote = computed(() =>
  errorRouting.value?.to === 'thread'
    ? 'Sent to the thread that just changed this part of your app.'
    : errorRouting.value?.to === 'coordinator'
      ? 'Sent to the coordinator, which is getting it fixed.'
      : ''
)
// Key of the error the user dismissed; the banner stays hidden until a
// different error shows up.
const dismissedErrorKey = ref<string | null>(null)

function consoleErrorKey(err: PreviewConsoleError): string {
  // Text alone, no ts: the in-page collector bumps ts on every repeat of the
  // same error, so a ts-based key would resurrect a dismissed banner on the
  // next poll for any recurring error (the most common failure mode).
  return err.text
}

const latestConsoleError = computed<PreviewConsoleError | null>(() => {
  let latest: PreviewConsoleError | null = null
  for (const err of consoleErrors.value) {
    if (err?.text && (!latest || err.ts >= latest.ts)) latest = err
  }
  return latest
})

const consoleBannerVisible = computed(() =>
  phase.value === 'ready' &&
  latestConsoleError.value !== null &&
  consoleErrorKey(latestConsoleError.value) !== dismissedErrorKey.value
)

function dismissConsoleBanner() {
  if (latestConsoleError.value) dismissedErrorKey.value = consoleErrorKey(latestConsoleError.value)
}

async function startPreview() {
  if (!props.projectId || phase.value === 'starting') return
  phase.value = 'starting'
  error.value = null
  const size = paneSize()
  viewportDsf = deviceScaleFactor()
  rememberPreviewViewport(size, viewportDsf)
  showRunningSession(size)
  try {
    const seq = ++requestSeq
    const result = await PreviewService.start(props.projectId, size, viewportDsf)
    if (disposed) return
    resyncScroll()
    applyStatus(result, seq)
    phase.value = 'ready'
    schedulePoll(200)
    // The size passed to start() can be stale — measured before the pane was
    // laid out, which falls back to a desktop width and makes the app render
    // its desktop layout squished into a phone. The ResizeObserver won't fix
    // it because the pane size never actually changes, so re-assert the
    // viewport against the now-laid-out pane once we're ready.
    requestAnimationFrame(() => void ensureViewportMatchesPane())
    // Starting may have scaffolded/hydrated the working copy the pages
    // menu reads from, so fetch it (again) now.
    void refreshPages()
  } catch (e) {
    if (disposed) return
    // Keep the failure local to this component — never call store.setError, or
    // the workspace-level error path can navigate the user back to /projects.
    phase.value = 'error'
    error.value = e instanceof Error ? e.message : 'Preview failed to start.'
  }
}

// A session that is already running (prewarmed at sign-in, or still up from
// a recent visit) goes on screen straight away: the frame endpoint answers
// without waiting behind start(), which still runs to claim the session and
// sync its viewport. Only a frame rendered at this pane's size is shown — one
// at another size would flash stretched until the resize lands. It is asked
// as a probe, so nothing running yet comes back as an answer, not an error.
function showRunningSession(size: { width: number; height: number }) {
  const seq = ++requestSeq
  PreviewService.frame(props.projectId, undefined, { probe: true })
    .then((f) => {
      if (disposed || phase.value !== 'starting' || !f.frame) return
      const [w, h] = f.viewport || [0, 0]
      if (Math.abs(w - size.width) >= 4 || Math.abs(h - size.height) >= 4) return
      if (f.device_scale_factor !== viewportDsf) return
      resyncScroll()
      applyStatus(f, seq)
      phase.value = 'ready'
      schedulePoll(200)
    })
    .catch(() => {})
}

function markSessionStopped() {
  phase.value = 'stopped'
  stopInertia()
  resyncScroll()
}

// While paused the frames aren't visible, so polling drops to a slow
// keep-alive that stops the session from idling out — never the active
// cadence, even when a caller asks for a short delay.
const PAUSED_KEEPALIVE_MS = 20000

function schedulePoll(delay?: number) {
  if (pollTimer) window.clearTimeout(pollTimer)
  if (disposed) return
  if (props.paused) {
    pollTimer = window.setTimeout(pollFrame, PAUSED_KEEPALIVE_MS)
    return
  }
  const active = Date.now() - lastActivityAt < 4000
  pollTimer = window.setTimeout(pollFrame, delay ?? (active ? 120 : 1500))
}

async function pollFrame() {
  if (disposed || phase.value !== 'ready') return
  if (document.hidden) {
    schedulePoll(1000)
    return
  }
  if (inputInFlight > 0) {
    // Input responses carry frames themselves; just check back in shortly.
    schedulePoll(300)
    return
  }
  try {
    const seq = ++requestSeq
    const f = await PreviewService.frame(props.projectId, etag.value)
    applyStatus(f, seq)
    void maybeRefreshBackdrop()
  } catch (e) {
    if (e instanceof PreviewNotRunningError) {
      markSessionStopped()
      return
    }
    // Transient failure (network hiccup): keep polling.
  }
  schedulePoll()
}

// ---------------------------------------------------------------------------
// Scrolling
//
// The page lives in a remote browser, so a scroll otherwise shows nothing
// until a round trip brings back a frame. Instead the client keeps its own
// idea of where the page is scrolled (targetScrollY) and moves it the moment a
// wheel, drag or glide happens. Every frame reports the scroll offset it was
// captured at (shownScrollY once on screen), so the frame is drawn shifted by
// exactly the distance between the two (compositor-only translate3d). When a
// frame arrives that already shows the scroll, the shift disappears in the
// same paint the new pixels appear: nothing moves, the gap just fills in.
//
// Being absolute is what keeps it steady. An earlier version counted deltas
// in flight and retired them as responses arrived, and any response that
// raced another (a poll beside an input batch, two workers answering out of
// order) counted a scroll twice or not at all, which read as the page jumping.
//
// The client's estimate is replaced by the server's offset whenever a
// response covers every input sent (reconcileScroll), replaying wheel deltas
// that haven't been sent yet. Pages whose scrolling happens inside an element
// rather than the document report nothing to scroll; those get no
// optimistic shift, just frames.
// ---------------------------------------------------------------------------

/** Scroll metrics from the latest response: page height, background. */
const scrollInfo = ref<PreviewScroll | null>(null)
/** Scroll offset (page px) of the frame on screen. */
const shownScrollY = ref(0)
/** Where the page is, or is about to be, scrolled to (page px). */
const targetScrollY = ref(0)

// Scroll input not yet sent, in order: wheel deltas, or an absolute offset
// from the scrollbar. Replayed onto the server's offset in reconcileScroll.
type ScrollOp = { dy: number } | { top: number }
let unsentScroll: ScrollOp[] = []

const maxScrollY = computed(() => {
  const s = scrollInfo.value
  return s ? Math.max(0, s.height - s.viewport_height) : 0
})

function clampScroll(y: number): number {
  return Math.max(0, Math.min(y, maxScrollY.value))
}

function replayScroll(from: number, ops: ScrollOp[]): number {
  let y = from
  for (const op of ops) y = 'top' in op ? clampScroll(op.top) : clampScroll(y + op.dy)
  return y
}

// f answers every input sent so far: adopt its offset plus what's unsent.
function reconcileScroll(f: PreviewFrame) {
  targetScrollY.value = f.scroll ? replayScroll(f.scroll.y, unsentScroll) : shownScrollY.value
}

// A wheel delta the server is about to apply. Deltas of one sign merge (the
// clamp at the page edge gives the same answer either way); a reversal starts
// a new entry, matching the separate wheel events enqueue sends for it.
function scrollLocallyBy(dy: number) {
  if (!dy) return
  const last = unsentScroll[unsentScroll.length - 1]
  if (last && 'dy' in last && Math.sign(last.dy) === Math.sign(dy)) last.dy += dy
  else unsentScroll.push({ dy })
  targetScrollY.value = clampScroll(targetScrollY.value + dy)
}

function scrollLocallyTo(top: number) {
  // An absolute offset makes everything queued before it moot.
  unsentScroll = [{ top }]
  targetScrollY.value = clampScroll(top)
}

// Forget the estimate (navigation, pause, a dropped batch): show the frame
// where it is until the next response says where the page is.
function resyncScroll() {
  unsentScroll = []
  targetScrollY.value = shownScrollY.value
}

// The remote viewport's box in pane px (one page px is one pane px).
const viewportBox = computed(() => ({
  width: `${viewport.value[0]}px`,
  height: `${viewport.value[1]}px`,
}))

const frameStyle = computed(() => {
  // Beyond a screenful the frame has fully left the pane, so cap there.
  const limit = viewport.value[1]
  const raw = shownScrollY.value - targetScrollY.value
  // Whole device pixels, so text in the frame stays crisp while it is shifted.
  const shift = toDevicePx(Math.max(-limit, Math.min(raw, limit)))
  return {
    ...viewportBox.value,
    transform: `translate3d(0, ${shift}px, 0)`,
  }
})

// The strip a shift uncovers shows the page's own background, so a fast
// scroll reads as content still arriving rather than a dark hole.
const stageStyle = computed(() => {
  const bg = scrollInfo.value?.background || ''
  if (!bg) return undefined
  // Transparent all the way down means the browser's default white canvas.
  const transparent = /^rgba\(.*,\s*0(\.0+)?\)$/.test(bg)
  return { backgroundColor: transparent ? '#fff' : bg }
})

// ---------------------------------------------------------------------------
// Backdrop
//
// A frame shows only the viewport, so even a perfectly placed scroll has
// nothing to show for the part of the page coming into view until the next
// frame arrives. The backdrop is the page around the current scroll (up to
// ~10,000px of it), captured once per page in slices, with the page's fixed
// elements (a fixed or sticky header) captured separately on transparency.
// While a scroll is ahead of the frames, the backdrop is what's on screen,
// scrolled locally, with the fixed layer pinned on top: the page simply
// scrolls. Its slices are as sharp as a frame at rest, so a scroll it covers
// asks for no frames at all (they would only be lower-resolution motion
// frames); the crisp frame for where the page landed takes over once the
// gesture ends, showing the same pixels.
//
// Captured only while the user isn't interacting (it scrolls the remote page
// through, under a lock that holds input back), and again when the page,
// its height or the pane width changes, when a scroll settles near the edge
// of what it covers, or when the page has changed and it's a while old. The
// server keeps the last capture and hands it back while the page is
// unchanged, so one taken ahead of time (when the preview was warmed up) is
// asked for straight away, even mid-gesture.
// ---------------------------------------------------------------------------

interface Backdrop {
  path: string
  width: number
  height: number
  top: number
  bottom: number
  slices: Array<{ y: number; src: string }>
  overlay: string | null
  capturedAt: number
  etag?: string
}

const backdrop = shallowRef<Backdrop | null>(null)
let backdropLoading = false
let backdropGen = 0
let backdropRetryAt = 0
// Content can change under a backdrop (the agent edits the app, data loads);
// past this age, a changed frame triggers a fresh one.
const BACKDROP_STALE_MS = 15000
const BACKDROP_IDLE_MS = 400
// Mid-gesture, with no backdrop yet, how often to ask for a stored one.
const BACKDROP_CACHED_RETRY_MS = 1500

function dropBackdrop() {
  backdropGen++
  backdrop.value = null
}

const backdropUsable = computed(() => {
  const b = backdrop.value
  return !!b && b.path === currentPath.value && Math.abs(b.width - viewport.value[0]) <= 2
})

// Whether the backdrop covers the whole view with the page scrolled to y.
function backdropCovers(y: number): boolean {
  const b = backdrop.value
  if (!backdropUsable.value || !b) return false
  return y >= b.top - 0.5 && y + viewport.value[1] <= b.bottom + 0.5
}

// The backdrop, not the frame, is on screen: the scroll is ahead of the
// frames and the backdrop covers the whole view where the page is headed.
const backdropCarries = computed(() =>
  Math.abs(shownScrollY.value - targetScrollY.value) >= 0.5 && backdropCovers(targetScrollY.value)
)

function toDevicePx(px: number): number {
  const dpr = window.devicePixelRatio || 1
  return Math.round(px * dpr) / dpr
}

const backdropStyle = computed(() => {
  const b = backdrop.value
  if (!b) return undefined
  const shift = toDevicePx(b.top - targetScrollY.value)
  return { transform: `translate3d(0, ${shift}px, 0)` }
})

function sliceStyle(y: number) {
  const b = backdrop.value
  return {
    ...viewportBox.value,
    top: `${toDevicePx(y - (b?.top ?? 0))}px`,
  }
}

function backdropWanted(): boolean {
  const s = scrollInfo.value
  if (!s || maxScrollY.value <= 0) return false // nothing to scroll to
  const b = backdrop.value
  if (!b || !backdropUsable.value) return true
  if (Math.abs(b.height - s.height) > 2) return true
  const y = targetScrollY.value
  const vh = s.viewport_height
  if ((b.top > 0 && y < b.top + vh) || (b.bottom < s.height - 1 && y + 2 * vh > b.bottom)) return true
  return etag.value !== b.etag && Date.now() - b.capturedAt > BACKDROP_STALE_MS
}

function decodeImage(src: string): Promise<void> {
  const img = new Image()
  img.src = src
  return img.decode().catch(() => undefined)
}

async function maybeRefreshBackdrop() {
  if (backdropLoading || disposed || phase.value !== 'ready' || props.paused) return
  if (Date.now() < backdropRetryAt || !backdropWanted()) return
  // Never a capture mid-gesture: it holds input back while it runs. A
  // stored one costs nothing, so with none on screen ask for that.
  const busy = inputInFlight > 0 || inputQueue.length > 0 || Date.now() - lastActivityAt < BACKDROP_IDLE_MS
  if (busy && backdropUsable.value) return
  backdropLoading = true
  const gen = backdropGen
  try {
    const b = await PreviewService.backdrop(props.projectId, { cachedOnly: busy })
    if (!b?.slices?.length && busy) backdropRetryAt = Date.now() + BACKDROP_CACHED_RETRY_MS
    if (disposed || gen !== backdropGen || !b?.slices?.length || !b.scroll) return
    const slices = b.slices.map(sl => ({
      y: sl.y,
      src: `data:image/${sl.type === 'png' ? 'png' : 'jpeg'};base64,${sl.frame}`,
    }))
    const overlay = b.overlay ? `data:image/png;base64,${b.overlay}` : null
    // Decoded before use, so the first scroll over it doesn't stall a paint.
    await Promise.all([...slices.map(sl => decodeImage(sl.src)), overlay ? decodeImage(overlay) : null])
    if (disposed || gen !== backdropGen) return
    const vh = b.viewport[1]
    backdrop.value = {
      path: b.path,
      width: b.viewport[0],
      height: b.scroll.height,
      top: Math.min(...slices.map(sl => sl.y)),
      bottom: Math.max(...slices.map(sl => sl.y)) + vh,
      slices,
      overlay,
      capturedAt: Date.now(),
      etag: etag.value,
    }
  } catch (e) {
    backdropRetryAt = Date.now() + 10000
    if (e instanceof PreviewNotRunningError) markSessionStopped()
  } finally {
    backdropLoading = false
  }
}

// ---------------------------------------------------------------------------
// Scrollbar
//
// The page's own scrollbar is hidden server-side: drawn into the frame, it
// slid with the shift above and snapped back with each new frame. This one is
// drawn here from targetScrollY, so it moves the instant the page does. It
// shows while scrolling and on hover, like the workspace's other scrollbars.
// ---------------------------------------------------------------------------

const scrollbarRef = ref<HTMLElement | null>(null)
const scrollbarActive = ref(false)
let scrollbarTimer: number | null = null
let thumbDrag: { pointerId: number; startY: number; startTop: number; travel: number } | null = null
const thumbDragging = ref(false)

const scrollbar = computed(() => {
  const s = scrollInfo.value
  if (!s || maxScrollY.value <= 0 || s.height <= 0) return null
  return {
    // Share of the page in view, and how far down it is (0..1).
    size: Math.min(1, s.viewport_height / s.height),
    at: Math.max(0, Math.min(targetScrollY.value / maxScrollY.value, 1)),
  }
})

const thumbStyle = computed(() => {
  const bar = scrollbar.value
  if (!bar) return undefined
  return {
    '--pv-thumb-size': `${(bar.size * 100).toFixed(3)}%`,
    '--pv-thumb-at': bar.at.toFixed(5),
  }
})

function flashScrollbar() {
  scrollbarActive.value = true
  if (scrollbarTimer) window.clearTimeout(scrollbarTimer)
  scrollbarTimer = window.setTimeout(() => {
    scrollbarTimer = null
    scrollbarActive.value = false
  }, 900)
}

watch(targetScrollY, (next, prev) => {
  if (phase.value === 'ready' && Math.abs(next - prev) >= 1) flashScrollbar()
})

function thumbTravel(): number {
  const track = scrollbarRef.value
  const thumb = track?.querySelector<HTMLElement>('.pv-scrollbar-thumb')
  if (!track || !thumb) return 0
  return Math.max(1, track.clientHeight - thumb.offsetHeight)
}

function scrollToThumbTop(top: number) {
  if (phase.value !== 'ready' || !Number.isFinite(top)) return
  enqueue({ kind: 'scroll', y: Math.round(clampScroll(top)) })
}

function onScrollbarPointerDown(e: PointerEvent) {
  if (phase.value !== 'ready' || !scrollbar.value || e.button !== 0) return
  const track = scrollbarRef.value
  if (!track) return
  stopInertia()
  const travel = thumbTravel()
  const onThumb = (e.target as HTMLElement).classList.contains('pv-scrollbar-thumb')
  if (!onThumb) {
    // A press on the track jumps there, centring the thumb on the pointer,
    // and the same press can carry on as a drag.
    const rect = track.getBoundingClientRect()
    const thumbPx = rect.height - travel
    const ratio = (e.clientY - rect.top - thumbPx / 2) / travel
    scrollToThumbTop(Math.max(0, Math.min(ratio, 1)) * maxScrollY.value)
  }
  thumbDrag = { pointerId: e.pointerId, startY: e.clientY, startTop: targetScrollY.value, travel }
  thumbDragging.value = true
  try { track.setPointerCapture(e.pointerId) } catch {}
}

function onScrollbarPointerMove(e: PointerEvent) {
  if (!thumbDrag || e.pointerId !== thumbDrag.pointerId) return
  const dy = e.clientY - thumbDrag.startY
  scrollToThumbTop(thumbDrag.startTop + (dy / thumbDrag.travel) * maxScrollY.value)
}

function onScrollbarPointerUp(e: PointerEvent) {
  if (!thumbDrag || e.pointerId !== thumbDrag.pointerId) return
  try { scrollbarRef.value?.releasePointerCapture(e.pointerId) } catch {}
  thumbDrag = null
  thumbDragging.value = false
  flashScrollbar()
}

// ---------------------------------------------------------------------------
// Input forwarding
// ---------------------------------------------------------------------------

let inputQueue: PreviewInputEvent[] = []
// Batches sent and not yet answered. Usually one: input applies in order. Two
// wheel-only batches may overlap (see flushInput), which doubles how often
// new pixels arrive during a scroll on a slow link.
let inputInFlight = 0
let inFlightWheelOnly = false
let lastInputSeq = 0
let lastInputSentAt = 0
// A response that covers all input sent can't be identified while batches
// overlap or after one failed, so the next quiet poll settles the scroll.
let scrollNeedsResync = false
let flushTimer: number | null = null
// Set when a backdrop-carried scroll turns out not to move the page: until
// the scrolling pauses this long, batches ask for frames again.
let framesUntil = 0
const FRAMES_AFTER_STILL_SCROLL_MS = 500

// The second of two overlapping batches waits at least this long after the
// first, so a fast link still gathers a few wheel events into each.
const PIPELINE_GAP_MS = 40
// How soon after a gesture's last frame the crisp settled frame is fetched.
const SETTLE_POLL_MS = 50

function modifiersFrom(e: MouseEvent | KeyboardEvent): number {
  return (e.altKey ? 1 : 0) | (e.ctrlKey ? 2 : 0) | (e.metaKey ? 4 : 0) | (e.shiftKey ? 8 : 0)
}

function pageCoords(e: PointerEvent | WheelEvent): { x: number; y: number } {
  // The frame is drawn 1:1 from the pane's top-left corner (see frameStyle).
  const rect = screenRef.value?.getBoundingClientRect()
  if (!rect || rect.width === 0 || rect.height === 0) return { x: 0, y: 0 }
  const [vw, vh] = viewport.value
  return {
    x: Math.round(Math.max(0, Math.min(e.clientX - rect.left, vw)) * 100) / 100,
    y: Math.round(Math.max(0, Math.min(e.clientY - rect.top, vh)) * 100) / 100,
  }
}

function sameSign(a: number | undefined, b: number | undefined): boolean {
  return !a || !b || Math.sign(a) === Math.sign(b)
}

function enqueue(event: PreviewInputEvent, immediate = false) {
  if (phase.value !== 'ready') return
  lastActivityAt = Date.now()
  // Every wheel event moves the page here first (ctrl+wheel is a zoom
  // gesture, not a scroll); an absolute scroll from the scrollbar likewise.
  if (event.kind === 'wheel' && !((event.modifiers || 0) & 2)) scrollLocallyBy(event.deltaY || 0)
  if (event.kind === 'scroll') scrollLocallyTo(event.y || 0)
  // Coalesce consecutive mouse moves so dragging doesn't flood the queue.
  const last = inputQueue[inputQueue.length - 1]
  if (event.type === 'mouseMoved' && last?.type === 'mouseMoved') {
    inputQueue[inputQueue.length - 1] = event
  } else if (event.kind === 'scroll' && last?.kind === 'scroll') {
    inputQueue[inputQueue.length - 1] = event
  } else if (
    event.kind === 'wheel' && last?.kind === 'wheel' &&
    sameSign(last.deltaY, event.deltaY) && sameSign(last.deltaX, event.deltaX)
  ) {
    // Sum the deltas but take the newest coordinates/modifiers — the merged
    // event must land where the pointer is now, or a scroll that crosses into
    // a nested scroll container keeps scrolling the old one. A reversal stays
    // a separate event: the page clamps each one at its edge in turn, which
    // is what the local estimate assumes.
    last.deltaX = (last.deltaX || 0) + (event.deltaX || 0)
    last.deltaY = (last.deltaY || 0) + (event.deltaY || 0)
    last.x = event.x
    last.y = event.y
    last.modifiers = event.modifiers
  } else {
    inputQueue.push(event)
  }
  if (inputQueue.length > 64) {
    inputQueue = inputQueue.slice(-64)
    scrollNeedsResync = true
  }
  // Wheel events flush immediately: anything arriving while a batch is in
  // flight coalesces into the next one anyway, so pre-batching them only adds
  // latency between the gesture and the frame that shows it.
  scheduleFlush(immediate || event.kind === 'wheel' || event.kind === 'scroll' ? 0 : 24)
}

function scheduleFlush(delay: number) {
  if (flushTimer) return
  flushTimer = window.setTimeout(flushInput, delay)
}

async function flushInput() {
  flushTimer = null
  if (inputQueue.length === 0 || phase.value !== 'ready') return
  const wheelOnly = inputQueue.every(ev => ev.kind === 'wheel')
  if (inputInFlight > 0) {
    // Only a pure wheel batch may overlap a pure wheel batch: deltas add up
    // the same in either order, clicks and keys don't.
    if (inputInFlight > 1 || !wheelOnly || !inFlightWheelOnly) return
    const wait = lastInputSentAt + PIPELINE_GAP_MS - Date.now()
    if (wait > 0) {
      scheduleFlush(wait)
      return
    }
    scrollNeedsResync = true
  }
  const batch = inputQueue
  inputQueue = []
  // The wheel deltas in this batch are the server's to apply now.
  unsentScroll = []
  const seq = ++requestSeq
  lastInputSeq = seq
  lastInputSentAt = Date.now()
  inFlightWheelOnly = inputInFlight === 0 ? wheelOnly : inFlightWheelOnly && wheelOnly
  inputInFlight++
  // A plain page scroll the backdrop covers needs no frame back (see Backdrop).
  const now = Date.now()
  if (now < framesUntil) framesUntil = now + FRAMES_AFTER_STILL_SCROLL_MS
  const lite = now >= framesUntil && batch.every(isPageScroll) && backdropCovers(targetScrollY.value)
  const fromY = scrollInfo.value?.y
  let response: PreviewFrame | null = null
  try {
    response = await PreviewService.sendInput(props.projectId, batch, etag.value, { frame: !lite })
    if (applyFrame(response, seq) && lite && response.scroll && fromY !== undefined &&
        Math.abs(response.scroll.y - fromY) < 0.5 && !scrollsPastEdge(batch, fromY)) {
      // The page didn't move: the wheel went to something scrolling inside
      // it, which only frames can show.
      framesUntil = Date.now() + FRAMES_AFTER_STILL_SCROLL_MS
    }
    void maybeRefreshBackdrop()
  } catch (e) {
    // The batch never applied server-side, so the estimate that counted it
    // is wrong; the next quiet poll puts it right.
    scrollNeedsResync = true
    if (e instanceof PreviewNotRunningError) {
      inputInFlight--
      markSessionStopped()
      return
    }
    // Drop the batch on transient failure; interaction continues from live state.
  }
  inputInFlight--
  if (inputInFlight === 0) {
    if (scrollNeedsResync) {
      scrollNeedsResync = false
      if (inputQueue.length === 0) {
        resyncSoon()
        return
      }
    } else if (response && seq === lastInputSeq) {
      // The newest batch, nothing else out: the server's offset is current.
      reconcileScroll(response)
    }
  }
  if (inputQueue.length > 0) scheduleFlush(0)
  else if (inputInFlight === 0 && batch.some(isMotion)) {
    // A scroll or drag just ended on a low-resolution motion frame; fetch
    // the crisp one right away rather than at the next regular poll.
    schedulePoll(SETTLE_POLL_MS)
    return
  }
  schedulePoll() // activity-based: quick while the user is interacting
}

// A wheel or scrollbar move that scrolls the page vertically (ctrl+wheel is
// a zoom; a mostly sideways wheel likely scrolls something inside the page).
function isPageScroll(ev: PreviewInputEvent): boolean {
  if (ev.kind === 'scroll') return true
  return ev.kind === 'wheel' && !((ev.modifiers || 0) & 2) &&
    Math.abs(ev.deltaX || 0) <= Math.abs(ev.deltaY || 0)
}

// Whether a batch's wheel deltas only push against the end of the page it
// is already at (or carry no vertical movement), so not moving is expected.
function scrollsPastEdge(batch: PreviewInputEvent[], fromY: number): boolean {
  const dy = batch.reduce((sum, ev) => sum + (ev.kind === 'wheel' ? ev.deltaY || 0 : 0), 0)
  if (batch.some(ev => ev.kind === 'scroll') || Math.abs(dy) < 1) return true
  return dy > 0 ? fromY >= maxScrollY.value - 0.5 : fromY <= 0.5
}

// Matches the server's notion of a gesture (dispatch_input's `motion`).
function isMotion(ev: PreviewInputEvent): boolean {
  return ev.kind === 'wheel' || ev.kind === 'scroll' || (ev.type === 'mouseMoved' && !!ev.buttons)
}

// A poll sent while nothing else is out answers for all input.
function resyncSoon() {
  if (inputQueue.length > 0) scheduleFlush(0)
  schedulePoll(0)
}

const BUTTON_NAMES: Array<'left' | 'middle' | 'right'> = ['left', 'middle', 'right']

// A touch drag scrolls the previewed app (forwarded as wheel deltas) the way a
// finger scrolls a native page, instead of being sent as a mouse drag. A touch
// that barely moves is treated as a tap and forwarded as a click so buttons and
// links still work. When the finger lifts we keep emitting decaying wheel
// deltas (momentum) so the page glides to a stop instead of stopping dead —
// the streamed preview has no native inertial scrolling of its own.
const TOUCH_TAP_SLOP = 8       // page px of travel before a touch becomes a scroll
const INERTIA_FRICTION = 0.94  // fraction of velocity kept each animation frame
const INERTIA_MIN_SPEED = 0.03 // px/ms; the glide ends below this
const INERTIA_MAX_SPEED = 4     // px/ms; caps a hard flick so it stays controllable
let touchDrag: {
  pointerId: number
  startX: number
  startY: number
  lastX: number
  lastY: number
  // Client-px position, tracked separately from the page coords above: the
  // optimistic transform must follow the finger in screen pixels exactly.
  lastClientY: number
  lastT: number
  vx: number
  vy: number
  scrolling: boolean
  stoppedInertia: boolean
} | null = null

let inertiaRaf: number | null = null
let inertiaX = 0
let inertiaY = 0
let inertiaVx = 0
let inertiaVy = 0
let inertiaLastT = 0

function stopInertia() {
  if (inertiaRaf !== null) {
    cancelAnimationFrame(inertiaRaf)
    inertiaRaf = null
  }
}

function startInertia(x: number, y: number, vx: number, vy: number) {
  stopInertia()
  inertiaX = x
  inertiaY = y
  inertiaVx = Math.max(-INERTIA_MAX_SPEED, Math.min(vx, INERTIA_MAX_SPEED))
  inertiaVy = Math.max(-INERTIA_MAX_SPEED, Math.min(vy, INERTIA_MAX_SPEED))
  if (Math.hypot(inertiaVx, inertiaVy) < INERTIA_MIN_SPEED) return
  inertiaLastT = performance.now()
  const step = () => {
    inertiaRaf = null
    if (disposed || phase.value !== 'ready') return
    const now = performance.now()
    const dt = Math.min(32, now - inertiaLastT)
    inertiaLastT = now
    inertiaVx *= INERTIA_FRICTION
    inertiaVy *= INERTIA_FRICTION
    if (Math.hypot(inertiaVx, inertiaVy) < INERTIA_MIN_SPEED) return
    // Same convention as a drag: wheel delta is opposite the finger travel.
    // enqueue moves the content locally too, same as the drag did.
    enqueue({ kind: 'wheel', x: inertiaX, y: inertiaY, deltaX: -inertiaVx * dt, deltaY: -inertiaVy * dt, modifiers: 0 })
    inertiaRaf = requestAnimationFrame(step)
  }
  inertiaRaf = requestAnimationFrame(step)
}

function onPointerDown(e: PointerEvent) {
  screenRef.value?.focus()
  if (phase.value !== 'ready') return
  const { x, y } = pageCoords(e)
  if (e.pointerType === 'touch') {
    const stoppedInertia = inertiaRaf !== null
    stopInertia()
    touchDrag = {
      pointerId: e.pointerId,
      startX: x, startY: y,
      lastX: x, lastY: y,
      lastClientY: e.clientY,
      lastT: e.timeStamp,
      vx: 0, vy: 0,
      scrolling: false,
      stoppedInertia,
    }
    try { screenRef.value?.setPointerCapture(e.pointerId) } catch {}
    return
  }
  enqueue({
    kind: 'mouse',
    type: 'mousePressed',
    x, y,
    button: BUTTON_NAMES[e.button] || 'left',
    buttons: e.buttons,
    clickCount: Math.max(1, e.detail),
    modifiers: modifiersFrom(e),
  }, true)
}

function onPointerMove(e: PointerEvent) {
  if (phase.value !== 'ready') return
  const { x, y } = pageCoords(e)
  if (touchDrag && e.pointerId === touchDrag.pointerId) {
    const dx = x - touchDrag.lastX
    const dy = y - touchDrag.lastY
    if (!touchDrag.scrolling &&
        Math.hypot(x - touchDrag.startX, y - touchDrag.startY)> TOUCH_TAP_SLOP) {
      touchDrag.scrolling = true
    }
    if (touchDrag.scrolling && (dx !== 0 || dy !== 0)) {
      // Wheel delta is opposite the finger travel: drag up -> scroll down.
      // enqueue moves the content locally, so it follows the finger at once.
      enqueue({ kind: 'wheel', x, y, deltaX: -dx, deltaY: -dy, modifiers: 0 })
      // Track a smoothed finger velocity (px/ms) to seed the release glide.
      const dt = Math.max(1, e.timeStamp - touchDrag.lastT)
      touchDrag.vx = touchDrag.vx * 0.7 + (dx / dt) * 0.3
      touchDrag.vy = touchDrag.vy * 0.7 + (dy / dt) * 0.3
    }
    touchDrag.lastX = x
    touchDrag.lastY = y
    touchDrag.lastClientY = e.clientY
    touchDrag.lastT = e.timeStamp
    return
  }
  enqueue({
    kind: 'mouse',
    type: 'mouseMoved',
    x, y,
    button: 'none',
    buttons: e.buttons,
    modifiers: modifiersFrom(e),
  })
}

function onPointerUp(e: PointerEvent) {
  if (phase.value !== 'ready') return
  const { x, y } = pageCoords(e)
  if (touchDrag && e.pointerId === touchDrag.pointerId) {
    const drag = touchDrag
    touchDrag = null
    try { screenRef.value?.releasePointerCapture(e.pointerId) } catch {}
    if (drag.scrolling) {
      // Let the page keep gliding from the finger's release velocity.
      startInertia(drag.lastX, drag.lastY, drag.vx, drag.vy)
    } else if (!drag.stoppedInertia) {
      // A genuine tap (not a tap that just halted a glide) becomes a click.
      enqueue({ kind: 'mouse', type: 'mousePressed', x, y, button: 'left', buttons: 1, clickCount: 1, modifiers: modifiersFrom(e) }, true)
      enqueue({ kind: 'mouse', type: 'mouseReleased', x, y, button: 'left', buttons: 0, clickCount: 1, modifiers: modifiersFrom(e) }, true)
    }
    return
  }
  enqueue({
    kind: 'mouse',
    type: 'mouseReleased',
    x, y,
    button: BUTTON_NAMES[e.button] || 'left',
    buttons: e.buttons,
    clickCount: Math.max(1, e.detail),
    modifiers: modifiersFrom(e),
  }, true)
}

function onPointerCancel(e: PointerEvent) {
  if (touchDrag && e.pointerId === touchDrag.pointerId) {
    touchDrag = null
    try { screenRef.value?.releasePointerCapture(e.pointerId) } catch {}
    // The gesture is void; the next quiet poll says where the page ended up.
    scrollNeedsResync = true
    if (inputInFlight === 0) resyncSoon()
  }
}

// CDP's mouseWheel takes pixels; some browsers (Firefox with a mouse wheel)
// report lines or pages instead, which would scroll a few pixels per notch.
// Chromium's own line height for wheel scrolling is 40px.
const WHEEL_LINE_PX = 40

function onWheel(e: WheelEvent) {
  if (phase.value !== 'ready') return
  const { x, y } = pageCoords(e)
  // Read the deltas before deltaMode: Firefox only reports line deltas to
  // pages that check deltaMode first.
  let deltaX = e.deltaX
  let deltaY = e.deltaY
  if (e.deltaMode === 1) {
    deltaX *= WHEEL_LINE_PX
    deltaY *= WHEEL_LINE_PX
  } else if (e.deltaMode === 2) {
    deltaX *= viewport.value[0]
    deltaY *= viewport.value[1]
  }
  // A wheel takes over from a touch glide still running.
  if (!e.ctrlKey && deltaY !== 0) stopInertia()
  // enqueue moves the frame now instead of a round trip later.
  enqueue({ kind: 'wheel', x, y, deltaX, deltaY, modifiers: modifiersFrom(e) })
}

function keyEvent(e: KeyboardEvent, type: 'keyDown' | 'keyUp'): PreviewInputEvent {
  return {
    kind: 'key',
    type,
    key: e.key,
    code: e.code,
    text: e.key.length === 1 ? e.key : e.key === 'Enter' ? '\r' : '',
    keyCode: e.keyCode,
    modifiers: modifiersFrom(e),
  }
}

function onKeyDown(e: KeyboardEvent) {
  if (phase.value !== 'ready') return
  e.preventDefault()
  e.stopPropagation()
  enqueue(keyEvent(e, 'keyDown'), true)
}

function onKeyUp(e: KeyboardEvent) {
  if (phase.value !== 'ready') return
  e.preventDefault()
  e.stopPropagation()
  enqueue(keyEvent(e, 'keyUp'), true)
}

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------

async function doNavigate(action: 'goto' | 'back' | 'forward' | 'reload', path?: string) {
  if (phase.value !== 'ready') return
  lastActivityAt = Date.now()
  // Any scroll offset (optimistic or gliding) belongs to the page being left.
  stopInertia()
  resyncScroll()
  dropBackdrop()
  // Hard navigation clears the page's error buffer, so the same error text
  // on the fresh document should notify again.
  dismissedErrorKey.value = null
  navigating.value = true
  try {
    const seq = ++requestSeq
    const f = await PreviewService.navigate(props.projectId, action, path)
    applyStatus(f, seq)
    schedulePoll(300)
  } catch (e) {
    if (e instanceof PreviewNotRunningError) markSessionStopped()
  } finally {
    navigating.value = false
  }
}

function navigateTo(path: string) {
  void doNavigate('goto', normalizePath(path))
}

function goBack() {
  void doNavigate('back')
}

function goForward() {
  void doNavigate('forward')
}

function goHome() {
  navigateTo('/')
}

function reload() {
  if (phase.value === 'ready') {
    void doNavigate('reload')
  } else if (phase.value !== 'starting') {
    void startPreview()
  }
}

// ---------------------------------------------------------------------------
// Pane size -> remote viewport
// ---------------------------------------------------------------------------

// Resize the remote browser to match the pane's current CSS size, so the
// previewed app renders (and fills) at the real display width. No-op when it
// already matches.
async function ensureViewportMatchesPane() {
  if (disposed || phase.value !== 'ready') return
  const { width, height } = paneSize()
  const [vw, vh] = viewport.value
  const dsf = deviceScaleFactor()
  // Any difference at all: frames are drawn 1:1, so even a pixel off leaves a
  // sliver of the page cut off or a strip of stage showing.
  if (width === vw && height === vh && dsf === viewportDsf) return
  try {
    await PreviewService.resize(props.projectId, width, height, dsf)
    viewportDsf = dsf
    viewport.value = [width, height]
    etag.value = undefined // force a fresh frame at the new size
    schedulePoll(100)
  } catch (e) {
    if (e instanceof PreviewNotRunningError) markSessionStopped()
  }
}

// Pane resizes that arrive while paused are remembered, not acted on — the
// pane is often mid-layout-change (e.g. another pane going fullscreen) and
// resizing the remote browser for sizes nobody sees is wasted work. The
// single viewport check on unpause applies whatever size the pane settled at.
let paneResizedWhilePaused = false

function onPaneResized() {
  if (props.paused) {
    paneResizedWhilePaused = true
    return
  }
  if (resizeTimer) window.clearTimeout(resizeTimer)
  resizeTimer = window.setTimeout(() => void ensureViewportMatchesPane(), 350)
}

// Moving the window to a display with another pixel ratio (or zooming)
// re-renders the remote page at the new ratio. A resolution media query only
// fires once, so each change re-arms it for the new ratio.
let stopWatchingPixelRatio: (() => void) | null = null

function watchPixelRatio() {
  if (disposed || typeof window.matchMedia !== 'function') return
  const mq = window.matchMedia(`(resolution: ${window.devicePixelRatio || 1}dppx)`)
  const onChange = () => {
    stopWatchingPixelRatio?.()
    watchPixelRatio()
    onPaneResized()
  }
  mq.addEventListener?.('change', onChange)
  stopWatchingPixelRatio = () => mq.removeEventListener?.('change', onChange)
}

// ---------------------------------------------------------------------------
// App / page selector (read from the project's actual Vue routers)
// ---------------------------------------------------------------------------

const apps = ref<PreviewApp[]>([])

async function refreshPages() {
  if (!props.projectId) return
  try {
    apps.value = await PreviewService.pages(props.projectId)
  } catch {
    // Keep whatever menu we had; the preview itself is unaffected.
  }
}

function onMenuToggle() {
  menuOpen.value = !menuOpen.value
  if (menuOpen.value) {
    // Every section open: the menu's job is to show all the pages there are.
    expandedApps.value = apps.value.map(a => a.name)
    // Routes may have changed since the last fetch (the agent edits routers);
    // refresh in the background whenever the menu opens.
    void refreshPages()
  }
}

function isExpanded(name: string): boolean {
  return expandedApps.value.includes(name)
}

function toggleApp(name: string) {
  const i = expandedApps.value.indexOf(name)
  if (i >= 0) expandedApps.value.splice(i, 1)
  else expandedApps.value.push(name)
}

function normalizePath(input: string): string {
  const trimmed = (input || '').trim()
  if (!trimmed) return '/'
  if (/^https?:\/\//i.test(trimmed)) {
    try {
      const u = new URL(trimmed)
      return u.pathname + u.search + u.hash
    } catch {
      return '/'
    }
  }
  return trimmed.startsWith('/') ? trimmed : '/' + trimmed
}

const pageCount = computed(() => apps.value.reduce((n, a) => n + a.pages.length, 0))

function onSelectPage(path: string) {
  navigateTo(path)
  menuOpen.value = false
}

function onDocClick(e: MouseEvent) {
  if (!menuOpen.value) return
  if (menuRoot.value && !menuRoot.value.contains(e.target as Node)) {
    menuOpen.value = false
  }
}

// What the collapsed plate says: the section of the app holding the current
// page, then the page by name, as the menu lists it — "home / About".
const location = computed(() => {
  for (const app of apps.value) {
    const page = app.pages.find(p => p.path === currentPath.value)
    if (page) return { dir: app.name, page: page.title }
  }
  // No router claims this path — a 404, or a route the agent added since the
  // last fetch. There is no folder to name, so show the address itself.
  if (apps.value.length === 0) return { dir: '', page: 'No pages yet' }
  return { dir: '', page: currentPath.value || '/' }
})

// ---------------------------------------------------------------------------
// Start-up progress
//
// A cold start installs the project's whole dependency tree, so the wait runs
// to minutes. A bare spinner reads as "hung" at that length; an elapsed clock
// and copy that names the current stage read as "working".
// ---------------------------------------------------------------------------

const elapsed = ref(0)
let elapsedTimer: number | null = null

function stopElapsed() {
  if (elapsedTimer) {
    window.clearInterval(elapsedTimer)
    elapsedTimer = null
  }
}

watch(phase, (p) => {
  stopElapsed()
  if (p !== 'starting') return
  elapsed.value = 0
  const startedAt = Date.now()
  elapsedTimer = window.setInterval(() => {
    elapsed.value = Math.floor((Date.now() - startedAt) / 1000)
  }, 1000)
})

const elapsedLabel = computed(() => {
  const s = elapsed.value
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`
})

// Thresholds are the shape of a real cold start, not a promise about it — the
// copy stays true even if a stage runs long, because none of it claims to be
// nearly done until the wait is genuinely unusual. Dependencies are never
// installed here: every project links to a store installed once per machine
// at creation, and the servers start in a second or two — so a wait past a
// few seconds is the app compiling, and only a wait past that on a fresh
// machine (empty store) is an install.
const startingStage = computed(() => {
  const s = elapsed.value
  if (s < 5) return 'Waking the preview server…'
  if (s < 30) return 'Compiling your app…'
  if (s < 90) return 'Still going — a first start on a new machine installs dependencies, which can take a few minutes.'
  return 'Still going — a first start can take a few minutes.'
})

// ---------------------------------------------------------------------------
// Lifecycle
// ---------------------------------------------------------------------------

onMounted(() => {
  document.addEventListener('mousedown', onDocClick)
  if (screenRef.value && typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(onPaneResized)
    observer.observe(screenRef.value)
  }
  watchPixelRatio()
  void refreshPages()
  void startPreview()
})

onBeforeUnmount(() => {
  disposed = true
  document.removeEventListener('mousedown', onDocClick)
  if (pollTimer) window.clearTimeout(pollTimer)
  if (resizeTimer) window.clearTimeout(resizeTimer)
  if (flushTimer) window.clearTimeout(flushTimer)
  if (scrollbarTimer) window.clearTimeout(scrollbarTimer)
  stopElapsed()
  stopInertia()
  observer?.disconnect()
  stopWatchingPixelRatio?.()
})

watch(
  () => props.projectId,
  (next, prev) => {
    if (next && next !== prev) {
      // Drop any response or frame still on its way for the old project.
      shownFrameSeq = appliedSeq = ++requestSeq
      frameSrc.value = null
      scrollInfo.value = null
      shownScrollY.value = 0
      etag.value = undefined
      phase.value = 'idle'
      apps.value = []
      stopInertia()
      resyncScroll()
      dropBackdrop()
      consoleErrors.value = []
      errorRouting.value = null
      dismissedErrorKey.value = null
      void refreshPages()
      void startPreview()
    }
  }
)

watch(
  () => props.paused,
  (paused) => {
    if (disposed) return
    if (paused) {
      // A resize debounce armed just before pausing must not resize the
      // remote browser mid-pause; fold it into the deferred-resize marker.
      if (resizeTimer) {
        window.clearTimeout(resizeTimer)
        resizeTimer = null
        paneResizedWhilePaused = true
      }
      // Nobody can see the pane; a glide or half-reconciled optimistic offset
      // must not keep running (or linger) into the background.
      stopInertia()
      resyncScroll()
      // Likewise a poll timer set moments ago could still fire at the active
      // cadence; rescheduling drops it to the keep-alive interval right away.
      schedulePoll()
      return
    }
    // Unpaused: fetch a frame immediately — the one on screen may be minutes
    // old.
    void pollFrame()
    if (paneResizedWhilePaused) {
      paneResizedWhilePaused = false
      // The pane's geometry was in flux while paused (that's what set the
      // flag), so measure after layout settles — the same reason startPreview
      // re-asserts its first measurement in a rAF.
      requestAnimationFrame(() => void ensureViewportMatchesPane())
    } else {
      // Nothing was deferred, but re-check anyway; it no-ops when in sync.
      void ensureViewportMatchesPane()
    }
  }
)

defineExpose({ reload })
</script>

<style scoped>
/* What stays here: the entrance and loading animations (scoped keyframe names
   are hashed, so a utility can't reference them) and the orbit's masked
   conic ring, which has no readable utility form. */

/* Loading ribbon: a travelling sliver along the dock's lower edge. */
.pv-progress::after {
  animation: pv-slide 1.2s ease-in-out infinite;
}

@keyframes pv-slide {
  0% { transform: translateX(-110%); }
  100% { transform: translateX(400%); }
}

.pv-menu {
  animation: pv-menu-in 0.16s cubic-bezier(0.2, 0.9, 0.3, 1) both;
}

@keyframes pv-menu-in {
  from { opacity: 0; transform: translate(-50%, -4px) scale(0.98); }
  to { opacity: 1; transform: translateX(-50%); }
}

.pv-row {
  animation: pv-row-in 0.22s ease both;
  animation-delay: calc(var(--pv-i, 0) * 28ms);
}

@keyframes pv-row-in {
  from { opacity: 0; transform: translateY(-3px); }
  to { opacity: 1; transform: none; }
}

.pv-notice {
  animation: pv-notice-in 0.3s cubic-bezier(0.2, 0.9, 0.3, 1) both;
}

@keyframes pv-notice-in {
  from { opacity: 0; transform: translateY(8px) scale(0.985); }
  to { opacity: 1; transform: none; }
}

.pv-alert {
  animation: pv-alert-in 0.26s cubic-bezier(0.2, 0.9, 0.3, 1) both;
}

@keyframes pv-alert-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: none; }
}

/* A ring of ink drawn once around, with a heartbeat at the centre. */
.pv-orbit::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 9999px;
  background: conic-gradient(
    from 0deg,
    rgba(19, 26, 44, 0) 0deg,
    rgba(19, 26, 44, 0.1) 150deg,
    rgba(19, 26, 44, 0.85) 355deg
  );
  -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 2.5px), #000 calc(100% - 2.5px));
  mask: radial-gradient(farthest-side, transparent calc(100% - 2.5px), #000 calc(100% - 2.5px));
  animation: pv-rotate 1.1s linear infinite;
}

.dark .pv-orbit::before {
  background: conic-gradient(
    from 0deg,
    rgba(243, 237, 226, 0) 0deg,
    rgba(243, 237, 226, 0.12) 150deg,
    rgba(243, 237, 226, 0.9) 355deg
  );
}

/* No pv-breathe keyframes are defined, so this names an animation that never
   plays; kept as it was. */
.pv-orbit-core {
  animation: pv-breathe 1.8s ease-in-out infinite;
}

@keyframes pv-rotate {
  to { transform: rotate(360deg); }
}

@media (prefers-reduced-motion: reduce) {
  .pv-progress::after,
  .pv-orbit::before,
  .pv-orbit-core {
    animation: none;
  }

  .pv-menu,
  .pv-row,
  .pv-notice,
  .pv-alert {
    animation-duration: 0.01ms;
  }
}
</style>
