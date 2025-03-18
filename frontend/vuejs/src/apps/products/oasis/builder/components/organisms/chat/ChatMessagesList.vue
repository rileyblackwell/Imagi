<!--
  ChatMessagesList.vue - Component for displaying the conversation history
  
  This component is responsible for:
  1. Rendering the list of chat messages
  2. Handling loading states for AI responses
  3. Displaying different message types (user vs assistant)
-->
<template>
  <div ref="messagesContainer" class="chat-messages space-y-4">
    <TransitionGroup name="message-fade">
      <div
        v-for="(message, index) in messages"
        :key="message.timestamp"
        class="message-container"
      >
        <!-- User Message -->
        <div v-if="message.role === 'user'" class="flex justify-end mb-2">
          <div class="user-message max-w-3xl rounded-2xl rounded-tr-sm p-4 bg-blue-500 text-white shadow-sm">
            <div class="chat-text whitespace-pre-wrap">{{ message.content }}</div>
          </div>
        </div>
        
        <!-- Assistant Message -->
        <div v-else class="flex justify-start mb-2">
          <div class="assistant-message max-w-3xl rounded-2xl rounded-tl-sm p-4 bg-white dark:bg-gray-800 shadow-sm">
            <div class="chat-text whitespace-pre-wrap">{{ message.content }}</div>
            
            <!-- Code Block if exists -->
            <div 
              v-if="message.code" 
              class="mt-3 p-3 bg-gray-100 dark:bg-gray-900 rounded-md overflow-x-auto"
            >
              <pre class="text-sm text-gray-800 dark:text-gray-300"><code>{{ message.code }}</code></pre>
            </div>
          </div>
        </div>
      </div>
    </TransitionGroup>
    
    <!-- Loading Indicator -->
    <div v-if="isLoading" class="flex justify-start mb-2">
      <div class="assistant-message max-w-3xl rounded-2xl rounded-tl-sm p-4 bg-white dark:bg-gray-800 shadow-sm">
        <div class="flex space-x-2 items-center">
          <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
          <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-150"></div>
          <div class="w-2 h-2 bg-gray-400 rounded-full animate-pulse delay-300"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, onUpdated, nextTick, ref } from 'vue';
import type { AIMessage } from '../../../types';

const props = defineProps<{
  messages: AIMessage[];
  isLoading: boolean;
}>();

// Auto-scroll to bottom on new messages
const messagesContainer = ref<HTMLElement | null>(null);

onUpdated(() => {
  nextTick(() => {
    if (messagesContainer.value) {
      const container = messagesContainer.value;
      container.scrollTop = container.scrollHeight;
    }
  });
});
</script>

<style scoped>
.message-fade-enter-active,
.message-fade-leave-active {
  transition: all 0.3s ease;
}

.message-fade-enter-from,
.message-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.user-message {
  position: relative;
}

.assistant-message {
  position: relative;
}
</style> 