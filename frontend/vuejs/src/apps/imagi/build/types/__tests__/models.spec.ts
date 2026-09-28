import { describe, it, expect } from 'vitest'
import {
  AI_MODELS,
  DEFAULT_REASONING_EFFORT,
  LEGACY_MODEL_ALIASES,
  LEGACY_REASONING_EFFORT_ALIASES,
  MODEL_CONFIGS,
  REASONING_EFFORTS,
  canonicalModelId,
  clampEffortToModel,
  reasoningEffortsForModel,
} from '../services'

describe('the selectable model list', () => {
  it('offers one model per tier, faster to smarter', () => {
    // Quick & efficient, balanced all-rounder, frontier — a blend of
    // providers, each the best current fit for its tier.
    expect(AI_MODELS.map(m => m.id)).toEqual(['gpt-6-luna', 'claude-opus-5-5', 'gpt-6-astra'])
    expect(AI_MODELS.map(m => m.provider)).toEqual(['openai', 'anthropic', 'openai'])
  })

  it('makes Opus 5.5 the default rather than the priciest model', () => {
    const defaults = AI_MODELS.filter(m => m.default)
    expect(defaults).toHaveLength(1)
    expect(defaults[0]!.id).toBe('claude-opus-5-5')
  })

  it('prices every tier at its retail rate (2x list) with the 1M window', () => {
    const prices = Object.fromEntries(
      AI_MODELS.map(m => [m.id, [m.inputPricePerMTokens, m.outputPricePerMTokens, m.context_window]])
    )
    expect(prices).toEqual({
      'gpt-6-luna': [0.2, 1, 1000000],
      'claude-opus-5-5': [8, 40, 1000000],
      'gpt-6-astra': [20, 100, 1000000],
    })
  })

  it('carries a retired 5.6 model over to the current model for its tier', () => {
    // Stored conversations and older tabs still name these; mirrors the
    // backend's LEGACY_MODEL_ALIASES.
    expect(LEGACY_MODEL_ALIASES).toEqual({
      'gpt-5.6-luna': 'gpt-6-luna',
      'gpt-5.6-terra': 'claude-opus-5-5',
      'gpt-5.6-sol': 'claude-opus-5-5',
    })
    expect(canonicalModelId('gpt-5.6-terra')).toBe('claude-opus-5-5')
    expect(canonicalModelId('gpt-6-astra')).toBe('gpt-6-astra')
    expect(canonicalModelId(null)).toBeNull()
    expect(canonicalModelId('constructor')).toBe('constructor')
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
    expect(clampEffortToModel('minimal', 'claude-opus-5-5')).toBe('low')
    expect(clampEffortToModel('max', 'gpt-6-astra')).toBe('xhigh')
    expect(clampEffortToModel('max', 'claude-opus-5-5')).toBe('xhigh')
  })

  it('falls back to the default when nothing usable is selected', () => {
    expect(DEFAULT_REASONING_EFFORT).toBe('medium')
    expect(clampEffortToModel(null, 'gpt-6-astra')).toBe('medium')
    expect(clampEffortToModel(undefined, 'gpt-6-luna')).toBe('medium')
    expect(clampEffortToModel('', 'gpt-6-luna')).toBe('medium')
    expect(clampEffortToModel('bogus', 'claude-opus-5-5')).toBe('medium')
    // Object prototype names are not aliases either.
    expect(clampEffortToModel('constructor', 'claude-opus-5-5')).toBe('medium')
  })
})
