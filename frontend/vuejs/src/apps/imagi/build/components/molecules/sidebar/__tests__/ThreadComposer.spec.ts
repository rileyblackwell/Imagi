import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import ThreadComposer from '../ThreadComposer.vue'
import { useAgentStore } from '@/apps/imagi/build/stores/agentStore'
import type { AgentInstance } from '@/apps/imagi/build/types/services'

vi.mock('@/apps/imagi/build/services/agentService', () => ({
  AgentService: { updateConversation: vi.fn(() => Promise.resolve({})) },
}))

function makeThread(overrides: Partial<AgentInstance> = {}): AgentInstance {
  return {
    id: 'inst-thread',
    conversationId: 42,
    title: 'Booking page',
    kind: 'task',
    parentId: 1,
    reviewStatus: 'input',
    variantGroup: '',
    hasWorktree: true,
    totalTokens: null,
    selectedModelId: 'claude-opus-5-5',
    selectedEffort: 'medium',
    selectedFile: null,
    conversation: [],
    isProcessing: false,
    statusText: '',
    archivedAt: null,
    updatedAt: new Date().toISOString(),
    lastMessagePreview: '',
    lastAssistantSummary: '',
    brief: '',
    overview: '',
    messagesLoaded: true,
    hasUnread: false,
    queuedPrompt: null,
    ...overrides,
  }
}

function mountFor(thread: AgentInstance) {
  const store = useAgentStore()
  store.instances = [thread]
  // The store hands back its reactive copy; the component reads that one.
  const instance = store.instances[0]!
  return { store, wrapper: mount(ThreadComposer, { props: { instance } }) }
}

describe('ThreadComposer', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('sends what the user types to the thread and clears the box', async () => {
    const { store, wrapper } = mountFor(makeThread())
    const steer = vi.spyOn(store, 'steerThread').mockReturnValue(true)

    await wrapper.find('textarea').setValue('We are open Saturdays, 9 to 1')
    await wrapper.find('button.btn-send').trigger('click')

    expect(steer).toHaveBeenCalledWith('inst-thread', 'We are open Saturdays, 9 to 1')
    expect((wrapper.find('textarea').element as HTMLTextAreaElement).value).toBe('')
  })

  it('sends on Enter', async () => {
    const { store, wrapper } = mountFor(makeThread())
    const steer = vi.spyOn(store, 'steerThread').mockReturnValue(true)

    await wrapper.find('textarea').setValue('keep going')
    await wrapper.find('textarea').trigger('keydown', { key: 'Enter' })

    expect(steer).toHaveBeenCalledWith('inst-thread', 'keep going')
  })

  it('says the thread can be steered', () => {
    const { wrapper } = mountFor(makeThread({ reviewStatus: 'accepted' }))
    expect(wrapper.find('textarea').attributes('placeholder')).toBe('Steer this thread…')
  })

  it('asks for an answer when the thread is waiting on one', () => {
    const { wrapper } = mountFor(makeThread({ reviewStatus: 'input' }))
    expect(wrapper.find('textarea').attributes('placeholder')).toBe('Answer this thread, or steer it somewhere else…')
  })

  it('wears the coordinator composer: model and reasoning, usage, and the mic button', () => {
    const { wrapper } = mountFor(makeThread())
    const chips = wrapper.findAll('button.control-chip').map(c => c.attributes('aria-label'))
    expect(chips).toEqual(['Model and reasoning', 'Usage limits'])
    expect(wrapper.find('button.btn-send').exists()).toBe(true)
  })

  it('changes the model on this thread only', async () => {
    const { store, wrapper } = mountFor(makeThread())
    const setModel = vi.spyOn(store, 'setInstanceModel').mockImplementation(() => {})
    await wrapper.find('button[aria-label="Model and reasoning"]').trigger('click')
    const fable = wrapper.findAll('#tune-panel button.model-row').find(r => r.text().includes('Fable'))!
    await fable.trigger('click')
    expect(setModel).toHaveBeenCalledWith('inst-thread', 'claude-fable-5-1')
  })

  it('shows one family at a time, switched from the menu head', async () => {
    const { store, wrapper } = mountFor(makeThread())
    const setModel = vi.spyOn(store, 'setInstanceModel').mockImplementation(() => {})
    await wrapper.find('button[aria-label="Model and reasoning"]').trigger('click')
    const rows = () => wrapper.findAll('#tune-panel button.model-row').map(r => r.text())
    expect(rows().some(r => r.includes('Opus'))).toBe(true)
    expect(rows().some(r => r.includes('Sol'))).toBe(false)
    // No speed choice on a Claude model.
    expect(wrapper.find('[data-testid="speed-options"]').exists()).toBe(false)

    await wrapper.find('[data-testid="model-family-openai"]').trigger('click')
    expect(rows().map(r => r.split(' ')[0])).toEqual(['Luna', 'Terra', 'Sol', 'Astra'])
    expect(setModel).not.toHaveBeenCalled()
    const sol = wrapper.findAll('#tune-panel button.model-row').find(r => r.text().startsWith('Sol'))!
    await sol.trigger('click')
    expect(setModel).toHaveBeenCalledWith('inst-thread', 'gpt-6.1-sol')
  })

  it('offers Fast and Ultrafast on an OpenAI model, with what they cost', async () => {
    const { store, wrapper } = mountFor(makeThread({ selectedModelId: 'gpt-6.1-sol' }))
    const setTier = vi.spyOn(store, 'setInstanceServiceTier')
    await wrapper.find('button[aria-label="Model and reasoning"]').trigger('click')
    const speed = wrapper.find('[data-testid="speed-options"]')
    expect(speed.text()).toContain('2x price')
    expect(speed.text()).toContain('6x price')
    const note = wrapper.find('[data-testid="speed-cost-note"]')
    expect(note.text()).toContain('six times')
    expect(note.classes()).not.toContain('tune-note--cost')

    await wrapper.find('[data-testid="speed-ultrafast"]').trigger('click')
    expect(setTier).toHaveBeenCalledWith('inst-thread', 'ultrafast')
    expect(note.classes()).toContain('tune-note--cost')
    expect(wrapper.find('button[aria-label="Model and reasoning"]').text()).toContain('Sol · Medium · Ultrafast')
    // Max is Claude's alone.
    expect(wrapper.findAll('.effort-bar')).toHaveLength(4)
  })

  it('keeps Ultrafast off a model that lacks it', async () => {
    const { wrapper } = mountFor(makeThread({ selectedModelId: 'gpt-6-luna', serviceTier: 'ultrafast' }))
    await wrapper.find('button[aria-label="Model and reasoning"]').trigger('click')
    const ultrafast = wrapper.find('[data-testid="speed-ultrafast"]')
    expect(ultrafast.attributes('disabled')).toBeDefined()
    expect(ultrafast.text()).toContain('On Sol and Astra')
    expect(wrapper.find('[data-testid="speed-standard"]').attributes('aria-checked')).toBe('true')
  })

  it('stops this thread, not the coordinator, from a tap mid-run', async () => {
    const { store, wrapper } = mountFor(makeThread({ reviewStatus: 'active', isProcessing: true }))
    const abort = vi.spyOn(store, 'abortInstanceRun').mockImplementation(() => {})
    await wrapper.find('button.btn-send').trigger('click')
    expect(abort).toHaveBeenCalledWith('inst-thread')
  })

  it('shows a message queued behind a live run, and cancels it', async () => {
    const { store, wrapper } = mountFor(
      makeThread({ reviewStatus: 'active', isProcessing: true, queuedPrompt: 'Make it bold' })
    )
    expect(wrapper.text()).toContain('Make it bold')

    await wrapper.find('button[aria-label="Cancel queued message"]').trigger('click')
    expect(store.instances[0]!.queuedPrompt).toBeNull()
  })

  it('has no box for a discarded thread, only the way back', async () => {
    const { wrapper } = mountFor(makeThread({ reviewStatus: 'dismissed' }))
    expect(wrapper.find('textarea').exists()).toBe(false)
    expect(wrapper.text()).toContain('discarded')

    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('back')).toHaveLength(1)
  })

  it('offers Try again on a thread that stopped, which retries it', async () => {
    const { store, wrapper } = mountFor(makeThread({ reviewStatus: 'failed' }))
    const retry = vi.spyOn(store, 'retryTask').mockImplementation(() => {})

    const button = wrapper.findAll('button').find(b => b.text() === 'Try again')!
    await button.trigger('click')

    expect(retry).toHaveBeenCalledWith(42)
  })
})
