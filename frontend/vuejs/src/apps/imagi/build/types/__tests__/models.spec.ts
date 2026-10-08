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
    // All Claude for now: Haiku, Sonnet, Opus, Fable.
    expect(AI_MODELS.map(m => m.id)).toEqual([
      'claude-haiku-5-5', 'claude-sonnet-5-5', 'claude-opus-5-5', 'claude-fable-5-1',
    ])
    expect(new Set(AI_MODELS.map(m => m.provider))).toEqual(new Set(['anthropic']))
  })

  it('makes Opus 5.5 the default rather than the priciest model', () => {
    const defaults = AI_MODELS.filter(m => m.default)
    expect(defaults).toHaveLength(1)
    expect(defaults[0]!.id).toBe('claude-opus-5-5')
  })

  it('prices every tier at its list price, no markup, with the 1M window', () => {
    const prices = Object.fromEntries(
      AI_MODELS.map(m => [m.id, [m.inputPricePerMTokens, m.outputPricePerMTokens, m.context_window]])
    )
    expect(prices).toEqual({
      'claude-haiku-5-5': [0.1, 0.5, 1000000],
      'claude-sonnet-5-5': [2, 10, 1000000],
      'claude-opus-5-5': [4, 20, 1000000],
      'claude-fable-5-1': [10, 50, 1000000],
    })
  })

  it('carries a retired GPT model over to the current model for its tier', () => {
    // Stored conversations and older tabs still name these; mirrors the
    // backend's LEGACY_MODEL_ALIASES.
    expect(LEGACY_MODEL_ALIASES).toEqual({
      'gpt-6-luna': 'claude-haiku-5-5',
      'gpt-5.6-luna': 'claude-haiku-5-5',
      'gpt-6-astra': 'claude-fable-5-1',
      'gpt-5.6-terra': 'claude-opus-5-5',
      'gpt-5.6-sol': 'claude-opus-5-5',
    })
    expect(canonicalModelId('gpt-5.6-terra')).toBe('claude-opus-5-5')
    expect(canonicalModelId('gpt-6-astra')).toBe('claude-fable-5-1')
    expect(canonicalModelId('claude-sonnet-5-5')).toBe('claude-sonnet-5-5')
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
  const ladder = ['low', 'medium', 'high', 'xhigh', 'max'] as const

  it('offers the same five rungs, faster to smarter, to every model', () => {
    expect(REASONING_EFFORTS.map(o => o.id)).toEqual(ladder)
    for (const model of AI_MODELS) {
      expect(reasoningEffortsForModel(model.id).map(o => o.id)).toEqual(ladder)
    }
  })

  it('names and describes each rung for the picker', () => {
    expect(REASONING_EFFORTS.map(o => o.name)).toEqual(['Low', 'Medium', 'High', 'Extra High', 'Max'])
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

  it("re-seats the retired 'minimal' and 'none' rungs onto the ladder", () => {
    // OpenAI-only rungs an older tab or a stored selection can still send.
    expect(LEGACY_REASONING_EFFORT_ALIASES).toEqual({ minimal: 'low', none: 'low' })
    expect(clampEffortToModel('minimal', 'claude-fable-5-1')).toBe('low')
    expect(clampEffortToModel('none', 'claude-opus-5-5')).toBe('low')
    // Claude takes 'max' as it is.
    expect(clampEffortToModel('max', 'claude-haiku-5-5')).toBe('max')
  })

  it('falls back to the default when nothing usable is selected', () => {
    expect(DEFAULT_REASONING_EFFORT).toBe('medium')
    expect(clampEffortToModel(null, 'claude-fable-5-1')).toBe('medium')
    expect(clampEffortToModel(undefined, 'claude-haiku-5-5')).toBe('medium')
    expect(clampEffortToModel('', 'claude-haiku-5-5')).toBe('medium')
    expect(clampEffortToModel('bogus', 'claude-opus-5-5')).toBe('medium')
    // Object prototype names are not aliases either.
    expect(clampEffortToModel('constructor', 'claude-opus-5-5')).toBe('medium')
  })
})
