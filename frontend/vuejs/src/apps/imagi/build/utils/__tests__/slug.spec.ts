import { describe, it, expect } from 'vitest'
import { toSlug, matchesSlug, projectSlug, findProjectBySlug } from '../slug'

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

describe('projectSlug', () => {
  it('prefers the slug the backend assigned', () => {
    // The backend disambiguates; toSlug(name) would have said 'my-cool-app'.
    expect(projectSlug({ name: 'My Cool App', slug: 'my-cool-app-1' })).toBe('my-cool-app-1')
  })

  it('falls back to the name for a project served without one', () => {
    expect(projectSlug({ name: 'My Cool App' })).toBe('my-cool-app')
  })
})

describe('findProjectBySlug', () => {
  it('resolves each of two names that collapse to the same derived slug', () => {
    // Both names are valid for one user and both derive to 'my-app'; only the
    // backend slug keeps them apart.
    const projects = [
      { id: 1, name: 'My App', slug: 'my-app' },
      { id: 2, name: 'My-App', slug: 'my-app-1' },
    ]
    expect(findProjectBySlug(projects, 'my-app')?.id).toBe(1)
    expect(findProjectBySlug(projects, 'my-app-1')?.id).toBe(2)
  })

  it('matches the backend slug case-insensitively', () => {
    const projects = [{ id: 1, name: 'My Cool App', slug: 'my_cool_app' }]
    expect(findProjectBySlug(projects, 'MY_COOL_APP')?.id).toBe(1)
  })

  it('falls back to the name-derived slug for URLs minted before slugs were exposed', () => {
    // Django's slugify keeps underscores, toSlug converts them — so an old
    // bookmark can disagree with the backend slug for the same project.
    const projects = [{ id: 1, name: 'my_cool_app', slug: 'my_cool_app' }]
    expect(findProjectBySlug(projects, 'my-cool-app')?.id).toBe(1)
  })

  it('never lets the name fallback steal a slug from its real owner', () => {
    const projects = [
      { id: 1, name: 'my_cool_app', slug: 'my_cool_app' },
      { id: 2, name: 'my-cool-app', slug: 'my-cool-app' },
    ]
    expect(findProjectBySlug(projects, 'my-cool-app')?.id).toBe(2)
  })

  it('handles projects with no slug at all', () => {
    const projects = [{ id: 1, name: 'My Cool App' }]
    expect(findProjectBySlug(projects, 'my-cool-app')?.id).toBe(1)
  })

  it('returns undefined for an unknown or empty slug', () => {
    const projects = [{ id: 1, name: 'My Cool App', slug: 'my-cool-app' }]
    expect(findProjectBySlug(projects, 'nope')).toBeUndefined()
    expect(findProjectBySlug(projects, '')).toBeUndefined()
  })
})
