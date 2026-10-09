import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import About from '../About.vue'

const stubs = {
  DefaultLayout: { template: '<div class="layout"><slot /></div>' },
  ClosingSection: { props: ['title', 'secondaryButtonTo'], template: '<div class="closing-stub">{{ title }} {{ secondaryButtonTo }}</div>' },
  ProductShot: { props: ['src'], template: '<img class="shot-stub" :src="src" />' },
  StatusBadge: { props: ['label'], template: '<span class="badge-stub">{{ label }}</span>' },
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

  it('opens with its own headline, one word lit', () => {
    const w = wrapper()
    expect(w.find('h1').text()).toBe('An idea is enough')
    expect(w.find('h1 .sl-run').text()).toBe('enough')
  })

  it('walks through why, start, build, run and plans, in the homepage order', () => {
    const w = wrapper()
    expect(w.findAll('h2').map((h) => h.text())).toEqual([
      'Building the app shouldn’t be the hard part',
      'From a brief to a first version',
      'How the workspace works',
      'The business side, in the same project',
      'What it costs, and what’s next'
    ])
  })

  it('names the first build, the workspace and the three tools', () => {
    const w = wrapper()
    const rowTitles = w.findAll('.about-row__title').map((t) => t.text())
    expect(rowTitles).toContain('The home page')
    expect(rowTitles).toContain('The coordinator')
    expect(rowTitles).toContain('Threads')
    expect(w.findAll('.sl-card__title').map((t) => t.text())).toEqual(['Sell', 'Market', 'Operate'])
  })

  it('labels the run tools Beta and shows one workspace shot', () => {
    const w = wrapper()
    expect(w.find('.badge-stub').text()).toBe('Beta')
    expect(w.findAll('.shot-stub').map((s) => s.attributes('src'))).toEqual(['/product/build-workspace.webp'])
  })

  it('never promises deploying', () => {
    const text = wrapper().text().toLowerCase()
    expect(text).not.toMatch(/one-click deploy|put it online|deploy to/)
    expect(text).toContain('publishing your app to the web from imagi isn’t available yet')
  })

  it('closes on the Spotlight prompt, pointing at the docs', () => {
    expect(wrapper().find('.closing-stub').text()).toBe('Try it on your idea /docs')
  })
})
