import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import QuestionChoices from '../QuestionChoices.vue'

describe('QuestionChoices', () => {
  it('offers each answer as a button and reports the pick', async () => {
    const wrapper = mount(QuestionChoices, { props: { options: ['Pickup only', 'Pickup and delivery'] } })
    const buttons = wrapper.findAll('button')
    expect(buttons.map(b => b.text())).toEqual(['Pickup only', 'Pickup and delivery'])

    await buttons[1]!.trigger('click')
    expect(wrapper.emitted('pick')).toEqual([['Pickup and delivery']])
  })

  it('is inert once answered, showing what was picked', () => {
    const wrapper = mount(QuestionChoices, {
      props: { options: ['A', 'B'], disabled: true, picked: 'B' },
    })
    expect(wrapper.findAll('button').every(b => b.attributes('disabled') !== undefined)).toBe(true)
    expect(wrapper.find('.question-option--picked').text()).toBe('B')
  })

  it('draws the sketch with scripts, handlers and links stripped', () => {
    const wrapper = mount(QuestionChoices, {
      props: {
        visual:
          '<svg viewBox="0 0 10 10" onload="alert(1)"><script>alert(2)</script>' +
          '<a href="https://evil.test"><rect width="4" height="4"/></a><text x="1" y="9">Left</text></svg>',
      },
    })
    const html = wrapper.find('.question-visual').html()
    expect(html).toContain('<svg')
    expect(html).toContain('Left')
    expect(html).not.toContain('script')
    expect(html).not.toContain('onload')
    expect(html).not.toContain('evil.test')
  })

  it('draws nothing for a sketch that is not SVG', () => {
    const wrapper = mount(QuestionChoices, { props: { visual: '<img src=x onerror=alert(1)>' } })
    expect(wrapper.find('.question-visual').exists()).toBe(false)
  })
})
