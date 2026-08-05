import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import BaseNavbar from '../BaseNavbar.vue'

/**
 * The bar is fixed, and a fixed box with `top: auto` is painted at its static
 * position — wherever it would have landed in normal flow. App.vue crossfades
 * routed pages, so mid-navigation there is a layout pass with the outgoing page
 * still above the incoming one, and an unanchored bar resolves to the bottom of
 * the page you just left and stays there until the next reload.
 *
 * So the anchor is behaviour, not styling: assert it on the component that owns
 * it, since every consumer inherits the bug if it goes missing.
 */
describe('BaseNavbar', () => {
  const rootClasses = (props: object = {}) =>
    mount(BaseNavbar, {
      props,
      global: { stubs: { ImagiLogo: true } },
    })
      .find('nav')
      .classes()

  it('pins itself to the top of the viewport rather than to its static position', () => {
    expect(rootClasses()).toEqual(expect.arrayContaining(['fixed', 'top-0', 'left-0', 'right-0']))
  })

  it('keeps the anchor when rendered edge-to-edge', () => {
    expect(rootClasses({ fluid: true })).toEqual(
      expect.arrayContaining(['fixed', 'top-0', 'left-0', 'right-0']),
    )
  })

  it('caps its content at max-w-7xl by default and spans the full width when fluid', () => {
    const defaultRow = mount(BaseNavbar, { global: { stubs: { ImagiLogo: true } } })
    expect(defaultRow.find('nav > div').classes()).toContain('max-w-7xl')

    const fluidRow = mount(BaseNavbar, {
      props: { fluid: true },
      global: { stubs: { ImagiLogo: true } },
    })
    expect(fluidRow.find('nav > div').classes()).not.toContain('max-w-7xl')
  })
})
