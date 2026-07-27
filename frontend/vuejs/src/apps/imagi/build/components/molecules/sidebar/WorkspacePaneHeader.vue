<!--
  WorkspacePaneHeader.vue — the masthead shared by the two sidebar panes.

  The main agent and the subagents are two views of one workspace, so they wear
  the same plate: a mark identifying the pane, its name in the brand serif, a
  live status line, and — on desktop — a pill that names the pane it switches
  to and how much is happening over there. That count is the point: you can
  see background work piling up without leaving the thread you're in.
-->
<template>
  <div class="pane-header shrink-0 flex items-center gap-2.5 px-3.5 py-2.5">
    <!-- Identity: mark + name + what's happening right now. A pane can go
         without a mark (a subagent's thread names its task and needs no badge
         beside it); the live dot then stands on its own where the mark was. -->
    <div v-if="icon || live" class="relative shrink-0">
      <div
        v-if="icon"
        :class="['pane-mark', tone === 'primary' ? 'pane-mark--primary' : 'pane-mark--muted']"
      >
        <i :class="[icon, 'text-[11px]']"></i>
      </div>
      <!-- A run is live in this pane -->
      <span
        v-if="live"
        :class="['pane-pulse', icon ? '' : 'pane-pulse--bare']"
        aria-hidden="true"
      ></span>
    </div>

    <div class="flex-1 min-w-0">
      <h2 class="pane-title truncate">{{ title }}</h2>
      <!-- The status line is the most-changing text in the workspace ("Reading
           files…" → "Editing…" → "Ready when you are"). Swapping it in place
           reads as a flicker; cross-fading reads as the same line being
           updated, which is what it is. Keyed on the text so each new reading
           gets its own fade. -->
      <div v-if="status" class="pane-status-line">
        <Transition name="pane-status" mode="out-in">
          <p :key="status" class="pane-status truncate">{{ status }}</p>
        </Transition>
      </div>
    </div>

    <!-- Desktop pane switch. Mobile navigates from the navbar switcher, so
         this would be a second control for the same job. -->
    <button
      v-if="switchLabel"
      type="button"
      class="pane-switch iw-press group max-md:hidden"
      :aria-label="`Switch to ${switchLabel}`"
      @click="emit('switch')"
    >
      <i
        v-if="switchDirection === 'back'"
        class="fas fa-chevron-left pane-switch-chevron"
      ></i>
      <!-- The destination has a live run (a subagent working over there): the
           icon carries the same pulse the pane mark uses, so the link to the
           working subagent is always visible from the thread you're in. -->
      <span class="pane-switch-icon-wrap">
        <i :class="[switchIcon, 'pane-switch-icon']"></i>
        <span v-if="switchLive" class="pane-switch-pulse" aria-hidden="true"></span>
      </span>
      <span class="pane-switch-label">{{ switchLabel }}</span>
      <!-- Ambient count of what is waiting on the other side. Keyed on the
           number so it springs when the fleet grows instead of silently
           becoming a different digit. -->
      <Transition name="pane-count" mode="out-in">
        <span v-if="switchCount" :key="switchCount" class="pane-switch-count">{{ switchCount }}</span>
      </Transition>
      <i
        v-if="switchDirection === 'forward'"
        class="fas fa-chevron-right pane-switch-chevron"
      ></i>
    </button>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    /** Font Awesome classes for the pane's mark. Omit for a pane whose title
     *  already identifies it — the plate then leads with the name. */
    icon?: string
    /** 'primary' is the thread the user drives; 'muted' is everything observed */
    tone?: 'primary' | 'muted'
    title: string
    /** One line on what this pane is doing right now */
    status?: string
    /** A run is live here — the mark gets a pulsing dot */
    live?: boolean
    switchIcon?: string
    switchLabel?: string
    /** A run is live in the pane this switches to — the switch icon pulses */
    switchLive?: boolean
    /** Badge on the switch: how much is waiting in the other pane */
    switchCount?: number
    switchDirection?: 'forward' | 'back'
  }>(),
  { tone: 'muted', switchDirection: 'forward' }
)

const emit = defineEmits<{ (e: 'switch'): void }>()
</script>

<style scoped>
/* The plate: a translucent material rather than a painted strip. The pane
   scrolls beneath it, so the masthead takes its colour from whatever is
   passing underneath — saturated and blurred past legibility — and closes
   with a true hairline. This is what keeps the header feeling like a layer
   above the transcript instead of its first row. */
.pane-header {
  position: relative;
  z-index: 20;
  background: var(--iw-material-bg);
  -webkit-backdrop-filter: var(--iw-material-filter);
  backdrop-filter: var(--iw-material-filter);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* The separator is drawn rather than bordered: at 1px a border rounds up to a
   full device pixel on retina and reads as a line; a scaled pseudo-element
   stays a true hairline at any density. */
.pane-header::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1px;
  background: var(--iw-hairline);
  transform: scaleY(0.5);
  transform-origin: bottom;
}

/* No backdrop-filter (older Firefox, some Linux GPUs): fall back to the
   opaque wash the header used to carry, so it never turns see-through. */
@supports not ((backdrop-filter: blur(1px)) or (-webkit-backdrop-filter: blur(1px))) {
  .pane-header {
    background: linear-gradient(180deg, rgba(239, 246, 255, 0.92) 0%, rgba(239, 246, 255, 0.6) 100%);
  }

  .dark .pane-header {
    background: linear-gradient(180deg, rgba(24, 24, 27, 0.96) 0%, rgba(18, 18, 20, 0.85) 100%);
  }
}

/* Mark: navy ink for the thread you drive, a quiet tint for panes you watch */
.pane-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.875rem;
  height: 1.875rem;
  border-radius: var(--iw-r-md);
  transition:
    transform var(--iw-dur-2) var(--iw-ease-spring),
    box-shadow var(--iw-dur-2) var(--iw-ease-out),
    background-color var(--iw-dur-2) var(--iw-ease-out);
}

.pane-mark--primary {
  background: theme('colors.blue.950');
  color: #fdf9f2;
  box-shadow:
    0 1px 2px rgba(23, 37, 84, 0.22),
    0 4px 12px -4px rgba(23, 37, 84, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.16);
}

.dark .pane-mark--primary {
  background: #f3ede2;
  color: theme('colors.blue.950');
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 4px 12px -4px rgba(0, 0, 0, 0.5);
}

.pane-mark--muted {
  background: rgba(23, 37, 84, 0.07);
  color: rgba(23, 37, 84, 0.7);
  box-shadow: inset 0 0 0 1px rgba(23, 37, 84, 0.07);
}

.dark .pane-mark--muted {
  background: rgba(243, 237, 226, 0.1);
  color: rgba(243, 237, 226, 0.8);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

/* Live-run dot, ringed against the header so it reads on either surface. The
   dot itself holds steady — a marker that flickers looks like a rendering
   fault — and a halo breathes outward from under it. Reads as a signal
   radiating rather than a light being switched. */
.pane-pulse {
  position: absolute;
  right: -1px;
  bottom: -1px;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  background: theme('colors.blue.500');
  box-shadow: 0 0 0 2px rgba(var(--iw-surface), 1);
  animation: pane-pulse-core 2.4s var(--iw-ease-ambient) infinite;
}

.pane-pulse::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 9999px;
  background: inherit;
  animation: pane-pulse-halo 2.4s var(--iw-ease-ambient) infinite;
}

.dark .pane-pulse {
  background: theme('colors.blue.300');
}

/* With no mark to sit against, the dot holds the same left edge the mark did
   so the title does not shift between a pane that has one and a pane that
   does not. */
.pane-pulse--bare {
  position: static;
  display: block;
  margin: 0 0.6875rem;
}

@keyframes pane-pulse-core {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.78; }
}

@keyframes pane-pulse-halo {
  0% { opacity: 0.45; transform: scale(1); }
  70%, 100% { opacity: 0; transform: scale(2.4); }
}

@media (prefers-reduced-motion: reduce) {
  .pane-pulse,
  .pane-pulse::after,
  .pane-switch-pulse,
  .pane-switch-pulse::after { animation: none; }

  .pane-pulse::after,
  .pane-switch-pulse::after { opacity: 0; }
}

/* The name carries the brand serif (Fraunces) — the same face as the Imagi
   mark — so the workspace chrome speaks in the product's own voice instead of
   another line of bold UI sans. Softened and slightly wonky on its variable
   axes to keep it warm at this size. */
.pane-title {
  font-family: theme('fontFamily.display');
  font-variation-settings: 'opsz' 20, 'SOFT' 24, 'WONK' 1;
  font-size: 0.9375rem;
  font-weight: 600;
  line-height: 1.15;
  letter-spacing: -0.011em;
  color: theme('colors.blue.950');
}

.dark .pane-title {
  color: rgba(255, 255, 255, 0.94);
}

/* Reserves the line's height so the masthead never resizes underneath a
   cross-fade — the two readings swap inside a box that does not move. */
.pane-status-line {
  min-height: 0.9375rem;
}

.pane-status {
  margin-top: 0.0625rem;
  font-size: 0.65625rem;
  line-height: 1.3;
  letter-spacing: 0.005em;
  color: rgba(23, 37, 84, 0.45);
}

.dark .pane-status {
  color: rgba(219, 234, 254, 0.45);
}

/* One reading giving way to the next: down and out, up and in — the direction
   of a line being replaced from below. */
.pane-status-enter-active,
.pane-status-leave-active {
  transition:
    opacity var(--iw-dur-1) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.pane-status-enter-from {
  opacity: 0;
  transform: translateY(3px);
}

.pane-status-leave-to {
  opacity: 0;
  transform: translateY(-3px);
}

/* Switch: names its destination instead of hiding behind a tooltip. Rests
   flush with the masthead and lifts on hover — a control that comes to meet
   the pointer, then gives under the press (.iw-press). */
.pane-switch {
  display: inline-flex;
  align-items: center;
  gap: 0.3125rem;
  flex-shrink: 0;
  padding: 0.3125rem 0.5625rem;
  border-radius: 9999px;
  border: 1px solid rgba(23, 37, 84, 0.1);
  background: rgba(255, 255, 255, 0.7);
  color: rgba(23, 37, 84, 0.72);
  font-size: 0.6875rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: var(--iw-shadow-1);
  transition:
    background-color var(--iw-dur-2) var(--iw-ease-out),
    border-color var(--iw-dur-2) var(--iw-ease-out),
    color var(--iw-dur-2) var(--iw-ease-out),
    box-shadow var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-2) var(--iw-ease-out);
}

.pane-switch:hover {
  background: #ffffff;
  border-color: rgba(23, 37, 84, 0.18);
  color: theme('colors.blue.950');
  box-shadow: var(--iw-shadow-2);
  transform: translateY(-1px);
}

/* .iw-press owns the pressed scale; the lift simply returns to rest under it */
.pane-switch:active {
  transform: translateY(0) scale(0.97);
  box-shadow: var(--iw-shadow-1);
  transition-duration: var(--iw-dur-1);
}

.pane-switch:focus-visible {
  outline: none;
  box-shadow: var(--iw-focus-ring);
}

.dark .pane-switch {
  border-color: rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(219, 234, 254, 0.72);
}

.dark .pane-switch:hover {
  background: rgba(255, 255, 255, 0.09);
  border-color: rgba(255, 255, 255, 0.24);
  color: #ffffff;
}

.pane-switch-icon-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.pane-switch-icon {
  font-size: 0.625rem;
  opacity: 0.7;
  transition: opacity var(--iw-dur-2) var(--iw-ease-out);
}

.pane-switch:hover .pane-switch-icon {
  opacity: 0.95;
}

/* Same pulse as the pane mark, sized down for the switch icon — the link to a
   working subagent reads as live without stealing attention. */
.pane-switch-pulse {
  position: absolute;
  top: -2px;
  right: -3px;
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 9999px;
  background: theme('colors.blue.500');
  box-shadow: 0 0 0 2px rgba(var(--iw-surface), 0.9);
  animation: pane-pulse-core 2.4s var(--iw-ease-ambient) infinite;
}

.pane-switch-pulse::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 9999px;
  background: inherit;
  animation: pane-pulse-halo 2.4s var(--iw-ease-ambient) infinite;
}

.dark .pane-switch-pulse {
  background: theme('colors.blue.300');
}

.pane-switch-chevron {
  font-size: 0.5rem;
  opacity: 0.45;
  transition:
    transform var(--iw-dur-2) var(--iw-ease-out),
    opacity var(--iw-dur-2) var(--iw-ease-out);
}

.pane-switch:hover .pane-switch-chevron {
  opacity: 0.8;
}

.group:hover .fa-chevron-right.pane-switch-chevron {
  transform: translateX(2px);
}

.group:hover .fa-chevron-left.pane-switch-chevron {
  transform: translateX(-2px);
}

.pane-switch-label {
  white-space: nowrap;
}

/* Count of what is waiting on the other side — navy ink so it reads as a
   real number to deal with, not a decorative dot. */
.pane-switch-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.0625rem;
  height: 1.0625rem;
  padding: 0 0.25rem;
  border-radius: 9999px;
  background: theme('colors.blue.950');
  color: #fdf9f2;
  font-size: 0.625rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  line-height: 1;
}

.dark .pane-switch-count {
  background: #f3ede2;
  color: theme('colors.blue.950');
}

/* The badge springs in rather than appearing already there — the one place in
   the masthead where a change in the number is itself the news. */
.pane-count-enter-active {
  transition:
    opacity var(--iw-dur-2) var(--iw-ease-out),
    transform var(--iw-dur-2) var(--iw-ease-spring);
}

.pane-count-leave-active {
  transition:
    opacity var(--iw-dur-1) var(--iw-ease-out),
    transform var(--iw-dur-1) var(--iw-ease-out);
}

.pane-count-enter-from {
  opacity: 0;
  transform: scale(0.5);
}

.pane-count-leave-to {
  opacity: 0;
  transform: scale(0.7);
}
</style>
