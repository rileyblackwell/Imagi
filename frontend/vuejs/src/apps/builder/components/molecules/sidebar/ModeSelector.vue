<template>
  <div class="p-4 border-b border-dark-700">
    <label class="block text-sm font-medium text-gray-400 mb-2">Mode</label>
    <div class="flex bg-dark-900 rounded-lg p-1">
      <button
        v-for="modeOption in modes"
        :key="modeOption"
        @click="handleModeChange(modeOption)"
        class="flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors"
        :class="[
          mode === modeOption
            ? 'bg-primary-500 text-white'
            : 'text-gray-400 hover:text-white'
        ]"
      >
        <i :class="getModeIcon(modeOption)" class="mr-2"></i>
        {{ formatMode(modeOption) }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { BuilderMode } from '@/apps/builder/types/builder'

const props = defineProps<{
  mode: BuilderMode
  modes: BuilderMode[]
}>()

const emit = defineEmits<{
  (e: 'update:mode', value: BuilderMode): void
}>()

const handleModeChange = (newMode: BuilderMode) => {
  if (newMode !== props.mode) {
    emit('update:mode', newMode)
  }
}

const getModeIcon = (mode: BuilderMode): string => {
  const icons: Record<BuilderMode, string> = {
    chat: 'fas fa-comments',
    build: 'fas fa-code'
  }
  return icons[mode] || 'fas fa-code'
}

const formatMode = (mode: string): string => {
  return mode.charAt(0).toUpperCase() + mode.slice(1)
}
</script>
