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
      goal: 'Adding a contact page',
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

  it('offers to run the stopped subagent again', async () => {
    // The retry is the user's call and nobody else's — a run never restarts
    // itself — so the card that reports the failure is where it is made.
    const checkIn = makeCheckIn()
    const wrapper = mount(CheckInQueue, { props: { queue: [checkIn] } })

    await buttonLabelled(wrapper, 'Try again').trigger('click')

    expect(wrapper.emitted('retry')?.[0]).toEqual([checkIn])
    expect(wrapper.emitted('dismiss')).toBeUndefined()
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

describe('CheckInQueue completion card', () => {
  const finished = (overrides: Partial<CheckInDto> = {}) => makeCheckIn({
    kind: 'done',
    body: 'Your home page has a warmer look now, and the booking button sits '
      + 'right under the heading where people will see it.',
    task: { ...makeCheckIn().task, review_status: 'accepted', has_worktree: false },
    ...overrides,
  })

  it('never asks the user to approve work that is already in the app', async () => {
    // The whole point of handing a job to a subagent: it applies its own work.
    // A card offering to "add it" would be asking for a decision that has
    // already been made.
    const wrapper = mount(CheckInQueue, { props: { queue: [finished()] } })

    expect(wrapper.text()).toContain('Subagent complete')
    // The label is the fact and nothing more — the rail and the "Got it"
    // button already say the work is in.
    expect(wrapper.text()).not.toContain('added to your app')
    expect(wrapper.text()).not.toContain('Add to my app')
    expect(wrapper.text()).not.toContain('Discard')
  })

  it('clears the card without touching the subagent behind it', async () => {
    const checkIn = finished()
    const wrapper = mount(CheckInQueue, { props: { queue: [checkIn] } })

    await buttonLabelled(wrapper, 'Got it').trigger('click')

    expect(wrapper.emitted('skip')?.[0]).toEqual([checkIn])
    expect(wrapper.emitted('dismiss')).toBeUndefined()
    expect(wrapper.emitted('accept')).toBeUndefined()
  })

  it('shows the sign-off whole and opens the work behind it', async () => {
    const checkIn = finished()
    const wrapper = mount(CheckInQueue, { props: { queue: [checkIn] } })

    expect(wrapper.find('.check-in__text').text()).toBe(checkIn.body)

    await buttonLabelled(wrapper, 'See the work').trigger('click')
    expect(wrapper.emitted('view')?.[0]).toEqual([checkIn])
  })

  it('names the job the way the main thread names it', () => {
    const wrapper = mount(CheckInQueue, { props: { queue: [finished()] } })

    expect(wrapper.find('.check-in__title').text()).toBe('Adding a contact page')
  })

  it('offers the pick between takes the user asked to compare', async () => {
    // 'ready' is the one card left where finished work waits on a choice.
    const checkIn = makeCheckIn({
      kind: 'ready',
      body: 'Take one of the pricing table.',
      task: { ...makeCheckIn().task, review_status: 'ready', variant_group: 'v1' },
    })
    const wrapper = mount(CheckInQueue, { props: { queue: [checkIn] } })

    expect(wrapper.text()).toContain('Subagent complete — one of your options')
    await buttonLabelled(wrapper, 'Use this one').trigger('click')
    expect(wrapper.emitted('accept')?.[0]).toEqual([checkIn])
  })
})
