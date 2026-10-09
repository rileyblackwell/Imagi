import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'

const { start, frame, sendInput, pages, resize, backdrop } = vi.hoisted(() => ({
  backdrop: vi.fn(() => Promise.reject(new Error('no backdrop in this test'))),
  start: vi.fn(),
  frame: vi.fn(),
  sendInput: vi.fn(),
  pages: vi.fn(),
  resize: vi.fn(),
}))

vi.mock('../../../../services/previewService', () => ({
  PreviewService: { start, frame, sendInput, pages, resize, backdrop, navigate: vi.fn() },
  PreviewNotRunningError: class extends Error {},
}))

import WorkspacePreview from '../WorkspacePreview.vue'

const settle = async () => {
  await new Promise(r => setTimeout(r, 5))
  await flushPromises()
}

function translateY(wrapper: VueWrapper): number {
  const style = wrapper.find('img.pv-live').attributes('style') || ''
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
    expect(wrapper.find('img.pv-live').attributes('src')).toContain('BBBB')
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
    expect(wrapper.find('img.pv-live').attributes('src')).toContain('BBBB')
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

describe('WorkspacePreview frame sharpness', () => {
  let wrapper: VueWrapper

  beforeEach(() => {
    HTMLImageElement.prototype.decode = () => Promise.resolve()
    frame.mockResolvedValue({ frame: null, etag: 'a' })
    pages.mockResolvedValue([])
    resize.mockResolvedValue({})
  })

  afterEach(() => {
    wrapper.unmount()
    vi.restoreAllMocks()
    start.mockReset(); frame.mockReset(); resize.mockReset()
  })

  it('shows a lossless frame as PNG and others as JPEG', async () => {
    start.mockResolvedValue({ frame: 'PNG0', frame_type: 'png', etag: 'a', viewport: [320, 320], scroll: scrollAt(0) })
    wrapper = mount(WorkspacePreview, { props: { projectId: '7' } })
    await settle()
    expect(wrapper.find('img.pv-live').attributes('src')).toBe('data:image/png;base64,PNG0')

    frame.mockResolvedValue({ frame: 'JPG1', etag: 'b', scroll: scrollAt(0) })
    await new Promise(r => setTimeout(r, 250))
    await settle()
    expect(wrapper.find('img.pv-live').attributes('src')).toBe('data:image/jpeg;base64,JPG1')
  })

  it('draws the frame at the remote viewport size, never stretched to the pane', async () => {
    start.mockResolvedValue({ frame: 'AAAA', etag: 'a', viewport: [320, 320], scroll: scrollAt(0) })
    wrapper = mount(WorkspacePreview, { props: { projectId: '7' } })
    await settle()
    const style = wrapper.find('img.pv-live').attributes('style') || ''
    expect(style).toContain('width: 320px')
    expect(style).toContain('height: 320px')
    expect(style).not.toContain('object-fit')
  })

  it('resizes the remote viewport when the pane is off by a single pixel', async () => {
    vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({
      left: 0, top: 0, right: 641, bottom: 480, width: 641, height: 480, x: 0, y: 0, toJSON: () => ({}),
    } as DOMRect)
    start.mockResolvedValue({ frame: 'AAAA', etag: 'a', viewport: [640, 480], scroll: scrollAt(0) })
    wrapper = mount(WorkspacePreview, { props: { projectId: '7' } })
    await settle()
    await new Promise(r => requestAnimationFrame(() => r(null)))
    await settle()
    expect(resize).toHaveBeenCalledWith('7', 641, 480, expect.any(Number))
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

describe('WorkspacePreview backdrop', () => {
  let wrapper: VueWrapper

  beforeEach(async () => {
    HTMLImageElement.prototype.decode = () => Promise.resolve()
    start.mockResolvedValue({ frame: 'AAAA', etag: 'a', path: '/', viewport: [320, 320], scroll: scrollAt(0) })
    frame.mockResolvedValue({ frame: null, etag: 'a', path: '/', scroll: scrollAt(0) })
    pages.mockResolvedValue([])
    // jsdom has no layout, so a resize would adopt a made-up pane size; keep
    // the 320px viewport the backdrop was captured at.
    resize.mockRejectedValue(new Error('no layout'))
    backdrop.mockResolvedValue({
      path: '/',
      viewport: [320, 320],
      scroll: scrollAt(0),
      // The whole 2000px page in 320px slices; the last clamps at 1680.
      slices: [0, 320, 640, 960, 1280, 1600, 1680].map(y => ({ y, frame: `S${y}` })),
      overlay: 'HEADER',
    })
    wrapper = mount(WorkspacePreview, { props: { projectId: '7' } })
    // The first poll (200ms after start) finds the user idle and fetches it.
    await new Promise(r => setTimeout(r, 300))
    await flushPromises()
  })

  afterEach(() => {
    wrapper.unmount()
    vi.restoreAllMocks()
    start.mockReset(); frame.mockReset(); sendInput.mockReset(); backdrop.mockReset()
  })

  it('loads the page behind the frame once the user is idle', () => {
    expect(backdrop).toHaveBeenCalledTimes(1)
    expect(wrapper.findAll('.pv-backdrop-slice')).toHaveLength(7)
    // Settled: the frame itself is on screen, no overlay needed.
    expect(wrapper.find('img.pv-live').classes()).not.toContain('is-covered')
    expect(wrapper.find('.pv-backdrop-overlay').exists()).toBe(false)
  })

  it('scrolls through the backdrop until the frame catches up', async () => {
    let answer: (v: unknown) => void = () => {}
    sendInput.mockReturnValue(new Promise(r => { answer = r }))

    await wrapper.find('.pv-stage').trigger('wheel', { deltaY: 500, deltaMode: 0 })
    await flushPromises()
    expect(wrapper.find('img.pv-live').classes()).toContain('is-covered')
    expect(wrapper.find('.pv-backdrop').attributes('style')).toContain('translate3d(0, -500px, 0)')
    expect(wrapper.find('.pv-backdrop-overlay').attributes('src')).toContain('HEADER')

    answer({ frame: 'BBBB', etag: 'b', path: '/', scroll: scrollAt(500) })
    await settle()
    expect(wrapper.find('img.pv-live').classes()).not.toContain('is-covered')
    expect(wrapper.find('.pv-backdrop-overlay').exists()).toBe(false)
  })

  it('is set aside when the page changes', async () => {
    frame.mockResolvedValue({ frame: 'CCCC', etag: 'c', path: '/about', scroll: scrollAt(0) })
    backdrop.mockReturnValue(new Promise(() => {}))
    await new Promise(r => setTimeout(r, 1700))
    await flushPromises()
    expect(wrapper.find('.pv-backdrop').exists()).toBe(false)
  })
})


describe('WorkspacePreview error banner', () => {
  let wrapper: VueWrapper
  const error = { level: 'error', text: "TypeError: x is undefined", ts: 1 }

  beforeEach(() => {
    HTMLImageElement.prototype.decode = () => Promise.resolve()
    frame.mockResolvedValue({ frame: null, etag: 'a' })
    pages.mockResolvedValue([])
    resize.mockResolvedValue({})
  })

  afterEach(() => {
    wrapper.unmount()
    start.mockReset(); frame.mockReset()
  })

  async function mountWith(extra: Record<string, unknown>) {
    start.mockResolvedValue({
      frame: 'AAAA', etag: 'a', path: '/', viewport: [320, 320], scroll: scrollAt(0),
      console_errors: [error], ...extra,
    })
    wrapper = mount(WorkspacePreview, { props: { projectId: '7' } })
    await settle()
  }

  it('offers Fix it while nobody has the error yet', async () => {
    await mountWith({})
    expect(wrapper.find('.pv-alert').text()).toContain('Something broke in your app')
    expect(wrapper.find('.pv-alert').text()).toContain('Fix it')
  })

  it('says who is fixing an error the server already sent on', async () => {
    await mountWith({ error_routing: { to: 'thread', conversation_id: 12 } })
    const banner = wrapper.find('.pv-alert')
    expect(banner.text()).toContain('Imagi is fixing something in your app')
    expect(wrapper.find('[data-testid="error-routing-note"]').text()).toContain('the thread that just changed')
    expect(banner.text()).not.toContain('Fix it')
  })

  it('says a new thread is fixing an error no thread owned', async () => {
    await mountWith({ error_routing: { to: 'new_thread', conversation_id: 13 } })
    expect(wrapper.find('[data-testid="error-routing-note"]').text()).toBe('A new thread is fixing it.')
    expect(wrapper.find('.pv-alert').text()).not.toContain('Fix it')
  })
})

describe('WorkspacePreview opening onto a running session', () => {
  let wrapper: VueWrapper

  beforeEach(() => {
    HTMLImageElement.prototype.decode = () => Promise.resolve()
    pages.mockResolvedValue([])
    resize.mockResolvedValue({})
    // The start never answers in these tests: whatever shows came from the
    // frame endpoint alone.
    start.mockReturnValue(new Promise(() => {}))
  })

  afterEach(() => {
    wrapper.unmount()
    start.mockReset(); frame.mockReset()
  })

  // jsdom lays nothing out, so the pane measures as the 1280x800 fallback.
  it('shows a prewarmed preview without waiting for the start', async () => {
    frame.mockResolvedValue({ frame: 'WARM', etag: 'w', path: '/', viewport: [1280, 800], device_scale_factor: 1 })
    wrapper = mount(WorkspacePreview, { props: { projectId: '7' } })
    await settle()
    expect(wrapper.find('img.pv-live').attributes('src')).toContain('WARM')
  })

  it('waits for the start when the running preview is another size', async () => {
    frame.mockResolvedValue({ frame: 'SMALL', etag: 's', path: '/', viewport: [800, 600], device_scale_factor: 1 })
    wrapper = mount(WorkspacePreview, { props: { projectId: '7' } })
    await settle()
    expect(wrapper.find('img.pv-live').exists()).toBe(false)
  })

  it('waits for the start when nothing is running yet', async () => {
    frame.mockRejectedValue(new Error('not running'))
    wrapper = mount(WorkspacePreview, { props: { projectId: '7' } })
    await settle()
    expect(wrapper.find('img.pv-live').exists()).toBe(false)
  })
})
