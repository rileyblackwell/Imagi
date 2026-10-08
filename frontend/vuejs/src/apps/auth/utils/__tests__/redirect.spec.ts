import { describe, it, expect } from 'vitest'
import { safeRedirect } from '../redirect'

describe('safeRedirect', () => {
  it('keeps a path on this site', () => {
    expect(safeRedirect('/projects')).toBe('/projects')
    expect(safeRedirect('/imagi/42?tab=build#top')).toBe('/imagi/42?tab=build#top')
  })

  it('refuses links that would leave the site', () => {
    for (const target of [
      'https://evil.example',
      '//evil.example',
      '/\\evil.example',
      'javascript:alert(1)',
      'evil.example/path'
    ]) {
      expect(safeRedirect(target)).toBe('/')
    }
  })

  it('falls back when there is no usable redirect', () => {
    expect(safeRedirect(undefined)).toBe('/')
    expect(safeRedirect(['/a', '/b'])).toBe('/')
    expect(safeRedirect('', '/home')).toBe('/home')
  })
})
