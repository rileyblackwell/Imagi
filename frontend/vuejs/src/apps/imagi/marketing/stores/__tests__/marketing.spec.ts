import { describe, it, expect, vi, beforeEach } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('../../services/marketingService', () => ({
  default: {
    createAdDraft: vi.fn(),
    updateAdDraft: vi.fn(),
    deleteAdDraft: vi.fn(),
    listAdDrafts: vi.fn(),
  },
}))

import MarketingService from '../../services/marketingService'
import { useMarketingStore } from '../marketing'
import type { AdDraft } from '../../types'

const draft = (id: number, name = `Ad ${id}`): AdDraft => ({
  id,
  provider: 'google',
  name,
  goal: 'website',
  final_url: '',
  phone_number: '',
  headlines: [],
  descriptions: [],
  keywords: [],
  location: '',
  daily_budget: null,
  created_at: '2026-10-08T00:00:00Z',
  updated_at: '2026-10-08T00:00:00Z',
})

/** Google ad drafts: create when there's no id yet, update otherwise, newest first. */
describe('marketing store ad drafts', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('creates a draft without an id and puts it first', async () => {
    const store = useMarketingStore()
    store.setProject(7)
    store.adDrafts = [draft(1)]
    vi.mocked(MarketingService.createAdDraft).mockResolvedValue(draft(2))

    await store.saveAdDraft(null, { name: 'Ad 2' })

    expect(MarketingService.createAdDraft).toHaveBeenCalledWith(7, { name: 'Ad 2' })
    expect(store.adDrafts.map(d => d.id)).toEqual([2, 1])
  })

  it('updates an existing draft in place of the old copy', async () => {
    const store = useMarketingStore()
    store.setProject(7)
    store.adDrafts = [draft(1), draft(2)]
    vi.mocked(MarketingService.updateAdDraft).mockResolvedValue(draft(2, 'Renamed'))

    await store.saveAdDraft(2, { name: 'Renamed' })

    expect(MarketingService.updateAdDraft).toHaveBeenCalledWith(7, 2, { name: 'Renamed' })
    expect(store.adDrafts.map(d => d.name)).toEqual(['Renamed', 'Ad 1'])
  })

  it('drops a deleted draft', async () => {
    const store = useMarketingStore()
    store.setProject(7)
    store.adDrafts = [draft(1), draft(2)]
    vi.mocked(MarketingService.deleteAdDraft).mockResolvedValue()

    await store.deleteAdDraft(1)

    expect(store.adDrafts.map(d => d.id)).toEqual([2])
  })
})
