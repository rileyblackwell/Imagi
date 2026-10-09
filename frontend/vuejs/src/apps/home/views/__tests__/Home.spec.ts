import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

vi.mock('@/apps/home/services/healthService', () => ({
  checkBackendHealth: vi.fn().mockResolvedValue({ status: 'ok', database: 'ok' })
}))

import Home from '../Home.vue'

const stubs = {
  DefaultLayout: { template: '<div class="layout"><slot /></div>' },
  HeroSection: true,
  StartSection: true,
  FeaturesSection: true,
  KeyFeaturesSection: true,
  ClosingSection: true
}

describe('Home (Spotlight)', () => {
  it('renders the page, navbar and footer included, on the Spotlight stage', () => {
    const root = mount(Home, { global: { stubs } }).element as HTMLElement
    expect(root.classList.contains('spotlight')).toBe(true)
    expect(root.querySelector('.layout')).not.toBeNull()
  })

  it('follows the site theme instead of forcing dark', () => {
    // The light and dark palettes both live in spotlight.css, keyed off the
    // `.dark` class the theme store puts on <html>.
    const root = mount(Home, { global: { stubs } }).element as HTMLElement
    expect(root.classList.contains('dark')).toBe(false)
  })

  it('keeps the sections in order and closes on the Spotlight closing section', () => {
    const html = mount(Home, { global: { stubs } }).html()
    const order = ['hero-section', 'start-section', 'features-section', 'key-features-section', 'closing-section']
      .map((tag) => html.indexOf(`<${tag}-stub`))
    expect(order.every((i) => i >= 0)).toBe(true)
    expect([...order].sort((a, b) => a - b)).toEqual(order)
  })
})
