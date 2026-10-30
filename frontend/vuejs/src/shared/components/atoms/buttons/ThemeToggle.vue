<!-- The theme switch: a Spotlight segmented control of System, Light and Dark.
     It reads the --sl-* tokens of the .spotlight root it sits in (the
     footer's), with fallbacks so it still draws anywhere else. -->
<template>
  <div
    class="inline-flex p-[3px] rounded-full border border-[color:var(--sl-line-strong,rgba(127,127,127,0.25))] bg-[color:var(--sl-chip-bg,rgba(127,127,127,0.06))]"
    role="group"
    aria-label="Theme"
  >
    <button
      v-for="option in options"
      :key="option.value"
      type="button"
      class="py-[5px] px-[13px] [border:0] rounded-full text-[12.5px] font-semibold cursor-pointer
             [transition:background-color_0.2s_cubic-bezier(0.22,1,0.36,1),color_0.2s_cubic-bezier(0.22,1,0.36,1)]"
      :class="currentTheme === option.value
        ? 'bg-[color:var(--sl-surface-2,#fff)] text-[color:var(--sl-text,currentColor)] [box-shadow:0_1px_2px_rgba(0,0,0,0.08),0_0_0_1px_var(--sl-line,rgba(127,127,127,0.15))]'
        : 'bg-transparent text-[color:var(--sl-muted,currentColor)] hover:text-[color:var(--sl-text,currentColor)]'"
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
