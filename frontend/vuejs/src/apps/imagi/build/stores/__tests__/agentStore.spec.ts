import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import type { AgentInstance, ReasoningEffort } from '../../types/services'

// Mock the services the store talks to (no network in unit tests).
const agentService = vi.hoisted(() => ({
  listConversations: vi.fn(),
  createConversation: vi.fn(),
  getConversation: vi.fn(),
  getConversationMessages: vi.fn(),
  updateConversation: vi.fn(),
  cancelConversationRun: vi.fn(),
  acceptTask: vi.fn(),
  dismissTask: vi.fn(),
  restoreCheckpoint: vi.fn(),
  listCheckIns: vi.fn(),
  resolveCheckIn: vi.fn(),
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

  it('keeps archived threads and legacy chats in history, finished threads out', () => {
    // Finished threads have their own group now; history is what is left
    // over (archived, legacy chats) so it stays reachable.
    const store = useAgentStore()
    const archivedLead = makeInstance({ kind: 'lead', archivedAt: new Date().toISOString() })
    const archivedTask = makeInstance({ kind: 'task', reviewStatus: 'accepted', archivedAt: new Date().toISOString() })
    const chat = makeInstance({ kind: 'chat' })
    const accepted = makeInstance({ kind: 'task', reviewStatus: 'accepted' })
    const active = makeInstance({ kind: 'task', reviewStatus: 'active' })
    store.instances = [archivedLead, archivedTask, chat, accepted, active]

    const ids = store.historyInstances.map(i => i.id)
    expect(ids).toContain(archivedLead.id)
    expect(ids).toContain(archivedTask.id)
    expect(ids).toContain(chat.id)
    expect(ids).not.toContain(accepted.id)
    expect(ids).not.toContain(active.id)
  })
})

describe('agent store thread groups', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  it('splits threads into working, waiting on you, and finished', () => {
    const store = useAgentStore()
    const running = makeInstance({ kind: 'task', reviewStatus: 'active', isProcessing: true })
    const starting = makeInstance({ kind: 'task', reviewStatus: 'active' })
    const asking = makeInstance({ kind: 'task', reviewStatus: 'input' })
    const takes = makeInstance({ kind: 'task', reviewStatus: 'ready' })
    const stopped = makeInstance({ kind: 'task', reviewStatus: 'failed' })
    // Answered and running again: it is working, whatever it last asked.
    const resumed = makeInstance({ kind: 'task', reviewStatus: 'input', isProcessing: true })
    const done = makeInstance({ kind: 'task', reviewStatus: 'accepted' })
    const discarded = makeInstance({ kind: 'task', reviewStatus: 'dismissed' })
    const archived = makeInstance({ kind: 'task', reviewStatus: 'accepted', archivedAt: new Date().toISOString() })
    const lead = makeInstance({ kind: 'lead', isProcessing: true })
    store.instances = [running, starting, asking, takes, stopped, resumed, done, discarded, archived, lead]

    const ids = (list: { id: string }[]) => list.map(i => i.id).sort()
    expect(ids(store.workingThreads)).toEqual(ids([running, starting, resumed]))
    expect(ids(store.waitingThreads)).toEqual(ids([asking, takes, stopped]))
    expect(ids(store.finishedThreads)).toEqual(ids([done, discarded]))
  })

  it('counts only the check-ins that ask for something as waiting', () => {
    const store = useAgentStore()
    const card = (id: number, kind: string) => ({ id, kind, task: { id } }) as any
    store.checkIns = [card(1, 'done'), card(2, 'question'), card(3, 'ready'), card(4, 'error')]

    expect(store.waitingCheckIns.map(c => c.id)).toEqual([2, 3, 4])
  })
})

describe('agent store adopting threads from the queue', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  it('adds a thread it never saw dispatched when that thread checks in', async () => {
    // Dispatched from another tab: the first this tab hears of it is its
    // question in the queue, and the Threads pane must list it too.
    const store = useAgentStore()
    store.projectId = '1'
    store.instances = [makeInstance({ kind: 'lead' })]
    agentService.listCheckIns.mockResolvedValue([{ id: 31, kind: 'question', task: { id: 777, review_status: 'input' } }])
    agentService.getConversation.mockResolvedValue({
      id: 777, title: 'Gallery photos', kind: 'task', review_status: 'input', model_name: 'claude-opus-5-5',
      archived_at: null, updated_at: new Date().toISOString(), parent: null,
    })

    await store.loadCheckIns()
    await vi.waitFor(() => expect(store.waitingThreads.map(i => i.conversationId)).toEqual([777]))
    expect(agentService.getConversation).toHaveBeenCalledTimes(1)
  })
})

describe('agent store steering a thread', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  it('starts an idle thread again with the message and clears its waiting card', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    const task = makeInstance({ kind: 'task', reviewStatus: 'input', conversationId: 501 })
    store.instances = [task]
    store.checkIns = [{ id: 7, kind: 'question', task: { id: 501 } } as any]

    expect(store.steerThread(task.id, '  Open on weekends too  ')).toBe(true)
    await Promise.resolve()

    expect(runs).toHaveBeenCalledWith(task.id, 'Open on weekends too')
    expect(task.reviewStatus).toBe('active')
    expect(store.checkIns).toHaveLength(0)
    expect(store.workingThreads.map(i => i.id)).toEqual([task.id])
  })

  it('reopens a finished thread for a change to its work', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    const task = makeInstance({ kind: 'task', reviewStatus: 'accepted', conversationId: 502 })
    store.instances = [task]

    expect(store.steerThread(task.id, 'Make the button blue too')).toBe(true)
    await Promise.resolve()

    expect(runs).toHaveBeenCalledWith(task.id, 'Make the button blue too')
  })

  it('queues behind a live run instead of starting a second one', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    const task = makeInstance({ kind: 'task', reviewStatus: 'active', isProcessing: true, conversationId: 503 })
    store.instances = [task]

    store.steerThread(task.id, 'Use the green from the logo')
    store.steerThread(task.id, 'And make it bold')
    await Promise.resolve()

    expect(runs).not.toHaveBeenCalled()
    expect(task.queuedPrompt).toBe('Use the green from the logo\n\nAnd make it bold')
  })

  it('refuses a discarded or archived thread, and an empty message', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    const discarded = makeInstance({ kind: 'task', reviewStatus: 'dismissed' })
    const archived = makeInstance({ kind: 'task', reviewStatus: 'accepted', archivedAt: new Date().toISOString() })
    const live = makeInstance({ kind: 'task', reviewStatus: 'accepted' })
    const lead = makeInstance({ kind: 'lead' })
    store.instances = [discarded, archived, live, lead]

    expect(store.steerThread(discarded.id, 'hello')).toBe(false)
    expect(store.steerThread(archived.id, 'hello')).toBe(false)
    expect(store.steerThread(live.id, '   ')).toBe(false)
    expect(store.steerThread(lead.id, 'hello')).toBe(false)
    await Promise.resolve()
    expect(runs).not.toHaveBeenCalled()
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

describe('agent store openThread', () => {
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

    await store.openThread(task.id)

    expect(store.openedThread?.id).toBe(task.id)
    // The composer (and its draft) stay with the lead thread.
    expect(store.activeInstanceId).toBe(lead.id)
    expect(task.hasUnread).toBe(false)
  })

  it('goes back to the list on null', async () => {
    const store = useAgentStore()
    const task = makeInstance({ kind: 'task' })
    store.instances = [task]

    await store.openThread(task.id)
    await store.openThread(null)

    expect(store.openedThread).toBeNull()
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
      overview: 'I am giving your home page a real opening section with a '
        + 'headline and a photo, so visitors see what you offer straight away.',
      variant_group: '',
      parent: 1,
      model_name: 'claude-opus-5-5',
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

  it('starts a dispatched thread on the thread model, even from a retired one', () => {
    // The coordinator's own model (a retired GPT 5.6 one here) is not what a
    // new thread runs on: it starts on the user's thread model, so the chip
    // and the run never name a model the picker no longer offers.
    agentService.updateConversation.mockResolvedValue({})
    const store = useAgentStore()
    store.setTaskRunner(vi.fn())

    store.startDispatchedTasks([
      dispatched(9010, { model_name: 'gpt-5.6-terra' }),
      dispatched(9011, { model_name: 'gpt-5.6-luna' }),
      dispatched(9012, { model_name: 'gpt-6-astra' }),
    ])

    const model = (id: number) => store.instances.find(i => i.conversationId === id)?.selectedModelId
    expect(model(9010)).toBe('claude-opus-5-5')
    expect(model(9011)).toBe('claude-opus-5-5')
    expect(model(9012)).toBe('claude-opus-5-5')
  })

  it('carries the lead\'s goal and overview onto the card from the first frame', async () => {
    // The dispatch card reads both off the instance the moment it appears —
    // before any conversation DTO is fetched — so the payload's copy is the
    // one that has to land on it.
    const store = useAgentStore()
    store.setTaskRunner(vi.fn())

    store.startDispatchedTasks([dispatched(9005)])

    const adopted = store.instances.find(i => i.conversationId === 9005)
    expect(adopted?.brief).toBe('Giving your home page a clearer opening.')
    expect(adopted?.overview).toBe(
      'I am giving your home page a real opening section with a headline and '
      + 'a photo, so visitors see what you offer straight away.'
    )
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

describe('agent store follow-ups to an existing subagent', () => {
  // The lead routes a message about existing work to the subagent already
  // doing it (message_task). The payload rides the dispatch channel with
  // follow_up set, and must become that subagent's next turn — never a new
  // subagent, and never dropped because the task was fired once already.
  function followUp(conversationId: number, brief: string) {
    return {
      conversation_id: conversationId,
      title: 'Menu fix',
      brief,
      goal: 'Fixing the menu on phones',
      overview: '',
      variant_group: '',
      parent: 1,
      model_name: 'claude-opus-5-5',
      follow_up: true,
    }
  }

  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  it('runs an idle subagent again with the follow-up, even one already fired', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    store.startDispatchedTasks([{ ...followUp(9701, 'Fix the menu.'), follow_up: false }])
    await Promise.resolve()
    const task = store.instances.find(i => i.conversationId === 9701)!
    task.reviewStatus = 'accepted'

    store.startDispatchedTasks([followUp(9701, 'Make the menu button blue too.')])
    await Promise.resolve()

    expect(runs).toHaveBeenCalledTimes(2)
    expect(runs.mock.calls[1]).toEqual([task.id, 'Make the menu button blue too.'])
    expect(task.reviewStatus).toBe('active')
    expect(store.instances.filter(i => i.kind === 'task')).toHaveLength(1)
  })

  it('queues the follow-up behind a run that is still going', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    const task = makeInstance({ kind: 'task', conversationId: 9702, reviewStatus: 'active', isProcessing: true })
    store.instances.push(task)

    store.startDispatchedTasks([followUp(9702, 'Make it blue.')])
    store.startDispatchedTasks([followUp(9702, 'And a bit bigger.')])
    await Promise.resolve()

    expect(runs).not.toHaveBeenCalled()
    // Both reach the subagent: the second joins the first rather than
    // replacing it.
    expect(store.instances.find(i => i.conversationId === 9702)!.queuedPrompt)
      .toBe('Make it blue.\n\nAnd a bit bigger.')
  })

  it('ignores a follow-up for a subagent this tab does not have', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)

    store.startDispatchedTasks([followUp(9703, 'Make it blue.')])
    await Promise.resolve()

    expect(store.instances).toHaveLength(0)
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
      model_name: 'claude-opus-5-5',
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

describe('agent store failed subagents', () => {
  // A subagent that stops without finishing fails and says so; it runs
  // again only when the user asks. Left 'active' with no run behind it, a
  // task read "starting" forever on a card nobody could act on.
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  function failedDto(overrides = {}) {
    return {
      id: 1,
      title: 'Job',
      model_name: 'claude-opus-5-5',
      project_id: 1,
      kind: 'task',
      parent: 1,
      review_status: 'failed',
      variant_group: '',
      has_worktree: true,
      archived_at: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      last_message_preview: '',
      last_assistant_summary: '',
      brief: 'Doing a job.',
      overview: '',
      is_running: false,
      total_tokens: null,
      queued_prompt: '',
      ...overrides,
    }
  }

  it('fails a run that ended without finishing, and tells the server why', async () => {
    const store = useAgentStore()
    agentService.cancelConversationRun.mockResolvedValue(failedDto({ id: 9401 }))
    agentService.listCheckIns.mockResolvedValue([])
    store.projectId = '1'
    const task = makeInstance({ kind: 'task', conversationId: 9401, reviewStatus: 'active' })
    store.instances = [task]

    await store.failTaskRun(task.id, 'The connection dropped.')

    expect(task.reviewStatus).toBe('failed')
    expect(agentService.cancelConversationRun)
      .toHaveBeenCalledWith(9401, 'The connection dropped.')
    // The server filed the error in the queue — it is pulled now, not on
    // the next poll tick.
    expect(agentService.listCheckIns).toHaveBeenCalled()
  })

  it('reads as failed even when the server cannot be reached', async () => {
    // The request failing is often the reason the run died in the first
    // place; the card still has to stop saying "starting".
    const store = useAgentStore()
    agentService.cancelConversationRun.mockRejectedValue(new Error('offline'))
    const task = makeInstance({ kind: 'task', conversationId: 9402, reviewStatus: 'active' })
    store.instances = [task]

    await store.failTaskRun(task.id, 'The request did not get through.')

    expect(task.reviewStatus).toBe('failed')
  })

  it('keeps an unsent brief for the retry, without firing it again', async () => {
    // The run never started, so the brief was never consumed. It waits on
    // the instance for the user — a dispatch that re-fires itself on every
    // poll turns one failure into a loop.
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    agentService.cancelConversationRun.mockResolvedValue(failedDto({ id: 9403 }))
    const task = makeInstance({ kind: 'task', conversationId: 9403, reviewStatus: 'active' })
    store.instances = [task]

    await store.failTaskRun(task.id, 'The request did not get through.', 'Do job 9403.')
    store.firePendingDispatches()
    await Promise.resolve()

    expect(task.pendingBrief).toBe('Do job 9403.')
    expect(store.pendingDispatchInstances).toHaveLength(0)
    expect(runs).not.toHaveBeenCalled()
  })

  it('never relabels work the server says has finished', async () => {
    // A cancel from this tab can land after the run reported itself
    // elsewhere; the server refuses to call finished work failed, and its
    // word wins here too.
    const store = useAgentStore()
    agentService.cancelConversationRun.mockResolvedValue(
      failedDto({ id: 9404, review_status: 'accepted' })
    )
    const task = makeInstance({ kind: 'task', conversationId: 9404, reviewStatus: 'active' })
    store.instances = [task]

    await store.failTaskRun(task.id, 'The connection dropped.')

    expect(task.reviewStatus).toBe('accepted')
  })

  it('retries a dispatch that never started by firing its brief', async () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    const task = makeInstance({
      kind: 'task', conversationId: 9405, reviewStatus: 'failed', pendingBrief: 'Do job 9405.',
    })
    store.instances = [task]

    store.retryTask(9405)
    await Promise.resolve()

    expect(runs).toHaveBeenCalledWith(task.id, 'Do job 9405.')
    expect(task.reviewStatus).toBe('active')
    expect(task.pendingBrief).toBeNull()
  })

  it('retries a run that died part-way by telling it to carry on', async () => {
    // Its brief is already in its transcript and its half-done edits are in
    // its worktree, so it continues rather than being handed the job again.
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    const task = makeInstance({ kind: 'task', conversationId: 9406, reviewStatus: 'failed' })
    store.instances = [task]

    store.retryTask(9406)

    expect(runs).toHaveBeenCalledTimes(1)
    expect(runs.mock.calls[0]![0]).toBe(task.id)
    expect(runs.mock.calls[0]![1]).toMatch(/cut off before you finished/)
    expect(task.reviewStatus).toBe('active')
  })

  it('drops the error from the queue as the retry goes', () => {
    const store = useAgentStore()
    store.setTaskRunner(vi.fn())
    const task = makeInstance({ kind: 'task', conversationId: 9407, reviewStatus: 'failed' })
    store.instances = [task]
    store.checkIns = [
      {
        id: 1, kind: 'error', body: 'It stopped.', status: 'pending',
        created_at: '', resolved_at: null, project_id: 1, lead_id: 1,
        task: {
          id: 9407, title: 'Job', goal: '', kind: 'task', review_status: 'failed',
          variant_group: '', has_worktree: true, is_running: false,
        },
      },
    ]

    store.retryTask(9407)

    expect(store.checkIns).toHaveLength(0)
  })

  it('only retries a subagent that actually failed', () => {
    // A double press, a stale card, a run already going again: none of
    // these start a second run.
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    store.instances = [
      makeInstance({ kind: 'task', conversationId: 9408, reviewStatus: 'active' }),
      makeInstance({ kind: 'task', conversationId: 9409, reviewStatus: 'failed', isProcessing: true }),
      makeInstance({ kind: 'task', conversationId: 9410, reviewStatus: 'accepted' }),
    ]

    store.retryTask(9408)
    store.retryTask(9409)
    store.retryTask(9410)

    expect(runs).not.toHaveBeenCalled()
  })

  it('does not restart a failed dispatch when the workspace loads', async () => {
    // Its brief is still staged server-side (the run never consumed it),
    // but a reload is not the user asking for it to run again.
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    agentService.listConversations.mockResolvedValue([
      failedDto({ id: 9411, queued_prompt: 'Do job 9411.' }),
      { ...failedDto({ id: 9412, kind: 'lead', review_status: '' }) },
    ])
    agentService.getConversationMessages.mockResolvedValue([])
    agentService.listCheckIns.mockResolvedValue([])

    await store.loadInstances(1)
    await Promise.resolve()

    expect(runs).not.toHaveBeenCalled()
    const failed = store.instances.find(i => i.conversationId === 9411)
    expect(failed?.reviewStatus).toBe('failed')
    expect(failed?.pendingBrief).toBe('Do job 9411.')
    store.stopCheckInPolling()
  })
})

describe('agent store subagent outcomes', () => {
  // A subagent's run ends in its own time, in parallel with everything else,
  // and the queue is how a tab that is not streaming that run finds out. The
  // outcome then belongs on the subagent's card in the main thread — the same
  // card the dispatch put there — which is what these cover.
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
    agentService.listCheckIns.mockResolvedValue([])
  })

  function checkIn(id: number, taskId: number, kind: string, reviewStatus: string) {
    return {
      id,
      kind,
      body: 'Your home page now opens with a clear offer.',
      status: 'pending',
      created_at: new Date().toISOString(),
      resolved_at: null,
      project_id: 1,
      lead_id: 1,
      task: {
        id: taskId,
        title: 'Home page',
        goal: 'Redesigning your home page',
        kind: 'task',
        review_status: reviewStatus,
        variant_group: '',
        has_worktree: false,
        is_running: false,
      },
    }
  }

  function conversationDto(id: number, reviewStatus: string) {
    return {
      id,
      title: 'Home page',
      model_name: 'claude-opus-5-5',
      project_id: 1,
      kind: 'task',
      parent: 1,
      review_status: reviewStatus,
      variant_group: '',
      has_worktree: false,
      archived_at: null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      last_message_preview: 'Your home page now opens with a clear offer.',
      last_assistant_summary: 'Your home page now opens with a clear offer.',
      brief: 'Redesigning your home page',
      is_running: false,
      total_tokens: 120,
    }
  }

  /** A workspace with a lead thread and one subagent still showing as live. */
  function workspace() {
    const store = useAgentStore()
    store.projectId = '1'
    const lead = makeInstance({ kind: 'lead', conversationId: 1 })
    const task = makeInstance({ kind: 'task', reviewStatus: 'active' })
    store.instances = [lead, task]
    store.activeInstanceId = lead.id
    return { store, lead, task }
  }

  it('turns the subagent card over to what it did when it finishes', async () => {
    const { store, task } = workspace()
    agentService.listCheckIns.mockResolvedValue([
      checkIn(1, task.conversationId!, 'done', 'accepted'),
    ])
    agentService.getConversation.mockResolvedValue(
      conversationDto(task.conversationId!, 'accepted')
    )

    await store.loadCheckIns()
    await Promise.resolve()
    await Promise.resolve()

    expect(task.reviewStatus).toBe('accepted')
    expect(task.lastAssistantSummary)
      .toBe('Your home page now opens with a clear offer.')
  })

  it('refreshes the project once when a subagent applies its work', async () => {
    const { store, task } = workspace()
    const applied = vi.fn()
    store.setTaskAppliedHandler(applied)
    agentService.listCheckIns.mockResolvedValue([
      checkIn(2, task.conversationId!, 'done', 'accepted'),
    ])
    agentService.getConversation.mockResolvedValue(
      conversationDto(task.conversationId!, 'accepted')
    )

    await store.loadCheckIns()
    await Promise.resolve()
    await Promise.resolve()

    expect(applied).toHaveBeenCalledTimes(1)
  })

  it('reacts to a queue entry once however long it sits there', async () => {
    // The card stays up until the user clears it. Re-reacting every poll
    // would refetch the conversation every six seconds for as long as it does.
    const { store, task } = workspace()
    agentService.listCheckIns.mockResolvedValue([
      checkIn(3, task.conversationId!, 'done', 'accepted'),
    ])
    agentService.getConversation.mockResolvedValue(
      conversationDto(task.conversationId!, 'accepted')
    )

    await store.loadCheckIns()
    await Promise.resolve()
    await store.loadCheckIns()
    await store.loadCheckIns()

    expect(agentService.getConversation).toHaveBeenCalledTimes(1)
  })

  it('leaves a subagent this tab is still streaming alone', async () => {
    // This tab is driving that run and already has the truth; refetching
    // would only race the stream writing into it.
    const { store, task } = workspace()
    task.isProcessing = true
    agentService.listCheckIns.mockResolvedValue([
      checkIn(4, task.conversationId!, 'done', 'accepted'),
    ])

    await store.loadCheckIns()

    expect(agentService.getConversation).not.toHaveBeenCalled()
  })

  it('flags the main thread unread when the user is reading elsewhere', async () => {
    const { store, lead, task } = workspace()
    store.activeInstanceId = 'somewhere-else'
    agentService.listCheckIns.mockResolvedValue([
      checkIn(5, task.conversationId!, 'question', 'input'),
    ])
    agentService.getConversation.mockResolvedValue(
      conversationDto(task.conversationId!, 'input')
    )

    await store.loadCheckIns()

    expect(lead.hasUnread).toBe(true)
  })
})

describe('agentStore reasoning effort ladder', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
    agentService.updateConversation.mockResolvedValue(undefined)
  })

  it('leaves an effort on the ladder untouched when switching models', () => {
    // Every model shares the one ladder, so a switch never moves the rung.
    const store = useAgentStore()
    for (const effort of ['low', 'medium', 'high', 'xhigh'] as const) {
      const instance = makeInstance({ selectedEffort: effort })
      store.instances = [instance]

      store.setInstanceModel(instance.id, 'gpt-6-astra')
      expect(instance.selectedModelId).toBe('gpt-6-astra')
      expect(instance.selectedEffort).toBe(effort)

      store.setInstanceModel(instance.id, 'gpt-6-luna')
      expect(instance.selectedEffort).toBe(effort)
    }
  })

  it("re-seats a retired 'minimal' onto low when switching models", () => {
    // 'minimal' is off the ladder now. Restored from an older session and
    // carried over unclamped it would ride into the next request.
    const store = useAgentStore()
    const instance = makeInstance({ selectedEffort: 'minimal' as ReasoningEffort })
    store.instances = [instance]

    store.setInstanceModel(instance.id, 'gpt-6-astra')

    expect(instance.selectedModelId).toBe('gpt-6-astra')
    expect(instance.selectedEffort).toBe('low')
  })

  it("re-seats a retired 'max' onto xhigh when switching models", () => {
    // 'max' was never a rung the SDK accepted: sent through, the backend
    // dropped reasoning altogether rather than reasoning harder.
    const store = useAgentStore()
    const instance = makeInstance({ selectedModelId: 'gpt-6-astra', selectedEffort: 'max' as ReasoningEffort })
    store.instances = [instance]

    store.setInstanceModel(instance.id, 'claude-opus-5-5')

    expect(instance.selectedEffort).toBe('xhigh')
  })

  it('re-seats a retired rung chosen directly', () => {
    const store = useAgentStore()
    const instance = makeInstance({ selectedModelId: 'gpt-6-astra', selectedEffort: 'medium' })
    store.instances = [instance]

    store.setInstanceEffort(instance.id, 'minimal' as ReasoningEffort)
    expect(instance.selectedEffort).toBe('low')

    store.setInstanceEffort(instance.id, 'max' as ReasoningEffort)
    expect(instance.selectedEffort).toBe('xhigh')
  })

  it('keeps an effort on the ladder when chosen directly', () => {
    const store = useAgentStore()
    const instance = makeInstance({ selectedEffort: 'medium' })
    store.instances = [instance]

    store.setInstanceEffort(instance.id, 'xhigh')

    expect(instance.selectedEffort).toBe('xhigh')
  })

  it('drops an unknown effort back to the default', () => {
    const store = useAgentStore()
    const instance = makeInstance({ selectedEffort: 'high' })
    store.instances = [instance]

    store.setInstanceEffort(instance.id, 'bogus' as ReasoningEffort)
    expect(instance.selectedEffort).toBe('medium')

    instance.selectedEffort = undefined as unknown as ReasoningEffort
    store.setInstanceModel(instance.id, 'gpt-6-astra')
    expect(instance.selectedEffort).toBe('medium')
  })
})

describe('agent store workspace bootstrap', () => {
  // loadInstances is what opening a project's workspace runs: it decides
  // which thread the user lands in and picks up runs still going on the
  // server. Getting it wrong strands the user in a thread they cannot type
  // in, or leaves a finished run looking like it is still working.
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
    agentService.getConversationMessages.mockResolvedValue([])
    agentService.listCheckIns.mockResolvedValue([])
  })

  function dto(overrides: Record<string, unknown> = {}) {
    return {
      id: 1,
      title: '',
      model_name: 'claude-opus-5-5',
      project_id: 1,
      kind: 'lead',
      parent: null,
      review_status: '',
      variant_group: '',
      has_worktree: false,
      archived_at: null,
      created_at: '2026-10-01T00:00:00Z',
      updated_at: '2026-10-01T00:00:00Z',
      last_message_preview: '',
      is_running: false,
      total_tokens: null,
      ...overrides,
    }
  }

  async function load(store: ReturnType<typeof useAgentStore>) {
    store.setProjectId('1')
    await store.loadInstances('1')
  }

  it('creates the lead thread when the project has none', async () => {
    const store = useAgentStore()
    agentService.listConversations.mockResolvedValue([])
    agentService.createConversation.mockResolvedValue(dto({ id: 9501 }))

    await load(store)
    store.stopCheckInPolling()

    expect(agentService.createConversation).toHaveBeenCalledWith(
      '1', expect.objectContaining({ kind: 'lead' })
    )
    expect(store.activeInstance?.conversationId).toBe(9501)
  })

  it('reuses the existing lead instead of creating another', async () => {
    const store = useAgentStore()
    agentService.listConversations.mockResolvedValue([dto({ id: 9502 })])

    await load(store)
    store.stopCheckInPolling()

    expect(agentService.createConversation).not.toHaveBeenCalled()
    expect(store.activeInstance?.conversationId).toBe(9502)
  })

  it('never restores a subagent as the active thread', async () => {
    // A subagent's thread has no composer; landing in it on reload would
    // leave the user nowhere to type.
    const store = useAgentStore()
    localStorage.setItem('activeAgentInstance_1', '9504')
    agentService.listConversations.mockResolvedValue([
      dto({ id: 9503 }),
      dto({ id: 9504, kind: 'task', parent: 9503, review_status: 'ready' }),
    ])

    await load(store)
    store.stopCheckInPolling()

    expect(store.activeInstance?.conversationId).toBe(9503)
  })

  it('reloads a restored run once the server says it finished', async () => {
    vi.useFakeTimers()
    try {
      const store = useAgentStore()
      agentService.listConversations.mockResolvedValue([dto({ id: 9505, is_running: true })])
      await load(store)
      store.stopCheckInPolling()
      const lead = store.instances.find(i => i.conversationId === 9505)!
      expect(lead.isProcessing).toBe(true)
      agentService.getConversationMessages.mockClear()

      agentService.getConversation.mockResolvedValue(
        dto({ id: 9505, is_running: false, last_message_preview: 'Done' })
      )
      await vi.advanceTimersByTimeAsync(5000)

      expect(lead.isProcessing).toBe(false)
      expect(lead.lastMessagePreview).toBe('Done')
      expect(agentService.getConversationMessages).toHaveBeenCalledWith(9505)
    } finally {
      vi.useRealTimers()
    }
  })

  it('picks up a run whose stream dropped once the server finishes it', async () => {
    vi.useFakeTimers()
    try {
      const store = useAgentStore()
      agentService.listConversations.mockResolvedValue([dto({ id: 9507 })])
      await load(store)
      store.stopCheckInPolling()
      const lead = store.instances.find(i => i.conversationId === 9507)!
      // A live run in this tab whose connection closed mid-way.
      store.setInstanceProcessing(lead.id, true)
      store.registerAbortController(lead.id, new AbortController())

      store.followRunOnServer(lead.id)
      expect(lead.isProcessing).toBe(true)
      expect(lead.statusText).toBe('Working…')

      agentService.getConversationMessages.mockClear()
      agentService.getConversation.mockResolvedValue(
        dto({ id: 9507, is_running: false, last_message_preview: 'Finished' })
      )
      await vi.advanceTimersByTimeAsync(5000)

      expect(lead.isProcessing).toBe(false)
      expect(lead.lastMessagePreview).toBe('Finished')
      expect(agentService.getConversationMessages).toHaveBeenCalledWith(9507)
    } finally {
      vi.useRealTimers()
    }
  })

  it('keeps polling while the server run is still going', async () => {
    vi.useFakeTimers()
    try {
      const store = useAgentStore()
      agentService.listConversations.mockResolvedValue([dto({ id: 9506, is_running: true })])
      await load(store)
      store.stopCheckInPolling()
      agentService.getConversation.mockResolvedValue(dto({ id: 9506, is_running: true }))

      await vi.advanceTimersByTimeAsync(10_000)

      expect(agentService.getConversation).toHaveBeenCalledTimes(2)
      expect(store.instances[0].isProcessing).toBe(true)
    } finally {
      // Let the poller see the run end so its interval clears itself.
      agentService.getConversation.mockResolvedValue(dto({ id: 9506, is_running: false }))
      await vi.advanceTimersByTimeAsync(10_000)
      vi.useRealTimers()
    }
  })
})

describe('agent store check-in actions', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
  })

  function queued(id: number, taskId: number) {
    return {
      id,
      kind: 'question',
      body: 'Which colour?',
      status: 'pending',
      task: { id: taskId, title: 'Job', review_status: 'active' },
    } as any
  }

  it('puts a check-in back when the server fails to resolve it', async () => {
    // Dropping it locally on a failed resolve would lose the item for good.
    const store = useAgentStore()
    store.setProjectId('1')
    const item = queued(9601, 9701)
    store.checkIns = [item]
    agentService.resolveCheckIn.mockRejectedValue(new Error('offline'))
    agentService.listCheckIns.mockResolvedValue([item])

    await store.resolveCheckIn(9601)
    await vi.waitFor(() => expect(store.checkIns.map(c => c.id)).toEqual([9601]))
  })

  it('answers a question by restarting that subagent with the reply', () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    const task = makeInstance({ kind: 'task', conversationId: 9702 })
    store.instances = [task]
    store.checkIns = [queued(9602, 9702)]

    store.answerCheckIn(queued(9602, 9702), '  Blue  ')

    expect(runs).toHaveBeenCalledWith(task.id, 'Blue')
    expect(store.checkIns).toEqual([])
  })

  it('ignores an empty answer', () => {
    const store = useAgentStore()
    const runs = vi.fn()
    store.setTaskRunner(runs)
    store.instances = [makeInstance({ kind: 'task', conversationId: 9703 })]
    store.checkIns = [queued(9603, 9703)]

    store.answerCheckIn(queued(9603, 9703), '   ')

    expect(runs).not.toHaveBeenCalled()
    expect(store.checkIns).toHaveLength(1)
  })
})

describe('agent store thread model setting', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    Object.values(agentService).forEach((fn) => fn.mockReset())
    agentService.updateConversation.mockResolvedValue({})
  })

  const dispatch = (conversationId: number, model = 'claude-opus-5-5') => ({
    conversation_id: conversationId,
    title: 'Contact page',
    brief: 'Add a contact page.',
    goal: '',
    overview: '',
    variant_group: '',
    parent: 1,
    model_name: model,
  })

  it('starts on Opus 5.5', () => {
    expect(useAgentStore().threadModelId).toBe('claude-opus-5-5')
  })

  it('remembers the pick, and ignores a model the lineup does not offer', () => {
    useAgentStore().setThreadModel('gpt-6-luna')
    setActivePinia(createPinia())
    expect(useAgentStore().threadModelId).toBe('gpt-6-luna')

    localStorage.setItem('imagi.threadModel', 'not-a-model')
    setActivePinia(createPinia())
    expect(useAgentStore().threadModelId).toBe('claude-opus-5-5')
  })

  it('starts a new thread on the thread model, whatever the coordinator runs on', () => {
    const store = useAgentStore()
    store.setTaskRunner(vi.fn())
    store.setThreadModel('gpt-6-luna')

    store.startDispatchedTasks([dispatch(9801, 'gpt-6-astra')])

    const thread = store.instances.find(i => i.conversationId === 9801)!
    expect(thread.selectedModelId).toBe('gpt-6-luna')
    expect(agentService.updateConversation).toHaveBeenCalledWith(9801, { model_name: 'gpt-6-luna' })
  })

  it('switches every thread that can still run, and leaves the rest', () => {
    const store = useAgentStore()
    const open = makeInstance({ kind: 'task', reviewStatus: 'active', selectedModelId: 'gpt-6-astra' })
    const done = makeInstance({ kind: 'task', reviewStatus: 'accepted', selectedModelId: 'claude-opus-5-5' })
    const discarded = makeInstance({ kind: 'task', reviewStatus: 'dismissed', selectedModelId: 'gpt-6-astra' })
    const lead = makeInstance({ kind: 'lead', selectedModelId: 'claude-opus-5-5' })
    store.instances = [open, done, discarded, lead]
    store.setThreadModel('gpt-6-luna')

    expect(store.threadsOffThreadModel.map(i => i.id)).toEqual([open.id, done.id])
    expect(store.switchAllThreadsToThreadModel()).toBe(2)

    const model = (id: string) => store.instances.find(i => i.id === id)!.selectedModelId
    expect(model(open.id)).toBe('gpt-6-luna')
    expect(model(done.id)).toBe('gpt-6-luna')
    expect(model(discarded.id)).toBe('gpt-6-astra')
    expect(model(lead.id)).toBe('claude-opus-5-5')
    expect(store.threadsOffThreadModel).toHaveLength(0)
  })
})
