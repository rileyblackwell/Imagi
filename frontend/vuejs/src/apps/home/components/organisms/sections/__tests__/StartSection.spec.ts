import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StartSection from '../StartSection.vue'

const stubs = { ProductShot: true }
const directives = { reveal: {} }

describe('StartSection (step 01)', () => {
  const wrapper = () => mount(StartSection, { global: { stubs, directives } })

  it('is the target of the hero’s “See how it works” link', () => {
    expect(wrapper().find('section').attributes('id')).toBe('how-it-works')
  })

  it('leads with the free plan, the 10-minute build and who it is for', () => {
    const labels = wrapper().findAll('.fact__label').map((l) => l.text())
    expect(labels).toEqual(['Plans start at', 'Typical build', 'Made for'])
    const values = wrapper().findAll('.fact__value').map((v) => v.text())
    expect(values[0]).toBe('Free')
    expect(values[1]).toContain('10')
    expect(values[2]).toContain('Founders')
  })

  it('names the create form’s four steps, in order', () => {
    const titles = wrapper().findAll('.brief-step__title').map((t) => t.text())
    expect(titles).toEqual(['Name it', 'What is your app?', 'How does it work?', 'Set the look'])
  })

  it('shows the create form and the starter-design step', () => {
    const srcs = wrapper().findAll('product-shot-stub').map((s) => s.attributes('src'))
    expect(srcs).toEqual(['/product/create-brief.webp', '/product/create-look.webp'])
  })
})
