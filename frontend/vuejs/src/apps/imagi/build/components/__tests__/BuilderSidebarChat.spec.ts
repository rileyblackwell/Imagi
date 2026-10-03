import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import type { Ref } from 'vue'
import { useAgentStore } from '@/apps/imagi/build/stores/agentStore'
import type { AgentInstance, ReasoningEffort } from '@/apps/imagi/build/types/services'

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
  start: vi.fn(),
  stop: vi.fn(),
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
        start: dictation.start,
        stop: dictation.stop,
        cancel: dictation.cancel,
        selectInput: dictation.selectInput,
        unlockInputs: dictation.unlockInputs,
        refreshInputs: dictation.refreshInputs,
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
  selectedModelId: 'claude-opus-5-5',
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
  // The select callbacks write the store the way the workspace does, so the
  // panel's checked state follows a pick as it would in the app.
  const current = () => store.instances.find(i => i.id === active.id)!
  return mount(BuilderSidebarChat, {
    attachTo: document.body,
    props: {
      onPromptSubmit: vi.fn().mockResolvedValue(undefined),
      onModelSelect: vi.fn(async (id: string) => {
        current().selectedModelId = id
      }),
      onEffortSelect: vi.fn(async (effort: ReasoningEffort) => {
        current().selectedEffort = effort
      }),
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

/** Letting a key up. Which one matters: macOS delivers no keyup for the
 *  letter while Command is still down, so the modifier's is all there is. */
function release(key: string, target: EventTarget = document.body) {
  target.dispatchEvent(new KeyboardEvent('keyup', { key, bubbles: true, cancelable: true }))
}

/** The composer's one button: hold to dictate, click to send. */
function sendButton(wrapper: ReturnType<typeof mountWith>) {
  return wrapper.find('button.btn-send')
}

/** One pointer event on the button. Dispatched by hand: test-utils' trigger
 *  builds a MouseEvent and then cannot set its read-only `button`. */
async function pointer(wrapper: ReturnType<typeof mountWith>, type: string, mouseButton = 0) {
  sendButton(wrapper).element.dispatchEvent(
    new MouseEvent(type, { bubbles: true, cancelable: true, button: mouseButton })
  )
  await nextTick()
}

/** A press of the button that lets go after `heldFor` ms, then the click the
 *  browser fires on release. */
async function pressFor(wrapper: ReturnType<typeof mountWith>, heldFor: number) {
  await pointer(wrapper, 'pointerdown')
  await vi.advanceTimersByTimeAsync(heldFor)
  await pointer(wrapper, 'pointerup')
  await sendButton(wrapper).trigger('click')
}

async function typePrompt(wrapper: ReturnType<typeof mountWith>, text: string) {
  await wrapper.find('textarea').setValue(text)
}

/** The model + reasoning chip, the menu it opens, and the two radio groups
 *  inside it: the model list and the reasoning-effort bars. */
function tuneChip(wrapper: ReturnType<typeof mountWith>) {
  return wrapper.find('button[aria-label="Model and reasoning"]')
}
function tunePanel(wrapper: ReturnType<typeof mountWith>) {
  return wrapper.find('#tune-panel')
}
function modelRows(wrapper: ReturnType<typeof mountWith>) {
  return wrapper.findAll('#tune-panel button.model-row')
}
function effortGroup(wrapper: ReturnType<typeof mountWith>) {
  return wrapper.find('#tune-panel [role="radiogroup"][aria-labelledby="tune-effort-heading"]')
}
function effortBars(wrapper: ReturnType<typeof mountWith>) {
  return effortGroup(wrapper).findAll('button[role="radio"]')
}
type Radios = ReturnType<typeof modelRows>
/** Which option in a radio group is checked, as an index. */
const checked = (radios: Radios) => radios.findIndex(r => r.attributes('aria-checked') === 'true')
const readout = (wrapper: ReturnType<typeof mountWith>) =>
  tunePanel(wrapper).find('.effort-readout__name').text()
async function openTune(wrapper: ReturnType<typeof mountWith>) {
  await tuneChip(wrapper).trigger('click')
  await nextTick()
}

describe('BuilderSidebarChat dictation', () => {
  let wrapper: ReturnType<typeof mountWith> | null = null

  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
    dictation.supported = true
    // The real start() opens the mic and resolves once it is live.
    dictation.start.mockImplementation(() => {
      dictation.state.value = 'recording'
      return Promise.resolve()
    })
    Object.defineProperty(navigator, 'platform', { value: 'MacIntel', configurable: true })
  })
  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
    vi.useRealTimers()
  })

  it('offers model and reasoning as one chip that opens a model list and an effort meter', async () => {
    wrapper = mountWith()
    const chips = wrapper.findAll('button.control-chip').map(c => c.attributes('aria-label'))
    expect(chips).toEqual(['Model and reasoning', 'Usage limits'])
    const chip = tuneChip(wrapper)
    expect(chip.text()).toBe('Opus 5.5 · Medium')
    expect(chip.attributes('aria-controls')).toBe('tune-panel')
    expect(chip.attributes('aria-expanded')).toBe('false')
    expect(tunePanel(wrapper).exists()).toBe(false)

    await openTune(wrapper)
    expect(chip.attributes('aria-expanded')).toBe('true')
    expect(tunePanel(wrapper).attributes('role')).toBe('group')
    expect(tunePanel(wrapper).attributes('aria-label')).toBe('Model and reasoning')

    // The model list: three tiers, faster → smarter, each with its tag and
    // what it is for, the one in use checked and focused on open.
    const rows = modelRows(wrapper)
    expect(rows.map(r => r.find('.model-row__name').text())).toEqual([
      'Luna Fast',
      'Opus 5.5 Balanced',
      'Astra Frontier',
    ])
    expect(rows[1]!.find('.model-row__blurb').text()).toBe(
      'Thoughtful and dependable, with strong judgment on code and design. The default.'
    )
    expect(checked(rows)).toBe(1)
    expect(rows.map(r => r.attributes('tabindex'))).toEqual(['-1', '0', '-1'])
    expect(document.activeElement).toBe(rows[1]!.element)

    // Reasoning effort: four bars, Medium by default, filled up to the
    // chosen rung, with the cost spelled out.
    const bars = effortBars(wrapper)
    expect(bars.map(b => b.attributes('aria-label'))).toEqual([
      'Low: Quick answers for small edits',
      'Medium: The balanced default for everyday building',
      'High: Deeper thinking for multi-step work',
      'Extra High: The most thorough, for the hardest tasks',
    ])
    expect(checked(bars)).toBe(1)
    expect(bars.map(b => b.classes('effort-bar--on'))).toEqual([true, true, false, false])
    expect(readout(wrapper)).toBe('Medium')
    expect(effortGroup(wrapper).attributes('aria-describedby')).toBe('tune-effort-note')
    expect(wrapper.find('#tune-effort-note').text()).toBe(
      "More reasoning helps with difficult problems but uses more of your plan's usage. Medium is the default."
    )

    // Clicking hands the change to the workspace, and the menu follows it.
    await rows[2]!.trigger('click')
    expect(wrapper.props('onModelSelect')).toHaveBeenCalledWith('gpt-6-astra')
    await nextTick()
    expect(checked(modelRows(wrapper))).toBe(2)
    await effortBars(wrapper)[0]!.trigger('click')
    expect(wrapper.props('onEffortSelect')).toHaveBeenCalledWith('low')
    await nextTick()
    expect(checked(effortBars(wrapper))).toBe(0)
    expect(chip.text()).toBe('Astra · Low')

    // Picking what is already chosen writes nothing.
    await modelRows(wrapper)[2]!.trigger('click')
    expect(wrapper.props('onModelSelect')).toHaveBeenCalledTimes(1)

    // The menu stays open while both are being tuned; the chip puts it away.
    expect(tunePanel(wrapper).exists()).toBe(true)
    await chip.trigger('click')
    expect(tunePanel(wrapper).exists()).toBe(false)
    expect(chip.attributes('aria-expanded')).toBe('false')
  })

  it('hovering a bar previews its rung without choosing it', async () => {
    wrapper = mountWith()
    await openTune(wrapper)
    await effortBars(wrapper)[3]!.trigger('mouseenter')
    expect(readout(wrapper)).toBe('Extra High')
    expect(effortBars(wrapper)[3]!.classes()).toContain('effort-bar--preview')
    expect(checked(effortBars(wrapper))).toBe(1)
    await effortGroup(wrapper).trigger('mouseleave')
    expect(readout(wrapper)).toBe('Medium')
    expect(wrapper.props('onEffortSelect')).not.toHaveBeenCalled()
  })

  it('arrow keys move each group, clamped at the ends, and focus follows', async () => {
    wrapper = mountWith()
    await openTune(wrapper)
    const list = tunePanel(wrapper).find('[aria-labelledby="tune-model-heading"]')
    // Down the list is smarter.
    await list.trigger('keydown', { key: 'ArrowDown' })
    expect(wrapper.props('onModelSelect')).toHaveBeenLastCalledWith('gpt-6-astra')
    await nextTick()
    expect(document.activeElement).toBe(modelRows(wrapper)[2]!.element)
    await list.trigger('keydown', { key: 'ArrowDown' })
    expect(wrapper.props('onModelSelect')).toHaveBeenCalledTimes(1)
    await list.trigger('keydown', { key: 'Home' })
    expect(wrapper.props('onModelSelect')).toHaveBeenLastCalledWith('gpt-6-luna')

    // The bars stand left to right, so Up is more.
    await effortGroup(wrapper).trigger('keydown', { key: 'ArrowUp' })
    expect(wrapper.props('onEffortSelect')).toHaveBeenLastCalledWith('high')
    await nextTick()
    expect(document.activeElement).toBe(effortBars(wrapper)[2]!.element)
    await effortGroup(wrapper).trigger('keydown', { key: 'End' })
    expect(wrapper.props('onEffortSelect')).toHaveBeenLastCalledWith('xhigh')
    await nextTick()
    await effortGroup(wrapper).trigger('keydown', { key: 'ArrowRight' })
    expect(wrapper.props('onEffortSelect')).toHaveBeenCalledTimes(2)
  })

  it('a conversation on a model the menu does not offer sits on the default', async () => {
    wrapper = mountWith(instance({ selectedModelId: 'claude-sonnet-5' }))
    await openTune(wrapper)
    expect(checked(modelRows(wrapper))).toBe(1)
    expect(tuneChip(wrapper).text()).toBe('Opus 5.5 · Medium')
  })

  it('Escape puts the menu away and hands focus back to the chip', async () => {
    wrapper = mountWith()
    await openTune(wrapper)
    expect(document.activeElement).not.toBe(tuneChip(wrapper).element)
    await tunePanel(wrapper).trigger('keydown', { key: 'Escape' })
    await nextTick()
    expect(tunePanel(wrapper).exists()).toBe(false)
    expect(tuneChip(wrapper).attributes('aria-expanded')).toBe('false')
    expect(document.activeElement).toBe(tuneChip(wrapper).element)
  })

  it('closes on a mousedown outside the menu, and stays for one inside it', async () => {
    wrapper = mountWith()
    await openTune(wrapper)
    modelRows(wrapper)[0]!.element.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }))
    await nextTick()
    expect(tunePanel(wrapper).exists()).toBe(true)

    document.body.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }))
    await nextTick()
    expect(tunePanel(wrapper).exists()).toBe(false)
    expect(tuneChip(wrapper).attributes('aria-expanded')).toBe('false')
  })

  it('has nothing to act on without an instance: every option goes disabled', async () => {
    wrapper = mountWith()
    await openTune(wrapper)
    useAgentStore().$patch({ activeInstanceId: '' })
    await nextTick()
    expect(modelRows(wrapper).every(r => r.attributes('disabled') !== undefined)).toBe(true)
    expect(effortBars(wrapper).every(b => b.attributes('disabled') !== undefined)).toBe(true)
    await effortGroup(wrapper).trigger('keydown', { key: 'ArrowUp' })
    expect(wrapper.props('onEffortSelect')).not.toHaveBeenCalled()
    expect(tuneChip(wrapper).attributes('disabled')).toBeDefined()
  })

  it('has one button and nothing beside it, and it gains a send arrow once there is text', async () => {
    wrapper = mountWith()
    expect(wrapper.find('button.btn-dictate').exists()).toBe(false)
    expect(wrapper.find('button.mic-caret').exists()).toBe(false)
    // The only microphone glyph in the composer is on the send button itself.
    expect(wrapper.findAll('.fa-microphone')).toHaveLength(1)
    const button = sendButton(wrapper)
    expect(button.exists()).toBe(true)
    expect(button.attributes('title')).toBe(
      'Hold to dictate, or hold ⌘D · click to send (Enter) · right-click to choose microphone'
    )
    // Nothing to send yet, but a hold still records — so never disabled.
    expect(button.attributes('disabled')).toBeUndefined()
    expect(button.classes()).toContain('btn-send--idle')
    expect(button.find('.fa-microphone').exists()).toBe(true)

    // Text turns it into the red record button wearing a send arrow, so a
    // click visibly sends; a hold still records more onto the words.
    await typePrompt(wrapper, 'Add a contact page')
    expect(button.classes()).toContain('btn-send--ready')
    expect(button.find('.fa-arrow-up').exists()).toBe(true)
    expect(button.find('.fa-microphone').exists()).toBe(false)
    expect(button.attributes('title')).toBe(
      'Hold to dictate, or hold ⌘D · click to send (Enter) · right-click to choose microphone'
    )

    // Whitespace alone is nothing to send.
    await typePrompt(wrapper, '   ')
    expect(button.classes()).toContain('btn-send--idle')
    expect(button.find('.fa-microphone').exists()).toBe(true)
  })

  it('goes back to the plain mic once the box is emptied by sending', async () => {
    wrapper = mountWith()
    await typePrompt(wrapper, 'Add a contact page')
    const button = sendButton(wrapper)
    expect(button.find('.fa-arrow-up').exists()).toBe(true)
    await pressFor(wrapper, 80)
    expect(wrapper.props('onPromptSubmit')).toHaveBeenCalledWith('Add a contact page')
    expect(button.classes()).toContain('btn-send--idle')
    expect(button.find('.fa-microphone').exists()).toBe(true)
    expect(button.find('.fa-arrow-up').exists()).toBe(false)
  })

  it('shows the mic, not the arrow, while a hold over existing text is recording', async () => {
    wrapper = mountWith()
    await typePrompt(wrapper, 'Add a contact page')
    const button = sendButton(wrapper)
    await pointer(wrapper, 'pointerdown')
    await vi.advanceTimersByTimeAsync(300)
    expect(dictation.start).toHaveBeenCalledTimes(1)
    expect(button.classes()).toContain('btn-send--recording')
    expect(button.find('.fa-microphone').exists()).toBe(true)
    expect(button.find('.fa-arrow-up').exists()).toBe(false)
    await pointer(wrapper, 'pointerup')
    await button.trigger('click')
    expect(wrapper.props('onPromptSubmit')).not.toHaveBeenCalled()
  })

  it('a click sends the prompt and never touches the mic', async () => {
    wrapper = mountWith()
    await typePrompt(wrapper, 'Add a contact page')
    await pressFor(wrapper, 80)
    expect(wrapper.props('onPromptSubmit')).toHaveBeenCalledWith('Add a contact page')
    expect(dictation.start).not.toHaveBeenCalled()
    expect((wrapper.find('textarea').element as HTMLTextAreaElement).value).toBe('')
  })

  it('a click on an empty box sends nothing', async () => {
    wrapper = mountWith()
    await pressFor(wrapper, 80)
    expect(wrapper.props('onPromptSubmit')).not.toHaveBeenCalled()
    expect(dictation.start).not.toHaveBeenCalled()
  })

  it('Enter sends too', async () => {
    wrapper = mountWith()
    await typePrompt(wrapper, 'Add a contact page')
    await wrapper.find('textarea').trigger('keydown', { key: 'Enter' })
    expect(wrapper.props('onPromptSubmit')).toHaveBeenCalledWith('Add a contact page')
  })

  it('a hold records, and letting go transcribes rather than sends', async () => {
    wrapper = mountWith()
    await typePrompt(wrapper, 'Add a contact page')
    const button = sendButton(wrapper)
    await pointer(wrapper, 'pointerdown')
    await vi.advanceTimersByTimeAsync(200)
    expect(dictation.start).not.toHaveBeenCalled()
    await vi.advanceTimersByTimeAsync(100)
    expect(dictation.start).toHaveBeenCalledTimes(1)
    expect(button.classes()).toContain('btn-send--recording')
    expect(button.attributes('aria-pressed')).toBe('true')

    await pointer(wrapper, 'pointerup')
    await button.trigger('click')
    expect(dictation.stop).toHaveBeenCalledTimes(1)
    // The click a release fires is the end of the hold, not a send.
    expect(wrapper.props('onPromptSubmit')).not.toHaveBeenCalled()
    expect((wrapper.find('textarea').element as HTMLTextAreaElement).value).toBe('Add a contact page')
  })

  it('hold, hold again, then tap: two transcripts join and one tap sends them', async () => {
    wrapper = mountWith()
    await pressFor(wrapper, 400)
    dictation.state.value = 'idle'
    dictation.onTranscript!('Add a contact page')
    await nextTick()

    await pressFor(wrapper, 400)
    dictation.state.value = 'idle'
    dictation.onTranscript!('with a map')
    await nextTick()
    expect(dictation.start).toHaveBeenCalledTimes(2)
    expect(dictation.stop).toHaveBeenCalledTimes(2)
    expect(wrapper.props('onPromptSubmit')).not.toHaveBeenCalled()

    await pressFor(wrapper, 80)
    expect(wrapper.props('onPromptSubmit')).toHaveBeenCalledWith('Add a contact page with a map')
  })

  it('letting go while the mic is still opening drops the clip silently', async () => {
    wrapper = mountWith()
    let open!: () => void
    dictation.start.mockImplementation(
      () =>
        new Promise<void>(resolve => {
          open = resolve
        })
    )
    await pointer(wrapper, 'pointerdown')
    await vi.advanceTimersByTimeAsync(300)
    expect(dictation.start).toHaveBeenCalledTimes(1)
    await pointer(wrapper, 'pointerup')
    await sendButton(wrapper).trigger('click')
    expect(dictation.cancel).toHaveBeenCalledTimes(1)
    expect(dictation.stop).not.toHaveBeenCalled()
    expect(wrapper.props('onPromptSubmit')).not.toHaveBeenCalled()
    open()
  })

  it('a tap while a ⌘D hold has the mic open stops dictating instead of sending', async () => {
    wrapper = mountWith()
    await typePrompt(wrapper, 'Add a contact page')
    press({ key: 'd', metaKey: true })
    expect(dictation.start).toHaveBeenCalledTimes(1)
    await nextTick()
    // The button says what ends it, and it is not another press.
    expect(sendButton(wrapper).attributes('title')).toBe("Listening — let go of ⌘D when you're done")
    await pressFor(wrapper, 80)
    expect(dictation.stop).toHaveBeenCalledTimes(1)
    expect(wrapper.props('onPromptSubmit')).not.toHaveBeenCalled()
  })

  it('a hold while a ⌘D hold has the mic open takes it over: letting go stops', async () => {
    wrapper = mountWith()
    dictation.state.value = 'recording'
    await nextTick()
    await pressFor(wrapper, 400)
    expect(dictation.start).not.toHaveBeenCalled()
    expect(dictation.stop).toHaveBeenCalledTimes(1)
  })

  it('ignores a right-button press', async () => {
    wrapper = mountWith()
    await pointer(wrapper, 'pointerdown', 2)
    await vi.advanceTimersByTimeAsync(400)
    expect(dictation.start).not.toHaveBeenCalled()
  })

  it('while a run is in flight a tap stops the agent and a hold still dictates', async () => {
    wrapper = mountWith(instance({ isProcessing: true }))
    const button = sendButton(wrapper)
    expect(button.attributes('title')).toBe(
      'Hold to dictate, or hold ⌘D · click to stop the agent · right-click to choose microphone'
    )
    expect(button.find('.fa-stop').exists()).toBe(true)

    await pressFor(wrapper, 400)
    expect(dictation.start).toHaveBeenCalledTimes(1)
    expect(dictation.stop).toHaveBeenCalledTimes(1)
    expect(wrapper.emitted('stop')).toBeUndefined()

    dictation.state.value = 'idle'
    await nextTick()
    await pressFor(wrapper, 80)
    expect(wrapper.emitted('stop')).toHaveLength(1)
  })

  it('shows the button as live while recording, and busy while transcribing', async () => {
    wrapper = mountWith()
    dictation.activeInput.value = BUILT_IN
    dictation.state.value = 'recording'
    await nextTick()
    const button = sendButton(wrapper)
    expect(button.classes()).toContain('btn-send--recording')
    expect(button.attributes('aria-pressed')).toBe('true')
    expect(button.find('.fa-microphone').exists()).toBe(true)
    // Says which mic it is listening on, so a headset in a drawer is noticed.
    expect(wrapper.find('textarea').attributes('placeholder')).toMatch(
      /Listening on MacBook Pro Microphone \(Built-in\)/
    )

    dictation.state.value = 'transcribing'
    await nextTick()
    expect(button.attributes('disabled')).toBeDefined()
    expect(button.find('.fa-spin').exists()).toBe(true)
    expect(wrapper.find('textarea').attributes('placeholder')).toBe('Transcribing…')
  })

  it('widens the ring with the voice level while recording', async () => {
    wrapper = mountWith()
    dictation.state.value = 'recording'
    dictation.level.value = 0.5
    await nextTick()
    const style = (sendButton(wrapper).element as HTMLElement).style
    expect(style.getPropertyValue('--dictate-ring')).toBe('7px')
    dictation.state.value = 'idle'
    await nextTick()
    expect(style.getPropertyValue('--dictate-ring')).toBe('')
  })

  it('opens the microphone picker on a right-click of the button, built-in marked and chosen', async () => {
    wrapper = mountWith()
    dictation.inputs.value = [BUILT_IN, AIRPODS]
    dictation.activeInput.value = BUILT_IN
    await nextTick()
    expect(wrapper.find('.mic-panel').exists()).toBe(false)

    const menu = new MouseEvent('contextmenu', { bubbles: true, cancelable: true, button: 2 })
    sendButton(wrapper).element.dispatchEvent(menu)
    await nextTick()
    // The browser's own menu never shows over the picker.
    expect(menu.defaultPrevented).toBe(true)
    expect(sendButton(wrapper).attributes('aria-expanded')).toBe('true')
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

  it('a right-click never starts a hold, and a press puts the picker away', async () => {
    wrapper = mountWith()
    dictation.inputs.value = [BUILT_IN]
    await nextTick()
    // The right button going down is the menu, not a hold-to-talk.
    await pointer(wrapper, 'pointerdown', 2)
    await sendButton(wrapper).trigger('contextmenu')
    await vi.advanceTimersByTimeAsync(400)
    expect(dictation.start).not.toHaveBeenCalled()
    expect(wrapper.find('.mic-panel').exists()).toBe(true)

    // The picker gives way to a hold the moment the primary button goes down.
    await pointer(wrapper, 'pointerdown')
    expect(wrapper.find('.mic-panel').exists()).toBe(false)
    await vi.advanceTimersByTimeAsync(400)
    expect(dictation.start).toHaveBeenCalledTimes(1)
    await pointer(wrapper, 'pointerup')
  })

  it('asks for access first when the browser is hiding microphone names', async () => {
    wrapper = mountWith()
    dictation.inputs.value = [{ id: '', label: '' }]
    dictation.labelsHidden.value = true
    await nextTick()
    await sendButton(wrapper).trigger('contextmenu')
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

  it('⌘D is a hold from anywhere in the workspace: down opens, up closes', async () => {
    wrapper = mountWith()
    const event = press({ key: 'd', metaKey: true })
    expect(dictation.start).toHaveBeenCalledTimes(1)
    // The browser's own ⌘D (bookmark this page) must not fire too.
    expect(event.defaultPrevented).toBe(true)
    await nextTick()
    expect(sendButton(wrapper).classes()).toContain('btn-send--recording')
    expect(wrapper.find('textarea').attributes('placeholder')).toMatch(/let go of ⌘D when you're done/)

    release('d')
    expect(dictation.stop).toHaveBeenCalledTimes(1)
    // Nothing left holding: a stray keyup afterwards is not a second stop.
    release('Meta')
    expect(dictation.stop).toHaveBeenCalledTimes(1)
  })

  it('one hold is one recording, however many repeats the key sends', () => {
    wrapper = mountWith()
    press({ key: 'd', metaKey: true })
    const repeat = press({ key: 'd', metaKey: true, repeat: true })
    press({ key: 'd', metaKey: true, repeat: true })
    expect(dictation.start).toHaveBeenCalledTimes(1)
    // Still swallowed, or the browser bookmarks the page mid-sentence.
    expect(repeat.defaultPrevented).toBe(true)
  })

  it('ends the hold when the modifier comes up, which is all macOS sends', () => {
    wrapper = mountWith()
    press({ key: 'd', metaKey: true })
    release('Meta')
    expect(dictation.stop).toHaveBeenCalledTimes(1)
  })

  it('ends the hold when the window goes away mid-sentence', () => {
    wrapper = mountWith()
    press({ key: 'd', metaKey: true })
    window.dispatchEvent(new Event('blur'))
    expect(dictation.stop).toHaveBeenCalledTimes(1)
  })

  it('drops the clip when the keys come up while the mic is still opening', async () => {
    wrapper = mountWith()
    let open!: () => void
    dictation.start.mockImplementation(
      () =>
        new Promise<void>(resolve => {
          open = resolve
        })
    )
    press({ key: 'd', metaKey: true })
    release('d')
    expect(dictation.cancel).toHaveBeenCalledTimes(1)
    expect(dictation.stop).not.toHaveBeenCalled()
    open()
  })

  it('leaves other D chords, and plain D, alone', () => {
    wrapper = mountWith()
    press({ key: 'd' })
    press({ key: 'd', metaKey: true, shiftKey: true })
    press({ key: 'd', ctrlKey: true })
    press({ key: 'k', metaKey: true })
    expect(dictation.start).not.toHaveBeenCalled()
  })

  it('uses Ctrl+D off Apple hardware', async () => {
    Object.defineProperty(navigator, 'platform', { value: 'Win32', configurable: true })
    wrapper = mountWith()
    expect(sendButton(wrapper).attributes('title')).toBe(
      'Hold to dictate, or hold Ctrl+D · click to send (Enter) · right-click to choose microphone'
    )
    press({ key: 'd', ctrlKey: true })
    expect(dictation.start).toHaveBeenCalledTimes(1)
    await nextTick()
    expect(wrapper.find('textarea').attributes('placeholder')).toMatch(/let go of Ctrl\+D when you're done/)
    release('Control')
    expect(dictation.stop).toHaveBeenCalledTimes(1)
  })

  it('yields to the preview when it has already taken the keystroke', () => {
    wrapper = mountWith()
    const event = new KeyboardEvent('keydown', { key: 'd', metaKey: true, bubbles: true, cancelable: true })
    event.preventDefault()
    document.body.dispatchEvent(event)
    expect(dictation.start).not.toHaveBeenCalled()
  })

  it('has no composer and ignores ⌘D on a read-only task thread', () => {
    wrapper = mountWith(instance({ id: 'task-1', kind: 'task', title: 'Contact page' }))
    expect(sendButton(wrapper).exists()).toBe(false)
    expect(wrapper.find('.fa-microphone').exists()).toBe(false)
    press({ key: 'd', metaKey: true })
    expect(dictation.start).not.toHaveBeenCalled()
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

  it('is a plain send arrow where the browser cannot record, with the picker shut', async () => {
    dictation.supported = false
    wrapper = mountWith()
    expect(wrapper.find('button.mic-caret').exists()).toBe(false)
    const button = sendButton(wrapper)
    expect(button.attributes('title')).toBe('Send (Enter)')
    expect(button.attributes('aria-expanded')).toBeUndefined()
    // No microphone glyph to promise a recording that cannot happen.
    expect(button.find('.fa-microphone').exists()).toBe(false)
    expect(button.find('.fa-arrow-up').exists()).toBe(true)
    await sendButton(wrapper).trigger('contextmenu')
    expect(wrapper.find('.mic-panel').exists()).toBe(false)
    await typePrompt(wrapper, 'Add a contact page')
    await pressFor(wrapper, 80)
    expect(wrapper.props('onPromptSubmit')).toHaveBeenCalledWith('Add a contact page')
    press({ key: 'd', metaKey: true })
    expect(dictation.start).not.toHaveBeenCalled()
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

  it('leaves the textbox editable around dictation: type, select, delete, dictate again', async () => {
    wrapper = mountWith()
    const textarea = wrapper.find('textarea')
    const el = textarea.element as HTMLTextAreaElement
    dictation.onTranscript!('Add a contact page')
    await nextTick()
    // The mic being the default takes nothing away from the keyboard.
    expect(el.disabled).toBe(false)
    expect(el.readOnly).toBe(false)
    expect(document.activeElement).toBe(el)
    // The caret sits after the words, so typing follows on from them.
    expect(el.selectionStart).toBe('Add a contact page'.length)
    expect(el.selectionEnd).toBe('Add a contact page'.length)

    // Highlight "contact" and press Backspace: an ordinary edit, and nothing
    // in the composer intercepts the key.
    el.setSelectionRange(6, 13)
    const backspace = new KeyboardEvent('keydown', { key: 'Backspace', bubbles: true, cancelable: true })
    el.dispatchEvent(backspace)
    expect(backspace.defaultPrevented).toBe(false)
    await textarea.setValue('Add a  page')
    // Words in the box: the record button wears its send arrow, and a hold
    // on it still records more.
    expect(sendButton(wrapper).classes()).toContain('btn-send--ready')
    expect(sendButton(wrapper).find('.fa-arrow-up').exists()).toBe(true)

    // A hold after the edit puts its words where the caret was left.
    el.setSelectionRange(6, 6)
    dictation.onTranscript!('pricing')
    await nextTick()
    expect(el.value).toBe('Add a pricing page')
    expect(wrapper.props('onPromptSubmit')).not.toHaveBeenCalled()
  })

  it('puts a transcript at the caret, or in place of a selection, while the box has focus', async () => {
    wrapper = mountWith()
    const textarea = wrapper.find('textarea')
    const el = textarea.element as HTMLTextAreaElement
    await typePrompt(wrapper, 'Add a page')
    el.focus()
    // Caret between "a " and "page": the words go in the middle, spaced.
    el.setSelectionRange(6, 6)
    dictation.onTranscript!('contact')
    await nextTick()
    expect(el.value).toBe('Add a contact page')
    expect(el.selectionStart).toBe('Add a contact'.length)
    expect(el.selectionEnd).toBe('Add a contact'.length)

    // A highlighted word is what the next transcript replaces.
    el.setSelectionRange(6, 13)
    dictation.onTranscript!('pricing')
    await nextTick()
    expect(el.value).toBe('Add a pricing page')
    expect(el.selectionStart).toBe('Add a pricing'.length)

    // With focus elsewhere the words go on the end, where they can be seen,
    // and the box takes focus back for the read-over.
    el.blur()
    el.setSelectionRange(0, 0)
    dictation.onTranscript!('with a map')
    await nextTick()
    expect(el.value).toBe('Add a pricing page with a map')
    expect(document.activeElement).toBe(el)
  })

  it('stops listening for ⌘D once unmounted', () => {
    wrapper = mountWith()
    wrapper.unmount()
    wrapper = null
    press({ key: 'd', metaKey: true })
    release('d')
    window.dispatchEvent(new Event('blur'))
    expect(dictation.start).not.toHaveBeenCalled()
    expect(dictation.stop).not.toHaveBeenCalled()
  })
})
