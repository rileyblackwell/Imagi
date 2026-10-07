import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

vi.mock('@/apps/home/services/healthService', () => ({
  checkBackendHealth: vi.fn().mockResolvedValue({ status: 'ok', database: 'ok' })
}))

import Home from '../Home.vue'

const stubs = {
  DefaultLayout: { template: '<div class="layout"><slot /></div>' },
  HeroSection: true,
  StatsSection: true,
  FeaturesSection: true,
  KeyFeaturesSection: true,
  ClosingSection: true
}

describe('Home (Spotlight)', () => {
  it('renders the page, navbar and footer included, on the dark Spotlight stage', () => {
    const root = mount(Home, { global: { stubs } }).element as HTMLElement
    expect(root.classList.contains('spotlight')).toBe(true)
    // `dark` sits on the same wrapper so the shared navbar and footer use
    // their dark variants here whatever the visitor's saved theme is.
    expect(root.classList.contains('dark')).toBe(true)
    expect(root.querySelector('.layout')).not.toBeNull()
  })

  it('keeps the sections in order and closes on the Spotlight closing section', () => {
    const html = mount(Home, { global: { stubs } }).html()
    const order = ['hero-section', 'stats-section', 'features-section', 'key-features-section', 'closing-section']
      .map((tag) => html.indexOf(`<${tag}-stub`))
    expect(order.every((i) => i >= 0)).toBe(true)
    expect([...order].sort((a, b) => a - b)).toEqual(order)
  })
})
