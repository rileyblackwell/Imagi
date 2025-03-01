<!-- Chat Conversation Component -->
<template>
  <div class="flex flex-col space-y-4 p-4 overflow-y-auto">
    <TransitionGroup 
      name="fade"
      tag="div"
      class="flex flex-col space-y-4"
    >
      <div v-for="(message, index) in messages" 
           :key="message.timestamp + index" 
           class="flex flex-col"
      >
        <!-- User Message -->
        <div v-if="message.role === 'user'" 
             class="flex justify-end mb-4"
        >
          <div class="bg-primary-500/20 text-white rounded-lg p-3 max-w-[80%] break-words">
            {{ message.content }}
          </div>
        </div>
        
        <!-- Assistant Message -->
        <div v-else-if="message.role === 'assistant'" 
             class="flex justify-start mb-4"
        >
          <div class="bg-dark-700 text-white rounded-lg p-3 max-w-[80%]">
            <div v-if="message.code" class="mb-2">
              <pre class="bg-dark-800 p-2 rounded overflow-x-auto">
                <code class="text-sm">{{ message.code }}</code>
              </pre>
            </div>
            <div class="whitespace-pre-wrap break-words">{{ message.content }}</div>
          </div>
        </div>
      </div>
    </TransitionGroup>

    <!-- Loading Indicator -->
    <div v-if="isLoading" class="flex justify-start mb-4">
      <div class="bg-dark-700 text-white rounded-lg p-3">
        <div class="flex items-center space-x-2">
          <div class="w-2 h-2 bg-primary-500 rounded-full animate-bounce"></div>
          <div class="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
          <div class="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AIMessage } from '../../types'

defineProps<{
  messages: AIMessage[]
  isLoading?: boolean
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
</style>