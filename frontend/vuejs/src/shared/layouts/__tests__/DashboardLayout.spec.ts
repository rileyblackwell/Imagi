import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'

vi.mock('@/shared/components', () => ({
  BaseNavbar: { name: 'BaseNavbar', template: '<nav data-bar="base"><slot name="left-leading" /></nav>' },
  SiteNavbar: { name: 'SiteNavbar', template: '<nav data-bar="site"><slot name="left-leading" /></nav>' },
  BaseFooter: { name: 'BaseFooter', template: '<footer />' },
}))

import DashboardLayout from '../DashboardLayout.vue'

/**
 * Docs are public, so they wear the site's full bar (links, Sign in, Start
 * building); the builder workspace keeps the bare wordmark bar. Either way
 * the sidebar toggle stays pinned before the wordmark.
 */
describe('DashboardLayout', () => {
  const mountLayout = (props: object) =>
    mount(DashboardLayout, { props, global: { stubs: { SidebarToggle: { template: '<button class="sidebar-toggle" />' } } } })

  it('keeps the bare bar by default', () => {
    const w = mountLayout({})
    expect(w.find('[data-bar="base"]').exists()).toBe(true)
    expect(w.find('[data-bar="site"]').exists()).toBe(false)
  })

  it('uses the site bar when asked, with the sidebar toggle still in it', () => {
    const w = mountLayout({ siteNav: true })
    const bar = w.find('[data-bar="site"]')
    expect(bar.exists()).toBe(true)
    expect(bar.find('.sidebar-toggle').exists()).toBe(true)
  })
})
