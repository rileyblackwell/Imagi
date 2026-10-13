import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises, type VueWrapper } from '@vue/test-utils'

const { start, status, logs, action, pages } = vi.hoisted(() => ({
  start: vi.fn(),
  status: vi.fn(),
  logs: vi.fn(),
  action: vi.fn(),
  pages: vi.fn(),
}))

vi.mock('../../../../services/livePreviewService', async (importOriginal) => {
  const real = await importOriginal<typeof import('../../../../services/livePreviewService')>()
  return { ...real, LivePreviewService: { start, status, logs, action, mode: vi.fn() } }
})
vi.mock('../../../../services/previewService', () => ({
  PreviewService: { pages },
}))

import LivePreview from '../LivePreview.vue'

const ORIGIN = 'https://preview.example'
const SESSION = {
  running: true, mode: 'live', origin: ORIGIN, base: '/s/tok/', url: `${ORIGIN}/s/tok/`, cold: false,
}

const settle = async () => {
  await new Promise((r) => setTimeout(r, 5))
  await flushPromises()
}

describe('LivePreview', () => {
  let wrapper: VueWrapper

  function frameWindow() {
    return (wrapper.find('iframe').element as HTMLIFrameElement).contentWindow!
  }

  /** A message as the bridge in the iframe would post it. */
  async function fromApp(data: Record<string, unknown>, origin = ORIGIN, source: Window | null = frameWindow()) {
    window.dispatchEvent(new MessageEvent('message', { data: { source: 'imagi-preview', ...data }, origin, source }))
    await settle()
  }

  beforeEach(async () => {
    start.mockResolvedValue(SESSION)
    status.mockResolvedValue({ running: true, backend: { state: 'ready' }, frontend: { state: 'ready' } })
    pages.mockResolvedValue([])
    wrapper = mount(LivePreview, { props: { projectId: '7' }, attachTo: document.body })
    await settle()
    await fromApp({ type: 'ready', path: '/', title: 'Demo' })
  })

  afterEach(() => {
    wrapper.unmount()
    vi.clearAllMocks()
  })

  it('shows the app on the preview origin, sandboxed', () => {
    const frame = wrapper.find('iframe')
    expect(frame.attributes('src')).toBe(`${ORIGIN}/s/tok/`)
    expect(frame.attributes('sandbox')).toContain('allow-scripts')
    expect(frame.attributes('sandbox')).not.toContain('allow-top-navigation')
  })

  it('follows the app as it navigates', async () => {
    await fromApp({ type: 'nav', path: '/about', title: 'About', canGoBack: true, canGoForward: false })
    expect((wrapper.find('.lp-address-input').element as HTMLInputElement).value).toBe('/about')
    expect(wrapper.find('button[aria-label=Back]').attributes('disabled')).toBeUndefined()
  })

  it('ignores messages from other origins and windows', async () => {
    await fromApp({ type: 'nav', path: '/evil', canGoBack: false, canGoForward: false }, 'https://evil.example')
    await fromApp({ type: 'nav', path: '/evil', canGoBack: false, canGoForward: false }, ORIGIN, window)
    expect((wrapper.find('.lp-address-input').element as HTMLInputElement).value).toBe('/')
  })

  it('sends a typed address to the app, only to its origin', async () => {
    const post = vi.spyOn(frameWindow(), 'postMessage')
    const input = wrapper.find('.lp-address-input')
    await input.trigger('focus')
    await input.setValue('contact')
    await input.trigger('keydown', { key: 'Enter' })
    expect(post).toHaveBeenCalledWith({ target: 'imagi-preview', cmd: 'navigate', path: '/contact' }, ORIGIN)
  })

  it('sends an error the app logs straight on, with no Fix it button', async () => {
    status.mockResolvedValue({
      running: true, backend: { state: 'ready' }, frontend: { state: 'ready' },
      error_routing: { to: 'coordinator', conversation_id: 5, new: true },
    })
    await fromApp({ type: 'console', level: 'error', text: 'TypeError: boom', ts: Date.now() })
    await new Promise((r) => setTimeout(r, 350))
    await flushPromises()
    // The error went out with the next status poll, nobody pressing anything.
    const sent = status.mock.calls.map((call) => call[1]).flat()
    expect(sent.some((e: { text: string }) => e?.text === 'TypeError: boom')).toBe(true)
    expect(wrapper.emitted('errors-routed')?.[0]?.[0]).toEqual({ to: 'coordinator', conversation_id: 5, new: true })
    const banner = wrapper.find('[role=alert]')
    expect(banner.text()).toContain('TypeError: boom')
    expect(banner.text()).toContain('Sent to the coordinator')
    expect(banner.text()).not.toContain('Fix it')
  })

  it("doesn't treat a dropped live-reload socket as the app breaking", async () => {
    await fromApp({ type: 'console', level: 'error', text: '[vite] failed to connect to websocket.', ts: Date.now() })
    expect(wrapper.find('[role=alert]').exists()).toBe(false)
  })

  it('keeps the app behind a building notice until the home page lands, then loads it fresh', async () => {
    await wrapper.setProps({ building: true })
    await settle()
    const veil = wrapper.find('[data-testid=building-veil]')
    expect(veil.exists()).toBe(true)
    expect(veil.text()).toContain('Building your home page')
    // The servers came up underneath meanwhile.
    expect(veil.findAll('.lp-stage-row')[1]!.classes()).toContain('is-done')

    const before = wrapper.find('iframe').element
    await wrapper.setProps({ building: false })
    await settle()
    // A fresh frame for the finished page; the notice stays until it loads.
    expect(wrapper.find('iframe').element).not.toBe(before)
    expect(wrapper.find('[data-testid=building-veil]').exists()).toBe(true)
    await fromApp({ type: 'ready', path: '/', title: 'Demo' })
    expect(wrapper.find('[data-testid=building-veil]').exists()).toBe(false)
  })

  it('opens as soon as the home page is hot-swapped in, without reloading the frame', async () => {
    await wrapper.setProps({ building: true })
    await settle()
    const before = wrapper.find('iframe').element
    // Another file changing doesn't open it.
    await fromApp({ type: 'hmr', files: ['/src/apps/home/site-pages.ts'] })
    expect(wrapper.find('[data-testid=building-veil]').exists()).toBe(true)
    await fromApp({ type: 'hmr', files: ['/src/apps/home/views/HomeView.vue'] })
    expect(wrapper.find('[data-testid=building-veil]').exists()).toBe(false)
    // The build's status catching up leaves the open app alone.
    await wrapper.setProps({ building: false })
    await settle()
    expect(wrapper.find('iframe').element).toBe(before)
    expect(wrapper.find('[data-testid=building-veil]').exists()).toBe(false)
  })

  it("doesn't let a status poll sent before the app started stop it", async () => {
    wrapper.unmount()
    let started!: (s: typeof SESSION) => void
    let answered!: (s: Record<string, unknown>) => void
    start.mockReturnValue(new Promise((r) => { started = r }))
    status.mockReturnValue(new Promise((r) => { answered = r }))
    wrapper = mount(LivePreview, { props: { projectId: '7', building: true }, attachTo: document.body })
    // The start-progress poll goes out while the servers are still coming up.
    await new Promise((r) => setTimeout(r, 350))
    await flushPromises()
    expect(status).toHaveBeenCalled()
    started(SESSION)
    await settle()
    answered({ running: false })
    await settle()
    expect(wrapper.find('iframe').exists()).toBe(true)
    await wrapper.setProps({ building: false })
    await settle()
    await fromApp({ type: 'ready', path: '/', title: 'Demo' })
    expect(wrapper.find('[data-testid=building-veil]').exists()).toBe(false)
  })

  it('keeps the building notice up when the home page lands before the app has started', async () => {
    wrapper.unmount()
    let started!: (s: typeof SESSION) => void
    start.mockReturnValue(new Promise((r) => { started = r }))
    wrapper = mount(LivePreview, { props: { projectId: '7', building: true }, attachTo: document.body })
    await settle()
    await wrapper.setProps({ building: false })
    await settle()
    const veil = wrapper.find('[data-testid=building-veil]')
    expect(veil.exists()).toBe(true)
    expect(veil.findAll('.lp-stage-row')[0]!.classes()).toContain('is-done')

    started(SESSION)
    await settle()
    await fromApp({ type: 'ready', path: '/', title: 'Demo' })
    expect(wrapper.find('[data-testid=building-veil]').exists()).toBe(false)
  })

  it('follows an agent using the app in its own browser, and says who', async () => {
    // A status poll on demand: the page coming back into view asks for one.
    const poll = async () => {
      document.dispatchEvent(new Event('visibilitychange'))
      await settle()
    }
    const post = vi.spyOn(frameWindow(), 'postMessage')
    const ready = { running: true, backend: { state: 'ready' }, frontend: { state: 'ready' } }
    status.mockResolvedValue({ ...ready, agent: { path: '/book', action: 'left_click', label: 'Coordinator', at: 1 } })
    await poll()
    expect(post).toHaveBeenCalledWith({ target: 'imagi-preview', cmd: 'navigate', path: '/book' }, ORIGIN)
    expect(wrapper.find('[data-testid=agent-note]').text()).toBe('Coordinator is clicking')

    // The same action again doesn't pull the person back if they moved on.
    post.mockClear()
    await fromApp({ type: 'nav', path: '/faq', title: 'FAQ', canGoBack: true, canGoForward: false })
    await poll()
    expect(post).not.toHaveBeenCalledWith(expect.objectContaining({ cmd: 'navigate' }), ORIGIN)

    status.mockResolvedValue({ ...ready, agent: null })
    await poll()
    expect(wrapper.find('[data-testid=agent-note]').exists()).toBe(false)
  })

  it('turns a picked element into context for the agent', async () => {
    await fromApp({
      type: 'picked', path: '/about',
      element: { tag: 'h1', id: '', classes: '', text: 'About', component: 'AboutView', chain: ['AboutView'], file: 'src/AboutView.vue' },
    })
    const text = wrapper.emitted('pick-element')?.[0]?.[0] as string
    expect(text).toContain('/about')
    expect(text).toContain('AboutView')
  })
})
