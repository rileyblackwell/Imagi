import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import ChatConversation from '../organisms/chat/ChatConversation.vue'
import { useAgentStore } from '@/apps/imagi/build/stores/agentStore'
import type { AgentInstance, AIMessage } from '@/apps/imagi/build/types/services'

const user = (content: string): AIMessage => ({
  role: 'user', content, timestamp: '2026-01-01T00:00:00Z', id: 'u1',
})
const assistant = (content: string): AIMessage => ({
  role: 'assistant', content, timestamp: '2026-01-01T00:00:01Z', id: 'a1',
})

const indicatorText = (wrapper: ReturnType<typeof mount>) => {
  const indicator = wrapper.find('.agent-status')
  return indicator.exists() ? indicator.element.textContent?.trim() : null
}

describe('ChatConversation activity indicator', () => {
  // Dispatch cards read subagent state straight from the store, so the
  // component needs a pinia even when the transcript has no cards in it.
  beforeEach(() => setActivePinia(createPinia()))

  const mountWith = (props: object) =>
    mount(ChatConversation, { props: { messages: [user('hi')], ...props } })

  it('shows the status while the agent has not started replying', () => {
    const wrapper = mountWith({ isProcessing: true, statusText: 'Thinking…' })
    expect(indicatorText(wrapper)).toBe('Thinking…')
  })

  it('falls back to a generic label without a status', () => {
    const wrapper = mountWith({ isProcessing: true })
    expect(indicatorText(wrapper)).toBe('Working…')
  })

  it('hides while the reply is streaming in', () => {
    // The growing assistant message already shows progress; a second
    // indicator under it would just dangle.
    const wrapper = mountWith({
      isProcessing: true,
      statusText: '',
      messages: [user('hi'), assistant('partial reply')],
    })
    expect(indicatorText(wrapper)).toBeNull()
  })

  it('returns with tool activity after text has streamed', () => {
    const wrapper = mountWith({
      isProcessing: true,
      statusText: 'Editing project files…',
      messages: [user('hi'), assistant('working on it')],
    })
    expect(indicatorText(wrapper)).toBe('Editing project files…')
  })

  it('hides when the run is over', () => {
    const wrapper = mountWith({
      isProcessing: false,
      messages: [user('hi'), assistant('done')],
    })
    expect(indicatorText(wrapper)).toBeNull()
  })
})

describe('ChatConversation dispatch card', () => {
  beforeEach(() => setActivePinia(createPinia()))

  const withSubagent = (instance: Partial<AgentInstance>) => {
    const store = useAgentStore()
    store.instances = [{
      id: 'inst-1',
      conversationId: 7,
      title: 'Contact page',
      kind: 'task',
      parentId: null,
      reviewStatus: '',
      variantGroup: '',
      hasWorktree: false,
      totalTokens: null,
      selectedModelId: null,
      selectedEffort: 'medium',
      selectedFile: null,
      conversation: [],
      isProcessing: false,
      statusText: '',
      archivedAt: null,
      updatedAt: '2026-01-01T00:00:00Z',
      lastMessagePreview: '',
      messagesLoaded: true,
      hasUnread: false,
      queuedPrompt: null,
      ...instance,
    } as AgentInstance]
    const reply: AIMessage = {
      ...assistant('On it.'),
      dispatchedTasks: [{ conversationId: 7, title: 'Contact page' }],
    }
    return mount(ChatConversation, { props: { messages: [user('hi'), reply] } })
  }

  it('names the task and says it is being worked on', () => {
    const wrapper = withSubagent({
      isProcessing: true,
      lastMessagePreview: 'Reading the router…',
    })

    const card = wrapper.find('.dispatch-card')
    expect(card.classes()).toContain('dispatch-card--working')
    expect(card.text()).toContain('Contact page')
    expect(card.text()).toContain('Working on this now…')
    // Mid-run chatter is not a result; the card stays a status, not a log.
    expect(card.text()).not.toContain('Reading the router…')
  })

  it('turns into a confirmation once the work lands', () => {
    // The card is the notice, not the transcript: it confirms the named task
    // landed, and the subagent's full account stays in its own thread (one
    // click away) rather than being pasted into the main thread.
    const wrapper = withSubagent({
      reviewStatus: 'accepted',
      lastMessagePreview: 'Added a /contact route with a validated form.',
    })

    const card = wrapper.find('.dispatch-card')
    expect(card.classes()).toContain('dispatch-card--done')
    expect(card.text()).toContain('Contact page')
    expect(card.text()).toContain('Done')
    expect(card.text()).not.toContain('Added a /contact route with a validated form.')
  })

  it('surfaces a subagent that is blocked on a question', () => {
    // The question is answered in the check-in queue above the composer, but
    // it has to be readable from the card too — a status line alone cannot be
    // acted on.
    const wrapper = withSubagent({
      reviewStatus: 'input',
      lastMessagePreview: 'Should the form email you or open a ticket?',
    })

    const card = wrapper.find('.dispatch-card')
    expect(card.classes()).toContain('dispatch-card--asking')
    expect(card.text()).toContain('Needs an answer from you')
    expect(card.text()).toContain('Should the form email you or open a ticket?')
  })

  it('falls back to starting when the store has no instance yet', () => {
    // A reloaded transcript renders its cards before the instances load.
    const store = useAgentStore()
    store.instances = []
    const reply: AIMessage = {
      ...assistant('On it.'),
      dispatchedTasks: [{ conversationId: 7, title: 'Contact page' }],
    }
    const wrapper = mount(ChatConversation, { props: { messages: [user('hi'), reply] } })

    const card = wrapper.find('.dispatch-card')
    expect(card.text()).toContain('Contact page')
    expect(card.text()).toContain('Starting…')
  })
})
