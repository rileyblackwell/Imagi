import type { AIModel } from '../types'
import { AI_MODELS } from '../types/builder'

interface ModelConfig {
  maxTokens: number
  rateLimits: {
    tokensPerMinute: number
    requestsPerMinute: number
  }
  contextWindow: number
  capabilities: string[]
}

const MODEL_CONFIGS: Record<string, ModelConfig> = {
  'gpt-4': {
    maxTokens: 8192,
    rateLimits: {
      tokensPerMinute: 40000,
      requestsPerMinute: 200
    },
    contextWindow: 8192,
    capabilities: ['code_generation', 'chat', 'analysis']
  },
  'claude-2': {
    maxTokens: 100000,
    rateLimits: {
      tokensPerMinute: 100000,
      requestsPerMinute: 300
    },
    contextWindow: 100000,
    capabilities: ['code_generation', 'chat', 'analysis']
  },
  'claude-3-5-sonnet-20241022': {
    maxTokens: 200000,
    rateLimits: {
      tokensPerMinute: 100000,
      requestsPerMinute: 300
    },
    contextWindow: 200000,
    capabilities: ['code_generation', 'chat', 'analysis']
  },
  'gpt-4o': {
    maxTokens: 128000,
    rateLimits: {
      tokensPerMinute: 60000,
      requestsPerMinute: 250
    },
    contextWindow: 128000,
    capabilities: ['code_generation', 'chat', 'analysis']
  },
  'gpt-4o-mini': {
    maxTokens: 128000,
    rateLimits: {
      tokensPerMinute: 80000,
      requestsPerMinute: 350
    },
    contextWindow: 128000,
    capabilities: ['code_generation', 'chat', 'analysis']
  }
}

export class ModelService {
  private static requestCounts: Map<string, number> = new Map()
  private static lastResetTime: number = Date.now()
  private static RESET_INTERVAL = 60000 // 1 minute

  static getConfig(model: AIModel): ModelConfig {
    return MODEL_CONFIGS[model.id] || {
      maxTokens: 4096,
      rateLimits: {
        tokensPerMinute: 20000,
        requestsPerMinute: 150
      },
      contextWindow: 4096,
      capabilities: ['chat']
    }
  }

  static async checkRateLimit(modelId: string): Promise<boolean> {
    // Reset counters if minute has passed
    if (Date.now() - this.lastResetTime > this.RESET_INTERVAL) {
      this.requestCounts.clear()
      this.lastResetTime = Date.now()
    }

    const currentCount = this.requestCounts.get(modelId) || 0
    const config = MODEL_CONFIGS[modelId]
    
    if (!config) return true // Allow if no config found
    
    if (currentCount >= config.rateLimits.requestsPerMinute) {
      throw new Error(`Rate limit exceeded for model ${modelId}. Please wait a moment.`)
    }

    this.requestCounts.set(modelId, currentCount + 1)
    return true
  }

  static canGenerateCode(model: AIModel): boolean {
    const config = this.getConfig(model)
    return config.capabilities.includes('code_generation')
  }

  static estimateTokens(text: string): number {
    // Rough estimation: ~4 chars per token
    return Math.ceil(text.length / 4)
  }
  
  static getDefaultModels(): AIModel[] {
    return AI_MODELS
  }
}