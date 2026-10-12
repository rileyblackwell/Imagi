import { describe, it, expect } from 'vitest'
import { normalizeAddress, parseBridgeMessage } from '../livePreviewService'

describe('parseBridgeMessage', () => {
  it('ignores anything that is not from the bridge', () => {
    expect(parseBridgeMessage(null)).toBeNull()
    expect(parseBridgeMessage('nav')).toBeNull()
    expect(parseBridgeMessage({ type: 'nav', path: '/' })).toBeNull()
    expect(parseBridgeMessage({ source: 'imagi-preview', type: 'eval', code: 'x' })).toBeNull()
  })

  it('keeps only well-formed fields', () => {
    expect(parseBridgeMessage({ source: 'imagi-preview', type: 'nav', path: 7, canGoBack: 'yes', canGoForward: true }))
      .toEqual({ type: 'nav', path: '/', title: '', canGoBack: false, canGoForward: true })
    expect(parseBridgeMessage({ source: 'imagi-preview', type: 'console', level: 'alert', text: 'hi', ts: 5 }))
      .toEqual({ type: 'console', level: 'log', text: 'hi', ts: 5 })
    const net = parseBridgeMessage({ source: 'imagi-preview', type: 'net', id: 1, method: 'post', url: '/api/x', status: 500, ms: 12 })
    expect(net).toEqual({ type: 'net', id: 1, method: 'POST', url: '/api/x', status: 500, ms: 12 })
  })

  it('clips long text the page sends', () => {
    const msg = parseBridgeMessage({ source: 'imagi-preview', type: 'console', level: 'error', text: 'x'.repeat(10000) })
    expect(msg && msg.type === 'console' && msg.text.length).toBe(4000)
  })

  it('reads a picked element, or a cancelled pick', () => {
    expect(parseBridgeMessage({ source: 'imagi-preview', type: 'picked', element: null })).toEqual({ type: 'picked', element: null })
    const picked = parseBridgeMessage({
      source: 'imagi-preview', type: 'picked', path: '/about',
      element: { tag: 'h1', id: '', classes: 'title', text: 'About', component: 'AboutView', chain: ['AboutView', 3], file: 'src/About.vue' },
    })
    expect(picked).toMatchObject({ type: 'picked', path: '/about', element: { tag: 'h1', chain: ['AboutView'], file: 'src/About.vue' } })
  })
})

describe('normalizeAddress', () => {
  it('turns what was typed into an in-app path', () => {
    expect(normalizeAddress('')).toBe('/')
    expect(normalizeAddress('  about ')).toBe('/about')
    expect(normalizeAddress('/shop?x=1#top')).toBe('/shop?x=1#top')
    expect(normalizeAddress('https://anything.example/pricing?a=1')).toBe('/pricing?a=1')
  })

  it('never leaves the app', () => {
    expect(normalizeAddress('//evil.example/')).toBe('/')
    expect(normalizeAddress('/\\evil.example')).toBe('/')
  })
})
