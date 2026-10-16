import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import IntroSection from '../IntroSection.vue'

const directives = { reveal: {} }

describe('IntroSection (what Imagi is)', () => {
  const wrapper = () => mount(IntroSection, { global: { directives } })

  it('says who Imagi is for', () => {
    expect(wrapper().find('h2').text()).toBe('For anyone with an idea')
  })

  it('leads with the free plan, the build time and who it is made for', () => {
    const labels = wrapper().findAll('.fact__label').map((l) => l.text())
    expect(labels).toEqual(['Price', 'Your app is built in under', 'Made for'])
    const values = wrapper().findAll('.fact__value').map((v) => v.text())
    expect(values[0]).toBe('Free')
    expect(values[1]).toContain('10')
    expect(values[1]).toContain('sec')
    expect(values[2]).toContain('Founders')
  })
})
