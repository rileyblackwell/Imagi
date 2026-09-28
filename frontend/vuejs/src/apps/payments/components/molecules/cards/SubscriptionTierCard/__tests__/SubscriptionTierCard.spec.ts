import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SubscriptionTierCard from '../SubscriptionTierCard.vue'

const pro = { name: 'Pro', price: 25, lookupKey: 'pro_monthly', cta: 'Get started', weeklyLimit: '$15', features: [] }
const free = { name: 'Free', price: 0, lookupKey: null, cta: 'Start for free', weeklyLimit: '$5', features: [] }
const max = {
  name: 'Max',
  cta: 'Get started',
  options: [
    { label: '5× usage', price: 100, lookupKey: 'max_5x_monthly', weeklyLimit: '$75', features: [] },
    { label: '20× usage', price: 200, lookupKey: 'max_20x_monthly', weeklyLimit: '$300', features: [] },
  ],
}

const cta = (wrapper: ReturnType<typeof mount>) => wrapper.find('button.tier__cta')

describe('SubscriptionTierCard', () => {
  it('shows the tier CTA when the plan is unknown (signed out)', () => {
    const wrapper = mount(SubscriptionTierCard, { props: pro })
    expect(cta(wrapper).text()).toBe('Get started')
    expect(cta(wrapper).attributes('disabled')).toBeUndefined()
  })

  it('a Free user sees Free as current and paid plans as ordinary checkouts', () => {
    expect(cta(mount(SubscriptionTierCard, { props: { ...free, currentPlanKey: null } })).text()).toBe('Current plan')
    expect(cta(mount(SubscriptionTierCard, { props: { ...pro, currentPlanKey: null } })).text()).toBe('Get started')
  })

  it('a subscriber switches plans instead of checking out again', () => {
    const current = mount(SubscriptionTierCard, { props: { ...pro, currentPlanKey: 'pro_monthly' } })
    expect(cta(current).text()).toBe('Current plan')
    expect(cta(current).attributes('disabled')).toBeDefined()

    const other = mount(SubscriptionTierCard, { props: { ...max, currentPlanKey: 'pro_monthly' } })
    expect(cta(other).text()).toBe('Switch to this plan')

    // Going down to Free is cancelling, which lives in the billing portal.
    expect(cta(mount(SubscriptionTierCard, { props: { ...free, currentPlanKey: 'pro_monthly' } })).text()).toBe('Manage billing')
  })

  it('a multi-option tier marks only the option in use as current', async () => {
    const wrapper = mount(SubscriptionTierCard, { props: { ...max, currentPlanKey: 'max_20x_monthly' } })
    expect(cta(wrapper).text()).toBe('Switch to this plan')
    await wrapper.findAll('button.tier__option')[1]!.trigger('click')
    expect(cta(wrapper).text()).toBe('Current plan')
  })

  it('does not emit subscribe for the current plan', async () => {
    const wrapper = mount(SubscriptionTierCard, { props: { ...pro, currentPlanKey: 'pro_monthly' } })
    await cta(wrapper).trigger('click')
    expect(wrapper.emitted('subscribe')).toBeUndefined()
  })
})
