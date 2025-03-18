<template>
  <div class="h-full flex flex-col">
    <!-- Messages Container -->
    <div class="flex-1 overflow-y-auto h-full">
      <template v-if="messages && messages.length > 0">
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="py-6 px-4 md:px-8 lg:px-12"
          v-if="message && message.role && message.content"
          :class="[
            message.role === 'assistant' ? 'bg-dark-900' : 'bg-dark-950'
          ]"
        >
          <div class="max-w-3xl mx-auto flex items-start gap-4">
            <!-- Avatar -->
            <div 
              class="shrink-0 w-10 h-10 rounded-full flex items-center justify-center"
              :class="[
                message.role === 'assistant' 
                  ? 'bg-primary-500/20 text-primary-400'
                  : 'bg-violet-500/20 text-violet-400'
              ]"
            >
              <i :class="[
                'fas',
                message.role === 'assistant' ? 'fa-robot' : 'fa-user'
              ]" />
            </div>

            <!-- Message Content -->
            <div class="flex-1 space-y-3">
              <!-- Role Label -->
              <div class="text-sm font-medium flex items-center gap-2 text-gray-400">
                <span>{{ formatRole(message.role) }}</span>
                <span v-if="message.timestamp" class="text-xs text-gray-500">
                  {{ formatTimestamp(message.timestamp) }}
                </span>
              </div>

              <!-- Content -->
              <div 
                class="prose prose-invert max-w-none"
                v-html="formatMessage(message.content)"
              />

              <!-- Code Block with Actions -->
              <div v-if="message.role === 'assistant' && message.code" class="mt-4 border border-dark-700 rounded-lg overflow-hidden">
                <!-- Code Header -->
                <div class="px-4 py-2 bg-dark-800 flex items-center justify-between border-b border-dark-700">
                  <span class="text-sm font-medium text-gray-300">
                    <i class="fas fa-code mr-2"></i>
                    Generated Code
                  </span>
                  <div class="flex items-center gap-2">
                    <button 
                      class="p-1.5 text-gray-400 hover:text-white transition-colors"
                      @click="copyToClipboard(message.code)"
                      title="Copy to clipboard"
                    >
                      <i class="fas fa-copy"></i>
                    </button>
                  </div>
                </div>
                
                <!-- Code Content -->
                <pre class="p-4 bg-dark-850 overflow-x-auto text-sm">
                  <code>{{ message.code }}</code>
                </pre>
                
                <!-- Code Actions -->
                <div class="px-4 py-2 bg-dark-800 border-t border-dark-700">
                  <button
                    class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-colors"
                    @click="$emit('apply-code', message.code)"
                  >
                    <i class="fas fa-magic mr-1.5"></i>
                    Apply Changes
                  </button>
                </div>
              </div>
            </div>
          </div>
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
import type { AIMessage } from '@/apps/products/oasis/builder/types'

const props = defineProps<{
  messages: AIMessage[]
}>()

const emit = defineEmits<{
  (e: 'apply-code', code: string): void
  (e: 'use-example', example: string): void
}>()

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

const formatMessage = (content: string) => {
  if (!content) return ''
  
  try {
    // Configure marked options
    marked.setOptions({
      gfm: true,
      breaks: true,
    })

    // Parse markdown and sanitize HTML
    const parsedContent = marked.parse(content) as string
    
    // Add syntax highlighting classes to code blocks
    const highlightedContent = parsedContent.replace(
      /<pre><code class="language-(\w+)">([\s\S]*?)<\/code><\/pre>/g,
      '<pre class="language-$1"><code>$2</code></pre>'
    );
    
    return DOMPurify.sanitize(highlightedContent)
  } catch (error) {
    console.error('Error formatting message:', error)
    return String(content) // Fallback to raw content
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