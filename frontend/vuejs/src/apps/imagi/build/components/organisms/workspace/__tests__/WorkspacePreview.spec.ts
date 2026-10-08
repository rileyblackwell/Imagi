import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'

const { start, frame, sendInput, pages, resize } = vi.hoisted(() => ({
  start: vi.fn(),
  frame: vi.fn(),
  sendInput: vi.fn(),
  pages: vi.fn(),
  resize: vi.fn(),
}))

vi.mock('../../../../services/previewService', () => ({
  PreviewService: { start, frame, sendInput, pages, resize, navigate: vi.fn() },
  PreviewNotRunningError: class extends Error {},
}))

import WorkspacePreview from '../WorkspacePreview.vue'

const settle = async () => {
  await new Promise(r => setTimeout(r, 5))
  await flushPromises()
}

function translateY(wrapper: VueWrapper): number {
  const style = wrapper.find('img').attributes('style') || ''
  const m = style.match(/translate3d\(0(?:px)?, (-?[\d.]+)px/)
  return m ? Number(m[1]) : 0
}

describe('WorkspacePreview wheel scrolling', () => {
  let wrapper: VueWrapper

  beforeEach(async () => {
    // jsdom has no image decoding; frames go on screen as soon as they arrive.
    HTMLImageElement.prototype.decode = () => Promise.resolve()
    start.mockResolvedValue({ frame: 'AAAA', etag: 'a', path: '/', viewport: [320, 320] })
    frame.mockResolvedValue({ frame: null, etag: 'a' })
    pages.mockResolvedValue([])
    resize.mockResolvedValue({})
    wrapper = mount(WorkspacePreview, { props: { projectId: '7' } })
    await settle()
  })

  afterEach(() => {
    wrapper.unmount()
    vi.restoreAllMocks()
    start.mockReset(); frame.mockReset(); sendInput.mockReset()
  })

  it('moves the frame before the server answers', async () => {
    let answer: (v: unknown) => void = () => {}
    sendInput.mockReturnValue(new Promise(r => { answer = r }))

    await wrapper.find('.pv-stage').trigger('wheel', { deltaY: 100, deltaMode: 0 })
    await flushPromises()
    expect(translateY(wrapper)).toBe(-100)

    // Once the frame that shows the scroll is up, the shift hands over to it.
    answer({ frame: 'BBBB', etag: 'b' })
    await settle()
    expect(translateY(wrapper)).toBe(0)
  })

  it('converts line-mode wheel deltas to pixels', async () => {
    sendInput.mockResolvedValue({ frame: 'BBBB', etag: 'b' })

    await wrapper.find('.pv-stage').trigger('wheel', { deltaY: 3, deltaMode: 1 })
    await settle()

    const events = sendInput.mock.calls[0][1]
    expect(events[0]).toMatchObject({ kind: 'wheel', deltaY: 120 })
  })

  it('stops shifting the frame at the page edge', async () => {
    // Unchanged pixels: the page is already at its bottom.
    sendInput.mockResolvedValue({ frame: null, etag: 'a' })
    const stage = wrapper.find('.pv-stage')

    await stage.trigger('wheel', { deltaY: 100, deltaMode: 0 })
    await settle()
    await stage.trigger('wheel', { deltaY: 100, deltaMode: 0 })
    await flushPromises()
    expect(translateY(wrapper)).toBe(0)

    // Scrolling back the other way still moves at once.
    sendInput.mockReturnValue(new Promise(() => {}))
    await settle()
    await stage.trigger('wheel', { deltaY: -100, deltaMode: 0 })
    await flushPromises()
    expect(translateY(wrapper)).toBe(100)
  })
})
