import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { AgentService } from '../services/agentService'
import { v4 as uuidv4 } from 'uuid'
import { useAuthStore } from '@/shared/stores/auth'
import { notify } from '@/shared/utils'

interface Message {
  id: string
  role: string
  content: string
  timestamp: string
  isStreaming?: boolean
}

interface Conversation {
  id: string
  messages: Message[]
}

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

      // Process streaming response
      const success = await AgentService.processChatStream(
        message,
        modelId,
        validProjectId,
        {
          conversationId: options.conversationId,
          mode: options.mode,
          currentFile: options.currentFile,
          callbacks: {
            onContent: (content: string) => {
              if (conversation.value) {
                const lastMsg = conversation.value.messages[conversation.value.messages.length - 1];
                if (lastMsg.role === 'assistant') {
                  lastMsg.content += content;
                }
              }
            },
            onConversationId: (id: string) => {
              if (!options.conversationId) {
                conversation.value = createConversation(id);
                conversation.value.messages.push(userMessage);
                conversation.value.messages.push(tempMessage);
              }
            },
            onDone: () => {
              // Mark as no longer streaming
              if (conversation.value) {
                const lastMsg = conversation.value.messages[conversation.value.messages.length - 1];
                if (lastMsg.role === 'assistant') {
                  lastMsg.isStreaming = false;
                }
              }
              isProcessing.value = false;
            },
            onError: (errorMessage: string) => {
              // Remove the temporary message
              if (conversation.value) {
                conversation.value.messages = conversation.value.messages.filter(msg => !msg.isStreaming);
              }
              
              // Format and handle specific types of errors for better UX
              if (errorMessage.includes('need more credits')) {
                // Extract needed amount from error message if possible
                const match = errorMessage.match(/need\s+([0-9.]+)\s+more\s+credits/i);
                const amount = match ? match[1] : '0.00';
                
                const formattedError = `Insufficient credits: You need $${amount} more to use ${modelId}. Please add more credits.`;
                error.value = formattedError;
                notify({ 
                  type: 'error', 
                  message: formattedError,
                  duration: 7000
                });
              } 
              else if (errorMessage.includes('insufficient_credits') || errorMessage.includes('Insufficient credits')) {
                error.value = `Insufficient credits to use ${modelId}. Please add more credits.`;
                notify({ 
                  type: 'error', 
                  message: `Insufficient credits to use ${modelId}. Please add more credits.`,
                  duration: 7000
                });
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
            }
          }
        }
      );
      
      if (!success) {
        // If streaming failed, remove the temporary message and handle error
        if (conversation.value) {
          conversation.value.messages = conversation.value.messages.filter(msg => !msg.isStreaming);
        }
        
        if (!error.value) {
          error.value = 'Failed to process your message. Please try again.';
          notify({ 
            type: 'error', 
            message: 'Failed to process your message. Please try again.',
            duration: 5000
          });
        }
      }
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