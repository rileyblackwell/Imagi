import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('vue-router', () => ({ useRouter: () => ({ push: vi.fn() }) }))
vi.mock('../../services/payment_service', () => ({ default: class {} }))

import PricingView from '../PricingView.vue'

const stubs = {
  PaymentLayout: { template: '<div class="layout"><slot /></div>' },
}

describe('PricingView (one open Free plan)', () => {
  beforeEach(() => setActivePinia(createPinia()))

  const wrapper = () => mount(PricingView, { global: { stubs } })

  it('shows only the Free plan, with no usage or project limit', () => {
    const w = wrapper()
    const names = w.findAll('.tier__name').map((n) => n.text())
    expect(names).toEqual(['Free'])
    expect(w.find('.tier__limits dd').text()).toBe('Unlimited usage')
    expect(w.text()).toContain('Unlimited projects')
    expect(w.text()).not.toContain('Pro')
    expect(w.text()).not.toContain('Max')
  })

  it('drops the Stripe checkout line while nothing is for sale', () => {
    const w = wrapper()
    expect(w.find('h1').text()).toBe('Imagi is free')
    expect(w.find('.pricing-stripe').exists()).toBe(false)
  })
})
