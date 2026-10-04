import { describe, it, expect, beforeEach } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import HeroSection from '../HeroSection.vue'

/**
 * The hero is copy only — the product shots live with the sections that
 * explain them. Lock down the headline's accent word and where the primary
 * call to action sends a signed-out visitor.
 */
describe('HeroSection', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  const mountHero = () =>
    mount(HeroSection, { global: { stubs: { RouterLink: RouterLinkStub } } })

  it('sets "run" apart as the accent word in the headline', () => {
    const h1 = mountHero().find('h1')
    expect(h1.text()).toBe('Build and run your business')
    expect(h1.find('em.hero-accent').text()).toBe('run')
  })

  it('keeps the hero free of product shots', () => {
    expect(mountHero().find('img').exists()).toBe(false)
  })

  it('sends signed-out visitors to sign in', () => {
    const link = mountHero().findComponent(RouterLinkStub)
    expect(link.props('to')).toEqual({ name: 'login' })
  })
})
