import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'

const apiMock = vi.hoisted(() => ({ post: vi.fn() }))
vi.mock('@/shared/services/api', () => ({ default: apiMock }))

type Mod = typeof import('@/shared/services/previewPrewarm')

describe('keeping recent previews warm', () => {
  let mod: Mod

  beforeEach(async () => {
    vi.useFakeTimers()
    localStorage.clear()
    vi.resetModules()
    apiMock.post.mockReset()
    apiMock.post.mockResolvedValue({ data: { started: true } })
    mod = await import('@/shared/services/previewPrewarm')
  })

  afterEach(() => {
    mod.stopKeepingPreviewsWarm()
    vi.useRealTimers()
  })

  const flush = async () => {
    await Promise.resolve()
    await Promise.resolve()
  }

  function setHidden(hidden: boolean) {
    Object.defineProperty(document, 'hidden', { configurable: true, get: () => hidden })
    document.dispatchEvent(new Event('visibilitychange'))
  }

  it('asks at sign-in, then keeps asking for as long as they stay signed in', async () => {
    mod.keepRecentPreviewsWarm('tok-1')
    mod.keepRecentPreviewsWarm('tok-1') // same sign-in: no second loop
    await flush()
    expect(apiMock.post).toHaveBeenCalledTimes(1)
    expect(apiMock.post).toHaveBeenCalledWith('/v1/builder/preview/prewarm/', {})

    await vi.advanceTimersByTimeAsync(2 * 60_000)
    expect(apiMock.post).toHaveBeenCalledTimes(2)
    await vi.advanceTimersByTimeAsync(2 * 60_000)
    expect(apiMock.post).toHaveBeenCalledTimes(3)
  })

  it('stops at sign-out', async () => {
    mod.keepRecentPreviewsWarm('tok-2')
    await flush()
    mod.stopKeepingPreviewsWarm()
    await vi.advanceTimersByTimeAsync(10 * 60_000)
    expect(apiMock.post).toHaveBeenCalledTimes(1)
  })

  it('pauses while the tab is hidden and beats again on return', async () => {
    mod.keepRecentPreviewsWarm('tok-3')
    await flush()
    setHidden(true)
    await vi.advanceTimersByTimeAsync(6 * 60_000)
    expect(apiMock.post).toHaveBeenCalledTimes(1)
    setHidden(false)
    await flush()
    expect(apiMock.post).toHaveBeenCalledTimes(2)
  })

  it('renders the previews at the size the pane had last time', async () => {
    mod.rememberPreviewViewport({ width: 900, height: 700 }, 2)
    mod.keepRecentPreviewsWarm('tok-4')
    await flush()
    expect(apiMock.post).toHaveBeenCalledWith('/v1/builder/preview/prewarm/', {
      viewport: { width: 900, height: 700 },
      device_scale_factor: 2,
    })
  })

  it('does nothing without a token', async () => {
    mod.keepRecentPreviewsWarm(null)
    await flush()
    expect(apiMock.post).not.toHaveBeenCalled()
  })

  it('swallows a failed request', async () => {
    apiMock.post.mockRejectedValue(new Error('offline'))
    expect(() => mod.keepRecentPreviewsWarm('tok-5')).not.toThrow()
    await flush()
  })
})
