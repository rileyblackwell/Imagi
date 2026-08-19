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
