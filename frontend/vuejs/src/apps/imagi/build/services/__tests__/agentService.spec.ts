import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { AgentService } from '../agentService'

// The service checks rate limits and prompt length before opening the stream.
vi.mock('../modelsService', () => ({
  ModelsService: {
    checkRateLimit: vi.fn().mockResolvedValue(undefined),
    getConfig: () => ({ maxTokens: 128000 }),
    estimateTokens: () => 10,
  },
}))

vi.mock('@/shared/services/api', () => ({
  default: {},
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
        sse({ type: 'tool_call', name: 'read_file' }),
        sse({
          type: 'done',
          response: 'Hello',
          conversation_id: 4,
          files_changed: ['a.vue'],
          tool_calls: ['read_file'],
          plan: [],
          single_message: true,
        }),
      ]) as any,
    )

    const deltas: string[] = []
    const tools: string[] = []
    let started: number | undefined

    const result = await call({
      onStart: (id: number) => { started = id },
      onDelta: (t: string) => deltas.push(t),
      onToolCall: (n: string) => tools.push(n),
    })

    expect(started).toBe(4)
    expect(deltas).toEqual(['Hel', 'lo'])
    expect(tools).toEqual(['read_file'])
    expect(result.response).toBe('Hello')
    expect(result.files_changed).toEqual(['a.vue'])
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

  it('keeps partial text when the stream ends without a done event', async () => {
    vi.mocked(fetch).mockResolvedValue(
      streamingResponse([sse({ type: 'delta', text: 'partial' })]) as any,
    )
    const result = await call()
    expect(result.response).toBe('partial')
  })

  it('surfaces a pre-stream error body', async () => {
    vi.mocked(fetch).mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ error: 'Authentication required' }),
    } as any)
    await expect(call()).rejects.toThrow('Authentication required')
  })
})
