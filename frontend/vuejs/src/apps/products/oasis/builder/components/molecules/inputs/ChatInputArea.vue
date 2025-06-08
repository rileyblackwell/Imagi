<template>
  <div class="chat-input-wrapper">
    <!-- Examples section if needed -->
    <slot name="examples" v-if="showExamples"></slot>
    
    <div class="relative">
      <!-- Mode indicator above input -->
      <div class="mb-3.5 flex justify-between items-center">
        <slot name="mode-indicator"></slot>
      </div>
      
      <!-- Simplified chat input matching dashboard input styling -->
      <div class="chat-input-area w-full">
        <!-- Enhanced Input Container -->
        <div class="relative w-full">
          <!-- Main chat input section -->
          <div class="relative">
            <div class="flex items-end w-full">
              <!-- Enhanced Form Container -->
              <form @submit.prevent="handleSubmit" class="relative z-10 w-full">
                <!-- Input container with dashboard-style background -->
                <div class="relative bg-white/5 border border-white/10 focus-within:border-violet-400/50 hover:border-white/15 rounded-xl transition-all duration-300 backdrop-blur-sm hover:bg-white/8 focus-within:bg-white/8 focus-within:shadow-lg focus-within:shadow-violet-500/20">
                  <!-- Modern textarea with enhanced styling -->
                  <textarea 
                    ref="inputRef"
                    v-model="localValue"
                    :placeholder="isProcessing ? 'AI is thinking...' : placeholder"
                    class="w-full bg-transparent text-white resize-none pr-14 p-4 rounded-xl transition-all placeholder-gray-400 border-0 focus:border-0 hover:border-0 outline-none focus:outline-none focus:ring-0 ring-0 leading-relaxed text-sm"
                    :class="{'min-h-[56px]': rows <= 1, 'max-h-48 overflow-y-auto': rows > 1}"
                    :style="{'height': textareaHeight}"
                    :disabled="isProcessing"
                    @input="autoGrow"
                    @keydown="handleKeydown"
                    @focus="isFocused = true"
                    @blur="isFocused = false"
                  ></textarea>
                  
                  <!-- Enhanced Submit button with improved glassmorphism -->
                  <button 
                    type="submit"
                    class="absolute right-3 bottom-3 p-2.5 rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center outline-none focus:outline-none border backdrop-blur-sm"
                    :class="[
                      canSubmit && !isProcessing 
                        ? 'bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 border-indigo-400/20 hover:border-indigo-300/30 shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 text-white hover:scale-105 active:scale-95 transform' 
                        : 'bg-white/5 border-white/10 text-gray-400 scale-95'
                    ]"
                    :disabled="!canSubmit || isProcessing"
                    aria-label="Send message"
                  >
                    <i 
                      class="fas text-sm transition-all duration-200" 
                      :class="isProcessing ? 'fa-spinner fa-spin' : 'fa-paper-plane'"
                    ></i>
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
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
  const minHeight = 48  // Reduced to match the new min-height
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

/* Ultra-premium custom scrollbar for textarea */
textarea {
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.3) transparent;
  transition: height 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  letter-spacing: 0.02em;
  line-height: 1.6;
}

textarea::-webkit-scrollbar {
  width: 6px;
}

textarea::-webkit-scrollbar-track {
  background: transparent;
}

textarea::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, rgba(139, 92, 246, 0.25), rgba(124, 58, 237, 0.3));
  border-radius: 12px;
  border: 1px solid rgba(139, 92, 246, 0.1);
}

textarea::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, rgba(139, 92, 246, 0.4), rgba(124, 58, 237, 0.5));
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

/* Ultra-premium styling for the kbd elements */
kbd {
  display: inline-block;
  line-height: 1.2;
  font-weight: 500;
  font-family: ui-monospace, SFMono-Regular, 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.5);
  transition: all 0.2s ease;
}

/* Enhanced interaction animations */
@keyframes gentle-glow {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 0.8; }
}

.group\/textarea-container:focus-within .blur-lg {
  animation: gentle-glow 2s ease-in-out infinite;
}

/* Premium placeholder animations */
textarea::placeholder {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0.6;
}

textarea:focus::placeholder {
  opacity: 0.4;
  transform: translateY(-1px);
}

/* Enhanced button interactions with sophisticated effects */
.group\/button {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.group\/button:hover {
  transform: scale(1.02) translateY(-0.5px);
}

.group\/button:active {
  transform: scale(0.98) translateY(0);
}

/* Premium hint container interactions */
.group\/hint {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.group\/hint:hover {
  transform: translateY(-1px);
}

/* Enhanced focus states for accessibility */
.group\/textarea-container:focus-within {
  transform: translateY(-0.5px);
}

/* Sophisticated typing indicator animations */
@keyframes sophisticated-typing {
  0%, 100% { opacity: 0.3; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.1); }
}

.animate-sophisticated-typing {
  animation: sophisticated-typing 1.8s ease-in-out infinite;
}

/* Ultra-smooth transitions for all interactive elements */
* {
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}
</style> 