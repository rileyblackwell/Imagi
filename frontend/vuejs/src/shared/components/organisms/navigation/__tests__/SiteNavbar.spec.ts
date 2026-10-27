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
 * Visitors get the wordmark and one ink Sign in pill, at every width. Signed
 * in, the Product menu and Pricing sit centred in the bar (Docs and About live
 * in the footer) with a quiet Sign out on the right. The current page reads in
 * full ink, and below md the signed-in links fold into a Menu sheet.
 */
describe('SiteNavbar', () => {
  const mountBar = () => mount(SiteNavbar, { global: { stubs } })

  beforeEach(() => {
    route.path = '/'
    route.fullPath = '/'
    auth.isAuthenticated = false
    logout.mockReset()
  })

  it('shows visitors only the wordmark and the ink Sign in pill', () => {
    const w = mountBar()
    const bar = w.find('nav')
    expect(bar.text()).toBe('Sign in')
    expect(w.find('a.site-nav-cta[href="/auth/signin"]').text()).toBe('Sign in')
    expect(w.find('a[href="/auth/register"]').exists()).toBe(false)
    expect(w.find('button[aria-haspopup="true"]').exists()).toBe(false)
    expect(w.find('button[aria-controls="site-nav-sheet"]').exists()).toBe(false)
  })

  it('centres Product and Pricing once signed in, with Sign out on the right', async () => {
    auth.isAuthenticated = true
    const w = mountBar()
    const center = w.find('nav .justify-center')
    expect(center.text()).toContain('Product')
    expect(center.text()).toContain('Pricing')
    expect(w.find('nav').text()).not.toContain('Docs')
    expect(w.find('nav').text()).not.toContain('About')
    expect(w.find('a[href="/auth/signin"]').exists()).toBe(false)
    const signOut = w.findAll('button').find((b) => b.text() === 'Sign out')
    expect(signOut).toBeTruthy()
    await signOut!.trigger('click')
    expect(logout).toHaveBeenCalled()
  })

  it('marks the current page, sub-pages included', () => {
    auth.isAuthenticated = true
    route.path = '/payments/pricing'
    const w = mountBar()
    const pricing = w.find('a.site-nav-link[href="/payments/pricing"]')
    expect(pricing.classes()).toContain('is-active')
    expect(pricing.attributes('aria-current')).toBe('page')

    route.path = '/docs/building'
    expect(mountBar().find('a.site-nav-link[href="/payments/pricing"]').classes()).not.toContain('is-active')
  })

  it('lights Product on the projects pages, and its menu holds Imagi', () => {
    auth.isAuthenticated = true
    route.path = '/imagi/projects'
    const w = mountBar()
    const trigger = w.find('button[aria-haspopup="true"]')
    expect(trigger.classes()).toContain('is-active')
    expect(w.find('a[href="/named/builder"]').text()).toContain('Imagi')
  })

  it('opens and closes the phone menu, and closes it on navigation', async () => {
    auth.isAuthenticated = true
    const w = mountBar()
    const menuBtn = w.find('button[aria-controls="site-nav-sheet"]')
    expect(w.find('#site-nav-sheet').exists()).toBe(false)

    await menuBtn.trigger('click')
    expect(menuBtn.attributes('aria-expanded')).toBe('true')
    const sheet = w.find('#site-nav-sheet')
    for (const label of ['Imagi', 'Pricing', 'Sign out']) {
      expect(sheet.text()).toContain(label)
    }
    expect(sheet.text()).not.toContain('Docs')
    expect(sheet.text()).not.toContain('Sign in')

    route.path = '/payments/pricing'
    route.fullPath = '/payments/pricing'
    await w.vm.$nextTick()
    await w.vm.$nextTick()
    expect(w.find('#site-nav-sheet').exists()).toBe(false)
  })
})
