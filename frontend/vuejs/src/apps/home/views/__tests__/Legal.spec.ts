import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TermsOfService from '../TermsOfService.vue'
import PrivacyPolicy from '../PrivacyPolicy.vue'

const stubs = {
  DefaultLayout: { template: '<div class="layout"><slot /></div>' },
  ClosingSection: { props: ['title', 'secondaryButtonTo'], template: '<div class="closing-stub">{{ title }} {{ secondaryButtonTo }}</div>' }
}

describe.each([
  ['Terms of Service', TermsOfService, '/privacy'],
  ['Privacy Policy', PrivacyPolicy, '/terms']
])('%s (Spotlight)', (title, page, sibling) => {
  const wrapper = () => mount(page, { global: { stubs } })

  it('sits on the Spotlight stage and follows the site theme', () => {
    const root = wrapper().element as HTMLElement
    expect(root.classList.contains('spotlight')).toBe(true)
    expect(root.classList.contains('dark')).toBe(false)
  })

  it('opens under the light with its title and the date it was last updated', () => {
    const w = wrapper()
    expect(w.find('.sl-opener h1').text()).toBe(title)
    expect(w.find('.legal-updated').text()).toMatch(/^Last updated: /)
  })

  it('keeps the legal text as numbered prose sections', () => {
    const w = wrapper()
    expect(w.findAll('.prose h2').length).toBeGreaterThan(5)
    expect(w.find('.prose .sec-num').text()).toBe('Section 01')
  })

  it('closes on the Spotlight prompt, linking to the other policy', () => {
    expect(wrapper().find('.closing-stub').text()).toBe(`Ready to start? ${sibling}`)
  })
})

describe('Legal text matches how Imagi works today', () => {
  const text = (page: unknown) => mount(page as never, { global: { stubs } }).find('.prose').text()

  it('names the outside services that receive user data', () => {
    const privacy = text(PrivacyPolicy)
    for (const provider of ['Anthropic', 'OpenAI', 'Stripe', 'Railway', 'Twilio']) {
      expect(privacy).toContain(provider)
    }
    expect(privacy).toContain('do not sell your personal information')
  })

  it('numbers every section, with no unnumbered tail', () => {
    for (const page of [PrivacyPolicy, TermsOfService]) {
      const eyebrows = mount(page, { global: { stubs } }).findAll('.prose .sec-num').map(n => n.text())
      expect(eyebrows.every(e => /^Section \d\d$/.test(e))).toBe(true)
    }
  })

  it('does not promise publishing apps, and marks the business tools as beta', () => {
    const terms = text(TermsOfService)
    expect(terms).toContain('publishing your app to the internet from Imagi is not available yet')
    expect(terms).toContain('Sell, Market and Operate are in beta')
  })
})
