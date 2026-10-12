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

  it('offers to fix an error the app logs', async () => {
    await fromApp({ type: 'console', level: 'error', text: 'TypeError: boom', ts: Date.now() })
    const banner = wrapper.find('[role=alert]')
    expect(banner.text()).toContain('TypeError: boom')
    await banner.find('button').trigger('click')
    expect(wrapper.emitted('fix-error')?.[0]?.[0]).toContain('TypeError: boom')
  })

  it("doesn't treat a dropped live-reload socket as the app breaking", async () => {
    await fromApp({ type: 'console', level: 'error', text: '[vite] failed to connect to websocket.', ts: Date.now() })
    expect(wrapper.find('[role=alert]').exists()).toBe(false)
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
