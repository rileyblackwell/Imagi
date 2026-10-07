import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

vi.mock('vue-router', () => ({ useRouter: () => ({ push: vi.fn() }) }))
vi.mock('@/shared/stores/auth', () => ({ useAuthStore: () => ({ isAuthenticated: false }) }))

import ClosingSection from '../ClosingSection.vue'

const stubs = { RouterLink: { props: ['to'], template: '<a :href="to"><slot /></a>' } }
const directives = { reveal: {} }

describe('ClosingSection', () => {
  const wrapper = () => mount(ClosingSection, { global: { stubs, directives } })

  it('closes on the same prompt the hero opens with', () => {
    const w = wrapper()
    expect(w.find('h2').text()).toBe('Start your business today')
    expect(w.find('textarea#closing-idea').exists()).toBe(true)
    expect(w.find('button[type="submit"]').text()).toContain('Start building')
  })

  it('keeps pricing one quiet link away, with the free-plan footnote', () => {
    const w = wrapper()
    expect(w.find('a').attributes('href')).toBe('/payments/pricing')
    expect(w.text()).toContain('Start for free. Upgrade anytime as you grow.')
  })
})
