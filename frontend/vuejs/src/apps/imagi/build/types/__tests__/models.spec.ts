import { describe, it, expect } from 'vitest'
import {
  AI_MODELS,
  DEFAULT_REASONING_EFFORT,
  LEGACY_REASONING_EFFORT_ALIASES,
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

describe('the reasoning effort ladder', () => {
  const ladder = ['low', 'medium', 'high', 'xhigh'] as const

  it('offers the same four rungs, faster to smarter, to every model', () => {
    expect(REASONING_EFFORTS.map(o => o.id)).toEqual(ladder)
    for (const model of AI_MODELS) {
      expect(reasoningEffortsForModel(model.id).map(o => o.id)).toEqual(ladder)
    }
  })

  it('names and describes each rung for the picker', () => {
    expect(REASONING_EFFORTS.map(o => o.name)).toEqual(['Low', 'Medium', 'High', 'Extra High'])
    for (const option of REASONING_EFFORTS) {
      expect(option.description.length).toBeGreaterThan(0)
    }
  })

  it('gives the full ladder to a model it does not know', () => {
    // A model the backend adds before the frontend catches up still needs a
    // usable picker rather than an empty one.
    expect(reasoningEffortsForModel('gpt-7-nova')).toEqual(REASONING_EFFORTS)
    expect(reasoningEffortsForModel(null)).toEqual(REASONING_EFFORTS)
  })

  it('passes through a rung on the ladder for any model', () => {
    for (const model of AI_MODELS) {
      for (const effort of ladder) {
        expect(clampEffortToModel(effort, model.id)).toBe(effort)
      }
    }
  })

  it("re-seats the retired 'minimal' and 'max' rungs onto the ladder", () => {
    // The SDK's ReasoningEffort literal tops out at xhigh — 'max' was never a
    // real rung — and 'minimal' was dropped so every model offers the same
    // choices. An older tab or a stored selection can still send either.
    expect(LEGACY_REASONING_EFFORT_ALIASES).toEqual({ minimal: 'low', max: 'xhigh' })
    expect(clampEffortToModel('minimal', 'gpt-6-astra')).toBe('low')
    expect(clampEffortToModel('minimal', 'gpt-5.6-terra')).toBe('low')
    expect(clampEffortToModel('max', 'gpt-6-astra')).toBe('xhigh')
    expect(clampEffortToModel('max', 'gpt-5.6-terra')).toBe('xhigh')
  })

  it('falls back to the default when nothing usable is selected', () => {
    expect(DEFAULT_REASONING_EFFORT).toBe('medium')
    expect(clampEffortToModel(null, 'gpt-6-astra')).toBe('medium')
    expect(clampEffortToModel(undefined, 'gpt-5.6-luna')).toBe('medium')
    expect(clampEffortToModel('', 'gpt-5.6-luna')).toBe('medium')
    expect(clampEffortToModel('bogus', 'gpt-5.6-sol')).toBe('medium')
    // Object prototype names are not aliases either.
    expect(clampEffortToModel('constructor', 'gpt-5.6-sol')).toBe('medium')
  })
})
