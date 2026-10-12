import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import type { AgentInstance, ThreadScheduleDto } from '../../types/services'

// Mock the services the store talks to (no network in unit tests).
const agentService = vi.hoisted(() => ({
  getConversation: vi.fn(),
  listCheckIns: vi.fn(),
  listMemory: vi.fn(),
  addMemory: vi.fn(),
  updateMemory: vi.fn(),
  deleteMemory: vi.fn(),
}))
vi.mock('../../services/agentService', () => ({ AgentService: agentService }))
vi.mock('../../services/fileService', () => ({ FileService: { getProjectFiles: vi.fn() } }))

import { useAgentStore, isHeldThread } from '@/apps/imagi/build/stores/agentStore'
import { heldStatus, scheduleLine } from '@/apps/imagi/build/utils/threadSchedule'

const settle = () => new Promise(resolve => setTimeout(resolve, 0))

let nextId = 100

function thread(overrides: Partial<AgentInstance> = {}): AgentInstance {
  return {
    id: `inst-${nextId++}`,
    conversationId: nextId,
    title: '',
    kind: 'task',
    parentId: 1,
    reviewStatus: 'active',
    variantGroup: '',
    hasWorktree: false,
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

function schedule(overrides: Partial<ThreadScheduleDto> = {}): ThreadScheduleDto {
  return {
    task_id: 1,
    status: 'waiting',
    placement: 'new',
    reason: '',
    waits_on: [{ id: 11, title: 'Adding a menu', review_status: 'active', status: 'running' }],
    queued_after: 0,
    forked_from: null,
    ...overrides,
  }
}

describe('scheduled threads', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  it('holds a dispatch that waits on other threads instead of starting it', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    const menu = thread({ conversationId: 11, brief: 'Adding a menu', isProcessing: true })
    store.instances = [menu]
    agentService.getConversation.mockResolvedValue({ id: 12, schedule: schedule(), review_status: 'active' })

    store.startDispatchedTasks([{
      conversation_id: 12, title: 'Link the shop', brief: 'Link the shop from the menu',
      goal: 'Linking the shop', overview: '', variant_group: '', parent: 1,
      model_name: 'claude-opus-5-5', waiting: true, depends_on_threads: [11],
    }])
    await settle()

    expect(runs).not.toHaveBeenCalled()
    const held = store.instances.find(i => i.conversationId === 12)!
    expect(isHeldThread(held)).toBe(true)
    expect(store.scheduledThreads.map(i => i.conversationId)).toEqual([12])
    expect(store.workingThreads.map(i => i.conversationId)).toEqual([11])
    expect(held.schedule?.waits_on[0]?.title).toBe('Adding a menu')
  })

  it('follows a held thread once the server releases it', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    const held = thread({ conversationId: 21, schedule: schedule() })
    store.instances = [held]

    agentService.getConversation.mockResolvedValue({
      id: 21, review_status: 'active', updated_at: new Date().toISOString(),
      schedule: schedule({ status: 'queued' }), queued_prompt: 'Link the shop', is_running: false,
    })
    await store.syncHeldThreads()
    await settle()

    expect(isHeldThread(held)).toBe(false)
    expect(runs).toHaveBeenCalledWith(held.id, 'Link the shop')
  })

  it('leaves a thread that is still waiting alone', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    const held = thread({ conversationId: 31, schedule: schedule() })
    store.instances = [held]
    agentService.getConversation.mockResolvedValue({
      id: 31, review_status: 'active', updated_at: new Date().toISOString(),
      schedule: schedule({ status: 'blocked', waits_on: [{ id: 11, title: 'Adding a menu', review_status: 'failed', status: 'failed' }] }),
      queued_prompt: '', is_running: false,
    })

    await store.syncHeldThreads()
    await settle()

    expect(runs).not.toHaveBeenCalled()
    expect(held.schedule?.status).toBe('blocked')
    expect(store.scheduledThreads).toHaveLength(1)
  })
})

describe('schedule wording', () => {
  it('says what a held thread starts after, or what it is on hold for', () => {
    expect(scheduleLine(schedule({
      waits_on: [
        { id: 1, title: 'Adding a menu', review_status: 'active' },
        { id: 2, title: 'Adding a shop', review_status: 'active' },
      ],
    }))?.text).toBe('Starts after Adding a menu and Adding a shop')
    const blocked = schedule({
      status: 'blocked',
      waits_on: [{ id: 1, title: 'Adding a menu', review_status: 'failed', status: 'failed' }],
    })
    expect(scheduleLine(blocked)?.kind).toBe('blocked')
    expect(heldStatus(blocked)).toBe('On hold: Adding a menu stopped')
  })

  it('names the thread a fork started from, and says nothing for plain threads', () => {
    expect(scheduleLine(schedule({
      status: 'running', waits_on: [], placement: 'fork',
      forked_from: { id: 4, title: 'Redesigning home', review_status: 'active' },
    }))?.text).toBe('Forked from Redesigning home')
    expect(scheduleLine(schedule({ status: 'running', waits_on: [] }))).toBeNull()
    expect(scheduleLine(null)).toBeNull()
  })
})

describe('project memory', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  it('replaces an entry saved again under the same topic', async () => {
    const store = useAgentStore()
    store.projectId = '5'
    store.memoryEntries = [
      { id: 1, key: 'Brand colors', value: 'Navy', status: 'active', author: 'user', source: null, updated_at: '' },
    ]
    agentService.addMemory.mockResolvedValue(
      { id: 2, key: 'brand colors', value: 'Navy and coral', status: 'active', author: 'user', source: null, updated_at: '' },
    )

    await store.addMemory('brand colors', 'Navy and coral')

    expect(store.memoryEntries.map(e => e.value)).toEqual(['Navy and coral'])
  })

  it('puts an entry back when removing it fails', async () => {
    const store = useAgentStore()
    const entry = { id: 3, key: 'Tone', value: 'Friendly', status: 'active' as const, author: 'user' as const, source: null, updated_at: '' }
    store.memoryEntries = [entry]
    agentService.deleteMemory.mockRejectedValue(new Error('offline'))

    await expect(store.removeMemory(3)).rejects.toThrow('offline')
    expect(store.memoryEntries).toEqual([entry])
  })
})
