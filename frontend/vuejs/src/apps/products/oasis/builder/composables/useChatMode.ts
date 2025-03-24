import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { AgentService } from '../services/agentService'
import { v4 as uuidv4 } from 'uuid'
import { useAuthStore } from '@/shared/stores/auth'

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
  
  const fallbackToRegularApiCall = async (
    message: string,
    modelId: string,
    projectId: string,
    options: {
      conversationId?: string,
      mode?: string,
      currentFile?: any
    } = {}
  ) => {
    try {
      isProcessing.value = true;
      const { mode = 'chat', currentFile } = options;
      
      console.log('Using regular API call with:', { 
        message, 
        model: modelId, 
        projectId,
        mode,
        hasCurrentFile: !!currentFile
      });
      
      // Match the interface expected by processChat
      const response = await AgentService.processChat(projectId, {
        prompt: message,
        model: modelId,
        mode,
        file: currentFile
      });
      
      if (response && response.response) {
        if (!conversation.value || (options.conversationId !== conversation.value.id)) {
          // Create a new conversation with the ID from options or a new one
          conversation.value = createConversation(options.conversationId || 'new');
        }
        
        // Add assistant response
        const assistantMessage: Message = {
          id: uuidv4(),
          role: 'assistant',
          content: response.response,
          timestamp: new Date().toISOString()
        };
        
        conversation.value.messages.push(assistantMessage);
        error.value = null;
      } else {
        error.value = 'No response received from the API';
        console.error('Chat API error: No response received');
      }
    } catch (e) {
      console.error('Error in regular chat API call:', e);
      error.value = e instanceof Error ? e.message : 'Unknown error occurred';
      
      // If there's a conversation with a streaming message that failed, remove it
      if (conversation.value) {
        conversation.value.messages = conversation.value.messages.filter(msg => !msg.isStreaming);
      }
    } finally {
      isProcessing.value = false;
    }
  };

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
      // Use streaming if supported
      if (streamingSupported.value) {
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
                  console.warn('Streaming error:', errorMessage);
                  error.value = errorMessage;
                  
                  // If we got a tuple object error, try disabling streaming for this session
                  if (errorMessage.includes('tuple') && errorMessage.includes('attribute')) {
                    console.warn('Disabling streaming due to tuple attribute error');
                    streamingSupported.value = false;
                  }
                  
                  // If we got an HTML response, this is likely a 500 error from Django
                  if (errorMessage.includes('<!DOCTYPE html>') || errorMessage.includes('<html>')) {
                    console.warn('Received HTML response instead of JSON, likely a server error');
                    error.value = 'Server error occurred. Please try again.';
                    streamingSupported.value = false;
                  }
                  
                  // If we get a HTTP error status, handle appropriately
                  if (errorMessage.includes('HTTP error') || errorMessage.includes('status code')) {
                    console.warn('HTTP error during streaming');
                    
                    // Status 400 often means invalid request parameters
                    if (errorMessage.includes('400')) {
                      error.value = 'Invalid request. Please check your input and try again.';
                    }
                    // Status 401/403 means authentication/permission issues
                    else if (errorMessage.includes('401') || errorMessage.includes('403')) {
                      error.value = 'Authentication error. Please log in again.';
                      // Try to refresh auth token
                      try {
                        const authStore = useAuthStore()
                        if (authStore) {
                          authStore.validateAuth()
                        }
                      } catch (e) {
                        console.error('Failed to refresh auth token:', e)
                      }
                    }
                    // Status 500 means server error
                    else if (errorMessage.includes('500')) {
                      error.value = 'Server error occurred. Please try again later.';
                    }
                    else {
                      error.value = `API error: ${errorMessage}`;
                    }
                  }
                  
                  // Remove the temporary message
                  if (conversation.value) {
                    conversation.value.messages = conversation.value.messages.filter(msg => !msg.isStreaming);
                  }
                  
                  // Try again with regular API
                  console.log('Falling back to regular API call due to streaming error');
                  fallbackToRegularApiCall(message, modelId, validProjectId, options);
                }
              }
            }
          );
          
          if (!success) {
            // If streaming setup failed, use regular API
            if (conversation.value) {
              // Remove temporary message first
              conversation.value.messages = conversation.value.messages.filter(msg => !msg.isStreaming);
            }
            
            await fallbackToRegularApiCall(message, modelId, validProjectId, options);
          }
          
        } catch (e) {
          console.error('Error in streaming chat:', e);
          error.value = e instanceof Error ? e.message : 'Unknown error occurred while streaming';
          
          // Fallback to regular API call
          if (conversation.value) {
            // Remove the temporary streaming message if it exists
            conversation.value.messages = conversation.value.messages.filter(msg => !msg.isStreaming);
          }
          
          await fallbackToRegularApiCall(message, modelId, validProjectId, options);
        }
      } else {
        // Use regular API for non-streaming
        await fallbackToRegularApiCall(message, modelId, validProjectId, options);
      }
    } catch (e) {
      console.error('Error in sendMessage:', e);
      error.value = e instanceof Error ? e.message : 'Unknown error occurred';
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