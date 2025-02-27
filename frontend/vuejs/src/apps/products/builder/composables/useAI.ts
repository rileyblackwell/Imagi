import { ref, computed } from 'vue'
import type { AIModel } from '../types/builder'
import { BuilderAPI } from '../services/api'
import axios from 'axios'
import { useProjects } from './useProjects'

interface PromptData {
  prompt: string
  context?: string
  mode: 'chat' | 'build'
  model?: string
}

interface ConversationMessage {
  role: 'user' | 'assistant'
  content: string
  code?: string
  timestamp: string
}

interface CodeChange {
  file_path: string
  content: string
}

// Match the actual API response structure
interface ChatResponse {
  response: string
  messages: any[]
}

export function useAI() {
  const availableModels = ref<AIModel[]>([])
  const selectedModel = ref<string | null>(null)
  const isProcessing = ref(false)
  const error = ref<string | null>(null)
  const conversation = ref<ConversationMessage[]>([])
  const credits = ref<number | null>(null)
  const { currentProject } = useProjects()

  const validateModelSelection = () => {
    if (!selectedModel.value) {
      throw new Error('Please select an AI model first')
    }
    const model = availableModels.value.find(m => m.id === selectedModel.value)
    if (!model) {
      throw new Error('Selected model is not available')
    }
    return model
  }

  const sendPrompt = async (projectId: string, promptData: PromptData): Promise<ChatResponse> => {
    const model = validateModelSelection()
    isProcessing.value = true
    error.value = null

    try {
      const response = await BuilderAPI.processChat(projectId, {
        prompt: promptData.prompt,
        model: model.id
      })

      conversation.value.push({
        role: 'user',
        content: promptData.prompt,
        timestamp: new Date().toISOString()
      })

      conversation.value.push({
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString()
      })

      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to process prompt'
      throw err
    } finally {
      isProcessing.value = false
    }
  }

  const loadModels = async () => {
    try {
      const models = await BuilderAPI.getAvailableModels()
      availableModels.value = models
      
      if (!selectedModel.value && models.length > 0) {
        selectedModel.value = models[0].id
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to load AI models'
      throw err
    }
  }

  const clearConversation = () => {
    conversation.value = []
  }

  const fetchConversationHistory = async (projectId: string) => {
    isProcessing.value = true
    error.value = null

    try {
      const response = await axios.get(`/api/ai/history/${projectId}/`)
      conversation.value = response.data
    } catch (err) {
      console.error('Failed to fetch conversation history:', err)
      error.value = err instanceof Error ? err.message : 'Failed to fetch conversation history'
    } finally {
      isProcessing.value = false
    }
  }

  const fetchCredits = async () => {
    try {
      const response = await axios.get('/api/ai/credits/')
      credits.value = response.data.credits
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch credits'
    }
  }

  const applyCodeChanges = async (changes: CodeChange) => {
    isProcessing.value = true
    error.value = null

    try {
      const response = await axios.post(`/api/ai/apply/${currentProject.value?.id}/`, changes)
      return response.data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to apply code changes'
      throw err
    } finally {
      isProcessing.value = false
    }
  }

  const getCodeSuggestions = async (filePath: string) => {
    isProcessing.value = true
    error.value = null

    try {
      const response = await axios.post('/api/ai/suggest/', {
        project_id: currentProject.value?.id,
        file_path: filePath
      })
      return response.data.suggestions
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to get code suggestions'
      throw err
    } finally {
      isProcessing.value = false
    }
  }

  return {
    // State
    availableModels: computed(() => availableModels.value),
    selectedModel: computed(() => selectedModel.value),
    isProcessing: computed(() => isProcessing.value),
    error: computed(() => error.value),
    conversation: computed(() => conversation.value),
    credits: computed(() => credits.value),

    // Methods
    sendPrompt,
    loadModels,
    setModel: (id: string) => selectedModel.value = id,
    clearConversation,
    fetchConversationHistory,
    fetchCredits,
    applyCodeChanges,
    getCodeSuggestions
  }
}