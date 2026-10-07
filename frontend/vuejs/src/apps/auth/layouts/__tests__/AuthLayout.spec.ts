import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import AuthLayout from '../AuthLayout.vue'

vi.mock('vue-router', () => ({
  useRoute: () => ({ meta: { title: 'Welcome Back', subtitle: 'Sign in to continue' } })
}))

const stubs = {
  DefaultLayout: { template: '<div class="layout"><slot /></div>' },
  ImagiLogo: true,
  RouterView: true
}

describe('AuthLayout (Spotlight)', () => {
  const wrapper = () => mount(AuthLayout, { global: { stubs } })

  it('sits on the Spotlight stage and follows the site theme', () => {
    const root = wrapper().element as HTMLElement
    expect(root.classList.contains('spotlight')).toBe(true)
    expect(root.classList.contains('dark')).toBe(false)
  })

  it('keeps the form in one centered card, titled from the route', () => {
    const w = wrapper()
    expect(w.findAll('.auth-panel')).toHaveLength(1)
    expect(w.find('.auth-panel h1').text()).toBe('Welcome Back')
    expect(w.find('.auth-panel .sl-lede').text()).toBe('Sign in to continue')
  })
})
