<template>
  <div class="chat-input-wrapper">
    <!-- Examples section if needed -->
    <slot name="examples" v-if="showExamples"></slot>
    
    <div class="relative">
      <!-- Mode indicator above input -->
      <div class="mb-3.5 flex justify-between items-center">
        <slot name="mode-indicator"></slot>
      </div>
      
      <!-- Simplified Input form with clean styling -->
      <form @submit.prevent="handleSubmit" class="relative">
        <div class="relative rounded-xl transition-all duration-200"
          :class="[
            isTyping || isFocused 
              ? 'bg-dark-800/60 ring-2 ring-violet-500/20' 
              : 'bg-dark-800/40 hover:bg-dark-800/50'
          ]"
        >
          <div class="relative z-10">
            <textarea 
              ref="inputRef"
              v-model="localValue"
              :placeholder="isProcessing ? 'AI is thinking...' : placeholder"
              class="w-full bg-transparent text-white resize-none p-4 pr-14 rounded-xl transition-all placeholder-gray-400 border-0 focus:border-0 hover:border-0 backdrop-blur-sm focus:shadow-lg focus:shadow-violet-500/20 outline-none focus:outline-none focus:ring-0 ring-0"
              :class="{'min-h-[56px]': rows <= 1, 'max-h-56 overflow-y-auto': rows > 1}"
              :style="{'height': textareaHeight}"
              :disabled="isProcessing"
              @input="autoGrow"
              @keydown="handleKeydown"
              @focus="isFocused = true"
              @blur="isFocused = false"
            ></textarea>
            
            <!-- Enhanced Submit button with modern design -->
            <button 
              type="submit"
              class="absolute right-3 bottom-3 p-2.5 text-white rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center outline-none focus:outline-none"
              :class="[
                canSubmit && !isProcessing 
                  ? 'bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 scale-100 shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/35 hover:scale-105' 
                  : 'bg-gray-600/70 scale-95'
              ]"
              :disabled="!canSubmit || isProcessing"
              aria-label="Send message"
            >
              <i 
                class="fas fa-paper-plane text-sm transition-transform"
                :class="{'hover:translate-x-0.5': canSubmit && !isProcessing}"
              ></i>
            </button>
          </div>
        </div>
        
        <!-- Enhanced keyboard shortcuts hint with modern styling -->
        <div class="mt-3 flex justify-center">
          <div class="text-xs text-gray-400/80 flex items-center gap-2 bg-gradient-to-r from-dark-900/60 to-dark-800/60 backdrop-blur-sm px-3 py-1.5 rounded-xl border border-dark-700/30">
            <span class="flex items-center">
              <kbd class="mx-1 px-2 py-1 bg-dark-800/80 rounded-lg border border-dark-700/70 text-gray-300 shadow-sm font-sans text-[10px] font-medium">Enter</kbd> 
              <span class="text-gray-500">to send</span>
            </span>
            <span class="text-gray-600/50">•</span>
            <span class="flex items-center">
              <kbd class="mx-1 px-2 py-1 bg-dark-800/80 rounded-lg border border-dark-700/70 text-gray-300 shadow-sm font-sans text-[10px] font-medium">Shift+Enter</kbd> 
              <span class="text-gray-500">for new line</span>
            </span>
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
const textareaHeight = ref('60px')
const inputRef = ref<HTMLTextAreaElement | null>(null)
const isFocused = ref(props.focused)
const isTyping = ref(false)
let typingTimer: number | null = null

// Computed properties
const canSubmit = computed(() => localValue.value.trim().length > 0)

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  localValue.value = newValue
  nextTick(() => autoGrow())
})

// Update parent model and handle typing indicator
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
  
  // Emit submit with timestamp
  emit('submit', {
    timestamp: new Date().toISOString()
  })
  
  // Don't clear the input here as the parent component should handle this
}

function handleKeydown(event: KeyboardEvent) {
  // Submit on Enter without Shift
  if (event.key === 'Enter' && !event.shiftKey && !event.altKey && !event.ctrlKey) {
    event.preventDefault()
    handleSubmit()
  }
}

function autoGrow() {
  if (!inputRef.value) return
  
  // Save current scroll positions before height changes
  const chatContainer = document.querySelector('.overflow-y-auto')
  const chatScrollPosition = chatContainer ? chatContainer.scrollTop : 0
  
  // Reset height to calculate properly
  inputRef.value.style.height = 'auto'
  
  // Get the scroll height (content height)
  const scrollHeight = inputRef.value.scrollHeight
  
  // Set the new height with proper constraints
  const minHeight = 60
  const maxHeight = 200
  const newHeight = Math.min(Math.max(scrollHeight, minHeight), maxHeight)
  
  // Update the height
  textareaHeight.value = `${newHeight}px`
  inputRef.value.style.height = textareaHeight.value
  
  // Calculate rows based on line height (approx 24px per line)
  rows.value = Math.ceil(scrollHeight / 24)
  
  // Restore chat container scroll position after height change (use requestAnimationFrame for better timing)
  requestAnimationFrame(() => {
    if (chatContainer) {
      chatContainer.scrollTop = chatScrollPosition
    }
  })
}

// Focus the input when the component is mounted
onMounted(async () => {
  await nextTick()
  autoGrow()
  
  if (props.focused && inputRef.value) {
    inputRef.value.focus()
  }
})

// Clean up typing timer on component unmount
onBeforeUnmount(() => {
  if (typingTimer) clearTimeout(typingTimer)
})
</script>

<style scoped>
/* Completely remove any browser default styling for form inputs */
input, textarea, button {
  outline: none !important;
  box-shadow: none !important;
  border: none !important;
  -webkit-appearance: none !important;
  -moz-appearance: none !important;
  appearance: none !important;
}

input:focus, textarea:focus, button:focus {
  outline: none !important;
  box-shadow: none !important;
  border: none !important;
  ring: none !important;
}

/* Remove any webkit/moz specific focus styling */
input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

textarea::-webkit-resizer {
  display: none;
}

/* Remove default button styling */
button::-moz-focus-inner {
  border: 0;
}

/* Ensure textarea doesn't get browser default focus styles */
.chat-input-wrapper textarea {
  outline: none !important;
  box-shadow: none !important;
}

.chat-input-wrapper textarea:focus {
  outline: none !important;
  box-shadow: none !important;
}

/* Ensure buttons don't get browser default focus styles */
.chat-input-wrapper button {
  outline: none !important;
  box-shadow: none !important;
}

.chat-input-wrapper button:focus {
  outline: none !important;
  box-shadow: none !important;
}

/* Legacy animations */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.animate-pulse-slow {
  animation: pulse 3s ease-in-out infinite;
}

@keyframes float-slow {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(-20px) translateX(10px); }
}

@keyframes float-slow-reverse {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(20px) translateX(-10px); }
}

.animate-float-slow {
  animation: float-slow 20s ease-in-out infinite;
}

.animate-float-slow-reverse {
  animation: float-slow-reverse 25s ease-in-out infinite;
}

.chat-input-wrapper {
  position: relative;
  width: 100%;
  z-index: 10;
}

/* Custom scrollbar for textarea */
textarea {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.dark.700') transparent;
  transition: height 0.15s ease;
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
@keyframes typing-pulse {
  0%, 100% { opacity: 0.4; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1); }
}

.animate-typing-pulse {
  animation: typing-pulse 1.5s ease-in-out infinite;
}

/* Hover animation for send button */
.hover-animate {
  transition: transform 0.3s ease;
}

button:hover .hover-animate {
  transform: translateX(1px) translateY(-1px) scale(1.05);
}

/* Better styling for the kbd elements */
kbd {
  display: inline-block;
  line-height: 1;
  font-weight: 500;
}
</style> 