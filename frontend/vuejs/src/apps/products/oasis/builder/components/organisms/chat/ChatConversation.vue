<template>
  <div class="h-full flex flex-col relative z-10" :class="{'mode-transition': disableAllAnimations}">
    <!-- Messages Container -->
    <div ref="messagesContainer" class="flex-grow overflow-y-auto p-4 space-y-4" :class="{ 'justify-end': true }">
      <!-- Empty state - Mode specific messages -->
      <div v-if="!processedMessages.length" class="h-full flex flex-col items-center justify-center px-8 py-12 text-center">
        <div class="max-w-lg">
          <div class="mb-6">
            <div class="w-16 h-16 mx-auto bg-primary-500/20 text-primary-400 rounded-full flex items-center justify-center mb-4">
              <i :class="[mode === 'chat' ? 'fas fa-comment-dots text-2xl' : 'fas fa-code-branch text-2xl']"></i>
            </div>
            <h3 class="text-xl font-medium text-white mb-2">
              {{ mode === 'chat' ? 'Start a conversation' : 'Build your application' }}
            </h3>
            <p class="text-gray-400 mb-6">
              {{ mode === 'chat' 
                 ? 'Ask me anything about your project, coding questions, or get help with a specific task.' 
                 : 'Tell me what you want to build, and I\'ll help you create it step by step.' }}
            </p>
          </div>

          <div class="bg-dark-800/60 backdrop-blur rounded-xl p-5 border border-dark-700">
            <h4 class="text-sm font-medium text-gray-300 mb-3">
              {{ mode === 'chat' ? 'Example questions:' : 'Example build commands:' }}
            </h4>
            <div class="space-y-2">
              <div 
                v-for="(example, index) in (mode === 'chat' ? chatExamples : buildExamples)" 
                :key="index"
                class="bg-dark-700/50 px-3 py-2 rounded-lg text-sm text-gray-300 cursor-pointer hover:bg-dark-700 transition-colors"
                @click="$emit('use-example', example)"
              >
                "{{ example }}"
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template v-if="processedMessages.length > 0">
        <div class="space-y-6 max-w-3xl mx-auto pb-4">
          <template v-for="(message, index) in processedMessages" :key="`msg-${message.id || index}`">
            <!-- User Message -->
            <div v-if="message.role === 'user'" class="flex justify-end gap-2 items-end mb-4" 
              :class="{ 'animate-message-in': message.isNew, 'no-animation': !message.isNew }" 
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <!-- User Message Bubble -->
              <div class="max-w-[75%] bg-primary-500 text-white px-4 py-2.5 rounded-2xl rounded-br-md shadow-sm">
                <p class="whitespace-pre-wrap break-words text-sm">{{ message.content }}</p>
                <div class="text-right mt-1">
                  <span class="text-[9px] opacity-70">{{ formatTimestamp(message.timestamp) }}</span>
                </div>
              </div>
              
              <!-- User Avatar - Only show on first message or after AI response -->
              <div 
                v-if="index === 0 || (index > 0 && processedMessages[index-1].role !== 'user')"
                class="shrink-0 w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white shadow-sm"
              >
                <i class="fas fa-user text-xs"></i>
              </div>
              <!-- Empty space placeholder when avatar is hidden -->
              <div v-else class="w-8"></div>
            </div>
            
            <!-- Assistant Message -->
            <div v-else-if="message.role === 'assistant'" class="flex justify-start gap-2 items-start mb-4" 
              :class="{ 'animate-message-in': message.isNew, 'no-animation': !message.isNew }" 
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <!-- AI Avatar - Only show on first message or after user/system response -->
              <div 
                v-if="index === 0 || (index > 0 && processedMessages[index-1].role !== 'assistant')"
                class="shrink-0 w-8 h-8 bg-violet-600 rounded-full flex items-center justify-center text-white shadow-sm mt-1"
              >
                <i class="fas fa-robot text-xs"></i>
              </div>
              <!-- Empty space placeholder when avatar is hidden -->
              <div v-else class="w-8"></div>
              
              <!-- Assistant Message Bubble -->
              <div class="max-w-[75%]">
                <!-- Message container with ChatGPT-like styling -->
                <div class="bg-dark-850 text-gray-100 px-4 py-2.5 rounded-2xl rounded-tl-md shadow-sm">
                  <!-- Content with better markdown rendering -->
                  <div 
                    class="prose prose-invert max-w-none prose-p:my-1 prose-headings:mb-2 prose-headings:mt-3"
                    v-if="message.content && message.content.trim().length > 0"
                    v-html="formatMessage(message.content)"
                  />
                  
                  <!-- Timestamp -->
                  <div class="text-left mt-1">
                    <span class="text-[9px] text-gray-500">{{ formatTimestamp(message.timestamp) }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- System Message - More subtle iMessage-like info bubble -->
            <div v-else-if="message.role === 'system'" class="flex justify-center my-3" 
              :class="{ 'animate-fade-in': message.isNew, 'no-animation': !message.isNew }" 
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <div class="bg-dark-900/60 text-gray-400 px-3 py-1.5 rounded-full text-xs shadow-sm border border-dark-800/30 flex items-center backdrop-blur-sm">
                <div class="mr-1.5 text-blue-400">
                  <i class="fas text-xs" :class="getSystemMessageIcon(message.content)"></i>
                </div>
                <span class="text-gray-400">{{ message.content }}</span>
              </div>
            </div>
            
            <!-- Other message types (if needed) -->
            <div v-else class="flex justify-center mb-4" 
              :class="{ 'animate-message-in': message.isNew, 'no-animation': !message.isNew }" 
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <div class="max-w-[90%] bg-dark-800/70 text-gray-400 px-4 py-2 rounded-full text-xs shadow-sm border border-dark-700/50">
                <span>{{ message.content }}</span>
              </div>
            </div>
          </template>
          
          <!-- "AI is typing" indicator - shown whenever processing is happening -->
          <div v-if="props.isProcessing" 
            class="flex justify-start gap-2 items-start animate-fade-in mb-4"> 
            <div class="shrink-0 w-8 h-8 bg-violet-600 rounded-full flex items-center justify-center text-white shadow-sm">
              <i class="fas fa-robot text-xs"></i>
            </div>
            <div class="bg-dark-850 text-gray-100 px-4 py-3 rounded-2xl rounded-tl-md shadow-sm border border-dark-700/50">
              <div class="flex items-center">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span class="ml-2 text-sm text-gray-300">{{ mode === 'chat' ? 'AI is thinking...' : 'Generating code...' }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import DOMPurify from 'isomorphic-dompurify'
import { ref, onUpdated, nextTick, watch, onMounted, computed } from 'vue'
import type { AIMessage } from '@/apps/products/oasis/builder/types/services'
import { useAgentStore } from '../../../stores/agentStore'

// Extended AIMessage interface to include isNew flag
interface ProcessedMessage extends AIMessage {
  isNew?: boolean;
  isTyping?: boolean;
}

const props = defineProps<{
  messages: AIMessage[]
  isProcessing?: boolean
}>()

const emit = defineEmits<{
  (e: 'apply-code', code: string): void
  (e: 'use-example', example: string): void
}>()

// Refs and reactive state
const messagesContainer = ref<HTMLElement | null>(null)
const isTyping = ref(false)
const previousMessageCount = ref(0)
const previousMode = ref('')
const disableAllAnimations = ref(false)

// Get current mode from agent store
const agentStore = useAgentStore()
const mode = computed(() => agentStore.mode)

// Track mode changes to prevent animation flashing on mode switch
watch(() => mode.value, (newMode, oldMode) => {
  if (newMode !== oldMode) {
    // When mode changes, disable all animations temporarily
    disableAllAnimations.value = true;
    previousMessageCount.value = 9999; // Set to high number to avoid "new" messages
    
    // After a short delay, restore normal animation behavior
    setTimeout(() => {
      previousMessageCount.value = props.messages.length;
      disableAllAnimations.value = false;
    }, 300); // Longer delay to ensure UI has settled
  }
  previousMode.value = newMode;
}, { immediate: true });

// Process messages to add isNew flag for animations
const processedMessages = computed<ProcessedMessage[]>(() => {
  // Skip animation completely during mode transitions or when switching files
  const isInModeTransition = previousMode.value !== mode.value;
  
  return props.messages.map((message, index) => {
    // Check if this is a mode change message by ID
    const isModeChangeMessage = message.id?.includes('system-mode-change-');
    
    // Only mark messages as new if:
    // 1. They're newly added AND
    // 2. Not during mode transition AND
    // 3. Not a mode change message AND
    // 4. Not during global animation disabled state
    const isNew = (index >= previousMessageCount.value) 
      && !isInModeTransition 
      && !isModeChangeMessage
      && !disableAllAnimations.value;
      
    return {
      ...message,
      isNew
    };
  });
});

// Update previousMessageCount after rendering
watch(() => props.messages.length, (newLength) => {
  // Only update the animation state after rendering is complete
  nextTick(() => {
    // Keep track of previous length to identify new messages
    previousMessageCount.value = newLength;
    scrollToBottom();
  });
}, { immediate: true });

// Also scroll on component update
onUpdated(() => {
  nextTick(() => {
    scrollToBottom()
  })
})

// Monitor message changes for content changes too (not just length)
watch(() => JSON.stringify(props.messages), () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })

// When the last message is from the user and there's no AI response yet, show typing indicator
watch(() => props.messages, (messages) => {
  if (messages.length > 0) {
    const lastMessage = messages[messages.length - 1]
    // Only show typing indicator if not currently processing
    isTyping.value = lastMessage.role === 'user' && !props.isProcessing
  } else {
    isTyping.value = false
  }
}, { immediate: true, deep: true })

// Also watch processing state to update typing indicator
watch(() => props.isProcessing, () => {
  if (props.messages.length > 0) {
    const lastMessage = props.messages[props.messages.length - 1]
    // When processing starts, turn off normal typing indicator
    isTyping.value = lastMessage.role === 'user' && !props.isProcessing
  }
})

// Initial scroll when component is mounted
onMounted(() => {
  nextTick(() => {
    // Initialize previous message count
    previousMessageCount.value = props.messages.length;
    scrollToBottom()
  })
})

function scrollToBottom() {
  if (messagesContainer.value) {
    const container = messagesContainer.value
    // Force scroll to bottom with animation
    container.scrollTo({
      top: container.scrollHeight,
      behavior: 'smooth'
    })
  }
}

// Utility functions
const formatTimestamp = (timestamp: string | number) => {
  if (!timestamp) return ''
  
  try {
    const date = typeof timestamp === 'string' ? new Date(timestamp) : new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (e) {
    return ''
  }
}

// Helper function to format markdown content
const formatMessage = (content: string) => {
  if (!content) {
    return '';
  }
  
  try {
    // Remove any code blocks from the content before rendering
    const contentWithoutCode = content.replace(/```[\s\S]*?```/g, '');
    
    // Configure marked options
    marked.setOptions({
      gfm: true,
      breaks: true,
    });

    // Parse markdown with type assurance
    const parsedContent = marked.parse(contentWithoutCode).toString();
    
    // Sanitize the content to prevent XSS
    return DOMPurify.sanitize(parsedContent);
  } catch (e) {
    console.error('Error parsing markdown:', e)
    return content
  }
}

const copyToClipboard = (code: string) => {
  navigator.clipboard.writeText(code)
    .then(() => {
      // You could add a notification here
      console.log('Code copied to clipboard')
    })
    .catch(err => {
      console.error('Could not copy code:', err)
    })
}

const getSystemMessageIcon = (content: string) => {
  if (content.includes('file:') || content.includes('File:')) return 'fa-file-code'
  if (content.includes('mode')) return 'fa-exchange-alt'
  if (content.includes('error') || content.includes('Error')) return 'fa-exclamation-triangle'
  if (content.includes('saved') || content.includes('Saved')) return 'fa-save'
  return 'fa-info-circle'
}

// Chat examples for empty state
const chatExamples = [
  "Can you explain how the routing works in this project?",
  "How can I improve the responsive design of this app?",
  "What's the best way to implement authentication?",
  "How should I structure the CSS for better maintainability?"
]

// Build examples for empty state
const buildExamples = [
  "Add a dark mode toggle to the header component",
  "Create a responsive product grid layout for the home page",
  "Implement a form validation system using Vue's composition API",
  "Build a notification system for user actions"
]
</script>

<style scoped>
.prose {
  font-size: 0.9375rem;
  line-height: 1.6;
}

.prose pre {
  background-color: theme('colors.dark.950');
  border: 1px solid theme('colors.dark.700');
  border-radius: 0.375rem;
  padding: 1rem;
  margin: 1rem 0;
  overflow-x: auto;
}

.prose code {
  color: theme('colors.primary.400');
  background-color: theme('colors.dark.800');
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.prose p {
  margin-bottom: 0.75rem;
}

.prose h1, .prose h2, .prose h3, .prose h4 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: theme('colors.gray.200');
}

.prose ul, .prose ol {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.prose li {
  margin-bottom: 0.5rem;
}

/* Message animation */
@keyframes message-in {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.animate-message-in {
  animation: message-in 0.25s ease-out forwards;
  will-change: opacity, transform;
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out forwards;
  will-change: opacity;
}

/* Add a no-animation class to prevent animations on existing messages */
.no-animation {
  animation: none !important;
  opacity: 1 !important;
  transform: translateY(0) !important;
  transition: none !important;
}

/* Add an ultra-stable class for mode transitions */
.mode-transition * {
  animation: none !important;
  transition: none !important;
  transform: none !important;
  opacity: 1 !important;
}

/* Hide scrollbar but allow scrolling */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.dark.700') transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: theme('colors.dark.700');
  border-radius: 9999px;
}

/* Typing indicator animation */
.typing-indicator {
  display: flex;
  align-items: center;
  margin: 0 0.25rem;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background: #a78bfa; /* Use a brighter violet color */
  display: block;
  border-radius: 50%;
  opacity: 0.7;
  margin: 0 2px;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 100% {
    transform: scale(0.7);
    opacity: 0.5;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.9;
  }
}

/* Code styling */
.language-code {
  color: theme('colors.gray.300');
  background-color: theme('colors.dark.900');
  line-height: 1.5;
}

/* Thinking text animation */
.thinking-text {
  display: inline-block;
  position: relative;
  font-weight: 500;
  color: #d1d5db;
  background: linear-gradient(90deg, rgba(146, 100, 245, 0.2), rgba(146, 100, 245, 0.05));
  padding: 2px 6px;
  border-radius: 4px;
  min-width: 80px;
  text-align: center;
}

.thinking-text:after {
  content: "Thinking";
  animation: thinking-text 2s infinite ease;
}

@keyframes thinking-text {
  0%, 100% { content: "Thinking"; }
  25% { content: "Thinking."; }
  50% { content: "Thinking.."; }
  75% { content: "Thinking..."; }
}
</style> 