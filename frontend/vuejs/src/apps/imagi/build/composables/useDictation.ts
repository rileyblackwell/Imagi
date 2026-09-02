import { ref, computed, getCurrentInstance, onBeforeUnmount } from 'vue'
import type { ComputedRef, Ref } from 'vue'
import { AgentService } from '../services/agentService'

export type DictationState = 'idle' | 'recording' | 'transcribing'

/** One microphone, as the browser lists it. `label` is empty until the user
 *  has allowed microphone access once — browsers hide device names before
 *  that, so the list can exist before it can be read. */
export interface AudioInput {
  id: string
  label: string
}

export interface DictationOptions {
  /** Receives the transcript, trimmed, once a clip has been transcribed. */
  onTranscript: (text: string) => void
}

export interface Dictation {
  state: Ref<DictationState>
  /** The last thing that went wrong, shown for a few seconds then cleared. */
  error: Ref<string | null>
  /** Whether this browser can record at all (secure context, MediaRecorder). */
  supported: boolean
  /** How loud the mic is right now while recording, 0–1. Stays 0 where the
   *  browser has no Web Audio, so it is decoration, never a gate. */
  level: Ref<number>
  /** The microphones the browser knows about, pseudo-entries removed. */
  inputs: Ref<AudioInput[]>
  /** The one that would be (or is being) recorded from. */
  activeInput: ComputedRef<AudioInput | null>
  /** True while the browser is withholding device names: the user has not
   *  allowed microphone access yet, so the picker cannot show anything. */
  labelsHidden: ComputedRef<boolean>
  /** Start when idle, stop when recording — the one entry point the button
   *  and the keyboard shortcut both call. A no-op while transcribing. */
  toggle: () => void
  start: () => Promise<void>
  stop: () => void
  /** Drop the recorder without transcribing (unmount, thread switch). */
  cancel: () => void
  /** Remember a microphone to record from. Null goes back to the built-in
   *  default. */
  selectInput: (id: string | null) => void
  /** Re-read the device list (AirPods may have connected since). */
  refreshInputs: () => Promise<void>
  /** Ask for microphone access once, so the browser reveals device names. */
  unlockInputs: () => Promise<void>
}

// Containers to ask MediaRecorder for, best first. Chrome and Firefox have
// Opus in webm; Safari only records mp4. The first the browser admits to wins,
// and an empty pick lets it choose.
const PREFERRED_MIME_TYPES = [
  'audio/webm;codecs=opus',
  'audio/webm',
  'audio/mp4',
  'audio/ogg;codecs=opus',
]

/** Where the chosen microphone is remembered. Device ids are stable per
 *  origin for as long as the browser keeps the permission, which is exactly
 *  the lifetime a saved choice should have. */
export const INPUT_STORAGE_KEY = 'imagi.dictation.inputDeviceId'

/** Chrome lists "Default" and "Communications" pseudo-devices that alias
 *  whatever the OS currently routes to — which is the AirPods problem in a
 *  nutshell. The picker shows real devices only. */
const PSEUDO_INPUT_IDS = new Set(['default', 'communications'])

/** How browsers name the microphone inside the machine (macOS: "MacBook Pro
 *  Microphone (Built-in)", Windows: "Microphone Array (Realtek…)"). */
const BUILT_IN_INPUT = /built-in|internal|microphone array|macbook|imac|mac mini|mac studio|mac pro/i

/** A clip shorter than this is a double-tap, not a sentence. It is dropped
 *  rather than sent: a near-empty clip is what makes a transcription model
 *  invent words. */
export const MIN_CLIP_MS = 300

/** How long a mistake stays on screen before the line clears itself. */
const ERROR_TTL_MS = 6000

/** The processing every dictation wants. Browsers default these on for a
 *  plain `audio: true`, but a deviceId constraint must restate them. */
const AUDIO_PROCESSING = {
  echoCancellation: true,
  noiseSuppression: true,
  autoGainControl: true,
}

export function isBuiltInInput(input: AudioInput | null | undefined): boolean {
  return !!input && BUILT_IN_INPUT.test(input.label)
}

/**
 * Which microphone to record from: the one the user picked if it is still
 * plugged in, else the computer's own. "Whatever the OS calls default" is
 * deliberately last — on a Mac that flips to AirPods the moment they connect,
 * and the AirPods mic in a case across the room hears nothing.
 */
export function preferredInput(inputs: AudioInput[], chosenId: string | null): AudioInput | null {
  if (chosenId) {
    const chosen = inputs.find(input => input.id === chosenId)
    if (chosen) return chosen
  }
  const real = inputs.filter(input => !PSEUDO_INPUT_IDS.has(input.id))
  return real.find(isBuiltInInput) ?? real[0] ?? inputs[0] ?? null
}

function pickMimeType(): string | undefined {
  if (typeof MediaRecorder === 'undefined' || typeof MediaRecorder.isTypeSupported !== 'function') {
    return undefined
  }
  return PREFERRED_MIME_TYPES.find(type => MediaRecorder.isTypeSupported(type))
}

function isSupported(): boolean {
  return (
    typeof window !== 'undefined' &&
    typeof MediaRecorder !== 'undefined' &&
    typeof navigator !== 'undefined' &&
    typeof navigator.mediaDevices?.getUserMedia === 'function'
  )
}

function constraintsFor(input: AudioInput | null): MediaStreamConstraints {
  // An empty id is a device the browser will not name yet; only a real id
  // can be asked for by name.
  if (!input?.id || PSEUDO_INPUT_IDS.has(input.id)) return { audio: { ...AUDIO_PROCESSING } }
  return { audio: { ...AUDIO_PROCESSING, deviceId: { exact: input.id } } }
}

/** The named device is gone or busy (unplugged AirPods, a mic another app
 *  holds): worth retrying with whatever the OS offers. */
function isDeviceError(err: unknown): boolean {
  const name = (err as { name?: string } | null)?.name
  return name === 'OverconstrainedError' || name === 'NotFoundError' || name === 'NotReadableError'
}

function messageForMicError(err: unknown): string {
  const name = (err as { name?: string } | null)?.name
  if (name === 'NotAllowedError' || name === 'SecurityError') {
    return 'Microphone access is blocked — allow it in your browser to dictate.'
  }
  if (name === 'NotFoundError' || name === 'OverconstrainedError') {
    return 'No microphone was found.'
  }
  return 'The microphone could not be started.'
}

function messageForTranscribeError(err: unknown): string {
  const e = err as { response?: { status?: number; data?: { error?: string } }; message?: string } | null
  const status = e?.response?.status
  const serverMessage = e?.response?.data?.error
  if (status === 429) return 'Usage limit reached — dictation is paused until it resets.'
  if (status === 503) return 'Dictation is not available on this server.'
  if (typeof serverMessage === 'string' && serverMessage) return serverMessage
  return "Couldn't transcribe that — try again."
}

function readStoredInput(): string | null {
  try {
    return localStorage.getItem(INPUT_STORAGE_KEY)
  } catch {
    return null
  }
}

function writeStoredInput(id: string | null) {
  try {
    if (id) localStorage.setItem(INPUT_STORAGE_KEY, id)
    else localStorage.removeItem(INPUT_STORAGE_KEY)
  } catch {
    // Private mode: the choice lasts the session.
  }
}

/**
 * Dictation for the composer: hold the mic open, then hand the clip to the
 * backend for OpenAI to transcribe. The transcript goes to onTranscript for
 * the caller to put in the textbox — it is never sent anywhere on its own.
 *
 * One recorder at a time. The returned `supported` is fixed at creation, so
 * a caller can hide the control entirely where recording is impossible.
 */
export function useDictation(opts: DictationOptions): Dictation {
  const state = ref<DictationState>('idle')
  const error = ref<string | null>(null)
  const level = ref(0)
  const inputs = ref<AudioInput[]>([])
  const chosenInputId = ref<string | null>(readStoredInput())
  const supported = isSupported()

  const activeInput = computed(() => preferredInput(inputs.value, chosenInputId.value))
  const labelsHidden = computed(
    () => inputs.value.length > 0 && inputs.value.every(input => !input.label)
  )

  let recorder: MediaRecorder | null = null
  let stream: MediaStream | null = null
  let chunks: Blob[] = []
  let startedAt = 0
  // Set by cancel(): the recorder's final stop event must then discard the
  // clip instead of transcribing it.
  let discarded = false
  let errorTimer: ReturnType<typeof setTimeout> | null = null

  // Level meter: a Web Audio analyser tapped off the live stream, read on a
  // plain interval rather than requestAnimationFrame — 25 readings a second
  // is plenty for a ring, and an interval keeps going when the tab is not
  // painting, which is what makes the meter checkable from outside.
  let audioContext: AudioContext | null = null
  let analyser: AnalyserNode | null = null
  let levelTimer: ReturnType<typeof setInterval> | null = null

  function setError(message: string) {
    error.value = message
    if (errorTimer) clearTimeout(errorTimer)
    errorTimer = setTimeout(() => {
      error.value = null
      errorTimer = null
    }, ERROR_TTL_MS)
  }

  async function refreshInputs() {
    if (!supported || typeof navigator.mediaDevices.enumerateDevices !== 'function') return
    try {
      const devices = await navigator.mediaDevices.enumerateDevices()
      const found = devices
        .filter(device => device.kind === 'audioinput')
        .map(device => ({ id: device.deviceId, label: device.label }))
      const real = found.filter(input => !PSEUDO_INPUT_IDS.has(input.id))
      inputs.value = real.length > 0 ? real : found
    } catch {
      // A browser that will not list devices still records from its default.
    }
  }

  function selectInput(id: string | null) {
    chosenInputId.value = id
    writeStoredInput(id)
  }

  function releaseStream(target: MediaStream | null = stream) {
    target?.getTracks().forEach(track => track.stop())
    if (target === stream) stream = null
  }

  /** Ask for access once and let go straight away, so device names appear
   *  in the picker before the first dictation. */
  async function unlockInputs() {
    if (!supported) return
    try {
      const granted = await navigator.mediaDevices.getUserMedia({ audio: true })
      releaseStream(granted)
    } catch (err) {
      setError(messageForMicError(err))
      return
    }
    await refreshInputs()
  }

  /**
   * Open the microphone to record from. Asks for the preferred device by
   * name when the browser will name devices; on the very first grant it
   * cannot, so the stream is taken on the OS default and then swapped to
   * the built-in mic once the names come through.
   */
  async function acquireStream(): Promise<MediaStream> {
    await refreshInputs()
    const namesKnown = inputs.value.length > 0 && !labelsHidden.value
    const target = activeInput.value
    let acquired: MediaStream
    try {
      acquired = await navigator.mediaDevices.getUserMedia(constraintsFor(target))
    } catch (err) {
      if (!target?.id || !isDeviceError(err)) throw err
      // The chosen device is gone: record on whatever the OS offers rather
      // than refuse, and let the picker show what happened.
      acquired = await navigator.mediaDevices.getUserMedia(constraintsFor(null))
    }
    if (namesKnown) return acquired

    await refreshInputs()
    const preferred = activeInput.value
    const current = acquired.getAudioTracks()[0]?.getSettings?.()?.deviceId
    if (!preferred?.id || PSEUDO_INPUT_IDS.has(preferred.id) || preferred.id === current) {
      return acquired
    }
    try {
      const swapped = await navigator.mediaDevices.getUserMedia(constraintsFor(preferred))
      releaseStream(acquired)
      return swapped
    } catch {
      return acquired
    }
  }

  function startLevelMeter(source: MediaStream) {
    if (typeof AudioContext === 'undefined') return
    try {
      audioContext = new AudioContext()
      analyser = audioContext.createAnalyser()
      analyser.fftSize = 512
      audioContext.createMediaStreamSource(source).connect(analyser)
      void audioContext.resume().catch(() => {})
      const samples = new Uint8Array(analyser.fftSize)
      const tick = () => {
        if (!analyser) return
        analyser.getByteTimeDomainData(samples)
        let sum = 0
        for (let i = 0; i < samples.length; i++) {
          const v = ((samples[i] ?? 128) - 128) / 128
          sum += v * v
        }
        // Speech peaks around 0.25 RMS; scale so a normal voice fills the ring.
        level.value = Math.min(1, Math.sqrt(sum / samples.length) * 4)
      }
      levelTimer = setInterval(tick, 40)
    } catch {
      // The meter is decoration; recording goes on without it.
    }
  }

  function stopLevelMeter() {
    if (levelTimer) clearInterval(levelTimer)
    levelTimer = null
    analyser = null
    void audioContext?.close().catch(() => {})
    audioContext = null
    level.value = 0
  }

  async function start() {
    if (!supported || state.value !== 'idle') return
    error.value = null
    discarded = false
    try {
      stream = await acquireStream()
    } catch (err) {
      setError(messageForMicError(err))
      return
    }
    // The user may have cancelled (or the pane unmounted) while the
    // permission prompt was up.
    if (discarded) {
      releaseStream()
      return
    }
    const mimeType = pickMimeType()
    chunks = []
    try {
      recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
      recorder.ondataavailable = event => {
        if (event.data && event.data.size > 0) chunks.push(event.data)
      }
      recorder.onstop = () => {
        void finish()
      }
      recorder.start()
    } catch {
      // A stream with no live track, or a container the recorder will not
      // take after all: let go of the mic and say so, rather than leaving a
      // rejected promise and a button that looks idle.
      recorder = null
      releaseStream()
      setError('The microphone could not be started.')
      return
    }
    startedAt = Date.now()
    startLevelMeter(stream)
    state.value = 'recording'
  }

  function stop() {
    if (state.value !== 'recording' || !recorder) return
    state.value = 'transcribing'
    // The clip is transcribed from the recorder's stop event, once the last
    // chunk has been delivered.
    recorder.stop()
  }

  async function finish() {
    const type = recorder?.mimeType || chunks[0]?.type || 'audio/webm'
    const heldFor = Date.now() - startedAt
    stopLevelMeter()
    releaseStream()
    recorder = null
    const blob = new Blob(chunks, { type })
    chunks = []
    if (discarded || blob.size === 0) {
      state.value = 'idle'
      return
    }
    if (heldFor < MIN_CLIP_MS) {
      state.value = 'idle'
      setError('That was too quick — hold the mic a moment longer.')
      return
    }
    try {
      const text = (await AgentService.transcribeAudio(blob)).trim()
      if (text) opts.onTranscript(text)
      else setError('Nothing was heard — check which microphone is selected and try again.')
    } catch (err) {
      setError(messageForTranscribeError(err))
    } finally {
      state.value = 'idle'
    }
  }

  function cancel() {
    discarded = true
    if (recorder && recorder.state !== 'inactive') {
      // finish() runs from onstop and sees `discarded`.
      recorder.stop()
    } else {
      stopLevelMeter()
      releaseStream()
      recorder = null
      chunks = []
    }
    if (state.value === 'recording') state.value = 'idle'
  }

  function toggle() {
    if (state.value === 'recording') stop()
    else if (state.value === 'idle') void start()
  }

  // Keep the list current as headsets come and go.
  const onDeviceChange = () => {
    void refreshInputs()
  }
  if (supported && typeof navigator.mediaDevices.addEventListener === 'function') {
    navigator.mediaDevices.addEventListener('devicechange', onDeviceChange)
    void refreshInputs()
  }

  // A hot mic must not outlive the pane that opened it.
  if (getCurrentInstance()) {
    onBeforeUnmount(() => {
      cancel()
      if (supported && typeof navigator.mediaDevices.removeEventListener === 'function') {
        navigator.mediaDevices.removeEventListener('devicechange', onDeviceChange)
      }
    })
  }

  return {
    state,
    error,
    supported,
    level,
    inputs,
    activeInput,
    labelsHidden,
    toggle,
    start,
    stop,
    cancel,
    selectInput,
    refreshInputs,
    unlockInputs,
  }
}
