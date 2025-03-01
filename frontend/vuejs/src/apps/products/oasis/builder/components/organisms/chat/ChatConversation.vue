<template>
  <div class="h-full flex flex-col">
    <!-- Messages Container -->
    <div class="flex-1 overflow-y-auto">
      <template v-if="messages.length > 0">
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="py-6 px-4 md:px-8 lg:px-12"
          :class="[
            message.role === 'assistant' ? 'bg-dark-900' : 'bg-dark-950'
          ]"
        >
          <div class="max-w-3xl mx-auto flex items-start gap-4">
            <!-- Avatar -->
            <div 
              class="shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
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
              <div class="text-sm font-medium text-gray-400">
                {{ formatRole(message.role) }}
              </div>

              <!-- Content -->
              <div 
                class="prose prose-invert max-w-none"
                v-html="formatMessage(message.content)"
              />

              <!-- Actions -->
              <div v-if="message.role === 'assistant' && message.code" class="flex items-center space-x-2 mt-4">
                <button
                  class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md bg-primary-500/20 text-primary-400 hover:bg-primary-500/30 transition-colors"
                  @click="$emit('apply-code', message.code)"
                >
                  <i class="fas fa-code mr-1.5" />
                  Apply Changes
                </button>
                <button
                  class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md bg-dark-800 text-gray-400 hover:bg-dark-700 transition-colors"
                  @click="copyToClipboard(message.code)"
                >
                  <i class="fas fa-copy mr-1.5" />
                  Copy Code
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Empty State -->
      <div v-else class="h-full flex items-center justify-center">
        <div class="text-center space-y-4 max-w-md px-4">
          <div class="text-5xl text-gray-600 mb-6">
            <i class="fas fa-robot" />
          </div>
          <h3 class="text-xl font-medium text-gray-300">
            Welcome to Imagi Oasis
          </h3>
          <p class="text-gray-400">
            Start a conversation with your AI assistant to build your web application. You can ask questions or describe what you want to build.
          </p>
          <div class="pt-4">
            <div v-for="(example, i) in examples" :key="i" class="mb-2">
              <button
                class="w-full text-left p-3 rounded-lg bg-dark-800 hover:bg-dark-700 text-gray-300 text-sm transition-colors"
                @click="$emit('use-example', example)"
              >
                "{{ example }}"
              </button>
            </div>
          </div>
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
const examples = [
  "Create a simple todo list app with Vue.js",
  "How do I implement user authentication in my app?",
  "Generate a responsive navigation menu component"
]

// Utility functions
const formatRole = (role: string) => {
  const roles: Record<string, string> = {
    'user': 'You',
    'assistant': 'AI Assistant',
    'system': 'System'
  }
  return roles[role] || role
}

const formatMessage = (content: string) => {
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