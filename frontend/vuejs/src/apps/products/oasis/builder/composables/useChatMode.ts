import { computed, ref } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { AgentService } from '../services/agentService'
import axios from 'axios'

interface ConversationMessage {
  role: 'user' | 'assistant'
  content: string
  code?: string
  timestamp: string
}

export function useChatMode() {
  // Support both old and new store for backward compatibility
  const agentStore = useAgentStore()
  // Use the agent store if available, otherwise fallback to builder store
  const store = agentStore
  
  const credits = ref<number | null>(null)
  const conversationHistory = ref<ConversationMessage[]>([])

  const sendMessage = async (params: {
    prompt: string;
    projectId: string;
    file?: any;
    modelId: string;
  }) => {
    if (!params.modelId) {
      throw new Error('Please select an AI model first')
    }

    store.$patch({ isProcessing: true, error: null })

    try {
      if (!params.projectId) {
        throw new Error('No project selected')
      }

      // Add user message to conversation
      store.addMessage({
        role: 'user',
        content: params.prompt,
        timestamp: new Date().toISOString()
      })

      // Call the agent service
      const response = await AgentService.processChat(params.projectId, {
        prompt: params.prompt,
        model: params.modelId,
        mode: store.mode
      })

      // Add assistant response to conversation
      if (response && response.messages && response.messages.length >= 2) {
        // Extract the assistant message (second element)
        const assistantMessage = response.messages[1];
        
        store.addMessage({
          role: 'assistant',
          content: assistantMessage.content || response.response,
          timestamp: assistantMessage.timestamp || new Date().toISOString(),
          code: assistantMessage.code
        })
      } else if (response && response.response) {
        // Fallback if messages array is not properly structured
        store.addMessage({
          role: 'assistant',
          content: response.response,
          timestamp: new Date().toISOString()
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
        await AgentService.clearConversation(store.projectId)
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
      // This endpoint should match the chat endpoint in the backend
      // Note: We're keeping the query parameter for conversation_id as this may be supported
      // by the backend implementation, even though it wasn't explicitly in the URL pattern
      const response = await axios.get(`/api/v1/agents/chat/?conversation_id=${projectId}`)
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
      // The payments API endpoint should be verified separately, as it's in a different app
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