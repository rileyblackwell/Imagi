import { computed, ref } from 'vue'
import { useBuilderStore } from '../stores/builderStore'
import { BuilderService } from '../services'
import type { AIMessage } from '../types/api'
import axios from 'axios'

interface ConversationMessage {
  role: 'user' | 'assistant'
  content: string
  code?: string
  timestamp: string
}

export function useChatMode() {
  const store = useBuilderStore()
  const credits = ref<number | null>(null)
  const conversationHistory = ref<ConversationMessage[]>([])

  const sendMessage = async (message: string) => {
    if (!store.selectedModel) {
      throw new Error('Please select an AI model first')
    }

    store.$patch({ isProcessing: true, error: null })

    try {
      if (!store.projectId) {
        throw new Error('No project selected')
      }

      const response = await BuilderService.processChat(store.projectId, {
        prompt: message,
        model: store.selectedModel.id,
        mode: store.mode
      })

      // Add messages to conversation history
      if (response.messages) {
        store.$patch({ 
          conversation: [...store.conversation, ...response.messages] 
        })
      }

      return response
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to send message'
      store.$patch({ error })
      throw err
    } finally {
      store.$patch({ isProcessing: false })
    }
  }

  const clearConversation = async () => {
    try {
      if (store.projectId) {
        await BuilderService.clearConversation(store.projectId)
      }
      store.$reset()
      conversationHistory.value = []
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to clear conversation'
      store.$patch({ error })
      throw err
    }
  }

  // Merged from useAI
  const fetchConversationHistory = async (projectId: string) => {
    store.$patch({ isProcessing: true, error: null })

    try {
      const response = await axios.get(`/api/v1/products/oasis/agents/conversations/${projectId}/`)
      conversationHistory.value = response.data.messages || []
      
      // Also update the store conversation if needed
      if (response.data.messages && Array.isArray(response.data.messages)) {
        // Reset the store and add new messages
        store.$reset()
        store.$patch({ 
          conversation: response.data.messages 
        })
      }
    } catch (err) {
      // Set error without console logging
      const error = err instanceof Error ? err.message : 'Failed to fetch conversation history'
      store.$patch({ error })
    } finally {
      store.$patch({ isProcessing: false })
    }
  }

  const fetchCredits = async () => {
    try {
      const response = await axios.get('/api/v1/payments/credits/')
      credits.value = response.data.credits
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to fetch credits'
      store.$patch({ error })
    }
  }

  return {
    conversation: computed(() => store.conversation),
    conversationHistory: computed(() => conversationHistory.value),
    isProcessing: computed(() => store.isProcessing),
    error: computed(() => store.error),
    credits: computed(() => credits.value),
    sendMessage,
    clearConversation,
    fetchConversationHistory,
    fetchCredits
  }
}