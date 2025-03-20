import { computed, ref } from 'vue'
import { useAgentStore } from '../stores/agentStore'
import { AgentService } from '../services/agentService'
import axios from 'axios'

interface ConversationMessage {
  role: 'user' | 'assistant' | 'system'
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

      // Debug: Log conversation state before adding message
      // console.log('Chat conversation before user message:', [...store.conversation])

      // Add user message to conversation
      const userMessage = {
        role: 'user' as const,
        content: params.prompt,
        timestamp: new Date().toISOString()
      };
      
      store.addMessage(userMessage);
      
      // Debug: Log conversation state after adding user message
      // console.log('Chat conversation after user message:', [...store.conversation])

      // Call the agent service
      // console.log('Sending chat request to backend with params:', {
      //   prompt: params.prompt,
      //   modelId: params.modelId,
      //   projectId: params.projectId
      // })
      
      const response = await AgentService.processChat(params.projectId, {
        prompt: params.prompt,
        model: params.modelId,
        mode: store.mode
      })

      // Debug: Log the response from the backend
      // console.log('Received chat response from backend:', response)

      // Make sure we have a valid response
      if (response && response.response) {
        // Add assistant response to conversation
        const assistantMessage = {
          role: 'assistant' as const,
          content: response.response,
          timestamp: new Date().toISOString(),
          code: response.messages && response.messages[1] && response.messages[1].code
        };
        
        // console.log('Adding assistant message to conversation:', assistantMessage)
        store.addMessage(assistantMessage);
        
        // Debug: Log conversation state after adding assistant message
        // console.log('Chat conversation after assistant message:', [...store.conversation])
      } else {
        console.error('Invalid response format:', response);
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