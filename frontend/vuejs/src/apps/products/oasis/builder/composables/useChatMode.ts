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
  const isStreamingSupported = ref(true)

  const sendMessage = async (params: {
    prompt: string
    projectId: string
    file?: any
    mode?: string
    model?: string
    modelId?: string
  }) => {
    const { prompt, projectId, file, mode = 'chat' } = params
    
    // Get model identifier from either model or modelId parameter
    const modelIdentifier = params.model || params.modelId || '';
    
    // Validate required parameters
    if (!modelIdentifier) {
      throw new Error('Model identifier is required')
    }

    // Reset error state
    store.$patch({ error: null, isProcessing: true })

    // Add user message to conversation
    const userMessage = {
      role: 'user' as const,
      content: prompt,
      timestamp: new Date().toISOString()
    }
    store.addMessage(userMessage)

    try {
      // Check if model is an OpenAI model and streaming is supported
      const useStreaming = isStreamingSupported.value && modelIdentifier.includes('gpt')
      
      if (useStreaming) {
        // Create a placeholder message for the assistant
        const tempAssistantMessage = {
          role: 'assistant' as const,
          content: '',
          timestamp: new Date().toISOString()
        }
        
        // Add empty message that we'll update with streaming content
        store.addMessage(tempAssistantMessage)
        
        let streamingContent = ''
        let conversationId: string | null = null
        
        try {
          await AgentService.processChatStream(
            projectId,
            {
              prompt,
              model: modelIdentifier,
              mode,
              file
            },
            // On each chunk
            (chunk) => {
              streamingContent += chunk
              store.updateLastAssistantMessage(streamingContent)
            },
            // On conversation ID
            (id) => {
              conversationId = id
            },
            // On done
            () => {
              // Nothing extra to do here as message is already updated
            },
            // On error
            (error) => {
              // If there's an error in streaming, we'll fall back to non-streaming
              console.error('Error in streaming, falling back to regular API:', error)
              isStreamingSupported.value = false
              
              // Remove the temporary message
              store.removeLastMessage()
              
              // Call regular method
              AgentService.processChat(projectId, {
                prompt,
                model: modelIdentifier,
                mode,
                file
              }).then(response => {
                if (response && response.response) {
                  const assistantMessage = {
                    role: 'assistant' as const,
                    content: response.response,
                    timestamp: new Date().toISOString(),
                    code: response.messages && response.messages[1] && response.messages[1].code
                  }
                  store.addMessage(assistantMessage)
                }
              })
            }
          )
          
          // Return expected response format to maintain compatibility
          return {
            response: streamingContent,
            messages: [
              userMessage,
              {
                role: 'assistant',
                content: streamingContent,
                timestamp: new Date().toISOString()
              }
            ],
            conversation_id: conversationId
          }
        } catch (streamingError) {
          // If streaming fails completely, fall back to regular API
          isStreamingSupported.value = false
          
          // Remove the placeholder message
          store.removeLastMessage()
          
          // Continue to regular API call below
          console.warn('Streaming not supported, falling back to regular API')
        }
      }
      
      // Use regular API if streaming is not supported or failed
      const response = await AgentService.processChat(projectId, {
        prompt,
        model: modelIdentifier,
        mode,
        file
      })

      // Make sure we have a valid response
      if (response && response.response) {
        // Add assistant response to conversation
        const assistantMessage = {
          role: 'assistant' as const,
          content: response.response,
          timestamp: new Date().toISOString(),
          code: response.messages && response.messages[1] && response.messages[1].code
        };
        
        store.addMessage(assistantMessage);
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