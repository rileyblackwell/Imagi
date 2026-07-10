import { describe, it, expect } from 'vitest'
import { toSlug, matchesSlug, getProjectSlug } from '../slug'

describe('toSlug', () => {
  it('lowercases and hyphenates spaces', () => {
    expect(toSlug('My Cool App')).toBe('my-cool-app')
  })

  it('replaces underscores with hyphens', () => {
    expect(toSlug('my_cool_app')).toBe('my-cool-app')
  })

  it('strips special characters', () => {
    expect(toSlug('Hello, World! @2024')).toBe('hello-world-2024')
  })

  it('collapses multiple separators into one hyphen', () => {
    expect(toSlug('a   b___c')).toBe('a-b-c')
  })

  it('trims leading and trailing hyphens', () => {
    expect(toSlug('  --Edge--  ')).toBe('edge')
  })
})

describe('matchesSlug', () => {
  it('matches a name against its slug case-insensitively', () => {
    expect(matchesSlug('My Cool App', 'my-cool-app')).toBe(true)
    expect(matchesSlug('My Cool App', 'MY-COOL-APP')).toBe(true)
  })

  it('does not match unrelated slugs', () => {
    expect(matchesSlug('My Cool App', 'other-app')).toBe(false)
  })
})

describe('getProjectSlug', () => {
  it('returns the slug for a project object', () => {
    expect(getProjectSlug({ name: 'Test Project' })).toBe('test-project')
  })
})
