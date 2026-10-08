import { describe, it, expect } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import ImagiLogo from '../ImagiLogo.vue'

const mountLogo = (props: object = {}) =>
  mount(ImagiLogo, { props, global: { stubs: { RouterLink: RouterLinkStub } } })

describe('ImagiLogo', () => {
  it('names the brand for assistive tech, since the visible letters are dotless i glyphs', () => {
    const wrapper = mountLogo()
    expect(wrapper.attributes('aria-label')).toBe('Imagi')
    expect(wrapper.find('.wordmark').attributes('aria-hidden')).toBe('true')
  })

  it('spells imagi with both i dots drawn, and lights only the last one', () => {
    const wrapper = mountLogo()
    expect(wrapper.find('.wordmark').text()).toBe('ımagı')
    const dots = wrapper.findAll('.wordmark__i')
    expect(dots).toHaveLength(2)
    expect(dots[0].classes()).not.toContain('wordmark__i--lit')
    expect(dots[1].classes()).toContain('wordmark__i--lit')
  })

  it('links home by default and to the given destination otherwise', () => {
    expect(mountLogo().findComponent(RouterLinkStub).props('to')).toBe('/')
    expect(mountLogo({ to: '/projects' }).findComponent(RouterLinkStub).props('to')).toBe('/projects')
  })

  it('maps the size variants onto text sizes', () => {
    expect(mountLogo({ size: 'sm' }).find('.wordmark').classes()).toContain('text-lg')
    expect(mountLogo({ size: 'xl' }).find('.wordmark').classes()).toContain('text-4xl')
  })
})
