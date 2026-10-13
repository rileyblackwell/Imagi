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

const question = (overrides: Partial<CheckInDto> = {}) => makeCheckIn({
  kind: 'question',
  body: 'Stripe or PayPal?',
  task: { ...makeCheckIn().task, review_status: 'input', has_worktree: true },
  ...overrides,
})

describe('CheckInQueue questions', () => {
  it('shows the question whole and opens the thread behind it', async () => {
    const checkIn = question()
    const wrapper = mount(CheckInQueue, { props: { queue: [checkIn] } })

    expect(wrapper.text()).toContain('Needs your answer')
    expect(wrapper.find('.check-in__text').text()).toBe('Stripe or PayPal?')

    await wrapper.find('.check-in__open').trigger('click')
    expect(wrapper.emitted('view')?.[0]).toEqual([checkIn])
  })

  it('sends a typed answer back', async () => {
    const checkIn = question()
    const wrapper = mount(CheckInQueue, { props: { queue: [checkIn] } })

    await wrapper.find('textarea').setValue('Stripe')
    await buttonLabelled(wrapper, 'Send answer').trigger('click')

    expect(wrapper.emitted('answer')).toEqual([[checkIn, 'Stripe']])
  })

  it('puts a question off to the back of the queue without clearing it', async () => {
    // "Later" keeps the question: the thread is still parked on it.
    const first = question()
    const second = question({ id: 2, body: 'Which colour?' })
    const wrapper = mount(CheckInQueue, { props: { queue: [first, second] } })

    await buttonLabelled(wrapper, 'Later').trigger('click')

    expect(wrapper.emitted('later')?.[0]).toEqual([first])
    expect(wrapper.emitted('dismiss')).toBeUndefined()
  })

  it('offers no "Later" when there is nothing to put it behind', () => {
    const wrapper = mount(CheckInQueue, { props: { queue: [question()] } })
    expect(wrapper.findAll('button').some(b => b.text().trim() === 'Later')).toBe(false)
  })

  it('counts what is waiting once more than one is', () => {
    const wrapper = mount(CheckInQueue, {
      props: { queue: [question(), question({ id: 2 })] },
    })
    expect(wrapper.find('.queue-head').text()).toContain('Waiting on you')
    expect(wrapper.find('.queue-head__count').text()).toBe('2')
  })

  it('names the job the way the coordinator chat names it', () => {
    const wrapper = mount(CheckInQueue, { props: { queue: [question()] } })

    expect(wrapper.find('.check-in__title').text()).toBe('Adding a contact page')
  })

  it('offers the pick between takes the user asked to compare', async () => {
    const checkIn = makeCheckIn({
      kind: 'ready',
      body: 'Take one of the pricing table.',
      task: { ...makeCheckIn().task, review_status: 'ready', variant_group: 'v1' },
    })
    const wrapper = mount(CheckInQueue, { props: { queue: [checkIn] } })

    expect(wrapper.text()).toContain('Pick one of your options')
    await buttonLabelled(wrapper, 'Use this one').trigger('click')
    expect(wrapper.emitted('accept')?.[0]).toEqual([checkIn])
    await buttonLabelled(wrapper, 'Discard').trigger('click')
    expect(wrapper.emitted('dismiss')?.[0]).toEqual([checkIn])
  })
})

describe('CheckInQueue question with choices', () => {
  it('answers with one tap', async () => {
    const checkIn = makeCheckIn({
      kind: 'question',
      body: 'Pickup or delivery?',
      options: ['Pickup only', 'Pickup and delivery'],
    })
    const wrapper = mount(CheckInQueue, { props: { queue: [checkIn] } })

    await buttonLabelled(wrapper, 'Pickup only').trigger('click')

    expect(wrapper.emitted('answer')).toEqual([[checkIn, 'Pickup only']])
  })
})
