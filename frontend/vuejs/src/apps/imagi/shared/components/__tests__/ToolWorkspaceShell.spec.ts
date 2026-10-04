import { describe, it, expect, vi } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import { defineComponent, h } from 'vue'

const routeName = { value: 'sell-overview' }

vi.mock('vue-router', () => ({
  useRoute: () => ({ name: routeName.value }),
}))

vi.mock('@/shared/layouts', () => ({
  DefaultLayout: defineComponent({ setup: (_, { slots }) => () => h('div', slots.default?.()) }),
}))

import ToolWorkspaceShell from '../ToolWorkspaceShell.vue'

/**
 * Sell, Market and Operate share this frame. What has to survive the move from
 * three copies to one: the loading and not-found states, the connect banner
 * only when asked for, and the tab that is lit — including for a child route
 * like a campaign's detail page.
 */
describe('ToolWorkspaceShell', () => {
  const tabs = [
    { name: 'sell-overview', label: 'Overview', icon: 'fa-chart-line' },
    { name: 'sell-campaigns', label: 'Campaigns', icon: 'fa-paper-plane', children: ['sell-campaign-detail'] },
  ]

  const mountShell = (props: Record<string, unknown> = {}) =>
    mount(ToolWorkspaceShell, {
      props: {
        projectName: 'ticker-insights',
        project: { name: 'Ticker Insights' },
        isLoading: false,
        title: 'Sell',
        description: 'Take payments for your business.',
        loadingLabel: 'Loading sell workspace…',
        tabs,
        ...props,
      },
      slots: {
        default: '<p class="tab-body">tab body</p>',
        banner: 'Connect Stripe to start selling.',
      },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })

  it('renders the editorial header with the project as the eyebrow', () => {
    const wrapper = mountShell()
    expect(wrapper.find('h1').text()).toBe('Sell')
    expect(wrapper.find('.eyebrow').text()).toContain('Ticker Insights')
    expect(wrapper.find('.lede').text()).toBe('Take payments for your business.')
    expect(wrapper.find('.tab-body').exists()).toBe(true)
  })

  it('shows the loading state instead of the workspace while loading', () => {
    const wrapper = mountShell({ isLoading: true, project: null })
    expect(wrapper.text()).toContain('Loading sell workspace…')
    expect(wrapper.find('.tab-body').exists()).toBe(false)
  })

  it('shows not-found when the project does not resolve', () => {
    const wrapper = mountShell({ project: null })
    expect(wrapper.text()).toContain('Project not found')
    expect(wrapper.find('.tab-body').exists()).toBe(false)
  })

  it('only shows the connect banner when asked to', () => {
    expect(mountShell().find('.banner').exists()).toBe(false)
    expect(mountShell({ showBanner: true }).find('.banner').text()).toContain('Connect Stripe')
  })

  it('lights the tab for the current route, and for its child routes', () => {
    routeName.value = 'sell-campaign-detail'
    const wrapper = mountShell()
    const active = wrapper.findAll('.tab--active')
    expect(active).toHaveLength(1)
    expect(active[0].text()).toContain('Campaigns')
    expect(active[0].attributes('aria-current')).toBe('page')
    routeName.value = 'sell-overview'
  })
})
