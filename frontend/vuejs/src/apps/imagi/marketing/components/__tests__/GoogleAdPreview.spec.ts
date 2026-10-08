import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GoogleAdPreview from '../GoogleAdPreview.vue'

/**
 * The ad builder's preview reads like a Google result: the site from the
 * landing page, up to three headlines joined by pipes, the descriptions, and
 * a call line only for the phone-calls goal.
 */
describe('GoogleAdPreview', () => {
  const mountPreview = (props: Record<string, unknown> = {}) =>
    mount(GoogleAdPreview, {
      props: {
        headlines: ['Fresh espresso', ' ', 'Open at 6am', 'Order ahead', 'Fourth one'],
        descriptions: ['Small-batch beans.', 'Roasted weekly.'],
        finalUrl: 'https://www.bloom.example.com/menu/fall',
        businessName: 'Bloom Coffee',
        goal: 'website',
        ...props,
      },
    })

  it('joins the first three non-blank headlines and both descriptions', () => {
    const text = mountPreview().text()
    expect(text).toContain('Fresh espresso | Open at 6am | Order ahead')
    expect(text).not.toContain('Fourth one')
    expect(text).toContain('Small-batch beans. Roasted weekly.')
  })

  it('shows the landing page host and path without www', () => {
    expect(mountPreview().text()).toContain('https://bloom.example.com › menu › fall')
  })

  it('falls back to placeholders while the ad is empty', () => {
    const text = mountPreview({ headlines: ['', '', ''], descriptions: [''], finalUrl: '' }).text()
    expect(text).toContain('Your headline appears here')
    expect(text).toContain('www.yourbusiness.com')
  })

  it('adds a call line only when the goal is phone calls', () => {
    expect(mountPreview({ phoneNumber: '+15551234567' }).text()).not.toContain('Call +15551234567')
    expect(mountPreview({ goal: 'calls', phoneNumber: '+15551234567' }).text()).toContain('Call +15551234567')
  })
})
