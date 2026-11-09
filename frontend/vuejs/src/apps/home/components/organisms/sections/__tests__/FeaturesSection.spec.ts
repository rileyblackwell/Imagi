import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import FeaturesSection, { TOUR_HOLD_MS } from '../FeaturesSection.vue'

const stubs = { ProductShot: true, LineIcon: true }
const directives = { reveal: {} }

// The tour only plays while it is on screen, so the tests drive the observer.
let onScreen: (visible: boolean) => void = () => {}
class FakeObserver {
  constructor(cb: (entries: { isIntersecting: boolean }[]) => void) {
    onScreen = (visible) => cb([{ isIntersecting: visible }])
  }
  observe() {}
  disconnect() {}
}

function mockReducedMotion(reduce: boolean) {
  vi.stubGlobal('matchMedia', (q: string) => ({ matches: reduce && q.includes('reduce') }))
}

describe('FeaturesSection (step 02, the workspace tour)', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.stubGlobal('IntersectionObserver', FakeObserver)
    onScreen = () => {}
  })
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  const wrapper = () => mount(FeaturesSection, { global: { stubs, directives } })
  const open = (w: ReturnType<typeof wrapper>) =>
    w.findAll('.tour__tab').map((t) => t.attributes('aria-expanded'))
  const shot = (w: ReturnType<typeof wrapper>) => w.find('product-shot-stub')

  it('names the three things the workspace does, in order', () => {
    mockReducedMotion(true)
    const titles = wrapper().findAll('.tour__tab').map((t) => t.text())
    expect(titles).toEqual(['Just say what you want', 'Threads do the work', 'A live app beside you'])
  })

  it('opens the first item and keeps the others folded', () => {
    mockReducedMotion(true)
    expect(open(wrapper())).toEqual(['true', 'false', 'false'])
  })

  it('ties each tab to its panel', () => {
    mockReducedMotion(true)
    const w = wrapper()
    w.findAll('.tour__tab').forEach((tab, i) => {
      expect(tab.attributes('aria-controls')).toBe(`tour-panel-${i}`)
      expect(w.find(`#tour-panel-${i}`).attributes('aria-labelledby')).toBe(tab.attributes('id'))
    })
  })

  it('opens the item the visitor picks, and its caption follows', async () => {
    mockReducedMotion(true)
    const w = wrapper()
    await w.findAll('.tour__tab')[1].trigger('click')
    expect(open(w)).toEqual(['false', 'true', 'false'])
    expect(shot(w).attributes('caption')).toContain('two threads')
  })

  it('shows the one workspace screenshot throughout', async () => {
    mockReducedMotion(true)
    const w = wrapper()
    expect(shot(w).attributes('src')).toBe('/product/build-workspace.webp')
    await w.findAll('.tour__tab')[2].trigger('click')
    expect(w.findAll('product-shot-stub')).toHaveLength(1)
  })

  it('plays itself only while on screen', async () => {
    mockReducedMotion(false)
    const w = wrapper()
    vi.advanceTimersByTime(TOUR_HOLD_MS * 2)
    await w.vm.$nextTick()
    expect(open(w)).toEqual(['true', 'false', 'false'])

    onScreen(true)
    vi.advanceTimersByTime(TOUR_HOLD_MS)
    await w.vm.$nextTick()
    expect(open(w)).toEqual(['false', 'true', 'false'])

    onScreen(false)
    vi.advanceTimersByTime(TOUR_HOLD_MS * 3)
    await w.vm.$nextTick()
    expect(open(w)).toEqual(['false', 'true', 'false'])
  })

  it('wraps round to the first item after the last', async () => {
    mockReducedMotion(false)
    const w = wrapper()
    onScreen(true)
    vi.advanceTimersByTime(TOUR_HOLD_MS * 3)
    await w.vm.$nextTick()
    expect(open(w)).toEqual(['true', 'false', 'false'])
  })

  it('stops playing for good once the visitor picks an item', async () => {
    mockReducedMotion(false)
    const w = wrapper()
    onScreen(true)
    await w.findAll('.tour__tab')[2].trigger('click')
    vi.advanceTimersByTime(TOUR_HOLD_MS * 4)
    await w.vm.$nextTick()
    expect(open(w)).toEqual(['false', 'false', 'true'])
  })

  it('never plays under reduced motion', async () => {
    mockReducedMotion(true)
    const w = wrapper()
    onScreen(true)
    vi.advanceTimersByTime(TOUR_HOLD_MS * 4)
    await w.vm.$nextTick()
    expect(open(w)).toEqual(['true', 'false', 'false'])
  })
})
