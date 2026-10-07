import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import About from '../About.vue'

const stubs = {
  DefaultLayout: { template: '<div class="layout"><slot /></div>' },
  ClosingSection: { props: ['title', 'secondaryButtonTo'], template: '<div class="closing-stub">{{ title }} {{ secondaryButtonTo }}</div>' },
  LineIcon: true
}
const directives = { reveal: {} }

describe('About (Spotlight)', () => {
  const wrapper = () => mount(About, { global: { stubs, directives } })

  it('sits on the Spotlight stage and follows the site theme', () => {
    const root = wrapper().element as HTMLElement
    expect(root.classList.contains('spotlight')).toBe(true)
    expect(root.classList.contains('dark')).toBe(false)
  })

  it('keeps its headline, with "run" lit like the home page', () => {
    const w = wrapper()
    expect(w.find('h1').text()).toBe('Build and run a business')
    expect(w.find('h1 .sl-run').text()).toBe('run')
  })

  it('keeps all three sections and their cards', () => {
    const w = wrapper()
    expect(w.findAll('h2').map((h) => h.text())).toEqual([
      'Entrepreneurship, without the gatekeeping',
      'One platform, not a dozen subscriptions',
      'Anyone with an idea and no engineering queue'
    ])
    expect(w.findAll('.sl-card')).toHaveLength(3 + 3 + 4)
  })

  it('closes on the Spotlight prompt, pointing at the docs', () => {
    expect(wrapper().find('.closing-stub').text()).toBe('Ready to start? /docs')
  })
})
