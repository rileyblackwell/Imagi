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

  it('stays out of the transcript when the pane reports the run itself', () => {
    // The main thread's masthead carries the status line, so a second one
    // trailing the transcript would say the same thing twice.
    const wrapper = mountWith({ isProcessing: true, statusText: 'Thinking…', showStatus: false })
    expect(indicatorText(wrapper)).toBeNull()
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
      brief: '',
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

  it('says what it is working on while it works', () => {
    const wrapper = withSubagent({
      isProcessing: true,
      brief: 'Add a contact page so customers can get in touch.',
      lastMessagePreview: 'Reading the router…',
    })

    const card = wrapper.find('.dispatch-card')
    expect(card.classes()).toContain('dispatch-card--working')
    expect(card.text()).toContain('Contact page')
    expect(card.text()).toContain('Working on this now…')
    expect(card.text()).toContain('Add a contact page so customers can get in touch.')
    // Mid-run chatter is not what it is working on; the card reports the job,
    // not the keystrokes.
    expect(card.text()).not.toContain('Reading the router…')
  })

  it('says what a dispatched task will work on before its run fires', () => {
    const wrapper = withSubagent({
      reviewStatus: 'active',
      brief: 'Add a contact page so customers can get in touch.',
    })

    const card = wrapper.find('.dispatch-card')
    expect(card.text()).toContain('Starting…')
    expect(card.text()).toContain('Add a contact page so customers can get in touch.')
  })

  it('reports the subagent complete, with what it did', () => {
    // The completion says two things: that the subagent is done, and — in its
    // own words — what it built. "Added to your app" told the user where the
    // work went but never what it was. The brief the working card was showing
    // is replaced by the result: the same line, now reporting the outcome.
    const wrapper = withSubagent({
      reviewStatus: 'accepted',
      brief: 'Add a contact page so customers can get in touch.',
      lastMessagePreview:
        'Your site now has a contact page. Visitors can send you a message '
        + 'without leaving the site, and it turns away obviously bad addresses '
        + 'before sending.',
    })

    const card = wrapper.find('.dispatch-card')
    expect(card.classes()).toContain('dispatch-card--done')
    expect(card.text()).toContain('Contact page')
    expect(card.text()).toContain('Subagent complete')
    expect(card.text()).toContain('Your site now has a contact page.')
    expect(card.text()).not.toContain('Add a contact page so customers can get in touch.')
  })

  it('falls back to the brief when a finished task left no summary', () => {
    // A run that died before its sign-off still has to say what it was for —
    // a green "complete" over an empty line tells the user nothing.
    const wrapper = withSubagent({
      reviewStatus: 'accepted',
      brief: 'Add a contact page so customers can get in touch.',
      lastMessagePreview: '',
    })

    expect(wrapper.find('.dispatch-card').text())
      .toContain('Add a contact page so customers can get in touch.')
  })

  it('describes the work on a completion that still wants a review', () => {
    // A task that could not merge itself parks at 'ready'. It is just as
    // finished, so it reports the same way — plus the pending decision.
    const wrapper = withSubagent({
      reviewStatus: 'ready',
      lastMessagePreview: 'Built two takes on the pricing table.',
    })

    const card = wrapper.find('.dispatch-card')
    expect(card.text()).toContain('Subagent complete — waiting on you')
    expect(card.text()).toContain('Built two takes on the pricing table.')
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
