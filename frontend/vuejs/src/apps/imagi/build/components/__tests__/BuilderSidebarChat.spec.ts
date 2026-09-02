import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import type { Ref } from 'vue'
import { useAgentStore } from '@/apps/imagi/build/stores/agentStore'
import type { AgentInstance } from '@/apps/imagi/build/types/services'

/** The dictation composable's surface, as the composer sees it. Its refs are
 *  made inside the mock factory (vue is only importable there) and parked
 *  here so tests can drive the state and read the callback. */
type AudioInput = { id: string; label: string }

const dictation = vi.hoisted(() => ({
  state: null as unknown as Ref<'idle' | 'recording' | 'transcribing'>,
  error: null as unknown as Ref<string | null>,
  level: null as unknown as Ref<number>,
  inputs: null as unknown as Ref<AudioInput[]>,
  activeInput: null as unknown as Ref<AudioInput | null>,
  labelsHidden: null as unknown as Ref<boolean>,
  supported: true,
  toggle: vi.fn(),
  cancel: vi.fn(),
  selectInput: vi.fn(),
  unlockInputs: vi.fn(),
  refreshInputs: vi.fn(),
  onTranscript: null as null | ((text: string) => void),
}))

vi.mock('../../composables/useDictation', async () => {
  const { ref } = await import('vue')
  return {
    isBuiltInInput: (input: AudioInput | null) => !!input && /built-in/i.test(input.label),
    useDictation: (opts: { onTranscript: (text: string) => void }) => {
      dictation.state = ref<'idle' | 'recording' | 'transcribing'>('idle')
      dictation.error = ref<string | null>(null)
      dictation.level = ref(0)
      dictation.inputs = ref<AudioInput[]>([])
      dictation.activeInput = ref<AudioInput | null>(null)
      dictation.labelsHidden = ref(false)
      dictation.onTranscript = opts.onTranscript
      return {
        state: dictation.state,
        error: dictation.error,
        level: dictation.level,
        inputs: dictation.inputs,
        activeInput: dictation.activeInput,
        labelsHidden: dictation.labelsHidden,
        supported: dictation.supported,
        toggle: dictation.toggle,
        cancel: dictation.cancel,
        selectInput: dictation.selectInput,
        unlockInputs: dictation.unlockInputs,
        refreshInputs: dictation.refreshInputs,
        start: vi.fn(),
        stop: vi.fn(),
      }
    },
  }
})

const BUILT_IN = { id: 'mic-builtin', label: 'MacBook Pro Microphone (Built-in)' }
const AIRPODS = { id: 'mic-airpods', label: "Riley's AirPods Pro" }

import BuilderSidebarChat from '../organisms/sidebar/BuilderSidebarChat.vue'

const instance = (overrides: Partial<AgentInstance> = {}): AgentInstance => ({
  id: 'lead-1',
  conversationId: 1,
  title: '',
  kind: 'lead',
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
  updatedAt: '2026-01-01T00:00:00Z',
  lastMessagePreview: '',
  lastAssistantSummary: '',
  brief: '',
  overview: '',
  messagesLoaded: true,
  hasUnread: false,
  queuedPrompt: null,
  ...overrides,
} as AgentInstance)

function mountWith(active: AgentInstance = instance()) {
  const store = useAgentStore()
  store.$patch({ instances: [active], activeInstanceId: active.id })
  return mount(BuilderSidebarChat, {
    attachTo: document.body,
    props: {
      onPromptSubmit: vi.fn().mockResolvedValue(undefined),
      onModelSelect: vi.fn().mockResolvedValue(undefined),
      onEffortSelect: vi.fn().mockResolvedValue(undefined),
    },
    global: {
      stubs: { ChatConversation: true, CheckInQueue: true, WorkspacePaneHeader: true },
    },
  })
}

function press(init: KeyboardEventInit, target: EventTarget = document.body) {
  const event = new KeyboardEvent('keydown', { bubbles: true, cancelable: true, ...init })
  target.dispatchEvent(event)
  return event
}

describe('BuilderSidebarChat dictation', () => {
  let wrapper: ReturnType<typeof mountWith> | null = null

  beforeEach(() => {
    setActivePinia(createPinia())
    dictation.supported = true
    Object.defineProperty(navigator, 'platform', { value: 'MacIntel', configurable: true })
  })
  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('puts a mic in the composer that toggles dictation', async () => {
    wrapper = mountWith()
    const mic = wrapper.find('button.btn-dictate')
    expect(mic.exists()).toBe(true)
    expect(mic.attributes('title')).toBe('Dictate a prompt (⌘D)')
    await mic.trigger('click')
    expect(dictation.toggle).toHaveBeenCalledTimes(1)
  })

  it('shows the mic as live while recording, and busy while transcribing', async () => {
    wrapper = mountWith()
    dictation.activeInput.value = BUILT_IN
    dictation.state.value = 'recording'
    await nextTick()
    const mic = wrapper.find('button.btn-dictate')
    expect(mic.classes()).toContain('btn-dictate--recording')
    expect(mic.attributes('aria-pressed')).toBe('true')
    expect(mic.attributes('title')).toBe('Stop dictating (⌘D)')
    // Says which mic it is listening on, so a headset in a drawer is noticed.
    expect(wrapper.find('textarea').attributes('placeholder')).toMatch(
      /Listening on MacBook Pro Microphone \(Built-in\)/
    )

    dictation.state.value = 'transcribing'
    await nextTick()
    expect(mic.attributes('disabled')).toBeDefined()
    expect(mic.find('.fa-spin').exists()).toBe(true)
    expect(wrapper.find('textarea').attributes('placeholder')).toBe('Transcribing…')
  })

  it('widens the ring with the voice level while recording', async () => {
    wrapper = mountWith()
    dictation.state.value = 'recording'
    dictation.level.value = 0.5
    await nextTick()
    const style = (wrapper.find('button.btn-dictate').element as HTMLElement).style
    expect(style.getPropertyValue('--dictate-ring')).toBe('7px')
    dictation.state.value = 'idle'
    await nextTick()
    expect(style.getPropertyValue('--dictate-ring')).toBe('')
  })

  it('offers a microphone picker beside the mic, built-in marked and chosen', async () => {
    wrapper = mountWith()
    dictation.inputs.value = [BUILT_IN, AIRPODS]
    dictation.activeInput.value = BUILT_IN
    await nextTick()
    expect(wrapper.find('.mic-panel').exists()).toBe(false)

    await wrapper.find('button.mic-caret').trigger('click')
    expect(dictation.refreshInputs).toHaveBeenCalled()
    const rows = wrapper.findAll('.mic-panel .mic-option')
    expect(rows).toHaveLength(2)
    expect(rows[0]!.text()).toContain('MacBook Pro Microphone (Built-in)')
    expect(rows[0]!.find('.mic-option-tag').text()).toBe('Built-in')
    expect(rows[0]!.attributes('aria-checked')).toBe('true')
    expect(rows[1]!.text()).toContain("Riley's AirPods Pro")
    expect(rows[1]!.find('.mic-option-tag').exists()).toBe(false)
    expect(rows[1]!.attributes('aria-checked')).toBe('false')

    await rows[1]!.trigger('click')
    expect(dictation.selectInput).toHaveBeenCalledWith('mic-airpods')
    expect(wrapper.find('.mic-panel').exists()).toBe(false)
  })

  it('asks for access first when the browser is hiding microphone names', async () => {
    wrapper = mountWith()
    dictation.inputs.value = [{ id: '', label: '' }]
    dictation.labelsHidden.value = true
    await nextTick()
    await wrapper.find('button.mic-caret').trigger('click')
    expect(wrapper.find('.mic-panel .mic-option').exists()).toBe(false)
    const allow = wrapper.find('.mic-panel button.mic-allow')
    expect(allow.text()).toBe('Allow microphone access')
    await allow.trigger('click')
    expect(dictation.unlockInputs).toHaveBeenCalled()
  })

  it('surfaces the last dictation error under the textarea', async () => {
    wrapper = mountWith()
    expect(wrapper.find('.dictation-error').exists()).toBe(false)
    dictation.error.value = 'Microphone access is blocked — allow it in your browser to dictate.'
    await nextTick()
    expect(wrapper.find('.dictation-error').text()).toMatch(/Microphone access is blocked/)
  })

  it('⌘D toggles dictation from anywhere in the workspace', () => {
    wrapper = mountWith()
    const event = press({ key: 'd', metaKey: true })
    expect(dictation.toggle).toHaveBeenCalledTimes(1)
    // The browser's own ⌘D (bookmark this page) must not fire too.
    expect(event.defaultPrevented).toBe(true)
  })

  it('leaves other D chords, and plain D, alone', () => {
    wrapper = mountWith()
    press({ key: 'd' })
    press({ key: 'd', metaKey: true, shiftKey: true })
    press({ key: 'd', ctrlKey: true })
    press({ key: 'k', metaKey: true })
    expect(dictation.toggle).not.toHaveBeenCalled()
  })

  it('uses Ctrl+D off Apple hardware', () => {
    Object.defineProperty(navigator, 'platform', { value: 'Win32', configurable: true })
    wrapper = mountWith()
    expect(wrapper.find('button.btn-dictate').attributes('title')).toBe('Dictate a prompt (Ctrl+D)')
    press({ key: 'd', ctrlKey: true })
    expect(dictation.toggle).toHaveBeenCalledTimes(1)
  })

  it('yields to the preview when it has already taken the keystroke', () => {
    wrapper = mountWith()
    const event = new KeyboardEvent('keydown', { key: 'd', metaKey: true, bubbles: true, cancelable: true })
    event.preventDefault()
    document.body.dispatchEvent(event)
    expect(dictation.toggle).not.toHaveBeenCalled()
  })

  it('has no mic and ignores ⌘D on a read-only task thread', () => {
    wrapper = mountWith(instance({ id: 'task-1', kind: 'task', title: 'Contact page' }))
    expect(wrapper.find('button.btn-dictate').exists()).toBe(false)
    press({ key: 'd', metaKey: true })
    expect(dictation.toggle).not.toHaveBeenCalled()
  })

  it('closes a live mic when the thread turns read-only', async () => {
    const lead = instance()
    const task = instance({ id: 'task-1', kind: 'task' })
    wrapper = mountWith(lead)
    const store = useAgentStore()
    store.$patch({ instances: [lead, task], activeInstanceId: task.id })
    await nextTick()
    expect(dictation.cancel).toHaveBeenCalled()
  })

  it('hides the mic where the browser cannot record', () => {
    dictation.supported = false
    wrapper = mountWith()
    expect(wrapper.find('button.btn-dictate').exists()).toBe(false)
    press({ key: 'd', metaKey: true })
    expect(dictation.toggle).not.toHaveBeenCalled()
  })

  it('drops the transcript into the textbox after what is already there, and never sends it', async () => {
    wrapper = mountWith()
    const textarea = wrapper.find('textarea')
    dictation.onTranscript!('Add a contact page')
    await nextTick()
    expect((textarea.element as HTMLTextAreaElement).value).toBe('Add a contact page')

    dictation.onTranscript!('with a map')
    await nextTick()
    expect((textarea.element as HTMLTextAreaElement).value).toBe('Add a contact page with a map')
    expect(document.activeElement).toBe(textarea.element)
    expect(wrapper.props('onPromptSubmit')).not.toHaveBeenCalled()
  })

  it('stops listening for ⌘D once unmounted', () => {
    wrapper = mountWith()
    wrapper.unmount()
    wrapper = null
    press({ key: 'd', metaKey: true })
    expect(dictation.toggle).not.toHaveBeenCalled()
  })
})
