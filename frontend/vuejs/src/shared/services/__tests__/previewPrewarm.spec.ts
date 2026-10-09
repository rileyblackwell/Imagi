import { describe, it, expect, beforeEach, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({ post: vi.fn() }))
vi.mock('@/shared/services/api', () => ({ default: apiMock }))

describe('prewarmRecentPreviews', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetModules()
    apiMock.post.mockReset()
  })

  async function load() {
    return (await import('@/shared/services/previewPrewarm')).prewarmRecentPreviews
  }

  it('asks the server once per sign-in', async () => {
    apiMock.post.mockResolvedValue({ data: { started: true } })
    const prewarm = await load()
    prewarm('tok-1')
    prewarm('tok-1')
    await Promise.resolve()
    await Promise.resolve()
    expect(apiMock.post).toHaveBeenCalledTimes(1)
    expect(apiMock.post).toHaveBeenCalledWith('/v1/builder/preview/prewarm/', {})

    // A different sign-in on the same page load prewarms again.
    prewarm('tok-2')
    await Promise.resolve()
    await Promise.resolve()
    expect(apiMock.post).toHaveBeenCalledTimes(2)
  })

  it('renders the previews at the size the pane had last time', async () => {
    apiMock.post.mockResolvedValue({ data: { started: true } })
    const mod = await import('@/shared/services/previewPrewarm')
    mod.rememberPreviewViewport({ width: 900, height: 700 }, 2)
    mod.prewarmRecentPreviews('tok-size')
    await Promise.resolve()
    await Promise.resolve()
    expect(apiMock.post).toHaveBeenCalledWith('/v1/builder/preview/prewarm/', {
      viewport: { width: 900, height: 700 },
      device_scale_factor: 2,
    })
  })

  it('does nothing without a token', async () => {
    const prewarm = await load()
    prewarm(null)
    await Promise.resolve()
    expect(apiMock.post).not.toHaveBeenCalled()
  })

  it('swallows a failed request', async () => {
    apiMock.post.mockRejectedValue(new Error('offline'))
    const prewarm = await load()
    expect(() => prewarm('tok-3')).not.toThrow()
    await new Promise(resolve => setTimeout(resolve, 0))
  })
})
