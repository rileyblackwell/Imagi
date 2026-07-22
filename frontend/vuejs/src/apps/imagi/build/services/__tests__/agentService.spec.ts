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

const { apiGet, apiPost } = vi.hoisted(() => ({ apiGet: vi.fn(), apiPost: vi.fn() }))

vi.mock('@/shared/services/api', () => ({
  default: { get: apiGet, post: apiPost },
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

  it('carries the parsed body of a 429 usage-limit rejection', async () => {
    // The body's window + resets_at feed the "Usage limit reached" bubble.
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 429,
      json: async () => ({
        error: 'usage_limit_exceeded',
        detail: 'limit reached',
        window: '5h',
        resets_at: '2026-07-22T18:00:00Z',
      }),
    } as any)
    await expect(call()).rejects.toMatchObject({
      status: 429,
      body: {
        error: 'usage_limit_exceeded',
        window: '5h',
        resets_at: '2026-07-22T18:00:00Z',
      },
    })
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

describe('AgentService task review (accept / dismiss)', () => {
  beforeEach(() => {
    apiPost.mockReset()
  })

  it('accepts a task through the accept endpoint', async () => {
    apiPost.mockResolvedValue({ data: { status: 'accepted' } })
    const result = await AgentService.acceptTask(12)
    expect(apiPost).toHaveBeenCalledWith('/v1/agents/conversations/12/accept/')
    expect(result).toEqual({ status: 'accepted' })
  })

  it('propagates the 409 merge_conflict body so the UI can show its detail', async () => {
    // Axios error shape: the response body rides on error.response.data.
    const conflict = Object.assign(new Error('Request failed with status code 409'), {
      response: {
        status: 409,
        data: { error: 'merge_conflict', detail: 'CONFLICT (content): src/App.vue' },
      },
    })
    apiPost.mockRejectedValue(conflict)
    await expect(AgentService.acceptTask(12)).rejects.toMatchObject({
      response: {
        status: 409,
        data: { error: 'merge_conflict', detail: 'CONFLICT (content): src/App.vue' },
      },
    })
  })

  it('dismisses a task through the dismiss endpoint', async () => {
    apiPost.mockResolvedValue({ data: { status: 'dismissed' } })
    const result = await AgentService.dismissTask(31)
    expect(apiPost).toHaveBeenCalledWith('/v1/agents/conversations/31/dismiss/')
    expect(result).toEqual({ status: 'dismissed' })
  })
})

describe('AgentService.createConversation', () => {
  beforeEach(() => {
    apiPost.mockReset()
  })

  it('sends kind, parent and variant_group when dispatching a task', async () => {
    apiPost.mockResolvedValue({ data: { id: 5 } })
    await AgentService.createConversation(3, {
      modelName: 'gpt-5.6-terra',
      kind: 'task',
      parent: 9,
      variantGroup: 'uuid-1',
    })
    expect(apiPost).toHaveBeenCalledWith('/v1/agents/conversations/', {
      project_id: 3,
      model_name: 'gpt-5.6-terra',
      title: '',
      kind: 'task',
      parent: 9,
      variant_group: 'uuid-1',
    })
  })

  it('omits the task fields entirely for plain conversations', async () => {
    apiPost.mockResolvedValue({ data: { id: 6 } })
    await AgentService.createConversation(3, { modelName: 'gpt-5.6-terra' })
    expect(apiPost).toHaveBeenCalledWith('/v1/agents/conversations/', {
      project_id: 3,
      model_name: 'gpt-5.6-terra',
      title: '',
    })
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
    expect(msgs[1]!.usage).toEqual({ costUsd: 0.012, inputTokens: 1000, outputTokens: 200 })
  })

  it('hydrates token counts even when the persisted metadata has no cost', async () => {
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
    expect(msgs[0]!.usage).toEqual({ inputTokens: 10, outputTokens: 5 })
  })

  it('leaves usage undefined when the metadata carries no usage fields', async () => {
    // Absent usage means "unknown", never "free" — no phantom zero object.
    apiGet.mockResolvedValue({
      data: [
        { id: 4, role: 'assistant', content: 'ok', timestamp: 't4', metadata: { usage: {} } },
        { id: 5, role: 'assistant', content: 'ok', timestamp: 't5', metadata: null },
      ],
    })
    const msgs = await AgentService.getConversationMessages(9)
    expect(msgs[0]!.usage).toBeUndefined()
    expect(msgs[1]!.usage).toBeUndefined()
  })
})
