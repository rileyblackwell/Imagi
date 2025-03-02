<template>
  <div class="p-4">
    <label class="block text-sm font-medium text-gray-200 mb-2">
      Mode
    </label>

    <div class="grid grid-cols-2 gap-2">
      <button
        v-for="option in modeOptions"
        :key="option.id"
        class="flex items-center justify-center p-3 rounded-lg border transition-colors"
        :class="[
          mode === option.id
            ? 'bg-primary-500/20 border-primary-500'
            : 'bg-dark-800 border-dark-700 hover:border-dark-600'
        ]"
        @click="handleModeChange(option.id)"
      >
        <div class="flex items-center space-x-2">
          <i :class="['fas', option.icon]" />
          <span>{{ option.label }}</span>
        </div>
      </button>
    </div>

    <!-- Mode Description -->
    <TransitionGroup 
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-300 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <p 
        v-if="currentModeOption"
        class="mt-3 text-sm text-gray-400"
      >
        {{ currentModeOption.description }}
      </p>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { BuilderMode } from '../../../types/builder'

const props = defineProps<{
  mode: BuilderMode
}>()

const emit = defineEmits<{
  (e: 'update:mode', value: BuilderMode): void
}>()

// Add a method to handle mode changes
const handleModeChange = (newMode: BuilderMode) => {
  if (props.mode !== newMode) {
    // Emit the update event
    emit('update:mode', newMode)
    
    // Force a DOM update to ensure the change is reflected
    setTimeout(() => {
      // Trigger a custom event that the parent component can listen for
      document.dispatchEvent(new CustomEvent('mode-selection-updated', { 
        detail: { mode: newMode }
      }))
    }, 50)
  }
}

const modeOptions = [
  {
    id: 'chat' as const,
    icon: 'fa-comments',
    label: 'Chat Mode',
    description: 'Have a conversation about your project and get assistance'
  },
  {
    id: 'build' as const,
    icon: 'fa-code',
    label: 'Build Mode',
    description: 'Generate and modify code directly in your project'
  }
]

const currentModeOption = computed(() => 
  modeOptions.find(option => option.id === props.mode)
)
</script>
