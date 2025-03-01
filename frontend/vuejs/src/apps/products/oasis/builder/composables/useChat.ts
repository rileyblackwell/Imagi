import { computed } from 'vue'
import { useBuilderStore } from '../stores/builderStore'
import { BuilderAPI } from '../services/api'
import type { AIMessage } from '../types/api'

export function useChat() {
  const store = useBuilderStore()

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
        model: store.selectedModel.id
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

  return {
    conversation: computed(() => store.conversation),
    isProcessing: computed(() => store.isProcessing),
    error: computed(() => store.error),
    sendMessage,
    clearConversation: () => store.reset()
  }
}