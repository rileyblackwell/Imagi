<template>
  <div class="chat-input-wrapper">
    <!-- Examples section if needed -->
    <slot name="examples" v-if="showExamples"></slot>
    
    <div class="relative">
      <!-- Mode indicator above input -->
      <div class="mb-3.5 flex justify-between items-center">
        <slot name="mode-indicator"></slot>
      </div>
      
      <!-- Input form with improved design -->
      <form @submit.prevent="handleSubmit" class="relative">
        <div class="relative rounded-2xl bg-dark-850/90 border transition-all duration-200 shadow-md"
          :class="[
            isTyping || isFocused 
              ? 'border-primary-500/50 ring-2 ring-primary-500/20' 
              : 'border-dark-700/60 hover:border-dark-600/70'
          ]"
        >
          <!-- Typing indicator dots when processing -->
          <div 
            v-if="isProcessing" 
            class="absolute left-5 top-1/2 -translate-y-1/2 flex items-center space-x-1.5 z-10"
          >
            <div v-for="i in 3" :key="i" class="w-2 h-2 rounded-full bg-primary-400 opacity-80 animate-typing-pulse" 
              :style="{ animationDelay: `${i * 150}ms` }"></div>
          </div>
          
          <!-- Subtle gradient overlay for input area -->
          <div class="absolute inset-0 rounded-2xl bg-gradient-to-b from-transparent to-dark-900/20 pointer-events-none z-0"></div>
          
          <div class="relative z-10">
            <textarea 
              ref="inputRef"
              v-model="localValue"
              :placeholder="isProcessing ? 'AI is thinking...' : placeholder"
              class="w-full bg-transparent text-white resize-none p-4 pr-14 rounded-2xl focus:outline-none transition-all"
              :class="{'min-h-[56px]': rows <= 1, 'max-h-56 overflow-y-auto': rows > 1}"
              :style="{'height': textareaHeight}"
              :disabled="isProcessing"
              @input="autoGrow"
              @keydown="handleKeydown"
              @focus="isFocused = true"
              @blur="isFocused = false"
            ></textarea>
            
            <!-- Submit button with improved design and animation -->
            <button 
              type="submit"
              class="absolute right-3 bottom-3 p-2.5 text-white rounded-full transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              :class="[
                canSubmit && !isProcessing 
                  ? 'bg-primary-500 hover:bg-primary-600 scale-100 shadow-md' 
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
        
        <!-- Keyboard shortcuts hint with improved styling -->
        <div class="mt-2 flex justify-end">
          <div class="text-xs text-gray-500/80 flex items-center gap-2 bg-dark-900/30 px-2.5 py-1 rounded-md backdrop-blur-sm">
            <span class="flex items-center">
              <kbd class="mx-1 px-1.5 py-0.5 bg-dark-800/80 rounded border border-dark-700/70 text-gray-400 shadow-sm font-sans text-[10px]">Enter</kbd> to send
            </span>
            <span class="text-gray-600/50">•</span>
            <span class="flex items-center">
              <kbd class="mx-1 px-1.5 py-0.5 bg-dark-800/80 rounded border border-dark-700/70 text-gray-400 shadow-sm font-sans text-[10px]">Shift+Enter</kbd> for new line
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
  
  // Store the current scroll position
  const scrollPos = window.scrollY
  
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
  
  // Restore scroll position
  window.scrollTo(0, scrollPos)
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