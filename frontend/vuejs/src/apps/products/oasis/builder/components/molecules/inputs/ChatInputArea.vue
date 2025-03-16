<template>
  <div class="relative">
    <!-- Examples section (slot) -->
    <div v-if="showExamples && $slots.examples" class="mb-4">
      <slot name="examples"></slot>
    </div>
    
    <div class="flex items-end border border-dark-700/70 rounded-xl bg-dark-800/50 backdrop-blur-sm shadow-lg transition-all duration-200 hover:border-dark-600/70 focus-within:border-primary-500/50 focus-within:ring-1 focus-within:ring-primary-500/30">
      <!-- Auto-expanding textarea -->
      <textarea
        id="user-input"
        ref="textareaRef"
        v-model="inputValue"
        :placeholder="placeholder"
        class="flex-1 bg-transparent text-white px-4 py-3 max-h-[200px] min-h-[56px] focus:outline-none resize-none overflow-y-auto rounded-l-xl"
        :rows="rows"
        @input="autoResize"
        @keydown.enter.prevent="handleEnterKey"
        :disabled="isProcessing"
      ></textarea>
      
      <!-- Examples button (conditional) -->
      <button
        v-if="showExamples && !inputValue.trim()"
        @click="$emit('examples')"
        class="p-3 text-gray-400 hover:text-gray-300 transition-colors"
        title="Show examples"
      >
        <i class="fas fa-lightbulb"></i>
      </button>
      
      <!-- Send button -->
      <button
        @click="handleSubmit"
        class="p-3 mr-2 mb-2 text-white rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        :class="[
          inputValue.trim() 
            ? 'bg-primary-500 hover:bg-primary-600 active:bg-primary-700 shadow-md hover:shadow-lg' 
            : 'bg-dark-700'
        ]"
        :disabled="isProcessing || !inputValue.trim()"
        :title="isProcessing ? 'Processing...' : 'Send message'"
      >
        <i class="fas" :class="isProcessing ? 'fa-spinner fa-spin' : 'fa-paper-plane'"></i>
      </button>
    </div>
    
    <!-- Helper text -->
    <div class="mt-2 flex justify-between items-center text-xs text-gray-500">
      <div>
        <slot name="mode-indicator">
          <!-- Empty by default -->
        </slot>
      </div>
      <div class="flex items-center space-x-2">
        <span class="flex items-center">
          <kbd class="px-1.5 py-0.5 bg-dark-800 rounded text-gray-400 border border-dark-700 shadow-sm">Enter</kbd>
          <span class="mx-1">to send</span>
        </span>
        <span class="flex items-center">
          <kbd class="px-1.5 py-0.5 bg-dark-800 rounded text-gray-400 border border-dark-700 shadow-sm">Shift+Enter</kbd>
          <span class="mx-1">for new line</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick } from 'vue'

const props = defineProps<{
  modelValue: string
  isProcessing?: boolean
  placeholder?: string
  focused?: boolean
  showExamples?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'submit', value: string): void
  (e: 'examples'): void
}>()

const inputValue = ref(props.modelValue)
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const rows = ref(1)

watch(() => props.modelValue, (newValue) => {
  inputValue.value = newValue
  nextTick(() => autoResize())
})

watch(inputValue, (newValue) => {
  emit('update:modelValue', newValue)
})

// Focus the input when the focused prop changes
watch(() => props.focused, (newValue) => {
  if (newValue && textareaRef.value) {
    textareaRef.value.focus()
  }
})

const autoResize = () => {
  if (!textareaRef.value) return
  
  // Reset height to calculate proper scrollHeight
  textareaRef.value.style.height = 'auto'
  
  // Set new height based on content
  const newHeight = Math.min(textareaRef.value.scrollHeight, 200)
  textareaRef.value.style.height = `${newHeight}px`
  
  // Update rows for accessibility
  rows.value = Math.max(1, Math.min(10, Math.ceil(newHeight / 24)))
}

const handleEnterKey = (event: KeyboardEvent) => {
  if (event.shiftKey) {
    // Allow Shift+Enter for new line
    const textarea = event.target as HTMLTextAreaElement
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    
    inputValue.value = 
      inputValue.value.substring(0, start) + 
      '\n' + 
      inputValue.value.substring(end)
    
    nextTick(() => {
      textarea.selectionStart = textarea.selectionEnd = start + 1
      autoResize()
    })
  } else {
    // Regular Enter submits the form
    handleSubmit()
  }
}

const handleSubmit = () => {
  if (!inputValue.value.trim() || props.isProcessing) return
  emit('submit', inputValue.value)
}

onMounted(() => {
  autoResize()
  
  // Focus the input if focused prop is true
  if (props.focused && textareaRef.value) {
    textareaRef.value.focus()
  }
})
</script>

<style scoped>
textarea {
  font-family: inherit;
  line-height: 1.5;
  font-size: 0.875rem;
}

/* Hide scrollbar but allow scrolling */
textarea::-webkit-scrollbar {
  width: 4px;
}

textarea::-webkit-scrollbar-track {
  background: transparent;
}

textarea::-webkit-scrollbar-thumb {
  background-color: theme('colors.dark.700');
  border-radius: 9999px;
}

textarea::-webkit-scrollbar-thumb:hover {
  background-color: theme('colors.dark.600');
}
</style> 