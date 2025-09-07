import api, { buildApiUrl } from '@/shared/services/api'
import type { AIModel, ModelConfig } from '../types/services'
import { AI_MODELS, MODEL_CONFIGS } from '../types/services'

// Static variables for rate limiting
let requestCounts: Map<string, number> = new Map()
let lastResetTime: number = Date.now()
const RESET_INTERVAL = 60000 // 1 minute

/**
 * Service for handling AI model information, configuration, and rate limiting
 */
export const ModelsService = {
  /**
   * Get configuration for a specific AI model
   * 
   * @param model - The AI model to get config for
   * @returns Configuration for the model
   */
  getConfig(model: AIModel): ModelConfig {
    return MODEL_CONFIGS[model.id] || {
      maxTokens: 4096,
      rateLimits: {
        tokensPerMinute: 20000,
        requestsPerMinute: 150
      },
      contextWindow: 4096,
      capabilities: ['chat']
    }
  },

  /**
   * Check if a model is within rate limits
   * 
   * @param modelId - The ID of the model to check
   * @returns Promise resolving to true if within limits
   * @throws Error if rate limit is exceeded
   */
  async checkRateLimit(modelId: string): Promise<boolean> {
    // Reset counters if minute has passed
    if (Date.now() - lastResetTime > RESET_INTERVAL) {
      requestCounts.clear()
      lastResetTime = Date.now()
    }

    const currentCount = requestCounts.get(modelId) || 0
    const config = MODEL_CONFIGS[modelId]
    
    if (!config) return true // Allow if no config found
    
    if (currentCount >= config.rateLimits.requestsPerMinute) {
      throw new Error(`Rate limit exceeded for model ${modelId}. Please wait a moment.`)
    }

    requestCounts.set(modelId, currentCount + 1)
    return true
  },

  /**
   * Check if a model can generate code
   * 
   * @param model - The AI model to check
   * @returns Whether the model can generate code
   */
  canGenerateCode(model: AIModel): boolean {
    const config = this.getConfig(model)
    return config.capabilities.includes('code_generation')
  },

  /**
   * Estimate the number of tokens in a text string
   * 
   * @param text - The text to estimate tokens for
   * @returns Estimated token count
   */
  estimateTokens(text: string): number {
    // Rough estimation: ~4 chars per token
    return Math.ceil(text.length / 4)
  },
  
  /**
   * Get the default available AI models
   * 
   * @returns Array of default AI models
   */
  getDefaultModels(): AIModel[] {
    return AI_MODELS
  },

  /**
   * Get available AI models from the API
   * 
   * @returns Promise resolving to array of available AI models
   */
  async getAvailableModels(): Promise<AIModel[]> {
    try {
      // Try to get from API first
      const response = await api.get(buildApiUrl('/api/v1/builder/models/'))
      
      if (response.data && Array.isArray(response.data.models)) {
        const apiModels: AIModel[] = response.data.models.map((model: any) => {
          // Infer a valid provider if not supplied by API
          let inferredProvider: 'openai' | 'anthropic' | 'google' | 'local' = 'local'
          const idStr = String(model.id || '')
          if (model.provider === 'openai' || model.provider === 'anthropic' || model.provider === 'google' || model.provider === 'local') {
            inferredProvider = model.provider
          } else if (idStr.startsWith('gpt')) {
            inferredProvider = 'openai'
          } else if (idStr.startsWith('claude')) {
            inferredProvider = 'anthropic'
          }

          return {
            id: model.id,
            name: model.name,
            description: model.description || '',
            capabilities: model.capabilities || ['chat'],
            // Use snake_case to match AIModel interface
            context_window: model.context_window || 4096,
            provider: inferredProvider
          } as AIModel
        })

        // Merge with static defaults to ensure completeness (e.g., gpt-5-nano)
        const defaults = AI_MODELS
        const apiIds = new Set(apiModels.map(m => m.id))
        const merged = [...apiModels]
        for (const d of defaults) {
          if (!apiIds.has(d.id)) merged.push(d)
        }
        return merged
      }
    } catch (error) {
      // If API request fails, fall back to default models
      console.warn('Failed to fetch models from API, using defaults', error)
    }
    
    // Fall back to defaults if API request failed or returned invalid data
    return this.getDefaultModels()
  },

  /**
   * Format an error object or string into a readable message
   * 
   * @param error - The error to format
   * @returns Formatted error message
   */
  formatError(error: any): string {
    if (error instanceof Error) {
      return error.message
    } else if (typeof error === 'string') {
      return error
    } else if (error && error.response && error.response.data) {
      const data = error.response.data
      
      if (data.detail) {
        return data.detail
      } else if (data.message) {
        return data.message
      } else if (data.error) {
        return data.error
      } else if (typeof data === 'string') {
        return data
      } else {
        try {
          return JSON.stringify(data)
        } catch (e) {
          return 'Unknown error occurred'
        }
      }
    } else if (error && error.message) {
      return error.message
    } else {
      try {
        return JSON.stringify(error)
      } catch (e) {
        return 'Unknown error occurred'
      }
    }
  }
} 