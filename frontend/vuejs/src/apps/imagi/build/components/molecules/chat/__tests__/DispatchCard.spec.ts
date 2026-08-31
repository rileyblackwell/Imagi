import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DispatchCard from '../DispatchCard.vue'
import type { AgentInstance } from '@/apps/imagi/build/types/services'

let nextId = 1

function makeTask(overrides: Partial<AgentInstance> = {}): AgentInstance {
  return {
    id: `inst-${nextId++}`,
    conversationId: nextId,
    title: 'Add a contact page',
    kind: 'task',
    parentId: 1,
    reviewStatus: 'active',
    variantGroup: '',
    hasWorktree: true,
    totalTokens: null,
    selectedModelId: 'gpt-5.6-terra',
    selectedEffort: 'medium',
    selectedFile: null,
    conversation: [],
    isProcessing: false,
    statusText: '',
    archivedAt: null,
    updatedAt: new Date().toISOString(),
    lastMessagePreview: '',
    lastAssistantSummary: '',
    brief: 'Adding a contact page so customers can reach you.',
    messagesLoaded: true,
    hasUnread: false,
    queuedPrompt: null,
    ...overrides,
  }
}

const mountCard = (instance: AgentInstance | null) =>
  mount(DispatchCard, { props: { title: 'Add a contact page', instance } })

const statusOf = (wrapper: ReturnType<typeof mountCard>) =>
  wrapper.find('.dispatch-card__status').text()

describe('DispatchCard', () => {
  it('reports a run that died instead of saying it is starting', () => {
    // The bug this covers: a failed task's status had no case of its own, so
    // the card fell through to the dispatched-but-not-started branch and read
    // "Starting…" forever — for a subagent that had already stopped.
    const wrapper = mountCard(makeTask({
      reviewStatus: 'failed',
      lastMessagePreview: 'I started on the contact form and',
    }))

    expect(statusOf(wrapper)).toBe('Stopped before finishing')
    expect(wrapper.classes()).toContain('dispatch-card--stopped')
    // What it managed to say before it died is still worth showing.
    expect(wrapper.find('.dispatch-card__result').text())
      .toBe('I started on the contact form and')
  })

  it('shows a finished subagent its whole sign-off, every sentence of it', () => {
    // The sign-off is a four-to-six-sentence paragraph written for the owner,
    // and this card is the only place most of them read it. Anything that
    // renders the clipped list-row preview instead drops the end of it.
    const signOff =
      'Your contact page now has a form people can fill in without leaving ' +
      'the site. It asks for a name, an email address and a message, and it ' +
      'tells someone right away if they have missed one. Your phone number ' +
      'and address sit next to the form so people can pick whichever suits ' +
      'them. The whole page reads clearly on a phone. Messages come to the ' +
      'email address in your settings, so change that if it is the wrong one.'
    const wrapper = mountCard(makeTask({
      reviewStatus: 'accepted',
      lastAssistantSummary: signOff,
      lastMessagePreview: 'Your contact page now has a form people can',
    }))

    expect(statusOf(wrapper)).toBe('Subagent complete')
    expect(wrapper.find('.dispatch-card__result').text()).toBe(signOff)
  })

  it('shows a stopped run its whole last words too', () => {
    // Same reason as a finished one: the half-finished account of what did
    // and did not land is exactly the part a clipped preview cuts off.
    const wrapper = mountCard(makeTask({
      reviewStatus: 'failed',
      lastAssistantSummary: 'I got the form onto the page, but the address block is still missing.',
      lastMessagePreview: 'I got the form onto the page, but',
    }))

    expect(wrapper.find('.dispatch-card__result').text())
      .toBe('I got the form onto the page, but the address block is still missing.')
  })

  it('never leaves a complete card with nothing under it', () => {
    // "Subagent complete" over an empty space says nothing about the app. A
    // run that signed off with no words at all still owes the owner a line.
    for (const reviewStatus of ['accepted', 'ready'] as const) {
      const wrapper = mountCard(makeTask({ reviewStatus }))
      expect(wrapper.find('.dispatch-card__result').text())
        .toBe('It finished without saying what it changed — open it to see the work.')
    }
  })

  it('still says the job it was given', () => {
    const wrapper = mountCard(makeTask({ reviewStatus: 'failed' }))
    expect(wrapper.find('.dispatch-card__task').text())
      .toBe('Adding a contact page so customers can reach you.')
  })

  it('shows a live run as working whatever its stored status', () => {
    const wrapper = mountCard(makeTask({ reviewStatus: 'failed', isProcessing: true }))
    expect(statusOf(wrapper)).toBe('Working on this now…')
  })

  it('keeps Starting… for a dispatch whose run has not fired', () => {
    expect(statusOf(mountCard(makeTask({ reviewStatus: 'active' }))))
      .toBe('Starting…')
    expect(statusOf(mountCard(null))).toBe('Starting…')
  })
})
