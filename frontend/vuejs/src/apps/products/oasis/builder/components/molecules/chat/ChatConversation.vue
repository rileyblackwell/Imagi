<!-- Chat Conversation Component -->
<template>
  <div class="flex flex-col space-y-6 p-4 overflow-y-auto">
    <TransitionGroup 
      name="fade"
      tag="div"
      class="flex flex-col space-y-6"
    >
      <div v-for="(message, index) in messages" 
           :key="message.timestamp + index" 
           class="flex flex-col"
      >
        <!-- User Message -->
        <div v-if="message.role === 'user'" 
             class="flex justify-end mb-2"
        >
          <div class="flex items-end space-x-2">
            <div class="text-xs text-gray-500 self-end pb-1">You</div>
            <div class="bg-primary-600/20 text-white rounded-2xl rounded-br-sm px-4 py-3 max-w-[80%] break-words shadow-sm">
              <div class="whitespace-pre-wrap">{{ message.content }}</div>
            </div>
          </div>
        </div>
        
        <!-- Assistant Message -->
        <div v-else-if="message.role === 'assistant'" 
             class="flex justify-start mb-2"
        >
          <div class="flex items-end space-x-2">
            <div class="flex flex-col items-center space-y-1">
              <div class="w-8 h-8 rounded-full bg-primary-500/20 flex items-center justify-center text-primary-400">
                <i class="fas fa-robot text-sm"></i>
              </div>
              <div class="text-xs text-gray-500">Imagi</div>
            </div>
            <div class="bg-dark-800 text-white rounded-2xl rounded-bl-sm px-4 py-3 max-w-[80%] shadow-sm">
              <div v-if="message.code" class="mb-3">
                <pre class="bg-dark-900 p-3 rounded-lg overflow-x-auto text-sm border border-dark-700/50">
                  <code>{{ message.code }}</code>
                </pre>
              </div>
              <div class="whitespace-pre-wrap break-words">{{ message.content }}</div>
            </div>
          </div>
        </div>
      </div>
    </TransitionGroup>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="flex justify-start mb-2">
      <div class="flex items-end space-x-2">
        <div class="flex flex-col items-center space-y-1">
          <div class="w-8 h-8 rounded-full bg-primary-500/20 flex items-center justify-center text-primary-400">
            <i class="fas fa-robot text-sm"></i>
          </div>
          <div class="text-xs text-gray-500">Imagi</div>
        </div>
        <div class="bg-dark-800 text-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
          <div class="flex items-center space-x-2">
            <div class="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
            <div class="w-2 h-2 bg-primary-500 rounded-full animate-pulse" style="animation-delay: 0.2s"></div>
            <div class="w-2 h-2 bg-primary-500 rounded-full animate-pulse" style="animation-delay: 0.4s"></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AIMessage } from '@/apps/products/oasis/builder/types'

defineProps<{
  messages: AIMessage[]
  isLoading?: boolean
}>()

defineEmits<{
  (e: 'use-example', prompt: string): void
}>()
</script>

<style scoped>
.fade-move,
.fade-enter-active,
.fade-leave-active {
  transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(30px);
}

.fade-leave-active {
  position: absolute;
}

/* Custom scrollbar */
:deep(.overflow-y-auto::-webkit-scrollbar) {
  width: 6px;
}

:deep(.overflow-y-auto::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(.overflow-y-auto::-webkit-scrollbar-thumb) {
  background-color: theme('colors.dark.700');
  border-radius: 9999px;
}

:deep(.overflow-y-auto::-webkit-scrollbar-thumb:hover) {
  background-color: theme('colors.dark.600');
}
</style>