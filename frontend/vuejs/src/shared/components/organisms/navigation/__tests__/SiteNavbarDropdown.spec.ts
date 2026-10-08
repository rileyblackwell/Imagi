import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SiteNavbarDropdown from '../SiteNavbarDropdown.vue'

/**
 * The Product menu's panel sits in the navbar, outside every page's .spotlight
 * root, so it carries its own — that is where its colours come from in both
 * themes. And the trigger reports its state, for screen readers and for the
 * chevron.
 */
describe('SiteNavbarDropdown', () => {
  const mountMenu = (open: boolean) =>
    mount(SiteNavbarDropdown, {
      props: { modelValue: open },
      slots: { default: 'Product', menu: '<a href="#">Imagi</a>' },
    })

  it('renders its panel as a Spotlight surface', () => {
    const panel = mountMenu(true).find('.nav-menu')
    expect(panel.classes()).toContain('spotlight')
    expect(panel.text()).toContain('Imagi')
  })

  it('reports whether it is open and turns the chevron with it', async () => {
    const closed = mountMenu(false)
    expect(closed.find('button').attributes('aria-expanded')).toBe('false')
    expect(closed.find('.nav-menu-chevron').classes()).not.toContain('is-open')

    const open = mountMenu(true)
    expect(open.find('button').attributes('aria-expanded')).toBe('true')
    expect(open.find('.nav-menu-chevron').classes()).toContain('is-open')
  })

  it('asks to toggle when the trigger is clicked', async () => {
    const wrapper = mountMenu(false)
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('update:modelValue')?.[0]).toEqual([true])
  })
})
