import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ProjectService } from '../projectService'

const { apiGet } = vi.hoisted(() => ({ apiGet: vi.fn() }))

vi.mock('@/shared/services/api', () => ({
  default: {
    get: apiGet,
    defaults: { headers: { common: { Authorization: 'Token t' } }, timeout: 60000 },
  },
}))

function httpError(status: number) {
  return Object.assign(new Error(`Request failed with status code ${status}`), {
    response: { status, data: {} },
  })
}

/**
 * The projects list must settle quickly either way: an empty list shows "No
 * projects yet", and a server that doesn't answer shows an error, never a
 * spinner that waits out the app-wide timeout.
 */
describe('ProjectService.getProjects', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    apiGet.mockReset()
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('asks with a short timeout and returns an empty list as is', async () => {
    apiGet.mockResolvedValue({ status: 200, data: [] })
    await expect(ProjectService.getProjects(true)).resolves.toEqual([])
    expect(apiGet).toHaveBeenCalledWith('/v1/project-manager/projects/', { timeout: 12000 })
  })

  it('retries a request that got no answer, then succeeds', async () => {
    apiGet
      .mockRejectedValueOnce(new Error('Request timeout'))
      .mockRejectedValueOnce(httpError(502))
      .mockResolvedValue({ status: 200, data: [{ id: 1, name: 'A' }] })
    const result = ProjectService.getProjects(true)
    await vi.runAllTimersAsync()
    await expect(result).resolves.toEqual([{ id: 1, name: 'A' }])
    expect(apiGet).toHaveBeenCalledTimes(3)
  })

  it('gives up after its retries with a message for people', async () => {
    apiGet.mockRejectedValue(new Error('Network error: Unable to connect to server'))
    const result = ProjectService.getProjects(true).catch((e) => e)
    await vi.runAllTimersAsync()
    const err = await result
    expect(err.message).toBe('Couldn’t reach Imagi to load your projects. Try again in a moment.')
    expect(apiGet).toHaveBeenCalledTimes(3)
  })

  it('does not retry an error the server meant', async () => {
    apiGet.mockRejectedValue(httpError(500))
    const result = ProjectService.getProjects(true).catch((e) => e)
    await vi.runAllTimersAsync()
    expect((await result).response.status).toBe(500)
    expect(apiGet).toHaveBeenCalledTimes(1)
  })
})
