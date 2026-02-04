<template>
  <div class="h-full flex flex-col relative z-10 transition-colors duration-300" :class="{'mode-transition': disableAllAnimations}">
    <!-- Messages Container -->
    <div ref="messagesContainer" class="flex-grow overflow-y-auto px-4 py-6">
      <!-- Empty state -->
      <div v-if="!processedMessages.length" class="h-full flex flex-col items-center justify-center px-6 py-4 text-center min-h-0">
        <!-- Empty state with no content -->
      </div>
      
      <template v-if="processedMessages.length > 0">
        <div class="space-y-6 max-w-3xl mx-auto">
          <template v-for="(message, index) in processedMessages" :key="`msg-${message.id || index}`">
            <!-- User Message -->
            <div v-if="message.role === 'user'" 
              class="message-block message-user"
              :class="{ 'animate-message-in': message.isNew }" 
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <div class="message-label text-gray-500 dark:text-gray-400">You</div>
              <div class="message-content text-gray-900 dark:text-white">
                <p class="whitespace-pre-wrap break-words text-sm leading-relaxed">{{ message.content }}</p>
              </div>
            </div>
            
            <!-- Assistant Message -->
            <div v-else-if="message.role === 'assistant'" 
              class="message-block message-assistant"
              :class="{ 'animate-message-in': message.isNew }" 
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <div class="message-label text-gray-500 dark:text-gray-400">Imagi</div>
              <div class="message-content">
                <div 
                  class="prose prose-gray dark:prose-invert max-w-none prose-p:my-2 prose-headings:mb-3 prose-headings:mt-4 leading-relaxed text-sm"
                  v-if="message.content && message.content.trim().length > 0"
                  v-html="formatMessage(message.content)"
                />
              </div>
            </div>
            
            <!-- System Message -->
            <div v-else-if="message.role === 'system'" 
              class="flex justify-center my-4" 
              :class="{ 'animate-fade-in': message.isNew }" 
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <span class="text-xs text-gray-400 dark:text-gray-500 px-3 py-1">{{ message.content }}</span>
            </div>
            
            <!-- Other message types -->
            <div v-else 
              class="flex justify-center my-4" 
              :class="{ 'animate-message-in': message.isNew }" 
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <span class="text-xs text-gray-400 dark:text-gray-500 px-3 py-1">{{ message.content }}</span>
            </div>
          </template>
          
          <!-- "AI is typing" indicator -->
          <div v-if="props.isProcessing" class="message-block message-assistant animate-fade-in">
            <div class="message-label text-gray-500 dark:text-gray-400">Imagi</div>
            <div class="message-content">
              <div class="flex items-center gap-3">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span class="text-sm text-gray-500 dark:text-gray-400">{{ mode === 'chat' ? 'Thinking...' : 'Generating...' }}</span>
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
import type { AIMessage } from '@/apps/products/imagi/types/services'
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
      console.log('Code copied to clipboard')
    })
    .catch(err => {
      console.error('Could not copy code:', err)
    })
}
</script>

<style scoped>
/* Clean message block styling */
.message-block {
  padding: 1.25rem 1.5rem;
  margin-left: -1rem;
  margin-right: -1rem;
  border-bottom: none;
}

.message-block:last-child {
  border-bottom: none;
}

/* Alternating backgrounds for user and assistant messages */
.message-user {
  background-color: #ffffff;
}

.dark .message-user {
  background-color: #000000;
}

.message-assistant {
  background-color: #f8fafc;
}

.dark .message-assistant {
  background-color: #1a1a1a;
}

.message-label {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  margin-bottom: 0.5rem;
}

.message-content {
  font-size: 0.875rem;
  line-height: 1.6;
}

/* Prose styling */
.prose {
  font-size: 0.875rem;
  line-height: 1.6;
  color: theme('colors.gray.900');
}

.dark .prose {
  color: theme('colors.gray.100');
}

.prose pre {
  background: theme('colors.gray.100');
  border: 1px solid theme('colors.gray.200');
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1rem 0;
  overflow-x: auto;
}

.dark .prose pre {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.prose code {
  color: theme('colors.gray.800');
  background: theme('colors.gray.100');
  padding: 0.125rem 0.375rem;
  border-radius: 0.375rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  border: 1px solid theme('colors.gray.200');
}

.dark .prose code {
  color: theme('colors.amber.300');
  background: rgba(31, 41, 55, 0.7);
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.prose p {
  margin-bottom: 0.75rem;
}

.prose p:last-child {
  margin-bottom: 0;
}

.prose h1, .prose h2, .prose h3, .prose h4 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: theme('colors.gray.900');
}

.dark .prose h1, .dark .prose h2, .dark .prose h3, .dark .prose h4 {
  color: theme('colors.gray.100');
}

.prose ul, .prose ol {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.prose li {
  margin-bottom: 0.5rem;
}

/* Message animations */
@keyframes message-in {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.animate-message-in {
  animation: message-in 0.3s ease-out forwards;
}

.animate-fade-in {
  animation: fade-in 0.3s ease-out forwards;
}

/* Minimal scrollbar */
.overflow-y-auto {
  scrollbar-width: thin;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.15);
}

:root.dark .overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
}

:root.dark .overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* Typing indicator */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 3px;
}

.typing-indicator span {
  height: 5px;
  width: 5px;
  background: theme('colors.gray.400');
  display: block;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.dark .typing-indicator span {
  background: theme('colors.gray.500');
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
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1.2);
    opacity: 1;
  }
}

/* Prose styling for dark mode */
.prose-invert h1,
.prose-invert h2,
.prose-invert h3,
.prose-invert h4,
.prose-invert h5,
.prose-invert h6 {
  color: theme('colors.gray.100');
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.prose-invert p {
  color: theme('colors.gray.300');
  line-height: 1.6;
  margin-bottom: 0.75rem;
}

.prose-invert p:last-child {
  margin-bottom: 0;
}

.prose-invert strong {
  color: theme('colors.white');
  font-weight: 600;
}

.prose-invert code {
  color: theme('colors.amber.300');
  background-color: rgba(31, 41, 55, 0.7);
  padding: 0.2rem 0.4rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.prose-invert blockquote {
  color: theme('colors.gray.400');
  border-left-color: theme('colors.gray.600');
  border-left-width: 4px;
  padding-left: 1rem;
  font-style: italic;
  margin: 1rem 0;
}

.prose-invert ul,
.prose-invert ol {
  color: theme('colors.gray.300');
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.prose-invert li {
  margin: 0.375rem 0;
  line-height: 1.5;
}

.prose-invert a {
  color: theme('colors.gray.400');
  text-decoration: underline;
  text-decoration-color: rgba(156, 163, 175, 0.4);
}

.prose-invert a:hover {
  color: theme('colors.gray.300');
  text-decoration-color: rgba(209, 213, 219, 0.6);
}
</style> 