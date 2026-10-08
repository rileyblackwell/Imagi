import { describe, it, expect } from 'vitest'
import { describePrice } from '@/apps/imagi/sell/utils/ui'

describe('describePrice', () => {
  it('describes each way to charge', () => {
    expect(describePrice({ price_cents: 1200, billing_interval: 'month' })).toMatch(/12\.00 \/ month$/)
    expect(describePrice({ price_cents: 9900, billing_interval: 'year' })).toMatch(/99\.00 \/ year$/)
    expect(describePrice({ price_cents: 3000, billing_interval: 'one_time' })).toMatch(/30\.00$/)
  })

  it('puts the unit count in pay-as-you-go prices', () => {
    expect(
      describePrice({ price_cents: 100, billing_interval: 'usage', usage_unit_count: 1000, usage_unit_label: 'message' })
    ).toMatch(/1\.00 per 1,000 messages$/)
    expect(
      describePrice({ price_cents: 5, billing_interval: 'usage', usage_unit_count: 1, usage_unit_label: 'API call' })
    ).toMatch(/0\.05 per API call$/)
  })
})
