import { describe, it, expect } from 'vitest'
import { updatedLabel } from '../updatedLabel'

describe('updatedLabel', () => {
  const now = new Date('2026-10-08T12:00:00Z')
  const ago = (ms: number) => new Date(now.getTime() - ms).toISOString()
  const MIN = 60_000
  const HOUR = 60 * MIN
  const DAY = 24 * HOUR

  it('says nothing without a usable timestamp', () => {
    expect(updatedLabel(undefined, now)).toBe('')
    expect(updatedLabel('not a date', now)).toBe('')
  })

  it('reads recent work in minutes and hours', () => {
    expect(updatedLabel(ago(20 * 1000), now)).toBe('Just now')
    expect(updatedLabel(ago(MIN), now)).toBe('1 minute ago')
    expect(updatedLabel(ago(12 * MIN), now)).toBe('12 minutes ago')
    expect(updatedLabel(ago(HOUR), now)).toBe('1 hour ago')
    expect(updatedLabel(ago(5 * HOUR), now)).toBe('5 hours ago')
  })

  it('reads older work in days, then as a date', () => {
    expect(updatedLabel(ago(DAY + HOUR), now)).toBe('Yesterday')
    expect(updatedLabel(ago(3 * DAY), now)).toBe('3 days ago')
    const lastMonth = ago(30 * DAY)
    expect(updatedLabel(lastMonth, now)).toBe(
      new Date(lastMonth).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    )
    expect(updatedLabel('2024-03-02T12:00:00Z', now)).toMatch(/2024/)
  })
})
