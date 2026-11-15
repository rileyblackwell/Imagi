import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SubscriptionTierCard from '../SubscriptionTierCard.vue'

const free = {
  name: 'Free',
  price: 0,
  cta: 'Start building',
  weeklyLimit: '$20 of usage per week',
  features: ['Unlimited projects'],
}

describe('SubscriptionTierCard', () => {
  it('shows the plan, its weekly allowance and its features', () => {
    const wrapper = mount(SubscriptionTierCard, { props: free })
    expect(wrapper.find('.tier__name').text()).toBe('Free')
    expect(wrapper.text()).toContain('$0')
    expect(wrapper.find('.tier__limits dd').text()).toBe('$20 of usage per week')
    expect(wrapper.text()).toContain('Unlimited projects')
  })

  it('emits start from its button', async () => {
    const wrapper = mount(SubscriptionTierCard, { props: free })
    const cta = wrapper.find('button.tier__cta')
    expect(cta.text()).toBe('Start building')
    await cta.trigger('click')
    expect(wrapper.emitted('start')).toHaveLength(1)
  })
})
