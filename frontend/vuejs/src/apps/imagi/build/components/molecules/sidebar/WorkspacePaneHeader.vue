<!--
  WorkspacePaneHeader.vue — the masthead shared by the two sidebar panes.

  The chat and the agent manager are two views of one workspace, so they wear
  the same plate: a mark identifying the pane, its name in the brand serif, a
  live status line, and — on desktop — a pill that names the pane it switches
  to and how much is happening over there. That count is the point: you can
  see background work piling up without leaving the thread you're in.
-->
<template>
  <div class="pane-header shrink-0 flex items-center gap-2.5 px-3.5 py-2.5">
    <!-- Identity: mark + name + what's happening right now -->
    <div class="relative shrink-0">
      <div :class="['pane-mark', tone === 'primary' ? 'pane-mark--primary' : 'pane-mark--muted']">
        <i :class="[icon, 'text-[11px]']"></i>
      </div>
      <!-- A run is live in this pane -->
      <span v-if="live" class="pane-pulse" aria-hidden="true"></span>
    </div>

    <div class="flex-1 min-w-0">
      <h2 class="pane-title truncate">{{ title }}</h2>
      <p v-if="status" class="pane-status truncate">{{ status }}</p>
    </div>

    <!-- Desktop pane switch. Mobile navigates from the navbar switcher, so
         this would be a second control for the same job. -->
    <button
      v-if="switchLabel"
      type="button"
      class="pane-switch group max-md:hidden"
      :aria-label="`Switch to ${switchLabel}`"
      @click="emit('switch')"
    >
      <i
        v-if="switchDirection === 'back'"
        class="fas fa-chevron-left pane-switch-chevron"
      ></i>
      <i :class="[switchIcon, 'pane-switch-icon']"></i>
      <span class="pane-switch-label">{{ switchLabel }}</span>
      <!-- Ambient count of what is waiting on the other side -->
      <span v-if="switchCount" class="pane-switch-count">{{ switchCount }}</span>
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
    /** Font Awesome classes for the pane's mark */
    icon: string
    /** 'primary' is the thread the user drives; 'muted' is everything observed */
    tone?: 'primary' | 'muted'
    title: string
    /** One line on what this pane is doing right now */
    status?: string
    /** A run is live here — the mark gets a pulsing dot */
    live?: boolean
    switchIcon?: string
    switchLabel?: string
    /** Badge on the switch: how much is waiting in the other pane */
    switchCount?: number
    switchDirection?: 'forward' | 'back'
  }>(),
  { tone: 'muted', switchDirection: 'forward' }
)

const emit = defineEmits<{ (e: 'switch'): void }>()
</script>

<style scoped>
/* The plate: a hairline rule plus the faintest wash, so the header reads as
   its own surface rather than the transcript's first row. */
.pane-header {
  background: linear-gradient(180deg, rgba(239, 246, 255, 0.5) 0%, rgba(239, 246, 255, 0) 100%);
  border-bottom: 1px solid rgba(23, 37, 84, 0.08);
}

.dark .pane-header {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.035) 0%, rgba(255, 255, 255, 0) 100%);
  border-bottom-color: rgba(255, 255, 255, 0.12);
}

/* Mark: navy ink for the thread you drive, a quiet tint for panes you watch */
.pane-mark {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.875rem;
  height: 1.875rem;
  border-radius: 0.625rem;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.pane-mark--primary {
  background: theme('colors.blue.950');
  color: #fdf9f2;
  box-shadow:
    0 1px 2px rgba(23, 37, 84, 0.22),
    0 3px 8px -3px rgba(23, 37, 84, 0.28),
    inset 0 1px 0 rgba(255, 255, 255, 0.14);
}

.dark .pane-mark--primary {
  background: #f3ede2;
  color: theme('colors.blue.950');
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.4),
    0 3px 8px -3px rgba(0, 0, 0, 0.45);
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

/* Live-run dot, ringed against the header so it reads on either surface */
.pane-pulse {
  position: absolute;
  right: -1px;
  bottom: -1px;
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  background: theme('colors.blue.500');
  box-shadow: 0 0 0 2px #ffffff;
  animation: pane-pulse 1.8s ease-in-out infinite;
}

.dark .pane-pulse {
  background: theme('colors.blue.300');
  box-shadow: 0 0 0 2px #0a0a0a;
}

@keyframes pane-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.55; transform: scale(0.86); }
}

@media (prefers-reduced-motion: reduce) {
  .pane-pulse { animation: none; }
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

/* Switch: names its destination instead of hiding behind a tooltip */
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
  transition: background-color 0.18s ease, border-color 0.18s ease, color 0.18s ease, transform 0.18s ease;
}

.pane-switch:hover {
  background: #ffffff;
  border-color: rgba(23, 37, 84, 0.2);
  color: theme('colors.blue.950');
  transform: translateY(-1px);
}

.pane-switch:active {
  transform: translateY(0);
}

.pane-switch:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px #ffffff, 0 0 0 4px rgba(59, 130, 246, 0.4);
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

.dark .pane-switch:focus-visible {
  box-shadow: 0 0 0 2px #0a0a0a, 0 0 0 4px rgba(147, 197, 253, 0.5);
}

.pane-switch-icon {
  font-size: 0.625rem;
  opacity: 0.7;
}

.pane-switch-chevron {
  font-size: 0.5rem;
  opacity: 0.45;
  transition: transform 0.18s ease, opacity 0.18s ease;
}

.pane-switch:hover .pane-switch-chevron {
  opacity: 0.8;
}

.group:hover .fa-chevron-right.pane-switch-chevron {
  transform: translateX(1px);
}

.group:hover .fa-chevron-left.pane-switch-chevron {
  transform: translateX(-1px);
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
</style>
