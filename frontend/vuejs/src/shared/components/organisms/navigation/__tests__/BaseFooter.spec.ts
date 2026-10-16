import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import BaseFooter from '../BaseFooter.vue'

const stubs = {
  ImagiLogo: true,
  RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' },
}

/**
 * The footer is a colophon: wordmark and one line, three short columns, and a
 * bottom line with the licence and the theme switch. It sits outside every
 * page's .spotlight root, so it carries its own.
 */
describe('BaseFooter', () => {
  const mountFooter = () => {
    setActivePinia(createPinia())
    return mount(BaseFooter, { global: { stubs } })
  }

  it('is its own Spotlight surface', () => {
    expect(mountFooter().find('footer').classes()).toContain('spotlight')
  })

  it('groups its links under Product, Company and Legal', () => {
    const w = mountFooter()
    expect(w.findAll('h2').map((h) => h.text())).toEqual(['Product', 'Company', 'Legal'])
    const hrefs = w.findAll('nav a').map((a) => a.attributes('href'))
    expect(hrefs).toEqual([
      '/imagi/projects',
      '/payments/pricing',
      '/docs',
      '/about',
      'https://github.com/rileyblackwell/imagi',
      '/privacy',
      '/terms',
    ])
  })

  it('opens the source code in a new tab', () => {
    const gh = mountFooter().find('a[href^="https://github.com"]')
    expect(gh.attributes('target')).toBe('_blank')
    expect(gh.attributes('rel')).toContain('noopener')
  })

  it('names the licence and offers the theme switch', () => {
    const w = mountFooter()
    expect(w.text()).toContain('MIT licensed')
    expect(w.findAll('[aria-label="Theme"] button').map((b) => b.text())).toEqual(['System', 'Light', 'Dark'])
  })
})
