import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

const transcribeAudio = vi.hoisted(() => vi.fn())
vi.mock('../../services/agentService', () => ({ AgentService: { transcribeAudio } }))

import { INPUT_STORAGE_KEY, MIN_CLIP_MS, preferredInput, useDictation } from '../useDictation'

/** A MediaRecorder that hands over one chunk and fires onstop when stopped. */
class FakeRecorder {
  static instances: FakeRecorder[] = []
  static isTypeSupported = (type: string) => type === 'audio/webm;codecs=opus'
  state: 'inactive' | 'recording' = 'inactive'
  mimeType: string
  ondataavailable: ((event: { data: Blob }) => void) | null = null
  onstop: (() => void) | null = null
  started = 0
  constructor(public stream: FakeStream, opts?: { mimeType?: string }) {
    this.mimeType = opts?.mimeType ?? 'audio/webm'
    FakeRecorder.instances.push(this)
  }
  start() {
    this.state = 'recording'
    this.started += 1
  }
  stop() {
    this.state = 'inactive'
    this.ondataavailable?.({ data: new Blob(['audio'], { type: this.mimeType }) })
    this.onstop?.()
  }
}

/** A stream that remembers which device it was opened on. */
class FakeStream {
  stopped = 0
  constructor(public deviceId: string) {}
  getTracks() {
    return [{ stop: () => void (this.stopped += 1) }]
  }
  getAudioTracks() {
    return [{ getSettings: () => ({ deviceId: this.deviceId }) }]
  }
}

const BUILT_IN = { deviceId: 'mic-builtin', kind: 'audioinput', label: 'MacBook Pro Microphone (Built-in)' }
const AIRPODS = { deviceId: 'mic-airpods', kind: 'audioinput', label: "Riley's AirPods Pro" }
const DEFAULT_ALIAS = { deviceId: 'default', kind: 'audioinput', label: "Default - Riley's AirPods Pro" }
const SPEAKER = { deviceId: 'out-1', kind: 'audiooutput', label: 'MacBook Pro Speakers' }
const UNNAMED = { deviceId: '', kind: 'audioinput', label: '' }

const flush = async () => {
  for (let i = 0; i < 8; i++) await Promise.resolve()
}

let streams: FakeStream[]
let getUserMedia: ReturnType<typeof vi.fn>
let enumerateDevices: ReturnType<typeof vi.fn>
let listeners: Record<string, Array<() => void>>

/** Install a browser that lists `devices` and opens a stream on whichever
 *  device a request names (or 'default' for an unnamed request). Once the
 *  first request has been granted, unnamed devices get their names. */
function installMedia(devices: Array<{ deviceId: string; kind: string; label: string }>, opts: { unnamedUntilGranted?: boolean } = {}) {
  streams = []
  listeners = {}
  let granted = false
  enumerateDevices = vi.fn(async () =>
    opts.unnamedUntilGranted && !granted ? [UNNAMED] : devices
  )
  getUserMedia = vi.fn(async (constraints: MediaStreamConstraints) => {
    const audio = constraints.audio as { deviceId?: { exact?: string } } | boolean
    const wanted = typeof audio === 'object' ? audio.deviceId?.exact : undefined
    if (wanted && !devices.some(d => d.deviceId === wanted)) {
      throw new DOMException('gone', 'OverconstrainedError')
    }
    granted = true
    const stream = new FakeStream(wanted ?? 'default')
    streams.push(stream)
    return stream
  })
  vi.stubGlobal('MediaRecorder', FakeRecorder)
  Object.defineProperty(navigator, 'mediaDevices', {
    value: {
      getUserMedia,
      enumerateDevices,
      addEventListener: (name: string, fn: () => void) => {
        ;(listeners[name] ??= []).push(fn)
      },
      removeEventListener: vi.fn(),
    },
    configurable: true,
  })
}

const exactId = (call: unknown[]) =>
  ((call[0] as MediaStreamConstraints).audio as { deviceId?: { exact?: string } }).deviceId?.exact

describe('preferredInput', () => {
  const inputs = [DEFAULT_ALIAS, AIRPODS, BUILT_IN].map(d => ({ id: d.deviceId, label: d.label }))

  it('prefers the computer\'s own microphone over the OS default', () => {
    expect(preferredInput(inputs, null)?.id).toBe('mic-builtin')
  })

  it('honours a choice the user made, while that device is still there', () => {
    expect(preferredInput(inputs, 'mic-airpods')?.id).toBe('mic-airpods')
    expect(preferredInput(inputs, 'mic-unplugged')?.id).toBe('mic-builtin')
  })

  it('skips the default alias when a real device is listed', () => {
    const noBuiltIn = [DEFAULT_ALIAS, AIRPODS].map(d => ({ id: d.deviceId, label: d.label }))
    expect(preferredInput(noBuiltIn, null)?.id).toBe('mic-airpods')
  })

  it('has nothing to prefer from an empty list', () => {
    expect(preferredInput([], null)).toBeNull()
  })
})

describe('useDictation', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    FakeRecorder.instances = []
    localStorage.clear()
    installMedia([BUILT_IN, AIRPODS, DEFAULT_ALIAS, SPEAKER])
  })
  afterEach(() => {
    vi.unstubAllGlobals()
    delete (navigator as { mediaDevices?: unknown }).mediaDevices
    vi.useRealTimers()
  })

  /** A whole dictation: open the mic, hold it long enough to count, stop. */
  async function record(dictation: ReturnType<typeof useDictation>) {
    await dictation.start()
    vi.advanceTimersByTime(MIN_CLIP_MS + 500)
    dictation.stop()
    await flush()
  }

  it('is unsupported, and inert, where the browser cannot record', async () => {
    vi.unstubAllGlobals()
    delete (navigator as { mediaDevices?: unknown }).mediaDevices
    const onTranscript = vi.fn()
    const dictation = useDictation({ onTranscript })
    expect(dictation.supported).toBe(false)
    dictation.toggle()
    await flush()
    expect(dictation.state.value).toBe('idle')
    expect(FakeRecorder.instances).toHaveLength(0)
  })

  it('lists real microphones only, and knows which is the built-in one', async () => {
    const dictation = useDictation({ onTranscript: vi.fn() })
    await flush()
    expect(dictation.inputs.value.map(i => i.id)).toEqual(['mic-builtin', 'mic-airpods'])
    expect(dictation.activeInput.value?.id).toBe('mic-builtin')
    expect(dictation.labelsHidden.value).toBe(false)
  })

  it('records from the built-in microphone by name, not the OS default', async () => {
    const dictation = useDictation({ onTranscript: vi.fn() })
    await dictation.start()
    expect(dictation.state.value).toBe('recording')
    expect(getUserMedia).toHaveBeenCalledTimes(1)
    expect(exactId(getUserMedia.mock.calls[0]!)).toBe('mic-builtin')
    const recorder = FakeRecorder.instances[0]!
    expect(recorder.mimeType).toBe('audio/webm;codecs=opus')
    expect(recorder.started).toBe(1)
  })

  it('records from the microphone the user picked, and remembers it', async () => {
    const dictation = useDictation({ onTranscript: vi.fn() })
    await flush()
    dictation.selectInput('mic-airpods')
    expect(dictation.activeInput.value?.label).toBe("Riley's AirPods Pro")
    expect(localStorage.getItem(INPUT_STORAGE_KEY)).toBe('mic-airpods')

    await dictation.start()
    expect(exactId(getUserMedia.mock.calls[0]!)).toBe('mic-airpods')

    // A fresh pane picks the choice back up.
    const later = useDictation({ onTranscript: vi.fn() })
    await flush()
    expect(later.activeInput.value?.id).toBe('mic-airpods')

    later.selectInput(null)
    expect(localStorage.getItem(INPUT_STORAGE_KEY)).toBeNull()
    expect(later.activeInput.value?.id).toBe('mic-builtin')
  })

  it('falls back to the OS default when the chosen microphone has gone', async () => {
    localStorage.setItem(INPUT_STORAGE_KEY, 'mic-airpods')
    const dictation = useDictation({ onTranscript: vi.fn() })
    await flush()
    // The AirPods vanish between the list being read and the mic opening.
    enumerateDevices.mockResolvedValue([BUILT_IN, SPEAKER])
    installMedia([BUILT_IN, SPEAKER])
    localStorage.setItem(INPUT_STORAGE_KEY, 'mic-airpods')
    const again = useDictation({ onTranscript: vi.fn() })
    await flush()
    expect(again.activeInput.value?.id).toBe('mic-builtin')
    await again.start()
    expect(again.state.value).toBe('recording')
    expect(dictation.state.value).toBe('idle')
  })

  it('retries on the OS default when the named device refuses to open', async () => {
    const dictation = useDictation({ onTranscript: vi.fn() })
    await flush()
    getUserMedia.mockRejectedValueOnce(new DOMException('busy', 'NotReadableError'))
    await dictation.start()
    expect(dictation.state.value).toBe('recording')
    expect(getUserMedia).toHaveBeenCalledTimes(2)
    expect(exactId(getUserMedia.mock.calls[1]!)).toBeUndefined()
  })

  it('swaps to the built-in mic once the first grant reveals device names', async () => {
    installMedia([DEFAULT_ALIAS, AIRPODS, BUILT_IN], { unnamedUntilGranted: true })
    const dictation = useDictation({ onTranscript: vi.fn() })
    await flush()
    expect(dictation.labelsHidden.value).toBe(true)

    await dictation.start()
    expect(dictation.state.value).toBe('recording')
    // First on whatever the OS offered (no name to ask for yet), then by name.
    expect(exactId(getUserMedia.mock.calls[0]!)).toBeUndefined()
    expect(exactId(getUserMedia.mock.calls[1]!)).toBe('mic-builtin')
    expect(streams[0]!.stopped).toBeGreaterThan(0)
    expect(FakeRecorder.instances[0]!.stream).toBe(streams[1])
    expect(dictation.labelsHidden.value).toBe(false)
    expect(dictation.activeInput.value?.id).toBe('mic-builtin')
  })

  it('unlockInputs asks once, lets go, and fills in the names', async () => {
    installMedia([BUILT_IN, AIRPODS], { unnamedUntilGranted: true })
    const dictation = useDictation({ onTranscript: vi.fn() })
    await flush()
    expect(dictation.labelsHidden.value).toBe(true)
    await dictation.unlockInputs()
    expect(getUserMedia).toHaveBeenCalledTimes(1)
    expect(streams[0]!.stopped).toBe(1)
    expect(dictation.labelsHidden.value).toBe(false)
    expect(dictation.inputs.value.map(i => i.label)).toEqual([BUILT_IN.label, AIRPODS.label])
    expect(dictation.state.value).toBe('idle')
  })

  it('re-reads the list when a headset connects', async () => {
    const dictation = useDictation({ onTranscript: vi.fn() })
    await flush()
    enumerateDevices.mockResolvedValue([BUILT_IN, SPEAKER])
    listeners.devicechange?.forEach(fn => fn())
    await flush()
    expect(dictation.inputs.value.map(i => i.id)).toEqual(['mic-builtin'])
  })

  it('transcribes the clip on stop and hands the text over, trimmed', async () => {
    transcribeAudio.mockResolvedValue('  Add a contact page  ')
    const onTranscript = vi.fn()
    const dictation = useDictation({ onTranscript })
    await dictation.start()
    vi.advanceTimersByTime(1000)

    dictation.stop()
    // Transcribing from the instant the mic closes — the button can say so.
    expect(dictation.state.value).toBe('transcribing')
    await flush()

    expect(transcribeAudio).toHaveBeenCalledTimes(1)
    const clip = transcribeAudio.mock.calls[0]![0] as Blob
    expect(clip.type).toBe('audio/webm;codecs=opus')
    expect(clip.size).toBeGreaterThan(0)
    expect(onTranscript).toHaveBeenCalledWith('Add a contact page')
    expect(dictation.state.value).toBe('idle')
    // The mic light must go out: the stream's tracks are stopped.
    expect(streams[0]!.stopped).toBeGreaterThan(0)
    expect(dictation.level.value).toBe(0)
    expect(dictation.error.value).toBeNull()
  })

  it('drops a double-tap instead of sending a clip too short to hold words', async () => {
    const onTranscript = vi.fn()
    const dictation = useDictation({ onTranscript })
    await dictation.start()
    vi.advanceTimersByTime(MIN_CLIP_MS - 100)
    dictation.stop()
    await flush()
    expect(transcribeAudio).not.toHaveBeenCalled()
    expect(onTranscript).not.toHaveBeenCalled()
    expect(dictation.state.value).toBe('idle')
    expect(dictation.error.value).toMatch(/too quick/)
  })

  it('toggle starts when idle and stops when recording', async () => {
    transcribeAudio.mockResolvedValue('hi')
    const dictation = useDictation({ onTranscript: vi.fn() })
    dictation.toggle()
    await flush()
    expect(dictation.state.value).toBe('recording')
    vi.advanceTimersByTime(1000)
    dictation.toggle()
    expect(dictation.state.value).toBe('transcribing')
    // A third press mid-transcription is ignored rather than opening the mic
    // again underneath the clip being transcribed.
    dictation.toggle()
    expect(FakeRecorder.instances).toHaveLength(1)
    await flush()
    expect(dictation.state.value).toBe('idle')
  })

  it('lets go of the mic and says so when the recorder will not start', async () => {
    const start = FakeRecorder.prototype.start
    FakeRecorder.prototype.start = () => {
      throw new DOMException('no live tracks', 'NotSupportedError')
    }
    try {
      const dictation = useDictation({ onTranscript: vi.fn() })
      await dictation.start()
      expect(dictation.state.value).toBe('idle')
      expect(dictation.error.value).toBe('The microphone could not be started.')
      expect(streams[0]!.stopped).toBeGreaterThan(0)
      // Idle for real: the next press opens the mic again.
      FakeRecorder.prototype.start = start
      await dictation.start()
      expect(dictation.state.value).toBe('recording')
    } finally {
      FakeRecorder.prototype.start = start
    }
  })

  it('says the mic is blocked when permission is refused', async () => {
    getUserMedia.mockRejectedValue({ name: 'NotAllowedError' })
    const dictation = useDictation({ onTranscript: vi.fn() })
    await dictation.start()
    expect(dictation.state.value).toBe('idle')
    expect(dictation.error.value).toMatch(/Microphone access is blocked/)
  })

  it('reports a transcription failure in the server\'s words when it has them', async () => {
    transcribeAudio.mockRejectedValue({ response: { status: 502, data: { error: "Couldn't transcribe that — try again" } } })
    const onTranscript = vi.fn()
    const dictation = useDictation({ onTranscript })
    await record(dictation)
    expect(onTranscript).not.toHaveBeenCalled()
    expect(dictation.state.value).toBe('idle')
    expect(dictation.error.value).toBe("Couldn't transcribe that — try again")
  })

  it('names the plan limit when dictation is refused for usage', async () => {
    transcribeAudio.mockRejectedValue({ response: { status: 429, data: { error: 'usage_limit_exceeded' } } })
    const dictation = useDictation({ onTranscript: vi.fn() })
    await record(dictation)
    expect(dictation.error.value).toMatch(/Usage limit reached/)
  })

  it('points at the microphone picker when nothing was heard', async () => {
    transcribeAudio.mockResolvedValue('   ')
    const onTranscript = vi.fn()
    const dictation = useDictation({ onTranscript })
    await record(dictation)
    expect(onTranscript).not.toHaveBeenCalled()
    expect(dictation.error.value).toMatch(/Nothing was heard.*which microphone/)
  })

  it('cancel drops the clip without transcribing and releases the mic', async () => {
    const onTranscript = vi.fn()
    const dictation = useDictation({ onTranscript })
    await dictation.start()
    vi.advanceTimersByTime(1000)
    dictation.cancel()
    await flush()
    expect(FakeRecorder.instances[0]!.state).toBe('inactive')
    expect(transcribeAudio).not.toHaveBeenCalled()
    expect(onTranscript).not.toHaveBeenCalled()
    expect(dictation.state.value).toBe('idle')
    expect(streams[0]!.stopped).toBeGreaterThan(0)
  })

  it('clears the error line on its own after a few seconds', async () => {
    getUserMedia.mockRejectedValue({ name: 'NotFoundError' })
    const dictation = useDictation({ onTranscript: vi.fn() })
    await dictation.start()
    expect(dictation.error.value).toMatch(/No microphone/)
    vi.advanceTimersByTime(6500)
    expect(dictation.error.value).toBeNull()
  })
})
