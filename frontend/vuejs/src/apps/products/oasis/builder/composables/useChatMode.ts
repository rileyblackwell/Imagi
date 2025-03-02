import { computed, ref } from 'vue'
import { useBuilderStore } from '../stores/builderStore'
import { BuilderAPI } from '../services/api'
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

    store.setProcessing(true)
    store.setError(null)

    try {
      if (!store.projectId) {
        throw new Error('No project selected')
      }

      const response = await BuilderAPI.processChat(store.projectId, {
        prompt: message,
        model: store.selectedModel.id,
        mode: store.mode
      })

      // Add messages to conversation history
      if (response.messages) {
        response.messages.forEach(msg => store.addMessage(msg))
      }

      return response
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to send message'
      store.setError(error)
      throw err
    } finally {
      store.setProcessing(false)
    }
  }

  const clearConversation = async () => {
    try {
      if (store.projectId) {
        await BuilderAPI.clearConversation(store.projectId)
      }
      store.reset()
      conversationHistory.value = []
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to clear conversation'
      store.setError(error)
      throw err
    }
  }

  // Merged from useAI
  const fetchConversationHistory = async (projectId: string) => {
    store.setProcessing(true)
    store.setError(null)

    try {
      const response = await axios.get(`/api/v1/products/oasis/agents/conversations/${projectId}/`)
      conversationHistory.value = response.data.messages || []
      
      // Also update the store conversation if needed
      if (response.data.messages && Array.isArray(response.data.messages)) {
        // Update each message individually instead of using setConversation
        store.reset() // Clear existing messages
        response.data.messages.forEach((msg: AIMessage) => {
          store.addMessage(msg)
        })
      }
    } catch (err) {
      // Set error without console logging
      const error = err instanceof Error ? err.message : 'Failed to fetch conversation history'
      store.setError(error)
    } finally {
      store.setProcessing(false)
    }
  }

  const fetchCredits = async () => {
    try {
      const response = await axios.get('/api/v1/payments/credits/')
      credits.value = response.data.credits
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Failed to fetch credits'
      store.setError(error)
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