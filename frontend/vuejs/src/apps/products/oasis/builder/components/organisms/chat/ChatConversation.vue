<template>
  <div class="h-full flex flex-col relative z-10">
    <!-- Messages Container -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto h-full px-4 py-4 pb-2 absolute inset-0">
      <!-- Debug message count display (enabled for troubleshooting) -->
      <div v-if="messages && messages.length > 0" class="mb-4 p-2 bg-dark-700 rounded text-xs sticky top-0 z-10 shadow-md">
        <p>Debug: {{ messages.length }} messages in chat</p>
        <p v-for="(message, i) in messages" :key="i" class="mt-1">
          Message {{ i + 1 }}: {{ message.role }} - {{ message.content ? message.content.substring(0, 30) : 'Empty' }}...
        </p>
      </div>
      
      <template v-if="messages && messages.length > 0">
        <div class="space-y-6 max-w-3xl mx-auto">
          <template v-for="(message, index) in messages" :key="`msg-${message.timestamp}-${index}`">
            <!-- User Message -->
            <div v-if="message.role === 'user'" class="flex justify-end gap-3 items-end mb-6 animate-message-in">
              <!-- User Message Bubble -->
              <div class="max-w-[80%] bg-primary-500 text-white px-4 py-3 rounded-2xl rounded-br-sm shadow-lg">
                <p class="whitespace-pre-wrap break-words text-sm">{{ message.content }}</p>
              </div>
              
              <!-- User Avatar -->
              <div class="shrink-0 w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center text-white shadow-md">
                <i class="fas fa-user text-sm"></i>
              </div>
            </div>
            
            <!-- Assistant Message -->
            <div v-else-if="message.role === 'assistant'" class="flex justify-start gap-3 items-end mb-6 animate-message-in">
              <!-- AI Avatar -->
              <div class="shrink-0 w-8 h-8 bg-violet-500 rounded-full flex items-center justify-center text-white shadow-md">
                <i class="fas fa-robot text-sm"></i>
              </div>
              
              <!-- Assistant Message Bubble -->
              <div class="max-w-[80%] bg-dark-800 text-gray-100 px-4 py-3 rounded-2xl rounded-bl-sm shadow-lg">
                <!-- Content -->
                <div 
                  class="prose prose-invert max-w-none"
                  v-if="message.content && message.content.trim().length > 0"
                  v-html="formatMessage(message.content)"
                />
                <div v-else class="text-gray-400 italic">
                  [Empty response]
                </div>
                
                <!-- Code Block with Actions -->
                <div v-if="message.code" class="mt-4 border border-dark-700 rounded-lg overflow-hidden shadow-sm">
                  <!-- Code Header -->
                  <div class="px-3 py-1.5 bg-dark-850 flex items-center justify-between border-b border-dark-700">
                    <span class="text-xs font-medium text-gray-300">
                      <i class="fas fa-code mr-1.5"></i>
                      Generated Code
                    </span>
                    <button 
                      class="p-1 text-xs text-gray-400 hover:text-white transition-colors"
                      @click="copyToClipboard(message.code)"
                      title="Copy to clipboard"
                    >
                      <i class="fas fa-copy"></i>
                    </button>
                  </div>
                  
                  <!-- Code Content -->
                  <pre class="p-3 bg-dark-900 overflow-x-auto text-xs">
                    <code>{{ message.code }}</code>
                  </pre>
                  
                  <!-- Code Actions -->
                  <div class="px-3 py-1.5 bg-dark-850 border-t border-dark-700">
                    <button
                      class="inline-flex items-center px-2 py-1 text-xs font-medium rounded bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-colors"
                      @click="$emit('apply-code', message.code)"
                    >
                      <i class="fas fa-magic mr-1.5"></i>
                      Apply Changes
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </template>

      <!-- Empty State with AI Chat Illustration -->
      <div v-else class="h-full flex items-center justify-center">
        <div class="text-center space-y-6 max-w-md px-4">
          <!-- AI Assistant Illustration -->
          <div class="relative mx-auto w-24 h-24">
            <div class="absolute inset-0 bg-primary-500/20 rounded-full animate-pulse"></div>
            <div class="relative flex items-center justify-center w-full h-full">
              <i class="fas fa-robot text-5xl text-primary-400"></i>
            </div>
          </div>
          
          <h3 class="text-xl font-medium text-gray-200">
            Welcome to Imagi Oasis
          </h3>
          <p class="text-gray-400">
            Start a conversation with your AI assistant to build your web application. You can ask questions or describe what you want to build.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import DOMPurify from 'isomorphic-dompurify'
import { ref, onUpdated, nextTick, watch, onMounted } from 'vue'
import type { AIMessage } from '@/apps/products/oasis/builder/types/api'

const props = defineProps<{
  messages: AIMessage[]
}>()

const emit = defineEmits<{
  (e: 'apply-code', code: string): void
  (e: 'use-example', example: string): void
}>()

// Ref for the message container to enable auto-scrolling
const messagesContainer = ref<HTMLElement | null>(null)

// Auto-scroll to bottom when messages change
watch(() => props.messages.length, () => {
  nextTick(() => {
    scrollToBottom()
  })
})

// Also scroll on component update
onUpdated(() => {
  nextTick(() => {
    scrollToBottom()
  })
})

// Debug: Log messages when they change
watch(() => props.messages, (newMessages) => {
  // console.log('ChatConversation: Messages updated:', newMessages)
}, { immediate: true, deep: true })

// Mount debugging
onMounted(() => {
  // console.log('ChatConversation: Component mounted, initial messages:', props.messages)
})

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Example prompts
const examples = []

// Utility functions
const formatRole = (role: string) => {
  const roles: Record<string, string> = {
    'user': 'You',
    'assistant': 'AI Assistant',
    'system': 'System'
  }
  return roles[role] || role
}

const formatTimestamp = (timestamp: string | number) => {
  if (!timestamp) return ''
  
  try {
    const date = typeof timestamp === 'string' ? new Date(timestamp) : new Date(timestamp)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch (e) {
    return ''
  }
}

const formatMessage = (content: string | any) => {
  if (!content) {
    // console.log('formatMessage: Empty content received');
    return '';
  }
  
  // console.log('formatMessage: Processing content:', typeof content, content);
  
  try {
    // If content is an object, extract the text content
    const textContent = typeof content === 'object' ? 
      (content.content || JSON.stringify(content)) : 
      content;
    
    // console.log('formatMessage: Extracted text content:', textContent);
    
    // Configure marked options
    marked.setOptions({
      gfm: true,
      breaks: true,
    });

    // Parse markdown and sanitize HTML
    const parsedContent = marked.parse(textContent) as string;
    // console.log('formatMessage: Parsed markdown content:', parsedContent.substring(0, 100) + '...');
    
    // Add syntax highlighting classes to code blocks
    const highlightedContent = parsedContent.replace(
      /<pre><code class="language-(\w+)">([\s\S]*?)<\/code><\/pre>/g,
      '<pre class="language-$1"><code>$2</code></pre>'
    );
    
    const sanitizedContent = DOMPurify.sanitize(highlightedContent);
    // console.log('formatMessage: Final sanitized content:', sanitizedContent.substring(0, 100) + '...');
    
    return sanitizedContent;
  } catch (error) {
    console.error('Error formatting message:', error);
    // Return string representation of content as fallback
    return typeof content === 'object' ? 
      (content.content || JSON.stringify(content)) : 
      String(content);
  }
}

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text)
    // Could add a notification here
  } catch (err) {
    console.error('Failed to copy text: ', err)
  }
}
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
  0% { opacity: 0; transform: translateY(10px); }
  100% { opacity: 1; transform: translateY(0); }
}

.animate-message-in {
  animation: message-in 0.3s ease-out forwards;
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
</style> 