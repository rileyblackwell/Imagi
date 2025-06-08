<template>
  <div class="h-full flex flex-col relative z-10" :class="{'mode-transition': disableAllAnimations}">
    <!-- Messages Container -->
    <div ref="messagesContainer" class="flex-grow overflow-y-auto p-6 space-y-4">
      <!-- Empty state - Enhanced sophisticated dark design -->
      <div v-if="!processedMessages.length" class="h-full flex flex-col items-center justify-start px-6 py-4 pt-32 text-center min-h-0">
        <div class="max-w-4xl w-full flex-1 flex flex-col justify-center">
          <div class="mb-6">
            <!-- Enhanced icon container with glassmorphism -->
            <div class="w-12 h-12 mx-auto bg-gradient-to-br from-indigo-500/20 to-violet-500/20 border border-indigo-400/20 rounded-xl flex items-center justify-center mb-4 shadow-lg shadow-indigo-500/10 backdrop-blur-sm">
              <i :class="[mode === 'chat' ? 'fas fa-comment-dots text-lg' : 'fas fa-code-branch text-lg', 'text-indigo-300']"></i>
            </div>
            <h3 class="text-xl font-semibold text-white mb-3 bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
              {{ mode === 'chat' ? 'Start a conversation' : 'Build your application' }}
            </h3>
            <p class="text-gray-300 mb-0 text-sm leading-relaxed max-w-lg mx-auto">
              {{ mode === 'chat' 
                 ? 'Ask me anything about your project, coding questions, or get help with a specific task.' 
                 : 'Tell me what you want to build, and I\'ll help you create it step by step.' }}
            </p>
          </div>

          <!-- Enhanced examples grid with glassmorphism - more compact -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
            <div v-for="(example, index) in (mode === 'chat' ? chatExamples : buildExamples)" :key="index"
                 class="group relative transform transition-all duration-300 hover:-translate-y-1 cursor-pointer"
                 @click="$emit('use-example', example)">
              <!-- Enhanced glassmorphism card -->
              <div class="absolute -inset-0.5 rounded-lg opacity-30 group-hover:opacity-60 bg-gradient-to-r from-indigo-500/30 to-violet-500/30 blur transition-all duration-300"></div>
              <div class="relative rounded-lg border border-white/10 bg-gradient-to-br from-dark-900/90 via-dark-900/80 to-dark-800/90 backdrop-blur-xl shadow-lg shadow-black/20 p-3 text-left transition-all duration-300 hover:border-white/20 hover:shadow-black/30">
                <!-- Sleek gradient header -->
                <div class="h-0.5 w-full bg-gradient-to-r from-indigo-400 via-violet-400 to-indigo-400 opacity-60 rounded-full mb-2"></div>
                
                <!-- Icon -->
                <div class="w-6 h-6 rounded-md bg-gradient-to-br from-indigo-500/20 to-violet-500/20 flex items-center justify-center mb-2 border border-indigo-400/20">
                  <i class="fas fa-lightbulb text-indigo-300 text-xs"></i>
                </div>
                
                <!-- Content -->
                <p class="text-gray-200 text-xs leading-relaxed group-hover:text-white transition-colors">{{ example }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <template v-if="processedMessages.length > 0">
        <div class="space-y-8 max-w-4xl mx-auto pb-4">
          <template v-for="(message, index) in processedMessages" :key="`msg-${message.id || index}`">
            <!-- User Message -->
            <div v-if="message.role === 'user'" class="flex justify-end gap-4 items-end mb-8" 
              :class="{ 'animate-message-in': message.isNew }" 
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <!-- User Message Bubble with enhanced glassmorphism -->
              <div class="relative group max-w-[80%]">
                <!-- Enhanced glow effect -->
                <div class="absolute -inset-0.5 rounded-2xl opacity-40 group-hover:opacity-70 bg-gradient-to-r from-indigo-500/40 to-violet-500/40 blur transition-all duration-300"></div>
                
                <!-- Modern glassmorphism container -->
                <div class="relative rounded-2xl rounded-br-lg border border-white/10 bg-gradient-to-br from-indigo-500/90 via-violet-500/85 to-indigo-600/90 backdrop-blur-xl shadow-2xl shadow-indigo-500/25 overflow-hidden transition-all duration-300 hover:shadow-indigo-500/40">
                  <!-- Sleek gradient header -->
                  <div class="h-0.5 w-full bg-gradient-to-r from-white/40 via-white/60 to-white/40"></div>
                  
                  <!-- Content -->
                  <div class="p-4">
                    <p class="whitespace-pre-wrap break-words text-sm leading-relaxed text-white font-medium">{{ message.content }}</p>
                    <div class="text-right mt-3">
                      <span class="text-xs text-white/80 font-medium">{{ formatTimestamp(message.timestamp) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Enhanced User Avatar -->
              <div 
                v-if="index === 0 || (index > 0 && processedMessages[index-1].role !== 'user')"
                class="shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/90 to-violet-500/90 border border-white/20 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30 backdrop-blur-sm"
              >
                <i class="fas fa-user text-sm"></i>
              </div>
              <div v-else class="w-10"></div>
            </div>
            
            <!-- Assistant Message -->
            <div v-else-if="message.role === 'assistant'" class="flex justify-start gap-4 items-start mb-8" 
              :class="{ 'animate-message-in': message.isNew }" 
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <!-- Enhanced AI Avatar -->
              <div 
                v-if="index === 0 || (index > 0 && processedMessages[index-1].role !== 'assistant')"
                class="shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-gray-600/90 to-gray-700/90 border border-white/20 flex items-center justify-center text-white mt-1 shadow-lg shadow-gray-600/30 backdrop-blur-sm"
              >
                <i class="fas fa-robot text-sm"></i>
              </div>
              <div v-else class="w-10"></div>
              
              <!-- Assistant Message Bubble with enhanced glassmorphism -->
              <div class="max-w-[80%]">
                <div class="relative group">
                  <!-- Enhanced glow effect -->
                  <div class="absolute -inset-0.5 rounded-2xl opacity-30 group-hover:opacity-60 bg-gradient-to-r from-gray-500/30 to-slate-500/30 blur transition-all duration-300"></div>
                  
                  <!-- Modern glassmorphism container -->
                  <div class="relative rounded-2xl rounded-tl-lg border border-white/10 bg-gradient-to-br from-dark-900/95 via-dark-800/90 to-dark-900/95 backdrop-blur-xl shadow-2xl shadow-black/30 overflow-hidden transition-all duration-300 hover:border-white/20 hover:shadow-black/40">
                    <!-- Sleek gradient header -->
                    <div class="h-0.5 w-full bg-gradient-to-r from-gray-400/30 via-slate-400/40 to-gray-400/30"></div>
                    
                    <!-- Subtle background effects -->
                    <div class="absolute -top-16 -right-16 w-32 h-32 bg-gradient-to-br from-gray-400/3 to-slate-400/2 rounded-full blur-2xl opacity-50"></div>
                    
                    <!-- Content -->
                    <div class="relative z-10 p-4">
                      <div 
                        class="prose prose-gray max-w-none prose-p:my-2 prose-headings:mb-3 prose-headings:mt-4 leading-relaxed text-sm prose-invert"
                        v-if="message.content && message.content.trim().length > 0"
                        v-html="formatMessage(message.content)"
                      />
                      
                      <!-- Enhanced Timestamp -->
                      <div class="text-left mt-3">
                        <span class="text-xs text-gray-400 font-medium">{{ formatTimestamp(message.timestamp) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Enhanced System Message -->
            <div v-else-if="message.role === 'system'" class="flex justify-center my-6" 
              :class="{ 'animate-fade-in': message.isNew }" 
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <div class="relative group">
                <!-- Enhanced glow effect -->
                <div class="absolute -inset-0.5 rounded-xl opacity-30 group-hover:opacity-50 bg-gradient-to-r from-amber-500/30 to-orange-500/30 blur transition-all duration-300"></div>
                
                <!-- Modern glassmorphism container -->
                <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-900/80 via-dark-800/75 to-dark-900/80 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden">
                  <!-- Sleek gradient header -->
                  <div class="h-0.5 w-full bg-gradient-to-r from-amber-400/40 via-orange-400/50 to-amber-400/40"></div>
                  
                  <!-- Content -->
                  <div class="px-4 py-3 flex items-center">
                    <div class="w-6 h-6 rounded-lg bg-gradient-to-br from-amber-500/20 to-orange-500/20 flex items-center justify-center mr-3 border border-amber-400/20">
                      <i class="fas text-xs text-amber-400" :class="getSystemMessageIcon(message.content)"></i>
                    </div>
                    <span class="text-sm text-gray-300 font-medium">{{ message.content }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Enhanced Other message types -->
            <div v-else class="flex justify-center mb-6" 
              :class="{ 'animate-message-in': message.isNew }" 
              :style="message.isNew ? { 'animation-delay': `${index * 0.05}s` } : {}">
              <div class="relative group max-w-[90%]">
                <!-- Enhanced glow effect -->
                <div class="absolute -inset-0.5 rounded-xl opacity-30 group-hover:opacity-50 bg-gradient-to-r from-slate-500/30 to-gray-500/30 blur transition-all duration-300"></div>
                
                <!-- Modern glassmorphism container -->
                <div class="relative rounded-xl border border-white/10 bg-gradient-to-br from-dark-900/70 via-dark-800/65 to-dark-900/70 backdrop-blur-xl shadow-lg shadow-black/20 overflow-hidden">
                  <!-- Content -->
                  <div class="px-4 py-3 text-center">
                    <span class="text-sm text-gray-300">{{ message.content }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
          
          <!-- Enhanced "AI is typing" indicator -->
          <div v-if="props.isProcessing" 
            class="flex justify-start gap-4 items-start animate-fade-in mb-8"> 
            <!-- Enhanced AI Avatar -->
            <div class="shrink-0 w-10 h-10 rounded-xl bg-gradient-to-br from-gray-600/90 to-gray-700/90 border border-white/20 flex items-center justify-center text-white shadow-lg shadow-gray-600/30 backdrop-blur-sm">
              <i class="fas fa-robot text-sm"></i>
            </div>
            
            <!-- Enhanced typing indicator container -->
            <div class="relative group">
              <!-- Enhanced glow effect -->
              <div class="absolute -inset-0.5 rounded-2xl opacity-40 group-hover:opacity-70 bg-gradient-to-r from-violet-500/30 to-indigo-500/30 blur transition-all duration-300"></div>
              
              <!-- Modern glassmorphism container -->
              <div class="relative rounded-2xl rounded-tl-lg border border-white/10 bg-gradient-to-br from-dark-900/95 via-dark-800/90 to-dark-900/95 backdrop-blur-xl shadow-2xl shadow-black/30 overflow-hidden">
                <!-- Sleek gradient header -->
                <div class="h-0.5 w-full bg-gradient-to-r from-violet-400/40 via-indigo-400/50 to-violet-400/40"></div>
                
                <!-- Content -->
                <div class="p-4">
                  <div class="flex items-center">
                    <div class="typing-indicator mr-4">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span class="text-sm text-gray-300 font-medium">{{ mode === 'chat' ? 'AI is thinking...' : 'Generating code...' }}</span>
                  </div>
                </div>
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

// Enhanced chat examples for empty state
const chatExamples = [
  "How can I optimize this app's performance and loading speed?",
  "What are the best practices for structuring this application?",
  "Can you review my code architecture and suggest improvements?",
  "How should I handle state management in this project?"
]

// Enhanced build examples for empty state
const buildExamples = [
  "Create a modern dashboard with responsive cards and charts",
  "Add smooth animations and transitions to improve user experience",
  "Build a comprehensive search and filter system",
  "Implement real-time notifications with elegant toast messages"
]
</script>

<style scoped>
.prose {
  font-size: 0.875rem;
  line-height: 1.6;
}

.prose pre {
  background: linear-gradient(to br, rgba(15, 23, 42, 0.8), rgba(15, 23, 42, 0.6));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1rem 0;
  overflow-x: auto;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

.prose code {
  color: theme('colors.indigo.300');
  background: linear-gradient(to br, rgba(139, 92, 246, 0.1), rgba(124, 58, 237, 0.1));
  padding: 0.125rem 0.375rem;
  border-radius: 0.375rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.prose p {
  margin-bottom: 0.75rem;
}

.prose h1, .prose h2, .prose h3, .prose h4 {
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: theme('colors.gray.100');
}

.prose ul, .prose ol {
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.prose li {
  margin-bottom: 0.5rem;
}

/* Enhanced message animations */
@keyframes message-in {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-message-in {
  animation: message-in 0.5s ease-out forwards;
}

.animate-fade-in {
  animation: fade-in 0.4s ease-out forwards;
}

/* Enhanced glassmorphism effects */
.backdrop-blur-xl {
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

/* Improved message container hover effects */
.group:hover .shadow-2xl {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

/* Enhanced border glow animations */
@keyframes border-glow {
  0%, 100% { 
    border-color: rgba(255, 255, 255, 0.1);
  }
  50% { 
    border-color: rgba(255, 255, 255, 0.2);
  }
}

.animate-border-glow {
  animation: border-glow 2s ease-in-out infinite;
}

/* Sophisticated dark scrollbar */
.overflow-y-auto {
  scrollbar-width: thin;
  scrollbar-color: rgba(139, 92, 246, 0.3) transparent;
}

.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, rgba(139, 92, 246, 0.4), rgba(124, 58, 237, 0.3));
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, rgba(139, 92, 246, 0.6), rgba(124, 58, 237, 0.5));
}

/* Enhanced modern typing indicator */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
}

.typing-indicator span {
  height: 6px;
  width: 6px;
  background: linear-gradient(45deg, #8b5cf6, #a855f7);
  display: block;
  border-radius: 50%;
  opacity: 0.4;
  animation: typing 1.6s infinite ease-in-out both;
  box-shadow: 0 0 8px rgba(139, 92, 246, 0.3);
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.3s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.6s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.4;
    box-shadow: 0 0 4px rgba(139, 92, 246, 0.2);
  }
  40% {
    transform: scale(1.3);
    opacity: 1;
    box-shadow: 0 0 12px rgba(139, 92, 246, 0.5);
  }
}

/* Enhanced prose styling for better message formatting */
.prose-invert h1,
.prose-invert h2,
.prose-invert h3,
.prose-invert h4,
.prose-invert h5,
.prose-invert h6 {
  color: #f3f4f6;
  font-weight: 600;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}

.prose-invert p {
  color: #e5e7eb;
  line-height: 1.6;
  margin-bottom: 0.75rem;
}

.prose-invert strong {
  color: #ffffff;
  font-weight: 600;
}

.prose-invert code {
  color: #fbbf24;
  background-color: rgba(31, 41, 55, 0.7);
  padding: 0.2rem 0.4rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  border: 1px solid rgba(251, 191, 36, 0.2);
}

.prose-invert blockquote {
  color: #d1d5db;
  border-left-color: #8b5cf6;
  border-left-width: 4px;
  padding-left: 1rem;
  font-style: italic;
  margin: 1rem 0;
}

.prose-invert ul,
.prose-invert ol {
  color: #e5e7eb;
  margin-left: 1.5rem;
  margin-bottom: 1rem;
}

.prose-invert li {
  margin: 0.375rem 0;
  line-height: 1.5;
}

.prose-invert a {
  color: #a78bfa;
  text-decoration: underline;
  text-decoration-color: rgba(167, 139, 250, 0.4);
}

.prose-invert a:hover {
  color: #c4b5fd;
  text-decoration-color: rgba(196, 181, 253, 0.6);
}
</style> 