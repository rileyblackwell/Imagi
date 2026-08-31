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
    lastAssistantSummary: '',
    brief: '',
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

describe('agent store workingAgentCount', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  it('counts only the subagents actually running', () => {
    // The badge on the main thread's Subagents switch. activeAgentInstances
    // also holds work that has finished and is waiting on you — a different
    // thing, with its own queue — so counting that list left the badge lit
    // with a number naming nothing the user could act on from there.
    const store = useAgentStore()
    store.instances = [
      makeInstance({ kind: 'task', reviewStatus: 'active', isProcessing: true }),
      makeInstance({ kind: 'task', reviewStatus: 'active', isProcessing: true }),
      makeInstance({ kind: 'task', reviewStatus: 'ready', isProcessing: false }),
      makeInstance({ kind: 'task', reviewStatus: 'input', isProcessing: false }),
    ]

    expect(store.activeAgentInstances).toHaveLength(4)
    expect(store.workingAgentCount).toBe(2)
  })

  it('keeps a task whose run died on the list', () => {
    // A failed task is not settled work: it still holds its worktree and
    // still wants a decision, and History only holds accepted/discarded. If
    // it dropped out of this list it would vanish from the pane entirely.
    const store = useAgentStore()
    const failed = makeInstance({ kind: 'task', reviewStatus: 'failed', isProcessing: false })
    store.instances = [failed]

    expect(store.activeAgentInstances.map(i => i.id)).toEqual([failed.id])
    expect(store.historyInstances).toHaveLength(0)
    // It is not running, so it must not light the Subagents badge.
    expect(store.workingAgentCount).toBe(0)
  })

  it('is zero when the crew is idle, so the badge draws nothing', () => {
    const store = useAgentStore()
    store.instances = [makeInstance({ kind: 'task', reviewStatus: 'ready', isProcessing: false })]

    expect(store.workingAgentCount).toBe(0)
  })

  it('ignores work that is no longer on the hook', () => {
    // Archived, accepted and discarded tasks are out of activeAgentInstances
    // already; a stale isProcessing on one must not leak into the count.
    const store = useAgentStore()
    store.instances = [
      makeInstance({ kind: 'task', reviewStatus: 'accepted', isProcessing: true }),
      makeInstance({ kind: 'task', reviewStatus: 'active', isProcessing: true, archivedAt: new Date().toISOString() }),
      // The lead is the chat pane itself, never one of its own subagents.
      makeInstance({ kind: 'lead', isProcessing: true }),
    ]

    expect(store.workingAgentCount).toBe(0)
  })
})

describe('agent store openSubagent', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  it('reads a subagent without moving the thread the user talks in', async () => {
    const store = useAgentStore()
    const lead = makeInstance({ kind: 'lead' })
    const task = makeInstance({ kind: 'task', hasUnread: true })
    store.instances = [lead, task]
    store.activeInstanceId = lead.id

    await store.openSubagent(task.id)

    expect(store.openedSubagent?.id).toBe(task.id)
    // The composer (and its draft) stay with the lead thread.
    expect(store.activeInstanceId).toBe(lead.id)
    expect(task.hasUnread).toBe(false)
  })

  it('goes back to the list on null', async () => {
    const store = useAgentStore()
    const task = makeInstance({ kind: 'task' })
    store.instances = [task]

    await store.openSubagent(task.id)
    await store.openSubagent(null)

    expect(store.openedSubagent).toBeNull()
  })

  it('closes a subagent the user deleted', async () => {
    const store = useAgentStore()
    const lead = makeInstance({ kind: 'lead' })
    const task = makeInstance({ kind: 'task' })
    store.instances = [lead, task]
    store.activeInstanceId = lead.id
    agentService.deleteConversation.mockResolvedValue(undefined)

    await store.openSubagent(task.id)
    await store.deleteInstance(task.id)

    expect(store.openedSubagentId).toBeNull()
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

describe('agent store startDispatchedTasks', () => {
  // The lead's dispatch payload is what starts a subagent's run, and it can
  // arrive more than once for one task (mid-stream event, then the terminal
  // payload's backstop). One job gets one run.
  function dispatched(conversationId: number, overrides = {}) {
    return {
      conversation_id: conversationId,
      title: 'Redesign the home page',
      brief: 'Redesign the home page with a real hero and testimonials.',
      goal: 'Giving your home page a clearer opening.',
      variant_group: '',
      parent: 1,
      model_name: 'gpt-5.6-terra',
      ...overrides,
    }
  }

  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  it('adopts a dispatched task and starts its run once', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)

    store.startDispatchedTasks([dispatched(9001)])
    await Promise.resolve()

    const adopted = store.instances.find(i => i.conversationId === 9001)
    expect(adopted?.kind).toBe('task')
    expect(runs).toHaveBeenCalledTimes(1)
    expect(runs.mock.calls[0]![0]).toBe(adopted!.id)
  })

  it('never starts a second run for a task it already fired', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)

    store.startDispatchedTasks([dispatched(9002)])
    store.startDispatchedTasks([dispatched(9002)])
    await Promise.resolve()

    expect(store.instances.filter(i => i.conversationId === 9002)).toHaveLength(1)
    expect(runs).toHaveBeenCalledTimes(1)
  })

  it('links a task the server says is already running without re-running it', async () => {
    // The lead asked twice for one job: the server hands back the subagent
    // already doing it, so the reply links to it and nothing restarts.
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)

    store.startDispatchedTasks([dispatched(9003, { already_running: true })])
    await Promise.resolve()

    expect(store.instances.find(i => i.conversationId === 9003)).toBeTruthy()
    expect(runs).not.toHaveBeenCalled()
  })
})

describe('agent store parallel subagents', () => {
  // Several subagents are meant to work at once. What matters is that a
  // dispatch is never lost: it either starts now or waits for a slot, and
  // whoever waited longest goes first.
  function dispatched(conversationId: number, overrides = {}) {
    return {
      conversation_id: conversationId,
      title: 'Job',
      brief: `Do job ${conversationId}.`,
      goal: 'Doing a job.',
      variant_group: '',
      parent: 1,
      model_name: 'gpt-5.6-terra',
      ...overrides,
    }
  }

  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  it('starts several dispatched subagents at once', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)

    store.startDispatchedTasks([
      dispatched(9101), dispatched(9102), dispatched(9103),
    ])
    await Promise.resolve()

    expect(runs).toHaveBeenCalledTimes(3)
  })

  it('holds a dispatch past the ceiling and starts it when a slot frees', async () => {
    const store = useAgentStore()
    const runs = vi.fn((instanceId: string) => {
      // The real runner flips the instance into a live run.
      store.setInstanceProcessing(instanceId, true)
    })
    store.setTaskRunner(runs)

    // Six jobs, five slots.
    store.startDispatchedTasks(
      [9111, 9112, 9113, 9114, 9115, 9116].map(id => dispatched(id))
    )
    await Promise.resolve()

    expect(runs).toHaveBeenCalledTimes(5)
    const waiting = store.instances.find(i => i.conversationId === 9116)
    expect(waiting?.pendingBrief).toBe('Do job 9116.')

    // One finishes; the one that has been waiting starts.
    const firstStarted = store.instances.find(i => i.conversationId === 9111)!
    store.setInstanceProcessing(firstStarted.id, false)
    await Promise.resolve()

    expect(runs).toHaveBeenCalledTimes(6)
    expect(runs.mock.calls[5]![0]).toBe(waiting!.id)
    expect(waiting!.pendingBrief).toBeNull()
  })

  it('starts waiting subagents in the order they were dispatched', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    // Newest first in the list, as a fresh dispatch is unshifted in.
    store.instances = [
      makeInstance({ kind: 'task', conversationId: 9203, pendingBrief: 'third' }),
      makeInstance({ kind: 'task', conversationId: 9202, pendingBrief: 'second' }),
      makeInstance({ kind: 'task', conversationId: 9201, pendingBrief: 'first' }),
    ]

    store.firePendingDispatches()
    await Promise.resolve()

    expect(runs.mock.calls.map(c => c[1])).toEqual(['first', 'second', 'third'])
  })

  it('re-queues a refused run instead of stranding the subagent', async () => {
    // The backend turned this run away because every slot was taken. The
    // brief goes back on the instance and starts when one frees — dropping it
    // left a subagent "working" on a run that never began.
    vi.useFakeTimers()
    try {
      const store = useAgentStore()
      const runs = vi.fn()
      store.setTaskRunner(runs)
      const task = makeInstance({ kind: 'task', conversationId: 9301 })
      store.instances = [task]

      store.requeueDispatch(task.id, 'Do job 9301.')
      expect(task.pendingBrief).toBe('Do job 9301.')

      vi.advanceTimersByTime(10_000)
      store.firePendingDispatches()
      await vi.advanceTimersByTimeAsync(0)

      expect(runs).toHaveBeenCalledWith(task.id, 'Do job 9301.')
    } finally {
      vi.useRealTimers()
    }
  })

  it('waits before retrying a run the backend just refused', async () => {
    // The two ceilings can disagree — the server counts a user's runs across
    // every project, this tab only sees one — so retrying the instant the
    // refusal lands is a network loop, not a retry.
    vi.useFakeTimers()
    try {
      const store = useAgentStore()
      const runs = vi.fn()
      store.setTaskRunner(runs)
      const task = makeInstance({ kind: 'task', conversationId: 9302 })
      store.instances = [task]

      store.requeueDispatch(task.id, 'Do job 9302.')
      store.firePendingDispatches()
      await vi.advanceTimersByTimeAsync(0)

      expect(runs).not.toHaveBeenCalled()
      expect(task.pendingBrief).toBe('Do job 9302.')
    } finally {
      vi.useRealTimers()
    }
  })
})

describe('agent store syncTaskReports', () => {
  // Subagents post what they did straight into the main thread when their own
  // run ends. This is the client noticing, while the user just sits there.
  function report(id: number, kind: string, content: string) {
    return {
      id,
      role: 'assistant' as const,
      content,
      timestamp: new Date().toISOString(),
      taskReport: { conversationId: 77, kind, title: 'Job', goal: 'Doing a job.' },
    }
  }

  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  // The "what have I already pulled?" bookkeeping lives at module scope (it
  // is about a fetch, not about rendered state), so each test gets its own
  // lead conversation rather than inheriting the last one's high-water mark.
  let nextLeadConversationId = 500
  function storeWithLead() {
    const store = useAgentStore()
    const conversationId = nextLeadConversationId++
    const lead = makeInstance({ kind: 'lead', conversationId, messagesLoaded: true })
    store.instances = [lead]
    store.activeInstanceId = lead.id
    return { store, lead, conversationId }
  }

  it('appends a finished subagent report to the main thread', async () => {
    const { store, lead, conversationId } = storeWithLead()
    agentService.getConversationMessages.mockResolvedValue([
      report(12, 'done', 'Your home page now opens with a clear offer.'),
    ])

    await store.syncTaskReports()

    expect(agentService.getConversationMessages).toHaveBeenCalledWith(conversationId, 0)
    expect(lead.conversation).toHaveLength(1)
    expect(lead.conversation[0]!.content).toBe(
      'Your home page now opens with a clear offer.'
    )
    expect(lead.conversation[0]!.taskReport?.kind).toBe('done')
  })

  it('leaves the main agent\'s own replies to the transcript that has them', async () => {
    // They are already on screen from the run that streamed them; re-adding
    // the persisted copy would show every reply twice.
    const { store, lead } = storeWithLead()
    agentService.getConversationMessages.mockResolvedValue([
      { id: 13, role: 'assistant', content: 'On it.', timestamp: '' },
    ])

    await store.syncTaskReports()

    expect(lead.conversation).toHaveLength(0)
  })

  it('refreshes the project once when a subagent applies its work', async () => {
    const { store } = storeWithLead()
    const applied = vi.fn()
    store.setTaskAppliedHandler(applied)
    agentService.getConversationMessages
      .mockResolvedValueOnce([report(14, 'done', 'Landed.')])
      .mockResolvedValueOnce([])

    await store.syncTaskReports()
    await store.syncTaskReports()

    expect(applied).toHaveBeenCalledTimes(1)
  })

  it('does not refresh the project for work still waiting on the user', async () => {
    const { store } = storeWithLead()
    const applied = vi.fn()
    store.setTaskAppliedHandler(applied)
    agentService.getConversationMessages.mockResolvedValue([
      report(15, 'question', 'Stripe or PayPal?'),
    ])

    await store.syncTaskReports()

    expect(applied).not.toHaveBeenCalled()
  })

  it('flags the main thread unread when the user is reading elsewhere', async () => {
    const { store, lead } = storeWithLead()
    store.activeInstanceId = 'somewhere-else'
    agentService.getConversationMessages.mockResolvedValue([
      report(16, 'done', 'Landed.'),
    ])

    await store.syncTaskReports()

    expect(lead.hasUnread).toBe(true)
  })

  it('waits for a streaming reply to finish before appending under it', async () => {
    const { store, lead } = storeWithLead()
    lead.isProcessing = true

    await store.syncTaskReports()

    expect(agentService.getConversationMessages).not.toHaveBeenCalled()
  })

  it('asks only for what has arrived since the last look', async () => {
    const { store, conversationId } = storeWithLead()
    agentService.getConversationMessages
      .mockResolvedValueOnce([report(20, 'done', 'Landed.')])
      .mockResolvedValueOnce([])

    await store.syncTaskReports()
    await store.syncTaskReports()

    expect(agentService.getConversationMessages)
      .toHaveBeenLastCalledWith(conversationId, 20)
  })
})
