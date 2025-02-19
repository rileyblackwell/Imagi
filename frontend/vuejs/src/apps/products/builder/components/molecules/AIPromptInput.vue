<template>
  <div class="relative">
    <!-- Input Area -->
    <div 
      class="flex items-start space-x-2 p-2 bg-dark-800 rounded-lg border border-dark-700 focus-within:border-primary-500 transition-colors"
      :class="{ 'opacity-75': loading }"
    >
      <textarea
        ref="textareaRef"
        v-model="inputValue"
        :placeholder="placeholder"
        class="flex-1 bg-transparent border-0 focus:ring-0 resize-none min-h-[2.5rem] max-h-32 text-white placeholder-gray-500"
        :rows="rows"
        @keydown.enter.prevent="handleEnter"
        @input="autoResize"
      />
      <button
        class="shrink-0 p-2 text-primary-500 hover:text-primary-400 disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="!canSubmit || loading"
        @click="submit"
      >
        <i class="fas" :class="loading ? 'fa-circle-notch fa-spin' : 'fa-paper-plane'" />
      </button>
    </div>

    <!-- Character Count -->
    <div 
      class="absolute bottom-2 right-12 text-xs"
      :class="isOverLimit ? 'text-red-500' : 'text-gray-500'"
    >
      {{ inputValue.length }}/{{ characterLimit }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import type { BuilderMode } from '../../types/builder'

const props = defineProps<{
  modelValue: string
  mode: BuilderMode
  placeholder?: string
  loading?: boolean
  characterLimit?: number
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'submit'): void
}>()

const textareaRef = ref<HTMLTextAreaElement>()
const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// Computed properties
const isOverLimit = computed(() => 
  inputValue.value.length > (props.characterLimit || 2000)
)

const canSubmit = computed(() => 
  inputValue.value.trim().length > 0 && !isOverLimit.value
)

const rows = computed(() => 
  Math.min(Math.max(inputValue.value.split('\n').length, 1), 5)
)

// Methods
const autoResize = () => {
  if (!textareaRef.value) return
  
  // Reset height to auto to get proper scrollHeight
  textareaRef.value.style.height = 'auto'
  
  // Set new height based on scrollHeight
  const newHeight = Math.min(
    textareaRef.value.scrollHeight,
    256 // max-height in pixels
  )
  textareaRef.value.style.height = `${newHeight}px`
}

const handleEnter = (event: KeyboardEvent) => {
  if (event.shiftKey) {
    // Allow newline with Shift+Enter
    return
  }
  
  if (canSubmit.value) {
    submit()
  }
}

const submit = () => {
  if (!canSubmit.value) return
  emit('submit')
}

// Lifecycle
onMounted(() => {
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.focus()
      autoResize()
    }
  })
})
</script>

<style scoped>
textarea {
  min-height: 2.5rem;
  line-height: 1.5;
  scrollbar-width: thin;
  scrollbar-color: theme('colors.dark.600') transparent;
}

textarea::-webkit-scrollbar {
  width: 6px;
}

textarea::-webkit-scrollbar-track {
  background: transparent;
}

textarea::-webkit-scrollbar-thumb {
  background-color: theme('colors.dark.600');
  border-radius: 3px;
}

/* Hide scrollbar when not hovering */
textarea:not(:hover)::-webkit-scrollbar-thumb {
  background: transparent;
}
</style>