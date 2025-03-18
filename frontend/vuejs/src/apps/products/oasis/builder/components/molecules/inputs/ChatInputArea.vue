<template>
  <div class="chat-input-wrapper">
    <!-- Examples section if needed -->
    <slot name="examples" v-if="showExamples"></slot>
    
    <div class="relative">
      <!-- Mode indicator above input -->
      <div class="mb-2 flex justify-between items-center">
        <slot name="mode-indicator"></slot>
      </div>
      
      <!-- Input form with iMessage/ChatGPT like design -->
      <form @submit.prevent="handleSubmit" class="relative">
        <div class="flex items-end space-x-2">
          <!-- Main textarea with auto-grow functionality -->
          <div class="flex-grow relative rounded-2xl bg-dark-800 border border-dark-700 focus-within:border-primary-500 focus-within:ring-1 focus-within:ring-primary-500/30 transition-all duration-200">
            <textarea 
              ref="inputRef"
              v-model="localValue"
              :placeholder="placeholder"
              class="w-full bg-transparent text-white resize-none p-3 pr-12 rounded-2xl focus:outline-none max-h-60"
              :rows="Math.min(5, rows)"
              :disabled="isProcessing"
              @input="autoGrow"
              @keydown.enter.exact.prevent="handleSubmit"
            ></textarea>
            
            <!-- Submit button inside the input area -->
            <button 
              type="submit"
              class="absolute right-2 bottom-2 p-2 text-white bg-primary-500 hover:bg-primary-600 rounded-full transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="!canSubmit || isProcessing"
              aria-label="Send message"
            >
              <i class="fas fa-paper-plane text-sm"></i>
            </button>
          </div>
        </div>
        
        <!-- Processing indicator -->
        <div v-if="isProcessing" class="mt-2 text-xs text-gray-400 flex items-center">
          <i class="fas fa-circle-notch fa-spin mr-2"></i>
          <span>AI is thinking...</span>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'

// Props
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Type a message...'
  },
  focused: {
    type: Boolean,
    default: false
  },
  isProcessing: {
    type: Boolean,
    default: false
  },
  showExamples: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'submit', 'examples'])

// Local state
const localValue = ref(props.modelValue)
const rows = ref(1)
const inputRef = ref<HTMLTextAreaElement | null>(null)

// Computed properties
const canSubmit = computed(() => localValue.value.trim().length > 0)

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  localValue.value = newValue
})

// Update parent model
watch(localValue, (newValue) => {
  emit('update:modelValue', newValue)
})

// Methods
function handleSubmit() {
  if (!canSubmit.value || props.isProcessing) return
  emit('submit')
  // Don't clear the input here as the parent component should handle this
}

function autoGrow() {
  // Reset height to calculate properly
  if (inputRef.value) {
    inputRef.value.style.height = 'auto'
    const newHeight = inputRef.value.scrollHeight
    inputRef.value.style.height = `${newHeight}px`
    
    // Calculate rows based on line height (approx 24px per line)
    rows.value = Math.ceil(newHeight / 24)
  }
}

// Focus the input when the component is mounted
onMounted(async () => {
  if (props.focused && inputRef.value) {
    await nextTick()
    inputRef.value.focus()
  }
})
</script>

<style scoped>
.chat-input-wrapper {
  position: relative;
}

/* Optional styling for chat bubbles */
.chat-bubble-user {
  @apply bg-primary-500 text-white rounded-2xl rounded-br-sm py-2 px-4;
}

.chat-bubble-ai {
  @apply bg-dark-800 text-white rounded-2xl rounded-bl-sm py-2 px-4;
}
</style> 