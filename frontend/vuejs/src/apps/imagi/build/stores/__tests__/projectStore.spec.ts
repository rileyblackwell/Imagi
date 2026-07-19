import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Mock the API client (pulled in transitively via the auth store).
const apiMock = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }))
vi.mock('@/shared/services/api', () => ({
  default: apiMock,
  getCsrfToken: vi.fn(),
}))

// Mock the project service (all static methods).
const projectService = vi.hoisted(() => ({
  getProjects: vi.fn(),
  getProject: vi.fn(),
  createProject: vi.fn(),
  deleteProject: vi.fn(),
  initializeProject: vi.fn(),
}))
vi.mock('../../services/projectService', () => ({
  ProjectService: projectService,
}))

import { useProjectStore } from '@/apps/imagi/build/stores/projectStore'

describe('project store', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(projectService).forEach((fn) => fn.mockReset())
  })

  describe('updateProjects', () => {
    it('normalizes projects and indexes them by id', () => {
      const store = useProjectStore()
      store.updateProjects([
        { id: 1, name: 'Alpha' },
        { id: 2, name: 'Beta' },
        null,
        'garbage',
      ])

      expect(store.projects).toHaveLength(2)
      expect(store.hasProjects).toBe(true)
      expect(store.getProjectById('1')?.name).toBe('Alpha')
      // normalizeProject coerces ids to strings.
      expect(store.projects[0].id).toBe('1')
    })
  })

  describe('slug getters', () => {
    it('finds a project by its URL slug', () => {
      const store = useProjectStore()
      store.updateProjects([{ id: 1, name: 'My Cool App' }])
      expect(store.getProjectBySlug('my-cool-app')?.name).toBe('My Cool App')
      expect(store.getProjectBySlug('nope')).toBeUndefined()
    })

    it('derives a slug for a project', () => {
      const store = useProjectStore()
      expect(store.getSlugForProject({ name: 'Some Thing' } as any)).toBe('some-thing')
    })
  })

  describe('sortedProjects', () => {
    it('orders projects newest-first by created_at', () => {
      const store = useProjectStore()
      store.updateProjects([
        { id: 1, name: 'Older', created_at: '2024-01-01T00:00:00Z' },
        { id: 2, name: 'Newer', created_at: '2024-06-01T00:00:00Z' },
      ])
      expect(store.sortedProjects.map((p) => p.name)).toEqual(['Newer', 'Older'])
    })
  })

  describe('setAuthenticated', () => {
    it('clears projects when logging out', () => {
      const store = useProjectStore()
      store.setAuthenticated(true)
      store.updateProjects([{ id: 1, name: 'Alpha' }])
      expect(store.projects).toHaveLength(1)

      store.setAuthenticated(false)
      expect(store.projects).toHaveLength(0)
      expect(store.initialized).toBe(false)
    })
  })

  describe('createProject', () => {
    it('throws when the user is not authenticated', async () => {
      const store = useProjectStore()
      store.setAuthenticated(false)
      await expect(
        store.createProject({ name: 'X', description: '' }),
      ).rejects.toThrow('You must be logged in')
    })

    it('adds the created project to local state', async () => {
      projectService.createProject.mockResolvedValue({
        id: 99,
        name: 'Fresh Project',
        description: 'desc',
      })
      projectService.initializeProject.mockResolvedValue({ success: true })

      const store = useProjectStore()
      store.setAuthenticated(true)
      const created = await store.createProject({
        name: 'Fresh Project',
        description: 'desc',
      })

      expect(created.id).toBe('99')
      expect(store.getProjectById('99')?.name).toBe('Fresh Project')
      expect(projectService.createProject).toHaveBeenCalled()
    })
  })

  describe('deleteProject', () => {
    it('requires authentication', async () => {
      const store = useProjectStore()
      store.setAuthenticated(false)
      await expect(store.deleteProject('1')).rejects.toThrow('You must be logged in')
    })

    it('optimistically removes the project, leaving the rest', async () => {
      projectService.deleteProject.mockResolvedValue(undefined)
      const store = useProjectStore()
      store.setAuthenticated(true)
      store.updateProjects([
        { id: 1, name: 'Keep' },
        { id: 2, name: 'Remove' },
      ])

      await store.deleteProject('2')

      expect(store.getProjectById('2')).toBeUndefined()
      expect(store.projects.map((p) => p.name)).toEqual(['Keep'])
      expect(projectService.deleteProject).toHaveBeenCalledWith('2')
    })

    it('restores the project when the server rejects a real error', async () => {
      const err: any = new Error('server exploded')
      err.response = { status: 500 }
      projectService.deleteProject.mockRejectedValue(err)
      const store = useProjectStore()
      store.setAuthenticated(true)
      store.updateProjects([
        { id: 1, name: 'Keep' },
        { id: 2, name: 'Remove' },
      ])

      await expect(store.deleteProject('2')).rejects.toThrow('server exploded')

      // The optimistic removal is rolled back so the list stays truthful.
      expect(store.getProjectById('2')?.name).toBe('Remove')
      expect(store.projects.map((p) => p.name)).toEqual(['Keep', 'Remove'])
    })

    it('does not raise the list loading flag while deleting', async () => {
      // Deletion is optimistic, so it must not flip `loading` — otherwise the
      // Project Library panel flashes (or hangs on) its full-page spinner.
      const store = useProjectStore()
      let loadingDuringServerCall = false
      projectService.deleteProject.mockImplementation(async () => {
        loadingDuringServerCall = store.loading
      })
      store.setAuthenticated(true)
      store.updateProjects([{ id: 1, name: 'Only' }])

      await store.deleteProject('1')

      expect(loadingDuringServerCall).toBe(false)
      expect(store.loading).toBe(false)
      // The last project is gone, so the view renders its empty state.
      expect(store.projects).toHaveLength(0)
    })

    it('treats a 404 from the server as success', async () => {
      const err: any = new Error('not found')
      err.response = { status: 404 }
      projectService.deleteProject.mockRejectedValue(err)
      const store = useProjectStore()
      store.setAuthenticated(true)
      store.updateProjects([{ id: 5, name: 'Ghost' }])

      await expect(store.deleteProject('5')).resolves.toBeUndefined()
      expect(store.getProjectById('5')).toBeUndefined()
    })
  })

  describe('fetchProjects', () => {
    it('skips fetching when not authenticated', async () => {
      const store = useProjectStore()
      store.setAuthenticated(false)
      const result = await store.fetchProjects()
      expect(result).toEqual([])
      expect(projectService.getProjects).not.toHaveBeenCalled()
    })
  })
})
