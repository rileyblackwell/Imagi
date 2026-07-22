import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { AgentService, labelForTool } from '../agentService'

// The service checks rate limits and prompt length before opening the stream.
vi.mock('../modelsService', () => ({
  ModelsService: {
    checkRateLimit: vi.fn().mockResolvedValue(undefined),
    getConfig: () => ({ maxTokens: 128000 }),
    estimateTokens: () => 10,
  },
}))

const { apiGet } = vi.hoisted(() => ({ apiGet: vi.fn() }))

vi.mock('@/shared/services/api', () => ({
  default: { get: apiGet },
  getAuthToken: () => 'test-token',
}))

vi.mock('@/apps/payments/stores/payments', () => ({
  usePaymentStore: () => ({ fetchBalance: vi.fn() }),
}))

/** A fetch Response whose body streams the given chunks verbatim. */
function streamingResponse(chunks: string[]) {
  const encoder = new TextEncoder()
  let i = 0
  return {
    ok: true,
    body: {
      getReader: () => ({
        read: async () =>
          i < chunks.length
            ? { value: encoder.encode(chunks[i++]), done: false }
            : { value: undefined, done: true },
      }),
    },
  }
}

const sse = (event: object) => `data: ${JSON.stringify(event)}\n\n`

describe('AgentService.streamAgent', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  const call = (handlers = {}) =>
    AgentService.streamAgent('13', { prompt: 'hi', model: 'gpt-5.6-sol' }, handlers)

  it('reports deltas as they arrive and resolves with the done payload', async () => {
    vi.mocked(fetch).mockResolvedValue(
      streamingResponse([
        sse({ type: 'start', conversation_id: 4 }),
        sse({ type: 'delta', text: 'Hel' }),
        sse({ type: 'delta', text: 'lo' }),
        sse({ type: 'tool_call', name: 'read_file', args: { path: 'src/App.vue' } }),
        sse({ type: 'tool_call', name: 'web_search' }),
        sse({
          type: 'done',
          response: 'Hello',
          conversation_id: 4,
          files_changed: ['a.vue'],
          tool_calls: ['read_file', 'web_search'],
          plan: [],
          usage: { input_tokens: 1200, output_tokens: 300, cost_usd: 0.0117 },
          single_message: true,
        }),
      ]) as any,
    )

    const deltas: string[] = []
    const tools: Array<{ name: string; args?: Record<string, string> }> = []
    let started: number | undefined

    const result = await call({
      onStart: (id: number) => { started = id },
      onDelta: (t: string) => deltas.push(t),
      onToolCall: (name: string, args?: Record<string, string>) => tools.push({ name, args }),
    })

    expect(started).toBe(4)
    expect(deltas).toEqual(['Hel', 'lo'])
    expect(tools).toEqual([
      { name: 'read_file', args: { path: 'src/App.vue' } },
      { name: 'web_search', args: undefined },
    ])
    expect(result.response).toBe('Hello')
    expect(result.files_changed).toEqual(['a.vue'])
    expect(result.usage).toEqual({ input_tokens: 1200, output_tokens: 300, cost_usd: 0.0117 })
  })

  it('leaves usage undefined when the done event omits it', async () => {
    vi.mocked(fetch).mockResolvedValue(
      streamingResponse([
        sse({ type: 'done', response: 'ok', conversation_id: 2 }),
      ]) as any,
    )
    const result = await call()
    expect(result.usage).toBeUndefined()
  })

  it('reassembles frames split across chunk boundaries', async () => {
    // TCP does not respect message boundaries: a frame can arrive in pieces.
    vi.mocked(fetch).mockResolvedValue(
      streamingResponse([
        'data: {"type": "delta", "te',
        'xt": "split"}\n\ndata: {"type": "do',
        'ne", "response": "split", "conversation_id": 1}\n\n',
      ]) as any,
    )

    const deltas: string[] = []
    const result = await call({ onDelta: (t: string) => deltas.push(t) })

    expect(deltas).toEqual(['split'])
    expect(result.response).toBe('split')
  })

  it('throws when the run reports an error', async () => {
    vi.mocked(fetch).mockResolvedValue(
      streamingResponse([sse({ type: 'error', error: 'model exploded' })]) as any,
    )
    await expect(call()).rejects.toThrow('model exploded')
  })

  it('surfaces the backend error code so callers can offer recovery', async () => {
    vi.mocked(fetch).mockResolvedValue(
      streamingResponse([
        sse({ type: 'error', error: 'Run hit the turn cap', code: 'max_turns' }),
      ]) as any,
    )
    await expect(call()).rejects.toMatchObject({
      message: 'Run hit the turn cap',
      code: 'max_turns',
    })
  })

  it('keeps partial text when the stream ends without a done event', async () => {
    vi.mocked(fetch).mockResolvedValue(
      streamingResponse([sse({ type: 'delta', text: 'partial' })]) as any,
    )
    const result = await call()
    expect(result.response).toBe('partial')
  })

  it('surfaces a pre-stream error body with its HTTP status', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ error: 'Authentication required' }),
    } as any)
    await expect(call()).rejects.toMatchObject({
      message: 'Authentication required',
      status: 401,
    })
  })

  it('surfaces the agent_busy 409 rejection with its status', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 409,
      json: async () => ({ detail: 'agent_busy' }),
    } as any)
    await expect(call()).rejects.toMatchObject({ message: 'agent_busy', status: 409 })
  })
})

describe('labelForTool', () => {
  it.each([
    ['read_file', { path: 'src/views/Home.vue' }, 'Read Home.vue'],
    ['edit_file', { path: 'src/views/Home.vue' }, 'Edited Home.vue'],
    ['update_file', { file_path: 'src/main.ts' }, 'Edited main.ts'],
    ['create_file', { path: 'src/new.vue' }, 'Created new.vue'],
    ['delete_file', { path: 'src/old.vue' }, 'Deleted old.vue'],
    ['read_file', undefined, 'Read a file'],
    ['grep_files', { pattern: 'navbar' }, 'Searched the project'],
    ['glob_files', undefined, 'Searched the project'],
    ['get_project_tree', undefined, 'Searched the project'],
    ['list_project_files', undefined, 'Searched the project'],
    ['update_plan', undefined, 'Updated the plan'],
    ['web_search', { query: 'vue router' }, 'Searched the web'],
    ['create_app', { app_name: 'shop' }, 'Created an app'],
    ['create_directory', { path: 'src/lib' }, 'Organized project folders'],
    ['delete_directory', { path: 'src/tmp' }, 'Organized project folders'],
    ['some_future_tool', undefined, 'Worked on the project'],
  ] as const)('%s → %s', (name, args, expected) => {
    expect(labelForTool(name, args as Record<string, string> | undefined)).toBe(expected)
  })
})

describe('AgentService.getConversationMessages', () => {
  beforeEach(() => {
    apiGet.mockReset()
  })

  it('hydrates persisted metadata into activity, plan, filesChanged and usage', async () => {
    apiGet.mockResolvedValue({
      data: [
        { id: 1, role: 'user', content: 'restyle the navbar', timestamp: 't1', metadata: null },
        {
          id: 2,
          role: 'assistant',
          content: 'Done.',
          timestamp: 't2',
          metadata: {
            tool_calls: [
              { name: 'read_file', args: { path: 'src/views/Home.vue' } },
              { name: 'grep_files', args: { pattern: 'navbar' } },
              { name: 'web_search' },
            ],
            files_changed: ['src/views/Home.vue'],
            plan: [{ step: 'Restyle navbar', status: 'completed' }],
            usage: { input_tokens: 1000, output_tokens: 200, cost_usd: 0.012 },
          },
        },
      ],
    })

    const msgs = await AgentService.getConversationMessages(7)

    expect(apiGet).toHaveBeenCalledWith('/v1/agents/conversations/7/messages/')
    expect(msgs[0]).toEqual({
      id: 1, role: 'user', content: 'restyle the navbar', timestamp: 't1',
    })
    expect(msgs[1]!.activity).toEqual([
      { name: 'read_file', label: 'Read Home.vue', detail: 'src/views/Home.vue' },
      { name: 'grep_files', label: 'Searched the project', detail: 'navbar' },
      { name: 'web_search', label: 'Searched the web' },
    ])
    expect(msgs[1]!.plan).toEqual([{ step: 'Restyle navbar', status: 'completed' }])
    expect(msgs[1]!.filesChanged).toEqual(['src/views/Home.vue'])
    expect(msgs[1]!.usage).toEqual({ costUsd: 0.012 })
  })

  it('omits usage when the persisted metadata has no cost', async () => {
    apiGet.mockResolvedValue({
      data: [
        {
          id: 3,
          role: 'assistant',
          content: 'ok',
          timestamp: 't3',
          metadata: { usage: { input_tokens: 10, output_tokens: 5 } },
        },
      ],
    })
    const msgs = await AgentService.getConversationMessages(8)
    expect(msgs[0]!.usage).toBeUndefined()
  })
})
