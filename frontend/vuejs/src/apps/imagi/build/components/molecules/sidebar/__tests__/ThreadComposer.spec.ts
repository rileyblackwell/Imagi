import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import ThreadComposer from '../ThreadComposer.vue'
import { useAgentStore } from '@/apps/imagi/build/stores/agentStore'
import type { AgentInstance } from '@/apps/imagi/build/types/services'

vi.mock('@/apps/imagi/build/services/agentService', () => ({ AgentService: {} }))

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
    await wrapper.find('button.thread-send').trigger('click')

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

  it('asks for an answer when the thread is waiting on one', () => {
    const { wrapper } = mountFor(makeThread({ reviewStatus: 'input' }))
    expect(wrapper.find('textarea').attributes('placeholder')).toBe('Answer this thread…')
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
