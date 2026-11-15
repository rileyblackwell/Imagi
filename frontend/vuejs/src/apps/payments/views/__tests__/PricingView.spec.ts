import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'

const push = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push }) }))

import PricingView from '../PricingView.vue'

const stubs = {
  PaymentLayout: { template: '<div class="layout"><slot /></div>' },
}

describe('PricingView (Free is the only plan)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    push.mockClear()
  })

  const wrapper = () => mount(PricingView, { global: { stubs } })

  it('shows only the Free plan, with its $20 weekly allowance and no project limit', () => {
    const w = wrapper()
    const names = w.findAll('.tier__name').map((n) => n.text())
    expect(names).toEqual(['Free'])
    expect(w.find('.tier__limits dd').text()).toBe('$20 of usage per week')
    expect(w.text()).toContain('Unlimited projects')
    expect(w.text()).not.toContain('Pro')
    expect(w.text()).not.toContain('Max')
  })

  it('sells nothing and says how the weekly allowance works', () => {
    const w = wrapper()
    expect(w.find('h1').text()).toBe('Imagi is free')
    expect(w.text()).not.toContain('Stripe')
    expect(w.text()).not.toContain('no weekly limit')
    expect(w.text()).toContain('rolling 7 days')
  })

  it('sends a signed-out visitor to sign up', async () => {
    await wrapper().find('button.tier__cta').trigger('click')
    expect(push).toHaveBeenCalledWith({ path: '/auth/register' })
  })
})
