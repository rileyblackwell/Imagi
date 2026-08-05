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

  it('lands directly under the message that started the run', () => {
    // The whole point of the indicator living here rather than in the
    // masthead: you send something and the answer to "is it doing anything?"
    // appears where you are already looking.
    const wrapper = mountWith({ isProcessing: true, statusText: 'Thinking…' })
    const rows = wrapper.findAll('.msg-row')
    expect(rows[rows.length - 1].find('.agent-status').exists()).toBe(true)
  })

  it('follows the run from step to step', async () => {
    const wrapper = mountWith({ isProcessing: true, statusText: 'Thinking…' })
    await wrapper.setProps({ statusText: 'Editing project files…' })
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

  const JOB = 'Adding a contact page so customers can get in touch with you.'
  const SUMMARY =
    'Your site now has a contact page. Visitors can send you a message without '
    + 'leaving the site, and it checks the address before sending so you get '
    + 'fewer dead replies.'

  it('says what it is working on while it works', () => {
    const wrapper = withSubagent({
      isProcessing: true,
      brief: JOB,
      lastMessagePreview: 'Reading the router…',
    })

    const card = wrapper.find('.dispatch-card')
    expect(card.classes()).toContain('dispatch-card--working')
    expect(card.text()).toContain('Working on this now…')
    expect(card.find('.dispatch-card__task').text()).toBe(JOB)
    // Nothing has come back yet, so there is no result half at all — and
    // mid-run chatter is not a result.
    expect(card.find('.dispatch-card__result').exists()).toBe(false)
    expect(card.text()).not.toContain('Reading the router…')
  })

  it('says what a dispatched task will work on before its run fires', () => {
    const wrapper = withSubagent({ reviewStatus: 'active', brief: JOB })

    const card = wrapper.find('.dispatch-card')
    expect(card.text()).toContain('Starting…')
    expect(card.find('.dispatch-card__task').text()).toBe(JOB)
  })

  it('keeps the job on screen and adds what it did once complete', () => {
    // "Complete" is only meaningful beside what was asked, so the finished
    // card carries both: the job it was given, then the changes it made.
    const wrapper = withSubagent({
      reviewStatus: 'accepted',
      brief: JOB,
      lastMessagePreview: SUMMARY,
    })

    const card = wrapper.find('.dispatch-card')
    expect(card.classes()).toContain('dispatch-card--done')
    expect(card.text()).toContain('Subagent complete')
    expect(card.find('.dispatch-card__task').text()).toBe(JOB)
    expect(card.find('.dispatch-card__result').text()).toBe(SUMMARY)
  })

  it('renders the whole description rather than clipping it', () => {
    // The complaint this card exists to answer: on a phone the job was cut to
    // one line and ellipsised. Nothing may clamp, truncate, or nowrap it.
    const wrapper = withSubagent({ isProcessing: true, brief: JOB })

    const task = wrapper.find('.dispatch-card__task')
    expect(task.text()).toBe(JOB)
    expect(task.text()).not.toContain('…')
    expect(task.classes()).not.toContain('truncate')
    expect(task.attributes('style') || '').not.toContain('nowrap')
  })

  it('still names the job when a finished task left no summary', () => {
    // A run that died before its sign-off has no result half — but a green
    // "complete" over an empty card would say nothing at all.
    const wrapper = withSubagent({
      reviewStatus: 'accepted',
      brief: JOB,
      lastMessagePreview: '',
    })

    const card = wrapper.find('.dispatch-card')
    expect(card.find('.dispatch-card__task').text()).toBe(JOB)
    expect(card.find('.dispatch-card__result').exists()).toBe(false)
  })

  it('describes the work on a completion that still wants a review', () => {
    // A task that could not merge itself parks at 'ready'. It is just as
    // finished, so it reports the same way — plus the pending decision.
    const wrapper = withSubagent({
      reviewStatus: 'ready',
      brief: JOB,
      lastMessagePreview: 'Built two takes on the pricing table.',
    })

    const card = wrapper.find('.dispatch-card')
    expect(card.text()).toContain('Subagent complete — waiting on you')
    expect(card.find('.dispatch-card__task').text()).toBe(JOB)
    expect(card.find('.dispatch-card__result').text()).toBe('Built two takes on the pricing table.')
  })

  it('surfaces a subagent that is blocked on a question', () => {
    // The question is answered in the check-in queue above the composer, but
    // it has to be readable from the card too — a status line alone cannot be
    // acted on.
    const wrapper = withSubagent({
      reviewStatus: 'input',
      brief: JOB,
      lastMessagePreview: 'Should the form email you or open a ticket?',
    })

    const card = wrapper.find('.dispatch-card')
    expect(card.classes()).toContain('dispatch-card--asking')
    expect(card.text()).toContain('Needs an answer from you')
    expect(card.find('.dispatch-card__result').text())
      .toBe('Should the form email you or open a ticket?')
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
