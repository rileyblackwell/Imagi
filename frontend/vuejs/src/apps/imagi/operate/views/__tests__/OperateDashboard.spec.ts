import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises, RouterLinkStub } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import type { AppSummary, BusinessSummary, DashboardPayload } from '../../types'

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { projectName: 'bloom-coffee' }, query: {} }),
}))

const service = vi.hoisted(() => ({
  getDashboard: vi.fn(),
  setLiveUrl: vi.fn(),
  checkApp: vi.fn(),
}))

vi.mock('../../services/operateService', () => ({
  default: service,
  extractError: (_error: unknown, fallback: string) => fallback,
}))

import OperateDashboard from '../OperateDashboard.vue'
import { useOperateStore } from '../../stores/operate'

const days = Array.from({ length: 14 }, (_, i) => ({ date: `2026-10-${String(i + 1).padStart(2, '0')}`, label: `Oct ${i + 1}`, visitors: 0 }))

function app(overrides: Partial<AppSummary> = {}): AppSummary {
  return {
    live_url: '',
    site_key: '',
    check_stale: false,
    status: null,
    uptime: { percent: null, checks: 0 },
    response_ms: { latest: null, median: null },
    traffic: { visitors: 0, page_views: 0, daily: days },
    ...overrides,
  }
}

function business(overrides: Partial<BusinessSummary> = {}): BusinessSummary {
  return {
    currency: 'usd',
    sell_connected: false,
    has_ledger: false,
    revenue_30d: 0,
    revenue_sell_30d: 0,
    revenue_recorded_30d: 0,
    expenses_30d: 0,
    profit_30d: 0,
    monthly: [],
    ...overrides,
  }
}

async function mountWith(payload: DashboardPayload) {
  service.getDashboard.mockResolvedValue(payload)
  useOperateStore().setProject(7)
  const wrapper = mount(OperateDashboard, {
    global: { stubs: { RouterLink: RouterLinkStub } },
  })
  await flushPromises()
  return wrapper
}

/** Operate is two halves: the live app, and the business's money. */
describe('OperateDashboard', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('asks for the live address before showing app numbers', async () => {
    const wrapper = await mountWith({ app: app(), business: business() })

    expect(wrapper.find('#operate-app-heading').text()).toBe('Your app')
    expect(wrapper.find('#operate-business-heading').text()).toBe('Your business')
    expect(wrapper.find('#operate-live-url').exists()).toBe(true)
    // No fake numbers: the app half reads as dashes until there is data.
    const appValues = wrapper.findAll('section')[0].findAll('.stat__value').map(v => v.text())
    expect(appValues).toEqual(['—', '—', '—'])
    expect(service.checkApp).not.toHaveBeenCalled()
  })

  it('saves the live address through the store', async () => {
    service.setLiveUrl.mockResolvedValue({
      monitor: { live_url: 'https://bloom.coffee/', site_key: 'k', updated_at: '' },
      app: app({ live_url: 'https://bloom.coffee/', site_key: 'k' }),
    })
    const wrapper = await mountWith({ app: app(), business: business() })

    await wrapper.find('#operate-live-url').setValue('bloom.coffee')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(service.setLiveUrl).toHaveBeenCalledWith(7, 'bloom.coffee')
    expect(wrapper.find('#operate-live-url').exists()).toBe(false)
    expect(wrapper.find('.tag__code').text()).toContain('/api/v1/operate/beacon/k/')
  })

  it('shows uptime, speed and visitors, and re-checks a stale app', async () => {
    const live = app({
        live_url: 'https://bloom.coffee/',
        site_key: 'k',
        check_stale: true,
        status: { is_up: true, checked_at: new Date().toISOString(), status_code: 200, response_ms: 240, error: '' },
        uptime: { percent: 99.5, checks: 200 },
        response_ms: { latest: 240, median: 310 },
        traffic: { visitors: 1204, page_views: 3100, daily: days },
      })
    service.checkApp.mockResolvedValue(live)
    const wrapper = await mountWith({ app: live, business: business() })

    const appValues = wrapper.findAll('section')[0].findAll('.stat__value').map(v => v.text())
    expect(appValues).toEqual(['99.50%', '240 ms', (1204).toLocaleString()])
    expect(wrapper.find('.status-pill').text()).toContain('Up')
    expect(service.checkApp).toHaveBeenCalledWith(7, true)
  })

  it('adds Sell payments and recorded income into revenue', async () => {
    const wrapper = await mountWith({
      app: app(),
      business: business({
        sell_connected: true,
        revenue_30d: 625.5,
        revenue_sell_30d: 125.5,
        revenue_recorded_30d: 500,
        expenses_30d: 700,
        profit_30d: -74.5,
      }),
    })

    const section = wrapper.findAll('section')[1]
    const values = section.findAll('.stat__value')
    expect(values.map(v => v.text())).toEqual(['$625.50', '$700.00', '-$74.50'])
    expect(values[2].classes()).toContain('text-[color:var(--sl-bad)]')
    expect(section.text()).toContain('$125.50 from Sell, $500.00 recorded')
    expect(section.text()).not.toContain('Connect Stripe')
  })
})
