import { describe, it, expect } from 'vitest'
import {
  AI_MODELS,
  MODEL_CONFIGS,
  REASONING_EFFORTS,
  clampEffortToModel,
  reasoningEffortsForModel,
} from '../services'

describe('the selectable model list', () => {
  it('offers GPT 6 Astra alongside the 5.6 suite', () => {
    expect(AI_MODELS.map(m => m.id)).toEqual([
      'gpt-5.6-terra',
      'gpt-5.6-sol',
      'gpt-5.6-luna',
      'gpt-6-astra',
    ])
  })

  it('keeps Terra the default rather than the priciest model', () => {
    const defaults = AI_MODELS.filter(m => m.default)
    expect(defaults).toHaveLength(1)
    expect(defaults[0]!.id).toBe('gpt-5.6-terra')
  })

  it('prices Astra at its retail rate and gives it the 1M window', () => {
    const astra = AI_MODELS.find(m => m.id === 'gpt-6-astra')!
    expect(astra.inputPricePerMTokens).toBe(20)
    expect(astra.outputPricePerMTokens).toBe(100)
    expect(astra.context_window).toBe(1000000)
    expect(MODEL_CONFIGS['gpt-6-astra']!.contextWindow).toBe(1000000)
  })

  it('has a rate-limit config for every model offered', () => {
    for (const model of AI_MODELS) {
      expect(MODEL_CONFIGS[model.id]).toBeDefined()
    }
  })
})

describe('per-model reasoning effort ladders', () => {
  it('gives Astra a max rung and no minimal one', () => {
    expect(reasoningEffortsForModel('gpt-6-astra').map(o => o.id)).toEqual([
      'low',
      'medium',
      'high',
      'xhigh',
      'max',
    ])
  })

  it('gives the 5.6 suite a minimal rung and no max one', () => {
    expect(reasoningEffortsForModel('gpt-5.6-sol').map(o => o.id)).toEqual([
      'minimal',
      'low',
      'medium',
      'high',
      'xhigh',
    ])
  })

  it('falls back to the full ladder for a model it does not know', () => {
    // A model the backend adds before the frontend catches up still needs a
    // usable picker rather than an empty one.
    expect(reasoningEffortsForModel('gpt-7-nova')).toEqual(REASONING_EFFORTS)
    expect(reasoningEffortsForModel(null)).toEqual(REASONING_EFFORTS)
  })

  it('clamps a rejected rung onto the nearest one the model has', () => {
    expect(clampEffortToModel('minimal', 'gpt-6-astra')).toBe('low')
    expect(clampEffortToModel('max', 'gpt-5.6-terra')).toBe('xhigh')
  })

  it('passes through a rung the model accepts', () => {
    for (const effort of ['low', 'medium', 'high', 'xhigh', 'max'] as const) {
      expect(clampEffortToModel(effort, 'gpt-6-astra')).toBe(effort)
    }
  })

  it('falls back to the default when nothing is selected', () => {
    expect(clampEffortToModel(null, 'gpt-6-astra')).toBe('medium')
    expect(clampEffortToModel(undefined, 'gpt-5.6-luna')).toBe('medium')
  })
})
