import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import CheckInQueue from '../CheckInQueue.vue'
import type { CheckInDto } from '@/apps/imagi/build/types/services'

function makeCheckIn(overrides: Partial<CheckInDto> = {}): CheckInDto {
  return {
    id: 1,
    kind: 'error',
    body: 'The task hit an error: model exploded',
    status: 'pending',
    created_at: '2026-08-18T00:00:00Z',
    resolved_at: null,
    project_id: 1,
    lead_id: 2,
    task: {
      id: 3,
      title: 'Add a contact page',
      kind: 'task',
      review_status: 'failed',
      variant_group: '',
      has_worktree: true,
      is_running: false,
      ...(overrides.task ?? {}),
    },
    ...overrides,
  }
}

const buttonLabelled = (wrapper: ReturnType<typeof mount>, label: string) =>
  wrapper.findAll('button').find(b => b.text().trim() === label)!

describe('CheckInQueue failed-task card', () => {
  it('dismisses the task, not just the card', async () => {
    // The bug this covers: Dismiss used to resolve the queue entry only. The
    // subagent behind it stayed 'failed' with its worktree still checked out,
    // and clearing the card removed the last way to reach it.
    const checkIn = makeCheckIn()
    const wrapper = mount(CheckInQueue, { props: { queue: [checkIn] } })

    await buttonLabelled(wrapper, 'Dismiss').trigger('click')

    expect(wrapper.emitted('dismiss')?.[0]).toEqual([checkIn])
    expect(wrapper.emitted('skip')).toBeUndefined()
  })

  it('says what happened and offers the task itself', async () => {
    const checkIn = makeCheckIn()
    const wrapper = mount(CheckInQueue, { props: { queue: [checkIn] } })

    expect(wrapper.text()).toContain('Stopped early')
    expect(wrapper.text()).toContain('model exploded')

    await buttonLabelled(wrapper, 'See what happened').trigger('click')
    expect(wrapper.emitted('view')?.[0]).toEqual([checkIn])
  })

  it('leaves a question card clearable without dismissing its task', async () => {
    // "Later" is the one action that really is card-only: the subagent is
    // still parked on its question, waiting for an answer that may come.
    const checkIn = makeCheckIn({ kind: 'question', body: 'Stripe or PayPal?' })
    const wrapper = mount(CheckInQueue, { props: { queue: [checkIn] } })

    await buttonLabelled(wrapper, 'Later').trigger('click')

    expect(wrapper.emitted('skip')?.[0]).toEqual([checkIn])
    expect(wrapper.emitted('dismiss')).toBeUndefined()
  })
})
