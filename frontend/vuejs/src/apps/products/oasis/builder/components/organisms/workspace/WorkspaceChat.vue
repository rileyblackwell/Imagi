<template>
  <div class="flex-1 flex flex-col overflow-hidden relative h-full min-h-full bg-dark-950 border border-dark-800">
    <!-- Updated background elements for iMessage/ChatGPT-like appearance -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <!-- Clean gradient background -->
      <div class="absolute inset-0 bg-gradient-to-br from-dark-900 to-dark-950"></div>
      
      <!-- Subtle highlight at top -->
      <div class="absolute top-0 left-0 right-0 h-32 bg-gradient-to-b from-primary-600/5 to-transparent"></div>
      
      <!-- Very subtle accent elements -->
      <div class="absolute top-[15%] right-[10%] w-64 h-64 bg-primary-600/3 rounded-full filter blur-3xl"></div>
      <div class="absolute bottom-[25%] left-[8%] w-56 h-56 bg-violet-600/3 rounded-full filter blur-3xl"></div>
    </div>

    <!-- Loading Overlay with improved animation -->
    <div 
      v-if="isProcessing"
      class="absolute inset-0 bg-dark-950/80 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity duration-300"
    >
      <div class="text-center p-6 rounded-xl bg-dark-900/70 backdrop-blur-md border border-dark-800/50 shadow-xl">
        <div class="inline-block w-14 h-14 border-4 border-primary-500/20 border-t-primary-500 rounded-full animate-spin mb-4"></div>
        <p class="text-lg text-white font-medium">Processing...</p>
        <p class="text-sm text-gray-400 mt-1">The AI is crafting a response</p>
      </div>
    </div>

    <!-- Main Flex Area Reorganized to have chat first, then input -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Chat Conversation Area (Main Content) -->
      <div class="flex-1 overflow-auto relative">
        <div class="p-4 h-full">
          <div class="max-w-4xl mx-auto h-full relative z-20">
            <ChatConversation 
              :messages="validatedMessages" 
              @use-example="$emit('use-example', $event)"
              @apply-code="handleApplyCode"
            />
          </div>
        </div>
      </div>

      <!-- AI Input Area (Now at the bottom) -->
      <div 
        class="shrink-0 p-4 border-t border-dark-700/30 bg-dark-900/95 backdrop-blur-md shadow-lg relative z-10"
        :class="{'opacity-80 pointer-events-none filter blur-sm': isProcessing}"
      >
        <!-- Subtle gradient header line -->
        <div class="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-primary-500/30 to-transparent"></div>
        
        <!-- Mode Indicator above the chat input -->
        <div class="max-w-4xl mx-auto mb-4">
          <ModeIndicator 
            :mode="mode" 
            :selected-file="selectedFile" 
            :selected-model-id="selectedModelId"
            :available-models="availableModels"
          />
        </div>
        
        <div class="max-w-4xl mx-auto">
          <ChatInputArea
            v-model="localPrompt"
            :placeholder="promptPlaceholder"
            :focused="true"
            :is-processing="isProcessing"
            :show-examples="false"
            @submit="handleSubmit"
            @examples="$emit('examples')"
          >
            <template #mode-indicator>
              <!-- Empty mode indicator slot since we moved it outside -->
            </template>
          </ChatInputArea>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ChatConversation } from '../../organisms/chat'
import { ChatInputArea } from '../../molecules'
import { ModeIndicator } from '../../molecules/display'
import type { BuilderMode } from '../../../types/components'
import type { AIModel, AIMessage } from '../../../types/services'
import type { SelectedFile } from '../../../types/components'

// Props
const props = defineProps<{
  messages: AIMessage[]
  isProcessing: boolean
  mode: BuilderMode
  selectedFile: SelectedFile | null
  selectedModelId: string | null
  availableModels: AIModel[]
  promptPlaceholder: string
  showExamples: boolean
  promptExamples: Array<{title: string, text: string}> | null
  modelValue: string
}>()

// Ensure all messages have required properties
const validatedMessages = computed(() => {
  if (!props.messages || !Array.isArray(props.messages) || props.messages.length === 0) {
    return []
  }
  
  const processed = props.messages.map(message => {
    // Ensure each message has valid content
    let content = message.content
    
    // Handle potential null or undefined content
    if (content === null || content === undefined) {
      content = '';
    }
    
    // If content is an object rather than a string (can happen with some API responses)
    if (typeof content === 'object') {
      try {
        content = JSON.stringify(content);
      } catch (e) {
        content = String(content);
      }
    }
    
    // Ensure each message has at least role, content, and timestamp
    return {
      role: message.role || 'user',
      content: content || '',
      timestamp: message.timestamp || Date.now(),
      code: message.code || undefined,
      id: message.id || `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    };
  });
  
  return processed;
});

// Emits
const emit = defineEmits([
  'update:modelValue',
  'submit',
  'examples',
  'use-example',
  'apply-code'
])

// Local state
const localPrompt = ref(props.modelValue)

// Watch for external changes
watch(() => props.modelValue, (newValue) => {
  localPrompt.value = newValue
})

// Update parent model
watch(localPrompt, (newValue) => {
  emit('update:modelValue', newValue)
})

// Methods
function handleSubmit() {
  if (!localPrompt.value.trim()) return
  emit('submit')
}

function handleApplyCode(code: string) {
  emit('apply-code', code)
}
</script>

<style scoped>
/* Animation for subtle floating elements */
@keyframes float-slow {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(-20px) translateX(10px); }
}

@keyframes float-slow-reverse {
  0%, 100% { transform: translateY(0) translateX(0); }
  50% { transform: translateY(20px) translateX(-10px); }
}

@keyframes pulse-slow {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.8; }
}

.animate-float-slow {
  animation: float-slow 25s ease-in-out infinite;
}

.animate-float-slow-reverse {
  animation: float-slow-reverse 30s ease-in-out infinite;
}

.animate-pulse-slow {
  animation: pulse-slow 3s ease-in-out infinite;
}

/* Smooth transitions for chat UI */
.flex-1 {
  transition: height 0.3s ease-in-out;
}

/* Improved scrollbar styles */
.overflow-auto {
  scrollbar-width: thin;
  scrollbar-color: theme('colors.dark.700') transparent;
}

.overflow-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-auto::-webkit-scrollbar-track {
  background: transparent;
}

.overflow-auto::-webkit-scrollbar-thumb {
  background-color: theme('colors.dark.700');
  border-radius: 9999px;
}

/* Ensure chat area expands properly */
.flex-col {
  display: flex;
  flex-direction: column;
}

/* Transition effect for message appearance */
@keyframes message-appear {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Ensure the chat container takes full height */
.h-full {
  height: 100%;
  min-height: 0; /* This is important for flex children to respect parent height */
}

/* Fix for overflow issues in chat area */
.overflow-hidden {
  overflow: hidden;
}

.overflow-auto {
  overflow: auto;
}

/* Make sure the main container expands properly */
.flex-1 {
  flex: 1 1 0%;
  min-height: 0; /* Important for Firefox */
}
</style> 