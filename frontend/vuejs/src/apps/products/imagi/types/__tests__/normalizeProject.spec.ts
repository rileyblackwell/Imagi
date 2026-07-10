import { describe, it, expect } from 'vitest'
import { normalizeProject } from '../components'

describe('normalizeProject', () => {
  it('returns an empty object for falsy input', () => {
    expect(normalizeProject(null)).toEqual({})
  })

  it('coerces the id to a string', () => {
    expect(normalizeProject({ id: 42, name: 'X' }).id).toBe('42')
  })

  it('generates an id when none is provided', () => {
    const project = normalizeProject({ name: 'No Id' })
    expect(typeof project.id).toBe('string')
    expect(project.id.length).toBeGreaterThan(0)
  })

  it('applies sensible defaults', () => {
    const project = normalizeProject({ id: 1 })
    expect(project.name).toBe('Untitled Project')
    expect(project.description).toBe('')
    expect(project.is_active).toBe(true)
    expect(project.is_initialized).toBe(false)
    expect(project.generation_status).toBe('pending')
    expect(project.files).toEqual([])
  })

  it('trims name and description', () => {
    const project = normalizeProject({ id: 1, name: '  Spaced  ', description: '  hi  ' })
    expect(project.name).toBe('Spaced')
    expect(project.description).toBe('hi')
  })

  it('maps camelCase timestamps to snake_case fields', () => {
    const project = normalizeProject({
      id: 1,
      createdAt: '2024-01-01T00:00:00Z',
      updatedAt: '2024-02-01T00:00:00Z',
    })
    expect(project.created_at).toBe('2024-01-01T00:00:00Z')
    expect(project.updated_at).toBe('2024-02-01T00:00:00Z')
  })
})
