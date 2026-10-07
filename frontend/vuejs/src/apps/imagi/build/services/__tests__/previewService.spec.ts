import { describe, it, expect, vi, beforeEach } from 'vitest'
import { PreviewService, PreviewNotRunningError } from '../previewService'

const { apiGet, apiPost } = vi.hoisted(() => ({ apiGet: vi.fn(), apiPost: vi.fn() }))

vi.mock('@/shared/services/api', () => ({
  default: { get: apiGet, post: apiPost },
}))

/** An axios-shaped rejection carrying an HTTP status and body. */
function httpError(status: number, data: unknown) {
  return Object.assign(new Error(`Request failed with status code ${status}`), {
    response: { status, data },
  })
}

describe('PreviewService', () => {
  beforeEach(() => {
    apiGet.mockReset()
    apiPost.mockReset()
  })

  describe('errors', () => {
    // WorkspacePreview offers a restart only for PreviewNotRunningError, so a
    // 409 from any endpoint has to come back as exactly that type.
    it('turns a 409 into PreviewNotRunningError carrying the server reason', async () => {
      apiGet.mockRejectedValue(httpError(409, { running: false, error: 'Browser exited' }))

      const err = await PreviewService.frame('7').catch(e => e)

      expect(err).toBeInstanceOf(PreviewNotRunningError)
      expect(err.message).toBe('Browser exited')
    })

    it('uses a default message when a 409 carries no reason', async () => {
      apiPost.mockRejectedValue(httpError(409, {}))

      const err = await PreviewService.sendInput('7', []).catch(e => e)

      expect(err).toBeInstanceOf(PreviewNotRunningError)
      expect(err.message).toBe('The preview session is not running.')
    })

    it('surfaces the server error or detail for other failures', async () => {
      apiPost.mockRejectedValueOnce(httpError(503, { error: 'Preview failed to start: npm' }))
      apiGet.mockRejectedValueOnce(httpError(404, { detail: 'Project not found' }))

      const startErr = await PreviewService.start('7').catch(e => e)
      const pagesErr = await PreviewService.pages('7').catch(e => e)

      expect(startErr).not.toBeInstanceOf(PreviewNotRunningError)
      expect(startErr.message).toBe('Preview failed to start: npm')
      expect(pagesErr.message).toBe('Project not found')
    })

    it('falls back to the transport message when the body has none', async () => {
      apiPost.mockRejectedValue(new Error('Network Error'))

      await expect(PreviewService.navigate('7', 'reload')).rejects.toThrow('Network Error')
    })
  })

  describe('requests', () => {
    it('sends the etag only when it has one', async () => {
      apiGet.mockResolvedValue({ data: { frame: null } })

      await PreviewService.frame('7')
      await PreviewService.frame('7', 'abc')

      expect(apiGet).toHaveBeenNthCalledWith(1, '/v1/builder/7/preview/frame/', { params: undefined })
      expect(apiGet).toHaveBeenNthCalledWith(2, '/v1/builder/7/preview/frame/', {
        params: { etag: 'abc' },
      })
    })

    it('gives start a long timeout, since a first start can npm install', async () => {
      apiPost.mockResolvedValue({ data: { running: true } })

      await PreviewService.start('7', { width: 390, height: 844 }, 2)

      const [url, body, config] = apiPost.mock.calls[0]
      expect(url).toBe('/v1/builder/7/preview/')
      expect(body).toEqual({ viewport: { width: 390, height: 844 }, device_scale_factor: 2 })
      expect(config.timeout).toBeGreaterThanOrEqual(300_000)
    })

    it('returns an empty page list when the project has no apps yet', async () => {
      apiGet.mockResolvedValue({ data: {} })

      await expect(PreviewService.pages('7')).resolves.toEqual([])
    })
  })
})
