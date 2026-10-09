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

  it('names the create form’s four steps, in order', () => {
    const titles = wrapper().findAll('.brief-step__title').map((t) => t.text())
    expect(titles).toEqual(['Name it', 'What is your app?', 'How does it work?', 'Set the look'])
  })

  it('shows the create form and the starter-design step', () => {
    const srcs = wrapper().findAll('product-shot-stub').map((s) => s.attributes('src'))
    expect(srcs).toEqual(['/product/create-brief.webp', '/product/create-look.webp'])
  })
})
