<template>
  <div class="usage-limits-display" role="status" aria-live="polite">
    <div class="usage-card">
      <div class="text-wrap">
        <div class="label-row">
          <span class="label">{{ planLabel }}</span>
        </div>
        <div class="value-row">
          <!-- Unknown usage renders as an em-dash, never as 0% -->
          <span class="value tabular-nums">
            {{ fiveHourPercent !== null ? `${fiveHourPercent}%` : '—' }}
          </span>
          <span v-if="fiveHourPercent !== null" class="meter" aria-hidden="true">
            <span class="meter-fill" :style="{ width: `${fiveHourPercent}%` }"></span>
          </span>
          <span class="window-tag">5h</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue';
import { useUsageStore } from '@/shared/stores/usage';
import { useAgentStore } from '../../../stores/agentStore';

const usageStore = useUsageStore();
const agentStore = useAgentStore();

const planLabel = computed(() => {
  const name = usageStore.plan?.name;
  return name ? `${name} plan` : 'Plan usage';
});

const fiveHourPercent = computed(() => usageStore.fiveHourPercent);

// When any run ends — the lead's or any parallel task's, active or not —
// refresh usage: that run's tokens have just been recorded server-side
// (small delay lets the write land). Watching the aggregate count (not a
// boolean) catches each run ending while others are still going.
watch(() => agentStore.processingCount, (newCount, oldCount) => {
  if (newCount < oldCount) {
    setTimeout(() => {
      void usageStore.fetchUsage();
    }, 500);
  }
});

// No fetch on mount: the workspace fetches usage once at boot, and this card
// just renders whatever the store holds (matching the old balance card).
</script>

<style scoped>
.usage-limits-display {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  transition: all 0.3s ease;
}

.usage-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.text-wrap { display: flex; flex-direction: column; gap: 0.125rem; min-width: 5.5rem; }
.label-row { display: flex; align-items: center; gap: 0.3rem; }
.label { font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; color: rgba(23, 37, 84, 0.55); font-weight: 600; }
.value-row { display: flex; align-items: center; gap: 0.375rem; }
.value {
  color: rgb(23, 37, 84);
  font-weight: 700;
  font-size: 1rem;
  line-height: 1;
}

/* 5-hour window meter: quiet navy ink bar matching the site's primary accent */
.meter {
  position: relative;
  width: 3rem;
  height: 0.25rem;
  border-radius: 9999px;
  background: rgba(23, 37, 84, 0.1);
  overflow: hidden;
}

.meter-fill {
  position: absolute;
  inset: 0 auto 0 0;
  border-radius: 9999px;
  background: theme('colors.blue.950');
  transition: width 0.3s ease;
}

.window-tag {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.04em;
  color: rgba(23, 37, 84, 0.4);
}

.tabular-nums { font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1; }
</style>

<style>
/* Dark mode styles - unscoped to access parent .dark class */
.dark .usage-limits-display .label {
  color: rgba(255, 255, 255, 0.5);
}

.dark .usage-limits-display .value {
  color: rgba(255, 255, 255, 0.95);
}

.dark .usage-limits-display .meter {
  background: rgba(255, 255, 255, 0.12);
}

.dark .usage-limits-display .meter-fill {
  background: #f3ede2;
}

.dark .usage-limits-display .window-tag {
  color: rgba(255, 255, 255, 0.4);
}
</style>
