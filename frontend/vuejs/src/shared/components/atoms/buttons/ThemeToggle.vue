<!-- The theme switch: a Spotlight segmented control of System, Light and Dark.
     It reads the --sl-* tokens of the .spotlight root it sits in (the
     footer's), with fallbacks so it still draws anywhere else. -->
<template>
  <div class="theme-seg" role="group" aria-label="Theme">
    <button
      v-for="option in options"
      :key="option.value"
      type="button"
      :aria-pressed="currentTheme === option.value ? 'true' : 'false'"
      :title="option.value === 'system' ? `Follow your device (${effectiveTheme} now)` : undefined"
      @click="selectTheme(option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useThemeStore } from '@/shared/stores/theme'

type Theme = 'light' | 'dark' | 'system'

const themeStore = useThemeStore()

const currentTheme = computed(() => themeStore.currentTheme)
const effectiveTheme = computed(() => themeStore.effectiveTheme)

const options: { value: Theme; label: string }[] = [
  { value: 'system', label: 'System' },
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
]

const selectTheme = (theme: Theme) => {
  themeStore.setTheme(theme)
}
</script>

<style scoped>
.theme-seg {
  display: inline-flex;
  padding: 3px;
  border-radius: 9999px;
  border: 1px solid var(--sl-line-strong, rgba(127, 127, 127, 0.25));
  background: var(--sl-chip-bg, rgba(127, 127, 127, 0.06));
}

.theme-seg button {
  padding: 5px 13px;
  border: 0;
  border-radius: 9999px;
  background: none;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--sl-muted, currentColor);
  cursor: pointer;
  transition: background-color 0.2s cubic-bezier(0.22, 1, 0.36, 1), color 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}

.theme-seg button:hover {
  color: var(--sl-text, currentColor);
}

.theme-seg button[aria-pressed='true'] {
  background: var(--sl-surface-2, #fff);
  color: var(--sl-text, currentColor);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08), 0 0 0 1px var(--sl-line, rgba(127, 127, 127, 0.15));
}
</style>
