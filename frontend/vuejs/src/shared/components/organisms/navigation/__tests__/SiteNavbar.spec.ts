import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { reactive } from 'vue'

const route = reactive({ path: '/', fullPath: '/' })
const auth = reactive({ isAuthenticated: false })
const logout = vi.fn()

vi.mock('vue-router', () => ({ useRouter: () => ({ push: vi.fn() }), useRoute: () => route }))
vi.mock('@/shared/stores/auth', () => ({ useAuthStore: () => auth }))
vi.mock('@/apps/auth', () => ({ useAuth: () => ({ logout }) }))

import SiteNavbar from '../SiteNavbar.vue'

const stubs = {
  ImagiLogo: true,
  RouterLink: {
    props: ['to'],
    template: '<a :href="typeof to === \'string\' ? to : \'/named/\' + to.name"><slot /></a>',
  },
}

/**
 * The bar is the same for everyone in the middle (Product, Docs, Pricing,
 * About) and changes only on the right: visitors can sign in or start
 * building, the signed-in can sign out. The current page reads in full ink,
 * and below md everything folds into a Menu sheet.
 */
describe('SiteNavbar', () => {
  const mountBar = () => mount(SiteNavbar, { global: { stubs } })

  beforeEach(() => {
    route.path = '/'
    route.fullPath = '/'
    auth.isAuthenticated = false
    logout.mockReset()
  })

  it('shows visitors the site links, Sign in and Start building', () => {
    const w = mountBar()
    const desktop = w.find('nav')
    expect(desktop.text()).toContain('Product')
    for (const label of ['Docs', 'Pricing', 'About']) expect(desktop.text()).toContain(label)
    expect(w.find('a[href="/auth/signin"]').text()).toBe('Sign in')
    expect(w.find('a.site-nav-cta[href="/auth/register"]').text()).toBe('Start building')
    expect(desktop.text()).not.toContain('Sign out')
  })

  it('swaps the visitor actions for Sign out once signed in', async () => {
    auth.isAuthenticated = true
    const w = mountBar()
    expect(w.find('a[href="/auth/register"]').exists()).toBe(false)
    const signOut = w.findAll('button').find((b) => b.text() === 'Sign out')
    expect(signOut).toBeTruthy()
    await signOut!.trigger('click')
    expect(logout).toHaveBeenCalled()
  })

  it('marks the current page, docs sub-pages included', () => {
    route.path = '/docs/building'
    const w = mountBar()
    const docs = w.find('a.site-nav-link[href="/docs"]')
    expect(docs.classes()).toContain('is-active')
    expect(docs.attributes('aria-current')).toBe('page')
    expect(w.find('a.site-nav-link[href="/about"]').classes()).not.toContain('is-active')
  })

  it('lights Product on the projects pages, and its menu holds Imagi', () => {
    route.path = '/imagi/projects'
    const w = mountBar()
    const trigger = w.find('button[aria-haspopup="true"]')
    expect(trigger.classes()).toContain('is-active')
    expect(w.find('a[href="/named/builder"]').text()).toContain('Imagi')
  })

  it('opens and closes the phone menu, and closes it on navigation', async () => {
    const w = mountBar()
    const menuBtn = w.find('button[aria-controls="site-nav-sheet"]')
    expect(w.find('#site-nav-sheet').exists()).toBe(false)

    await menuBtn.trigger('click')
    expect(menuBtn.attributes('aria-expanded')).toBe('true')
    const sheet = w.find('#site-nav-sheet')
    for (const label of ['Imagi', 'Pricing', 'Docs', 'About', 'Start building', 'Sign in']) {
      expect(sheet.text()).toContain(label)
    }

    route.path = '/docs'
    route.fullPath = '/docs'
    await w.vm.$nextTick()
    await w.vm.$nextTick()
    expect(w.find('#site-nav-sheet').exists()).toBe(false)
  })
})
