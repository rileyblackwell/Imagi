<template>
  <div class="h-full flex flex-col">
    <!-- Messages Container -->
    <div class="flex-1 overflow-y-auto p-4 space-y-4">
      <template v-if="messages.length > 0">
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="flex items-start space-x-4"
          :class="[
            message.role === 'assistant' ? 'bg-dark-800/50' : '',
            message.role === 'assistant' ? 'p-4 rounded-lg' : 'px-4'
          ]"
        >
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
          <div class="flex-1 space-y-2">
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
            <div v-if="message.role === 'assistant'" class="flex items-center space-x-2">
              <button
                v-if="message.code"
                class="text-xs text-primary-400 hover:text-primary-300 transition-colors"
                @click="$emit('apply-code', message.code)"
              >
                <i class="fas fa-code mr-1" />
                Apply Changes
              </button>
            </div>
          </div>
        </div>
      </template>

      <!-- Empty State -->
      <div v-else class="h-full flex items-center justify-center">
        <div class="text-center space-y-2">
          <div class="text-4xl text-gray-600">
            <i class="fas fa-comments" />
          </div>
          <div class="text-gray-400">
            Start a conversation with your AI assistant
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
}>()

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
    breaks: true
  })

  // Parse markdown and sanitize HTML
  const parsedContent = marked.parse(content) as string
  return DOMPurify.sanitize(parsedContent)
}
</script>

<style scoped>
.prose {
  font-size: 0.875rem;
}

.prose pre {
  background-color: theme('colors.dark.900');
  border: 1px solid theme('colors.dark.700');
  border-radius: 0.375rem;
}

.prose code {
  color: theme('colors.primary.400');
  background-color: theme('colors.dark.900');
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
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