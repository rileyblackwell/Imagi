import { describe, it, expect, beforeEach, vi } from 'vitest'
import { savePendingIdea, peekPendingIdea, takePendingIdea } from '../pendingIdea'

describe('pendingIdea', () => {
  beforeEach(() => sessionStorage.clear())

  it('carries a trimmed idea until it is taken, then forgets it', () => {
    savePendingIdea('  A booking site for my studio  ')
    expect(peekPendingIdea()).toBe('A booking site for my studio')
    expect(takePendingIdea()).toBe('A booking site for my studio')
    expect(takePendingIdea()).toBe('')
  })

  it('clears any earlier idea when saved empty', () => {
    savePendingIdea('An online store')
    savePendingIdea('   ')
    expect(peekPendingIdea()).toBe('')
  })

  it('fails soft when storage is unavailable', () => {
    const boom = () => { throw new Error('blocked') }
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(boom)
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(boom)
    vi.spyOn(Storage.prototype, 'removeItem').mockImplementation(boom)
    expect(() => savePendingIdea('idea')).not.toThrow()
    expect(peekPendingIdea()).toBe('')
    expect(takePendingIdea()).toBe('')
  })
})
