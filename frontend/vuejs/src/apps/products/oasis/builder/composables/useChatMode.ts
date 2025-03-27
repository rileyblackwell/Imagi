import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { AgentService } from '../services/agentService'
import { v4 as uuidv4 } from 'uuid'
import { useAuthStore } from '@/shared/stores/auth'
import { useBalanceStore } from '@/shared/stores/balance'
import { notify } from '@/shared/utils'
import type { Message, Conversation } from '../types/composables'

export default function useChatMode() {
  const route = useRoute()
  const conversation = ref<Conversation | null>(null)
  const error = ref<string | null>(null)
  const isProcessing = ref(false)
  const streamingSupported = ref(true)
  
  const createConversation = (id: string): Conversation => {
    return {
      id,
      messages: []
    }
  }

  const sendMessage = async (
    message: string,
    modelId: string,
    projectId: string,
    options: {
      conversationId?: string,
      mode?: string,
      currentFile?: any
    } = {}
  ) => {
    // Get balance store for refreshing credits
    const balanceStore = useBalanceStore()
    
    // Validate project ID - default to "default-project" if not provided
    const validProjectId = projectId || 'default-project';
    
    if (!message || !modelId) {
      error.value = 'Please provide both a message and a model';
      return;
    }
  
    if (isProcessing.value) {
      error.value = 'Already processing a message';
      return;
    }

    isProcessing.value = true;
    error.value = null;

    // Create conversation if needed
    if (!conversation.value || (options.conversationId && options.conversationId !== conversation.value.id)) {
      conversation.value = createConversation(options.conversationId || 'new');
    }

    // Add user message
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    conversation.value.messages.push(userMessage);
    
    // Immediately fetch balance before request to get current value
    await balanceStore.fetchBalance(false)

    try {
      // Add temporary message for streaming
      const tempMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString(),
        isStreaming: true
      };
      
      if (conversation.value) {
        conversation.value.messages.push(tempMessage);
      }

      // Prepare payload for streaming request
      const chatPayload: {
        message: string;
        model: string;
        project_id: string;
        conversation_id?: string;
        mode: string;
        current_file?: any;
        provider?: string;
      } = {
        message: message,
        model: modelId,
        project_id: validProjectId,
        conversation_id: options.conversationId,
        mode: options.mode || 'chat',
        current_file: options.currentFile
      };

      // Check if it's an OpenAI or Anthropic model and add provider info
      // This helps the backend identify the correct provider to use
      if (modelId.includes('gpt')) {
        chatPayload['provider'] = 'openai';
      } else if (modelId.includes('claude')) {
        chatPayload['provider'] = 'anthropic';
      }

      // Process streaming response
      await AgentService.processChatStream(
        chatPayload,
        // onChunk callback
        (content: string) => {
          if (conversation.value) {
            const lastMsg = conversation.value.messages[conversation.value.messages.length - 1];
            if (lastMsg.role === 'assistant') {
              // Ensure content is always a string before appending
              lastMsg.content += content ? String(content) : '';
            }
          }
        },
        // onError callback
        (errorMessage: string) => {
          // Remove the temporary message
          if (conversation.value) {
            conversation.value.messages = conversation.value.messages.filter(msg => !msg.isStreaming);
          }
          
          // Format and handle specific types of errors for better UX
          if (errorMessage.includes('need more credits')) {
            // Extract needed amount from error message if possible
            const match = errorMessage.match(/need\s+\$?([0-9.]+)\s+more/i);
            const amount = match ? match[1] : '0.00';
            
            const formattedError = `Insufficient credits: You need $${amount} more to use ${modelId}. Please add more credits.`;
            error.value = formattedError;
            notify({ 
              type: 'error', 
              message: formattedError,
              duration: 7000
            });
            
            // Refresh balance after error to ensure it's current
            balanceStore.fetchBalance(false)
          } 
          else if (errorMessage.includes('insufficient_credits') || errorMessage.includes('Insufficient credits')) {
            error.value = `Insufficient credits to use ${modelId}. Please add more credits.`;
            notify({ 
              type: 'error', 
              message: `Insufficient credits to use ${modelId}. Please add more credits.`,
              duration: 7000
            });
            
            // Refresh balance after error to ensure it's current
            balanceStore.fetchBalance(false)
          }
          else if (errorMessage.includes('401') || errorMessage.includes('403')) {
            error.value = 'Authentication error. Please log in again.';
            // Try to refresh auth token
            try {
              const authStore = useAuthStore();
              if (authStore) {
                authStore.validateAuth();
              }
            } catch (e) {
              console.error('Failed to refresh auth token:', e);
            }
            
            notify({ 
              type: 'error', 
              message: 'Authentication error. Please log in again.',
              duration: 5000
            });
          }
          else if (errorMessage.includes('500')) {
            error.value = 'Server error occurred. Please try again later.';
            notify({ 
              type: 'error', 
              message: 'Server error occurred. Please try again later.',
              duration: 5000
            });
          }
          else {
            // Default error case
            error.value = errorMessage;
            notify({ 
              type: 'error', 
              message: 'Error: ' + errorMessage,
              duration: 5000
            });
          }
          
          isProcessing.value = false;
        },
        // onDone callback
        () => {
          // Mark as no longer streaming
          if (conversation.value) {
            const lastMsg = conversation.value.messages[conversation.value.messages.length - 1];
            if (lastMsg.role === 'assistant') {
              lastMsg.isStreaming = false;
              
              // Ensure message content is valid before finishing
              if (lastMsg.content === null || lastMsg.content === undefined) {
                lastMsg.content = '';
              }
              if (typeof lastMsg.content === 'object') {
                try {
                  lastMsg.content = JSON.stringify(lastMsg.content);
                } catch (e) {
                  lastMsg.content = String(lastMsg.content);
                }
              }
            }
          }
          isProcessing.value = false;
          
          // After completion, refresh balance to reflect the usage cost
          balanceStore.fetchBalance(false)
        },
        // onConversationId callback
        (id: string) => {
          if (!options.conversationId) {
            conversation.value = createConversation(id);
            conversation.value.messages.push(userMessage);
            conversation.value.messages.push(tempMessage);
          }
        }
      );
    } catch (e) {
      console.error('Error in chat:', e);
      error.value = e instanceof Error ? e.message : 'Unknown error occurred';
      
      // Remove temporary streaming message if exists
      if (conversation.value) {
        conversation.value.messages = conversation.value.messages.filter(msg => !msg.isStreaming);
      }
      
      notify({ 
        type: 'error', 
        message: error.value,
        duration: 5000
      });
    } finally {
      isProcessing.value = false;
    }
  };

  return {
    conversation,
    error,
    isProcessing,
    streamingSupported,
    createConversation,
    sendMessage
  }
}