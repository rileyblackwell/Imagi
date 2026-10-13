import { describe, it, expect } from 'vitest'
import { sessionStartIndexes, formatSessionStart, SESSION_GAP_MS } from '../sessionBreaks'

const at = (iso: string) => ({ timestamp: iso })

describe('sessionStartIndexes', () => {
  it('starts a sitting at the first message', () => {
    expect([...sessionStartIndexes([at('2026-10-13T10:00:00Z')])]).toEqual([0])
  })

  it('starts a new sitting after a break of 30 minutes or more', () => {
    const starts = sessionStartIndexes([
      at('2026-10-13T10:00:00Z'),
      at('2026-10-13T10:29:59Z'),
      at('2026-10-13T10:59:59Z'),
      at('2026-10-13T11:29:59Z'),
      at('2026-10-13T11:30:00Z'),
    ])
    // 10:29:59 -> 10:59:59 is exactly the gap; 11:29:59 -> 11:30:00 is not.
    expect(SESSION_GAP_MS).toBe(30 * 60 * 1000)
    expect([...starts]).toEqual([0, 2, 3])
  })

  it('ignores messages without a readable time', () => {
    const starts = sessionStartIndexes([
      { timestamp: undefined },
      at('not a date'),
      at('2026-10-13T10:00:00Z'),
    ])
    expect([...starts]).toEqual([2])
  })
})

describe('formatSessionStart', () => {
  const now = new Date(2026, 9, 13, 15, 0)
  const local = (...args: [number, number, number, number, number]) => new Date(...args).toISOString()

  it('says Today and Yesterday by name', () => {
    expect(formatSessionStart(local(2026, 9, 13, 9, 5), now)).toMatch(/^Today · 9:05/)
    expect(formatSessionStart(local(2026, 9, 12, 21, 40), now)).toMatch(/^Yesterday · /)
  })

  it('names the weekday within the last week, then the date', () => {
    expect(formatSessionStart(local(2026, 9, 9, 8, 0), now)).not.toMatch(/^(Today|Yesterday)/)
    expect(formatSessionStart(local(2026, 9, 1, 8, 0), now)).toMatch(/1/)
    expect(formatSessionStart(local(2025, 11, 30, 8, 0), now)).toMatch(/2025/)
  })

  it('says nothing for an unreadable time', () => {
    expect(formatSessionStart(undefined, now)).toBe('')
  })
})
