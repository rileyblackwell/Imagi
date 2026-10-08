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

// A 320px-tall viewport onto a 2000px page: it can scroll 1680px.
const scrollAt = (y: number, extra: Record<string, unknown> = {}) => ({
  x: 0, y, width: 320, height: 2000, viewport_width: 320, viewport_height: 320,
  background: 'rgb(250, 249, 246)', ...extra,
})

describe('WorkspacePreview wheel scrolling', () => {
  let wrapper: VueWrapper

  async function mountAt(y: number) {
    start.mockResolvedValue({ frame: 'AAAA', etag: 'a', path: '/', viewport: [320, 320], scroll: scrollAt(y) })
    wrapper = mount(WorkspacePreview, { props: { projectId: '7' } })
    await settle()
  }

  beforeEach(() => {
    // jsdom has no image decoding; frames go on screen as soon as they arrive.
    HTMLImageElement.prototype.decode = () => Promise.resolve()
    frame.mockResolvedValue({ frame: null, etag: 'a' })
    pages.mockResolvedValue([])
    resize.mockResolvedValue({})
  })

  afterEach(() => {
    wrapper.unmount()
    vi.restoreAllMocks()
    start.mockReset(); frame.mockReset(); sendInput.mockReset()
  })

  it('moves the frame before the server answers', async () => {
    await mountAt(0)
    let answer: (v: unknown) => void = () => {}
    sendInput.mockReturnValue(new Promise(r => { answer = r }))

    await wrapper.find('.pv-stage').trigger('wheel', { deltaY: 100, deltaMode: 0 })
    await flushPromises()
    expect(translateY(wrapper)).toBe(-100)

    // Once the frame that shows the scroll is up, the shift hands over to it.
    answer({ frame: 'BBBB', etag: 'b', scroll: scrollAt(100) })
    await settle()
    expect(translateY(wrapper)).toBe(0)
  })

  it('places each frame by the scroll offset it reports', async () => {
    await mountAt(0)
    let answer: (v: unknown) => void = () => {}
    sendInput.mockReturnValueOnce(new Promise(r => { answer = r }))
    sendInput.mockReturnValue(new Promise(() => {}))
    const stage = wrapper.find('.pv-stage')

    await stage.trigger('wheel', { deltaY: 100, deltaMode: 0 })
    await settle()
    expect(sendInput).toHaveBeenCalledTimes(1)
    // More scrolling while the first batch is out.
    await stage.trigger('wheel', { deltaY: 60, deltaMode: 0 })
    await flushPromises()
    expect(translateY(wrapper)).toBe(-160)

    // The first batch's frame shows y=100; the page is headed for 160, so
    // that frame sits 60px up: no jump back, no double count.
    answer({ frame: 'BBBB', etag: 'b', scroll: scrollAt(100) })
    await settle()
    expect(wrapper.find('img').attributes('src')).toContain('BBBB')
    expect(translateY(wrapper)).toBe(-60)
  })

  it('ignores a poll that was sent before newer input', async () => {
    await mountAt(0)
    let answerPoll: (v: unknown) => void = () => {}
    frame.mockReturnValue(new Promise(r => { answerPoll = r }))
    // The first poll goes out 200ms after start.
    await new Promise(r => setTimeout(r, 250))
    expect(frame).toHaveBeenCalled()

    sendInput.mockResolvedValue({ frame: 'BBBB', etag: 'b', scroll: scrollAt(100) })
    await wrapper.find('.pv-stage').trigger('wheel', { deltaY: 100, deltaMode: 0 })
    await settle()
    expect(translateY(wrapper)).toBe(0)

    // The poll's older frame (y=0) arrives last and must not replace it.
    answerPoll({ frame: 'OLD0', etag: 'o', scroll: scrollAt(0) })
    await settle()
    expect(wrapper.find('img').attributes('src')).toContain('BBBB')
    expect(translateY(wrapper)).toBe(0)
  })

  it('converts line-mode wheel deltas to pixels', async () => {
    await mountAt(0)
    sendInput.mockResolvedValue({ frame: 'BBBB', etag: 'b', scroll: scrollAt(120) })

    await wrapper.find('.pv-stage').trigger('wheel', { deltaY: 3, deltaMode: 1 })
    await settle()

    const events = sendInput.mock.calls[0][1]
    expect(events[0]).toMatchObject({ kind: 'wheel', deltaY: 120 })
  })

  it('does not shift the frame past the end of the page', async () => {
    await mountAt(1680)
    sendInput.mockReturnValue(new Promise(() => {}))
    const stage = wrapper.find('.pv-stage')

    await stage.trigger('wheel', { deltaY: 100, deltaMode: 0 })
    await flushPromises()
    expect(translateY(wrapper)).toBe(0)

    // Scrolling back the other way still moves at once.
    await stage.trigger('wheel', { deltaY: -100, deltaMode: 0 })
    await flushPromises()
    expect(translateY(wrapper)).toBe(100)
  })

  it('does not shift a page that does not scroll', async () => {
    await mountAt(0)
    sendInput.mockReturnValue(new Promise(() => {}))
    start.mockReset()
    wrapper.unmount()
    start.mockResolvedValue({ frame: 'AAAA', etag: 'a', viewport: [320, 320], scroll: scrollAt(0, { height: 320 }) })
    wrapper = mount(WorkspacePreview, { props: { projectId: '8' } })
    await settle()

    await wrapper.find('.pv-stage').trigger('wheel', { deltaY: 100, deltaMode: 0 })
    await flushPromises()
    expect(translateY(wrapper)).toBe(0)
    expect(wrapper.find('.pv-scrollbar').exists()).toBe(false)
  })

  it('fills the stage behind the frame with the page background', async () => {
    await mountAt(0)
    expect(wrapper.find('.pv-stage').attributes('style')).toContain('background-color: rgb(250, 249, 246)')
  })
})

describe('WorkspacePreview scrollbar', () => {
  let wrapper: VueWrapper

  beforeEach(async () => {
    HTMLImageElement.prototype.decode = () => Promise.resolve()
    start.mockResolvedValue({ frame: 'AAAA', etag: 'a', viewport: [320, 320], scroll: scrollAt(840) })
    frame.mockResolvedValue({ frame: null, etag: 'a' })
    pages.mockResolvedValue([])
    resize.mockResolvedValue({})
    sendInput.mockReturnValue(new Promise(() => {}))
    wrapper = mount(WorkspacePreview, { props: { projectId: '7' } })
    await settle()
  })

  afterEach(() => {
    wrapper.unmount()
    vi.restoreAllMocks()
    start.mockReset(); frame.mockReset(); sendInput.mockReset()
  })

  function thumbAt(): number {
    const style = wrapper.find('.pv-scrollbar-thumb').attributes('style') || ''
    const m = style.match(/--pv-thumb-at: ([\d.]+)/)
    return m ? Number(m[1]) : NaN
  }

  it('sizes and places the thumb from the page', () => {
    const style = wrapper.find('.pv-scrollbar-thumb').attributes('style') || ''
    expect(style).toContain('--pv-thumb-size: 16.000%')
    expect(thumbAt()).toBeCloseTo(0.5)
  })

  it('moves with a wheel scroll before the server answers', async () => {
    await wrapper.find('.pv-stage').trigger('wheel', { deltaY: 840, deltaMode: 0 })
    await flushPromises()
    expect(thumbAt()).toBeCloseTo(1)
  })

  it('pressing the track scrolls the page there without clicking the page', async () => {
    // jsdom lays nothing out, so a press anywhere reads as the very bottom.
    wrapper.find('.pv-scrollbar').element.dispatchEvent(
      new MouseEvent('pointerdown', { clientY: 50, button: 0, bubbles: true }),
    )
    await settle()
    const events = sendInput.mock.calls[0][1]
    expect(events).toEqual([{ kind: 'scroll', y: 1680 }])
    // The page moves at once (by up to a screenful; that is where it caps).
    expect(translateY(wrapper)).toBeLessThan(0)
  })
})

describe('WorkspacePreview page menu', () => {
  let wrapper: VueWrapper

  beforeEach(async () => {
    HTMLImageElement.prototype.decode = () => Promise.resolve()
    start.mockResolvedValue({ frame: 'AAAA', etag: 'a', path: '/about', viewport: [320, 320] })
    frame.mockResolvedValue({ frame: null, etag: 'a' })
    resize.mockResolvedValue({})
    pages.mockResolvedValue([
      { name: 'home', pages: [{ path: '/', title: 'Home' }, { path: '/about', title: 'About' }] },
      { name: 'auth', pages: [{ path: '/auth/signin', title: 'Sign in' }] },
    ])
    wrapper = mount(WorkspacePreview, { props: { projectId: '7' }, attachTo: document.body })
    await settle()
  })

  afterEach(() => {
    wrapper.unmount()
    start.mockReset(); frame.mockReset(); pages.mockReset()
  })

  it('names the current page by its section and title', () => {
    expect(wrapper.find('.pv-plate').text()).toBe('home/About')
  })

  it('opens with every section expanded and lists pages by name, not path', async () => {
    await wrapper.find('.pv-plate').trigger('click')
    await flushPromises()

    const files = wrapper.findAll('.pv-file').map(f => f.text())
    expect(files).toEqual(['Home', 'AboutViewing', 'Sign in'])
    expect(wrapper.find('.pv-menu').text()).not.toContain('/auth/signin')
    expect(wrapper.find('.pv-menu-count').text()).toBe('3')
  })
})
