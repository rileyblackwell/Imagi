import { describe, it, expect, beforeEach } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import HeroSection from '../HeroSection.vue'

/**
 * The hero is the one screen every visitor sees, so it carries the product
 * shot itself. Lock down that the shot is there, that it is the eager one
 * (it sits on the first screen, so lazy loading would leave a blank frame),
 * and that the "See how it works" target still lives below it.
 */
describe('HeroSection', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
  })

  const mountHero = () =>
    mount(HeroSection, { global: { stubs: { RouterLink: RouterLinkStub } } })

  it('shows the project hub on the first screen, loaded eagerly', () => {
    const img = mountHero().find('img')
    expect(img.attributes('src')).toBe('/product/project-hub.webp')
    expect(img.attributes('loading')).toBe('eager')
    expect(img.attributes('fetchpriority')).toBe('high')
  })

  it('sets "run" apart as the accent word in the headline', () => {
    const h1 = mountHero().find('h1')
    expect(h1.text()).toBe('Build and run your business')
    expect(h1.find('em.hero-accent').text()).toBe('run')
  })

  it('sends signed-out visitors to sign in', () => {
    const link = mountHero().findComponent(RouterLinkStub)
    expect(link.props('to')).toEqual({ name: 'login' })
  })
})
