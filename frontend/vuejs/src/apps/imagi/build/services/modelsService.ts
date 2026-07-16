import type { AIModel, ModelConfig } from '../types/services'
import { AI_MODELS, MODEL_CONFIGS } from '../types/services'

// Static variables for rate limiting
const requestCounts: Map<string, number> = new Map()
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