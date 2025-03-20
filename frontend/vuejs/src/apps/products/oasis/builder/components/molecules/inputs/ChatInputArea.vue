<template>
  <div class="chat-input-wrapper">
    <!-- Examples section if needed -->
    <slot name="examples" v-if="false"></slot>
    
    <div class="relative">
      <!-- Mode indicator above input -->
      <div class="mb-2 flex justify-between items-center">
        <slot name="mode-indicator"></slot>
      </div>
      
      <!-- Input form with iMessage/ChatGPT like design -->
      <form @submit.prevent="handleSubmit" class="relative">
        <div class="flex items-end space-x-2">
          <!-- Main textarea with auto-grow functionality -->
          <div 
            class="flex-grow relative rounded-2xl bg-dark-800 border transition-all duration-200"
            :class="[
              isTyping || isFocused 
                ? 'border-primary-500/70 ring-2 ring-primary-500/20' 
                : 'border-dark-700 hover:border-dark-600'
            ]"
          >
            <!-- Typing indicator dots when processing -->
            <div 
              v-if="isProcessing" 
              class="absolute left-4 top-3.5 flex items-center space-x-1"
            >
              <div v-for="i in 3" :key="i" class="w-1.5 h-1.5 rounded-full bg-primary-500 opacity-70 animate-pulse" :style="{ animationDelay: `${i * 150}ms` }"></div>
            </div>
            
            <textarea 
              ref="inputRef"
              v-model="localValue"
              :placeholder="isProcessing ? 'AI is thinking...' : placeholder"
              class="w-full bg-transparent text-white resize-none p-3 pr-12 rounded-2xl focus:outline-none max-h-60 transition-all"
              :rows="Math.min(5, rows)"
              :disabled="isProcessing"
              @input="autoGrow"
              @keydown="handleKeydown"
              @focus="isFocused = true"
              @blur="isFocused = false"
            ></textarea>
            
            <!-- Submit button inside the input area -->
            <button 
              type="submit"
              class="absolute right-3 bottom-3 p-2 text-white rounded-full transition-all duration-200 disabled:opacity-30 disabled:cursor-not-allowed"
              :class="[
                canSubmit && !isProcessing 
                  ? 'bg-primary-500 hover:bg-primary-600 scale-100' 
                  : 'bg-gray-500 scale-95'
              ]"
              :disabled="!canSubmit || isProcessing"
              aria-label="Send message"
            >
              <i class="fas fa-paper-plane text-sm"></i>
            </button>
          </div>
        </div>
        
        <!-- Keyboard shortcuts hint -->
        <div class="mt-2 flex justify-end">
          <div class="text-xs text-gray-500 flex items-center">
            <span>Press <kbd class="px-1.5 py-0.5 bg-dark-800 rounded border border-dark-700 text-gray-400 mx-1">Enter</kbd> to send</span>
            <span class="mx-2">•</span>
            <span>Use <kbd class="px-1.5 py-0.5 bg-dark-800 rounded border border-dark-700 text-gray-400 mx-1">Shift</kbd> + <kbd class="px-1.5 py-0.5 bg-dark-800 rounded border border-dark-700 text-gray-400 mx-1">Enter</kbd> for new line</span>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick, onBeforeUnmount } from 'vue'

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
const isFocused = ref(props.focused)
const isTyping = ref(false)
let typingTimer: number | null = null

// Computed properties
const canSubmit = computed(() => localValue.value.trim().length > 0)

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  localValue.value = newValue
})

// Update parent model
watch(localValue, (newValue) => {
  emit('update:modelValue', newValue)
  
  // Set typing indicator
  if (newValue.trim()) {
    isTyping.value = true
    if (typingTimer) clearTimeout(typingTimer)
    typingTimer = window.setTimeout(() => {
      isTyping.value = false
    }, 1000)
  } else {
    isTyping.value = false
  }
})

// Methods
function handleSubmit() {
  if (!canSubmit.value || props.isProcessing) return
  emit('submit')
  // Don't clear the input here as the parent component should handle this
}

function handleKeydown(event: KeyboardEvent) {
  // Submit on Enter without Shift
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    handleSubmit()
  }
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

// Clean up typing timer on component unmount
onBeforeUnmount(() => {
  if (typingTimer) clearTimeout(typingTimer)
})
</script>

<style scoped>
.chat-input-wrapper {
  position: relative;
  width: 100%;
  z-index: 10;
}

/* Custom scrollbar for textarea */
textarea {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.dark.700') transparent;
}

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

/* Animated typing indicator */
@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1); }
}

.animate-pulse {
  animation: pulse 1.5s ease-in-out infinite;
}
</style> 