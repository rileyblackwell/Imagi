import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'

vi.mock('vue-router', () => ({ useRouter: () => ({ push: vi.fn() }) }))
vi.mock('@/shared/stores/auth', () => ({ useAuthStore: () => ({ isAuthenticated: false }) }))

import HeroSection, { EXAMPLES } from '../HeroSection.vue'

const stubs = { LineIcon: true }

function mockReducedMotion(reduce: boolean) {
  vi.stubGlobal('matchMedia', (q: string) => ({ matches: reduce && q.includes('reduce'), addEventListener() {}, removeEventListener() {} }))
}

describe('HeroSection', () => {
  beforeEach(() => vi.useFakeTimers())
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it('keeps the headline and the accented "run"', () => {
    mockReducedMotion(true)
    const wrapper = mount(HeroSection, { global: { stubs } })
    expect(wrapper.find('h1').text()).toBe('Build and run your business')
    expect(wrapper.find('.hero-accent').text()).toBe('run')
  })

  it('opens with the marquee label, its lit rule hidden from screen readers', () => {
    mockReducedMotion(true)
    const label = mount(HeroSection, { global: { stubs } }).find('.sl-pill')
    expect(label.text()).toBe('The all-in-one business platform')
    expect(label.find('.sl-pip').attributes('aria-hidden')).toBe('true')
  })

  it('has nothing below the prompt but its own meta line', () => {
    mockReducedMotion(true)
    expect(mount(HeroSection, { global: { stubs } }).find('.outputs').exists()).toBe(false)
  })

  it('keeps the hero free of product shots', () => {
    mockReducedMotion(true)
    expect(mount(HeroSection, { global: { stubs } }).find('img').exists()).toBe(false)
  })

  it('keeps a plain instruction in the box when motion is reduced', async () => {
    mockReducedMotion(true)
    const wrapper = mount(HeroSection, { global: { stubs } })
    vi.advanceTimersByTime(20000)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('textarea').attributes('placeholder')).toBe('Describe the business you want to start…')
  })

  it('types the example into the placeholder, and stops as soon as the visitor engages', async () => {
    mockReducedMotion(false)
    const wrapper = mount(HeroSection, { global: { stubs } })
    vi.advanceTimersByTime(1500)
    await wrapper.vm.$nextTick()
    const partial = wrapper.find('textarea').attributes('placeholder')!
    expect(EXAMPLES[0].startsWith(partial)).toBe(true)
    expect(partial.length).toBeLessThan(EXAMPLES[0].length)

    await wrapper.find('textarea').trigger('focus')
    vi.advanceTimersByTime(30000)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('textarea').attributes('placeholder')).toBe('Describe the business you want to start…')
  })
})
