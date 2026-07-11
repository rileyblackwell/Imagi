<!--
  ChatMessagesList.vue - Component for displaying the conversation history
  
  This component is responsible for:
  1. Rendering the list of chat messages
  2. Handling loading states for AI responses
  3. Displaying different message types (user vs assistant)
-->
<template>
  <div ref="messagesContainer" class="chat-messages">
    <TransitionGroup name="message-fade">
      <div
        v-for="(message, index) in messages"
        :key="message.timestamp"
        class="message-block"
        :class="message.role === 'user' ? 'message-user' : 'message-assistant'"
      >
        <!-- User Message -->
        <div v-if="message.role === 'user'">
          <div class="message-label text-gray-500 dark:text-gray-400">You</div>
          <div class="message-content text-gray-900 dark:text-white">
            <p class="whitespace-pre-wrap text-sm leading-relaxed">{{ message.content }}</p>
          </div>
        </div>
        
        <!-- Assistant Message -->
        <div v-else>
          <div class="message-label text-gray-500 dark:text-gray-400">Imagi</div>
          <div class="message-content text-gray-900 dark:text-white">
            <p class="whitespace-pre-wrap text-sm leading-relaxed">{{ message.content }}</p>
            
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
    <div v-if="isLoading" class="message-block message-assistant">
      <div class="message-label text-gray-500 dark:text-gray-400">Imagi</div>
      <div class="message-content">
        <div class="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onUpdated, nextTick, ref } from 'vue';
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
.message-block {
  padding: 1.25rem 1.5rem;
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

.message-fade-enter-active,
.message-fade-leave-active {
  transition: all 0.3s ease;
}

.message-fade-enter-from,
.message-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
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
  background: #9ca3af;
  display: block;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.dark .typing-indicator span {
  background: #6b7280;
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
</style> 