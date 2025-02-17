<template>
  <div class="p-4">
    <label class="block text-sm font-medium text-gray-400 mb-2">Mode</label>
    <div class="flex rounded-lg bg-dark-900 p-1">
      <button
        v-for="modeOption in modes"
        :key="modeOption"
        @click="handleModeChange(modeOption)"
        class="flex items-center justify-center flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors"
        :class="[
          mode === modeOption
            ? 'bg-primary-500 text-white'
            : 'text-gray-400 hover:text-white hover:bg-dark-700'
        ]"
      >
        <i :class="[getModeIcon(modeOption), 'mr-2']"></i>
        {{ formatMode(modeOption) }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { BuilderMode } from '@/apps/products/builder/types/builder'

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
