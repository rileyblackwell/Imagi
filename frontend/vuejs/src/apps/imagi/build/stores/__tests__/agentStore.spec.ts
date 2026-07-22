import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import type { AgentInstance } from '../../types/services'

// Mock the services the store talks to (no network in unit tests).
const agentService = vi.hoisted(() => ({
  listConversations: vi.fn(),
  createConversation: vi.fn(),
  getConversation: vi.fn(),
  getConversationMessages: vi.fn(),
  updateConversation: vi.fn(),
  deleteConversation: vi.fn(),
  cancelConversationRun: vi.fn(),
  acceptTask: vi.fn(),
  dismissTask: vi.fn(),
  restoreCheckpoint: vi.fn(),
}))
vi.mock('../../services/agentService', () => ({ AgentService: agentService }))

const fileService = vi.hoisted(() => ({
  getProjectFiles: vi.fn(),
  undoFileChanges: vi.fn(),
}))
vi.mock('../../services/fileService', () => ({ FileService: fileService }))

import { useAgentStore } from '@/apps/imagi/build/stores/agentStore'

let nextId = 1

function makeInstance(overrides: Partial<AgentInstance> = {}): AgentInstance {
  return {
    id: `inst-${nextId++}`,
    conversationId: nextId,
    title: '',
    kind: 'chat',
    parentId: null,
    reviewStatus: '',
    variantGroup: '',
    hasWorktree: false,
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
    messagesLoaded: true,
    hasUnread: false,
    queuedPrompt: null,
    ...overrides,
  }
}

describe('agent store manager taxonomy', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  it('keeps a live lead out of history', () => {
    const store = useAgentStore()
    store.instances = [makeInstance({ kind: 'lead' })]
    expect(store.historyInstances).toHaveLength(0)
    expect(store.leadInstance?.id).toBe(store.instances[0]!.id)
  })

  it('surfaces a duplicate live lead in history so it stays reachable', () => {
    // A backend race can leave two live leads; the loser matches no live
    // section, so History must show it (archivable/deletable) instead of
    // letting it become an invisible orphan.
    const store = useAgentStore()
    const primary = makeInstance({ kind: 'lead' })
    const duplicate = makeInstance({ kind: 'lead' })
    store.instances = [primary, duplicate]

    expect(store.leadInstance?.id).toBe(primary.id)
    expect(store.historyInstances.map(i => i.id)).toEqual([duplicate.id])
  })

  it('keeps archived leads, legacy chats and resolved tasks in history', () => {
    const store = useAgentStore()
    const archivedLead = makeInstance({ kind: 'lead', archivedAt: new Date().toISOString() })
    const chat = makeInstance({ kind: 'chat' })
    const accepted = makeInstance({ kind: 'task', reviewStatus: 'accepted' })
    const active = makeInstance({ kind: 'task', reviewStatus: 'active' })
    store.instances = [archivedLead, chat, accepted, active]

    const ids = store.historyInstances.map(i => i.id)
    expect(ids).toContain(archivedLead.id)
    expect(ids).toContain(chat.id)
    expect(ids).toContain(accepted.id)
    expect(ids).not.toContain(active.id)
  })
})

describe('agent store deleteInstance', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  it('removes the instance when the server delete succeeds', async () => {
    const store = useAgentStore()
    const lead = makeInstance({ kind: 'lead' })
    const task = makeInstance({ kind: 'task' })
    store.instances = [lead, task]
    store.activeInstanceId = lead.id
    agentService.deleteConversation.mockResolvedValue(undefined)

    await store.deleteInstance(task.id)

    expect(store.instances.map(i => i.id)).toEqual([lead.id])
  })

  it('keeps the instance and rethrows when the server refuses the delete', async () => {
    // A 409 agent_busy (running task) must not fake a local deletion that
    // resurrects on reload.
    const store = useAgentStore()
    const lead = makeInstance({ kind: 'lead' })
    const task = makeInstance({ kind: 'task', isProcessing: true })
    store.instances = [lead, task]
    store.activeInstanceId = lead.id
    const busy = Object.assign(new Error('agent_busy'), {
      response: { status: 409, data: { detail: 'agent_busy' } },
    })
    agentService.deleteConversation.mockRejectedValue(busy)

    await expect(store.deleteInstance(task.id)).rejects.toBe(busy)

    expect(store.instances.map(i => i.id)).toEqual([lead.id, task.id])
  })
})
