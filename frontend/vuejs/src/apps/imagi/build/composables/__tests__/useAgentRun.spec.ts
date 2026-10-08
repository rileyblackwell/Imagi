import { describe, it, expect, beforeEach, vi } from 'vitest'
import { ref } from 'vue'
import { setActivePinia, createPinia } from 'pinia'
import type { AgentInstance } from '../../types/services'
import type { AgentStreamHandlers } from '../../services/agentService'

// The run talks to the agent through streamAgent (a thread's run, through
// watchRun); each test scripts what the stream does by giving it a function
// that drives the handlers.
type Script = (handlers: AgentStreamHandlers, signal?: AbortSignal) => Promise<unknown>
let script: Script = async () => ({ response: '' })

const agentService = vi.hoisted(() => ({
  streamAgent: vi.fn(),
  watchRun: vi.fn(),
  updateConversation: vi.fn(),
  getConversation: vi.fn(),
  cancelConversationRun: vi.fn(),
  listCheckIns: vi.fn(),
}))
vi.mock('../../services/agentService', async (importOriginal) => ({
  ...(await importOriginal<typeof import('../../services/agentService')>()),
  AgentService: agentService,
}))

const fileService = vi.hoisted(() => ({ getProjectFiles: vi.fn() }))
vi.mock('../../services/fileService', () => ({ FileService: fileService }))

const versionControl = vi.hoisted(() => ({ commitAfterFileOperation: vi.fn() }))
vi.mock('../../services/versionControlService', () => ({
  VersionControlService: versionControl,
}))

const fetchUsage = vi.hoisted(() => vi.fn())
vi.mock('@/shared/stores/usage', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@/shared/stores/usage')>()),
  useUsageStore: () => ({ fetchUsage }),
}))

vi.mock('@/shared/stores/auth', () => ({
  useAuthStore: () => ({ validateAuth: () => Promise.resolve(true) }),
}))

import { useAgentStore } from '../../stores/agentStore'
import { useAgentRun, describeAgentTool } from '../useAgentRun'

let nextId = 1

function makeInstance(overrides: Partial<AgentInstance> = {}): AgentInstance {
  const n = nextId++
  return {
    id: `run-inst-${n}`,
    conversationId: 8000 + n,
    title: 'Existing',
    kind: 'lead',
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

/** An AgentStreamError-shaped rejection. */
function streamError(
  message: string,
  extra: { status?: number; code?: string; body?: object; reported?: boolean },
) {
  return Object.assign(new Error(message), extra)
}

function setup(overrides: Partial<AgentInstance> = {}) {
  const store = useAgentStore()
  const instance = makeInstance(overrides)
  store.instances = [instance]
  store.activeInstanceId = instance.id
  const { handlePrompt } = useAgentRun(ref('42'))
  // The store wraps the instance in a reactive proxy; read through it.
  const live = () => store.instances.find(i => i.id === instance.id)!
  return { store, handlePrompt, live }
}

const contents = (inst: AgentInstance) => inst.conversation.map(m => `${m.role}: ${m.content}`)

describe('useAgentRun', () => {
  beforeEach(() => {
    vi.useFakeTimers({ toFake: ['setTimeout'] })
    setActivePinia(createPinia())
    Object.values(agentService).forEach(fn => fn.mockReset())
    fileService.getProjectFiles.mockReset().mockResolvedValue([])
    versionControl.commitAfterFileOperation.mockReset()
    fetchUsage.mockReset()
    agentService.listCheckIns.mockResolvedValue([])
    agentService.cancelConversationRun.mockResolvedValue({ review_status: 'failed' })
    agentService.getConversation.mockResolvedValue({ id: 0, review_status: 'ready' })
    agentService.streamAgent.mockImplementation(
      (_project: string, _data: unknown, handlers: AgentStreamHandlers, signal?: AbortSignal) =>
        script(handlers, signal)
    )
    agentService.watchRun.mockImplementation(
      (_conversationId: number, handlers: AgentStreamHandlers, signal?: AbortSignal) =>
        script(handlers, signal)
    )
  })

  describe('a run that finishes', () => {
    it('streams the reply under the user message and ends processing', async () => {
      const { handlePrompt, live } = setup()
      script = async (h) => {
        expect(live().isProcessing).toBe(true)
        h.onStart?.(live().conversationId!, { userMessageId: 77, checkpoint: 'abc123' })
        h.onDelta?.('Hello ')
        h.onDelta?.('there')
        return { response: 'Hello there' }
      }

      await handlePrompt('Make the header blue')

      expect(contents(live())).toEqual(['user: Make the header blue', 'assistant: Hello there'])
      // The optimistic bubble is tied to its saved row so restore works.
      expect(live().conversation[0]).toMatchObject({ dbId: 77, checkpoint: 'abc123' })
      expect(live().isProcessing).toBe(false)
      expect(agentService.streamAgent).toHaveBeenCalledWith(
        '42',
        expect.objectContaining({ prompt: 'Make the header blue', model: 'claude-opus-5-5' }),
        expect.any(Object),
        expect.any(AbortSignal),
      )
    })

    it('uses the final text when the stream missed some of it', async () => {
      const { handlePrompt, live } = setup()
      script = async (h) => {
        h.onDelta?.('Partial')
        return { response: 'Partial and complete' }
      }

      await handlePrompt('Hi')

      expect(live().conversation[1].content).toBe('Partial and complete')
    })

    it('refreshes files and commits once when a lead run changed files', async () => {
      const { handlePrompt, live, store } = setup()
      fileService.getProjectFiles.mockResolvedValue([{ path: 'src/App.vue' }])
      script = async (h) => {
        h.onToolCall?.('edit_file', { file_path: 'src/App.vue' })
        h.onDelta?.('Done')
        return {
          response: 'Done',
          files_changed: ['src/App.vue', 'src/main.ts'],
          usage: { input_tokens: 10, output_tokens: 5, cost_usd: 0.01 },
        }
      }

      await handlePrompt('Edit the app')

      expect(fileService.getProjectFiles).toHaveBeenCalledTimes(1)
      expect(store.files).toEqual([{ path: 'src/App.vue' }])
      expect(versionControl.commitAfterFileOperation).toHaveBeenCalledTimes(1)
      expect(versionControl.commitAfterFileOperation).toHaveBeenCalledWith('42', 'src/App.vue', 'Edit the app')
      const reply = live().conversation[1]
      expect(reply.filesChanged).toEqual(['src/App.vue', 'src/main.ts'])
      expect(reply.usage).toEqual({ costUsd: 0.01, inputTokens: 10, outputTokens: 5 })
      expect(reply.activity).toHaveLength(1)
    })

    it('never refreshes or commits the main project for a subagent run', async () => {
      // A subagent edits its own worktree; committing the main tree here
      // would snapshot the main thread's half-finished edits.
      const { handlePrompt } = setup({ kind: 'task', reviewStatus: 'active' })
      script = async (h) => {
        h.onStart?.(1, {})
        h.onToolCall?.('create_file', {})
        return { response: 'Built it', files_changed: ['src/New.vue'] }
      }

      await handlePrompt('Build the page')

      expect(fileService.getProjectFiles).not.toHaveBeenCalled()
      expect(versionControl.commitAfterFileOperation).not.toHaveBeenCalled()
      // The server ran it; this tab watched.
      expect(agentService.streamAgent).not.toHaveBeenCalled()
      expect(agentService.watchRun).toHaveBeenCalled()
      // Its card catches up with the server's account of the run straight away.
      expect(agentService.getConversation).toHaveBeenCalled()
    })

    it('removes a reply that ended up showing nothing', async () => {
      const { handlePrompt, live } = setup()
      script = async (h) => {
        h.onPlan?.([])
        return { response: '' }
      }

      await handlePrompt('Hello?')

      expect(contents(live())).toEqual(['user: Hello?'])
    })

    it('starts dispatched subagents and links them from the reply', async () => {
      const { handlePrompt, live, store } = setup()
      const start = vi.spyOn(store, 'startDispatchedTasks').mockImplementation(() => {})
      const tasks = [{ conversation_id: 501, title: 'Pricing page' }]
      script = async (h) => {
        h.onTaskDispatch?.(tasks as never)
        h.onDelta?.('Handing that off.')
        return { response: 'Handing that off.' }
      }

      await handlePrompt('Add a pricing page')

      expect(start).toHaveBeenCalledWith(tasks)
      expect(live().conversation[1].dispatchedTasks).toEqual([
        { conversationId: 501, title: 'Pricing page' },
      ])
    })

    it('refreshes the usage meter after the run', async () => {
      const { handlePrompt } = setup()
      script = async () => ({ response: 'ok' })

      await handlePrompt('Hi')
      expect(fetchUsage).not.toHaveBeenCalled()
      await vi.advanceTimersByTimeAsync(1000)

      expect(fetchUsage).toHaveBeenCalled()
    })
  })

  describe('before the run', () => {
    it('queues a prompt sent while the thread is still working', async () => {
      const { handlePrompt, live } = setup({ isProcessing: true })

      await handlePrompt('And make it bigger')

      expect(agentService.streamAgent).not.toHaveBeenCalled()
      expect(live().queuedPrompt).toBe('And make it bigger')
    })

    it('ignores a blank prompt', async () => {
      const { handlePrompt, live } = setup()

      await handlePrompt('   ')

      expect(agentService.streamAgent).not.toHaveBeenCalled()
      expect(live().conversation).toEqual([])
    })

    it('runs on the thread it was queued for, not the one on screen', async () => {
      const { handlePrompt, store, live } = setup()
      const other = makeInstance()
      store.instances.push(other)
      script = async () => ({ response: 'ok' })

      await handlePrompt('Queued earlier', other.id)

      expect(live().conversation).toEqual([])
      expect(contents(store.instances[1])).toEqual(['user: Queued earlier', 'assistant: ok'])
    })
  })

  describe('a run that is turned away', () => {
    it('drops the message and says another agent is working on a 409', async () => {
      const { handlePrompt, live } = setup()
      script = async () => { throw streamError('agent_busy', { status: 409 }) }

      await handlePrompt('Change the footer')

      expect(contents(live())).toEqual([
        'assistant: Another agent is still working on this project — wait for it to finish or stop it.',
      ])
      expect(live().isProcessing).toBe(false)
    })

    it('tells the user when every parallel slot is taken', async () => {
      const { handlePrompt, live } = setup()
      script = async () => {
        throw streamError('busy', { status: 429, body: { error: 'too_many_concurrent_runs' } })
      }

      await handlePrompt('One more thing')

      expect(contents(live())).toEqual([
        'assistant: Too many agents are running at once — wait for one to finish, then send that again.',
      ])
    })

    it('watches a thread\'s run on the server rather than starting one', async () => {
      const { handlePrompt, live } = setup({ kind: 'task', reviewStatus: 'active' })
      script = async (h) => {
        h.onStart?.(live().conversationId!, {})
        h.onDelta?.('On it')
        return { response: 'On it' }
      }

      await handlePrompt('Build the pricing page')

      expect(agentService.watchRun).toHaveBeenCalledWith(
        live().conversationId, expect.any(Object), expect.any(AbortSignal), undefined,
      )
      expect(agentService.streamAgent).not.toHaveBeenCalled()
      expect(contents(live())).toEqual(['user: Build the pricing page', 'assistant: On it'])
    })

    it('explains a spent usage allowance and refreshes the meter', async () => {
      const { handlePrompt, live } = setup()
      script = async () => {
        throw streamError('usage', { status: 429, body: { error: 'usage_limit_exceeded', resets_at: null } })
      }

      await handlePrompt('Keep going')

      expect(live().conversation).toHaveLength(1)
      expect(live().conversation[0].content).toMatch(/^Usage allowance spent/)
      expect(fetchUsage).toHaveBeenCalled()
    })
  })

  describe('a run that ends early', () => {
    it('keeps a stopped run\'s partial reply and commits the edits it made', async () => {
      const { handlePrompt, live, store } = setup()
      script = (h, signal) => new Promise((_, reject) => {
        h.onToolCall?.('update_file', {})
        h.onDelta?.('Halfway')
        signal?.addEventListener('abort', () => reject(new Error('aborted')))
      })

      const run = handlePrompt('Redo the homepage')
      await vi.waitFor(() => expect(live().conversation).toHaveLength(2))
      store.abortInstanceRun(live().id)
      await run

      expect(contents(live())).toEqual(['user: Redo the homepage', 'assistant: Halfway'])
      expect(fileService.getProjectFiles).toHaveBeenCalled()
      expect(versionControl.commitAfterFileOperation).toHaveBeenCalledWith(
        '42', '/', 'Redo the homepage (stopped)'
      )
    })

    it('does not commit a stopped run that never touched files', async () => {
      const { handlePrompt, live, store } = setup()
      script = (h, signal) => new Promise((_, reject) => {
        h.onToolCall?.('read_file', {})
        signal?.addEventListener('abort', () => reject(new Error('aborted')))
      })

      const run = handlePrompt('Look around')
      await vi.waitFor(() => expect(live().conversation).toHaveLength(2))
      store.abortInstanceRun(live().id)
      await run

      expect(versionControl.commitAfterFileOperation).not.toHaveBeenCalled()
    })

    it('offers to continue a run that hit its turn limit', async () => {
      const { handlePrompt, live } = setup()
      script = async (h) => {
        h.onToolCall?.('edit_file', {})
        throw streamError('turns', { code: 'max_turns' })
      }

      await handlePrompt('Build everything')

      expect(live().conversation.at(-1)?.content).toMatch(/send "Continue"/)
      expect(versionControl.commitAfterFileOperation).toHaveBeenCalledWith(
        '42', '/', 'Build everything (turn limit)'
      )
    })

    it('shows any other failure in the chat', async () => {
      const { handlePrompt, live } = setup()
      script = async () => { throw new Error('Gateway timeout') }

      await handlePrompt('Hi')

      expect(live().conversation.at(-1)?.content).toBe('Error: Gateway timeout')
      expect(live().isProcessing).toBe(false)
    })

    it('keeps a thread working when this tab cannot watch it', async () => {
      // The thread runs on the server whatever happens to this tab, so a
      // failed watch is never reported as a failed thread.
      const { handlePrompt, live, store } = setup({ kind: 'task', reviewStatus: 'active' })
      const fail = vi.spyOn(store, 'failTaskRun').mockResolvedValue(undefined)
      const follow = vi.spyOn(store, 'followRunOnServer')
      script = async () => { throw new Error('Network Error') }

      await handlePrompt('Build the pricing page')

      expect(fail).not.toHaveBeenCalled()
      expect(follow).toHaveBeenCalledWith(live().id)
      expect(live().isProcessing).toBe(true)
      expect(agentService.cancelConversationRun).not.toHaveBeenCalled()
    })

    it('picks a dropped watch back up where it left off', async () => {
      const { handlePrompt, live } = setup({ kind: 'task', reviewStatus: 'active' })
      let calls = 0
      script = async (h) => {
        calls += 1
        if (calls === 1) {
          h.onStart?.(live().conversationId!, {})
          h.onDelta?.('Working ')
          throw streamError('The connection to the run dropped.', {
            code: 'stream_dropped', body: { conversation_id: live().conversationId, last_seq: 2 },
          })
        }
        h.onDelta?.('on it')
        return { response: 'Working on it' }
      }

      const run = handlePrompt('Build the pricing page')
      await vi.advanceTimersByTimeAsync(1000)
      await run

      expect(agentService.watchRun).toHaveBeenLastCalledWith(
        live().conversationId, expect.any(Object), expect.any(AbortSignal), 2,
      )
      expect(contents(live())).toEqual(['user: Build the pricing page', 'assistant: Working on it'])
      expect(live().isProcessing).toBe(false)
    })

    it('follows a thread from the server once re-attaching keeps failing', async () => {
      const { handlePrompt, live, store } = setup({ kind: 'task', reviewStatus: 'active' })
      const fail = vi.spyOn(store, 'failTaskRun').mockResolvedValue(undefined)
      const follow = vi.spyOn(store, 'followRunOnServer')
      script = async (h) => {
        h.onStart?.(live().conversationId!, {})
        throw streamError('The connection to the run dropped.', { code: 'stream_dropped' })
      }

      const run = handlePrompt('Build the pricing page')
      await vi.advanceTimersByTimeAsync(7000)
      await run

      expect(agentService.watchRun).toHaveBeenCalledTimes(4)
      expect(fail).not.toHaveBeenCalled()
      expect(follow).toHaveBeenCalledWith(live().id)
      expect(live().reviewStatus).toBe('active')
    })

    it('keeps the main thread working when its connection drops', async () => {
      const { handlePrompt, live } = setup()
      script = async (h) => {
        h.onStart?.(live().conversationId!, {})
        throw streamError('The connection to the run dropped.', { code: 'stream_dropped' })
      }

      await handlePrompt('Add a pricing page')

      expect(live().isProcessing).toBe(true)
      expect(live().statusText).toBe('Working…')
      expect(contents(live())).toEqual(['user: Add a pricing page'])
    })

    it('stops a thread on the server when the user stops it', async () => {
      const { handlePrompt, live, store } = setup({ kind: 'task', reviewStatus: 'active' })
      const fail = vi.spyOn(store, 'failTaskRun').mockResolvedValue(undefined)
      script = (h, signal) => new Promise((_, reject) => {
        h.onStart?.(live().conversationId!, {})
        h.onDelta?.('Working on it')
        signal?.addEventListener('abort', () => reject(new Error('aborted')))
      })

      const run = handlePrompt('Build the pricing page')
      await vi.waitFor(() => expect(live().conversation).toHaveLength(2))
      store.abortInstanceRun(live().id)
      await run

      expect(fail).toHaveBeenCalledWith(
        live().id, expect.stringContaining('was stopped before it finished'), null
      )
      expect(contents(live())[0]).toBe('user: Build the pricing page')
    })

    it('shows the reason a thread gave for stopping instead of blaming the connection', async () => {
      const { handlePrompt, live, store } = setup({ kind: 'task', reviewStatus: 'active' })
      const fail = vi.spyOn(store, 'failTaskRun').mockResolvedValue(undefined)
      const note = 'This stopped because the Anthropic account Imagi uses has run out of credit.'
      script = async (h) => {
        h.onStart?.(1, {})
        throw streamError(note, { code: 'out_of_credit', reported: true })
      }

      await handlePrompt('Build the pricing page')

      expect(fail).not.toHaveBeenCalled()
      expect(live().conversation.at(-1)?.content).toBe(note)
      expect(live().isProcessing).toBe(false)
    })

    it('explains a run that stopped at its spending ceiling', async () => {
      const { handlePrompt, live } = setup()
      const note = 'This run stopped after spending $10.00, the most one run may spend before checking in.'
      script = async (h) => {
        h.onStart?.(live().conversationId!, {})
        h.onToolCall?.('edit_file', {})
        throw streamError(note, { code: 'run_limit', reported: true })
      }

      await handlePrompt('Build everything')

      expect(live().conversation.at(-1)?.content).toBe(note)
      expect(versionControl.commitAfterFileOperation).toHaveBeenCalledWith(
        '42', '/', 'Build everything (stopped early)'
      )
    })

    it('tells the server to stop when the user stops the main thread', async () => {
      const { handlePrompt, live, store } = setup()
      script = (h, signal) => new Promise((_, reject) => {
        h.onStart?.(live().conversationId!, {})
        h.onDelta?.('Halfway')
        signal?.addEventListener('abort', () => reject(new Error('aborted')))
      })

      const run = handlePrompt('Redo the homepage')
      await vi.waitFor(() => expect(live().conversation).toHaveLength(2))
      store.abortInstanceRun(live().id)
      await run

      expect(agentService.cancelConversationRun).toHaveBeenCalledWith(live().conversationId)
      expect(live().isProcessing).toBe(false)
    })
  })
})

describe('describeAgentTool', () => {
  it('names what the agent is doing in plain words', () => {
    expect(describeAgentTool('update_plan')).toBe('Planning…')
    expect(describeAgentTool('grep_files')).toBe('Reading project files…')
    expect(describeAgentTool('delete_file')).toBe('Editing project files…')
    expect(describeAgentTool('web_search')).toBe('Searching the web…')
    expect(describeAgentTool('browser')).toBe('Using the preview…')
    expect(describeAgentTool('something_new')).toBe('Working…')
  })
})
