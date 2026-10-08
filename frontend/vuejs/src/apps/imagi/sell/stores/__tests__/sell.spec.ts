import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

const apiMock = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn(), put: vi.fn() }))
vi.mock('@/shared/services/api', () => ({ default: apiMock }))

import { useSellStore } from '@/apps/imagi/sell/stores/sell'

const settings = (overrides = {}) => ({
  connection_type: '',
  is_configured: false,
  payment_models: [],
  currency: 'usd',
  ...overrides,
})

describe('sell store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    Object.values(apiMock).forEach((fn) => fn.mockReset())
  })

  it('tells a linked-but-unfinished Stripe account from a ready one', () => {
    const store = useSellStore()
    store.settings = settings({ connection_type: 'connect' }) as never
    expect(store.isConnected).toBe(true)
    expect(store.isConfigured).toBe(false)
    store.settings = settings({ connection_type: 'connect', is_configured: true }) as never
    expect(store.isConfigured).toBe(true)
  })

  it('asks the backend for a Stripe sign-up link that returns to the console', async () => {
    const store = useSellStore()
    store.setProject(7)
    apiMock.post.mockResolvedValue({ data: { url: 'https://connect.stripe.com/setup/x' } })
    const url = await store.startConnect('/imagi/project/bloom/sales')
    expect(url).toBe('https://connect.stripe.com/setup/x')
    expect(apiMock.post).toHaveBeenCalledWith('/v1/sell/projects/7/connect/start/', {
      return_path: '/imagi/project/bloom/sales',
    })
  })

  it('keeps the app payments state from an install', async () => {
    const store = useSellStore()
    store.setProject(7)
    apiMock.post.mockResolvedValue({
      data: { installed: true, out_of_date: false, pages: [], routes: ['/pricing'], restyle_started: true },
    })
    const result = await store.installAppPayments()
    expect(result.routes).toEqual(['/pricing'])
    expect(store.appPayments?.installed).toBe(true)
    expect(apiMock.post).toHaveBeenCalledWith('/v1/sell/projects/7/app-payments/install/')
  })

  it('updates settings when the server key is rotated', async () => {
    const store = useSellStore()
    store.setProject(7)
    apiMock.post.mockResolvedValue({
      data: { server_key: 'imagi_sk_new', settings: settings({ server_key_set: true }) },
    })
    expect(await store.rotateServerKey()).toBe('imagi_sk_new')
    expect(store.settings?.server_key_set).toBe(true)
  })
})
