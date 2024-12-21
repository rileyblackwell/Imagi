<template>
  <base-layout>
    <template #hero>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h1 class="text-4xl font-extrabold text-white sm:text-5xl md:text-6xl">
            <span class="block">Build Your Web App</span>
            <span class="block text-primary-400">Using Natural Language</span>
          </h1>
          <p class="mt-3 max-w-md mx-auto text-base text-gray-300 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Describe what you want to build, and let our AI create the code for you.
          </p>
        </div>
      </div>
    </template>

    <template #default>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="bg-dark-800 rounded-lg shadow-xl overflow-hidden">
          <!-- Chat Interface -->
          <div class="h-[600px] flex flex-col">
            <!-- Chat Messages -->
            <div class="flex-1 overflow-y-auto p-4 space-y-4">
              <div v-for="(message, index) in messages" :key="index" 
                   :class="[
                     'flex',
                     message.type === 'user' ? 'justify-end' : 'justify-start'
                   ]">
                <div :class="[
                  'max-w-lg rounded-lg px-4 py-2',
                  message.type === 'user' 
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-700 text-gray-300'
                ]">
                  {{ message.content }}
                </div>
              </div>
            </div>

            <!-- Input Area -->
            <div class="border-t border-dark-700 p-4">
              <form @submit.prevent="sendMessage" class="flex space-x-4">
                <input
                  type="text"
                  v-model="newMessage"
                  placeholder="Describe what you want to build..."
                  class="flex-1 rounded-lg bg-dark-700 border-dark-600 text-white placeholder-gray-400 focus:ring-primary-500 focus:border-primary-500"
                />
                <button
                  type="submit"
                  :disabled="!newMessage.trim() || isLoading"
                  class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
                >
                  <i class="fas fa-paper-plane mr-2"></i>
                  Send
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </template>
  </base-layout>
</template>

<script>
import { ref } from 'vue'
import BaseLayout from '@/shared/layouts/BaseLayout.vue'

export default {
  name: 'Builder',
  components: {
    BaseLayout
  },
  setup() {
    const messages = ref([
      {
        type: 'assistant',
        content: 'Hello! I\'m your AI assistant. Tell me what kind of web application you\'d like to build.'
      }
    ])
    const newMessage = ref('')
    const isLoading = ref(false)

    async function sendMessage() {
      if (!newMessage.value.trim() || isLoading.value) return

      // Add user message
      messages.value.push({
        type: 'user',
        content: newMessage.value
      })

      isLoading.value = true
      try {
        // TODO: Implement actual API call to AI service
        // For now, just echo a response
        await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API delay
        
        messages.value.push({
          type: 'assistant',
          content: 'I understand you want to build something. Let me help you with that.'
        })
      } catch (error) {
        console.error('Failed to get AI response:', error)
        messages.value.push({
          type: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.'
        })
      } finally {
        newMessage.value = ''
        isLoading.value = false
      }
    }

    return {
      messages,
      newMessage,
      isLoading,
      sendMessage
    }
  }
}
</script> 