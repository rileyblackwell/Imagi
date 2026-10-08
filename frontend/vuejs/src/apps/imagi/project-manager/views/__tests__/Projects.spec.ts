import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises, RouterLinkStub } from '@vue/test-utils'
import { reactive, ref } from 'vue'

const push = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push, currentRoute: ref({ name: 'projects', params: {} }) }),
}))

const store = reactive({
  projects: [] as any[],
  loading: false,
  error: null as string | null,
  isAuthenticated: true,
  setAuthenticated: vi.fn(),
  fetchProjects: vi.fn().mockResolvedValue(undefined),
  createProject: vi.fn(),
  deleteProject: vi.fn(),
  clearError: vi.fn(),
})
vi.mock('@/apps/imagi/build/stores/projectStore', () => ({ useProjectStore: () => store }))
vi.mock('@/shared/stores/auth', () => ({ useAuthStore: () => ({ isAuthenticated: true }) }))
vi.mock('@/shared/composables/useNotification', () => ({ useNotification: () => ({ showNotification: vi.fn() }) }))
vi.mock('@/shared/stores/notificationStore', () => ({ useNotificationStore: () => ({ clear: vi.fn() }) }))
vi.mock('@/apps/imagi/build/composables/useConfirm', () => ({
  useConfirm: () => ({
    confirm: vi.fn(),
    isModalOpen: ref(false),
    modalOptions: ref({}),
    handleConfirm: vi.fn(),
    handleCancel: vi.fn(),
  }),
}))
vi.mock('@/apps/home/utils/pendingIdea', () => ({ takePendingIdea: () => null }))

import Projects from '../Projects.vue'

const mountPage = () =>
  mount(Projects, {
    global: {
      stubs: {
        DefaultLayout: { template: '<div class="layout"><slot /></div>' },
        ConfirmModal: true,
        RouterLink: RouterLinkStub,
      },
    },
  })

const DESCRIPTION = 'Neighbourhood sourdough bakery taking weekend pre-orders.'
const DETAILS = 'People can order bread for Saturday.'

/**
 * The create form is a four-step brief. What matters is that the steps and
 * the brief card follow what is typed, and that the button still sends the
 * same three fields under the same rules as before.
 */
describe('Projects (Brief)', () => {
  beforeEach(() => {
    store.projects = []
    store.createProject.mockReset()
    push.mockReset()
  })

  it('starts on the first step with nothing done and the button off', async () => {
    const wrapper = mountPage()
    await flushPromises()
    const steps = wrapper.findAll('.step')
    expect(steps).toHaveLength(4)
    expect(steps[0].classes()).toContain('is-current')
    expect(wrapper.findAll('.step.is-done')).toHaveLength(0)
    expect(wrapper.find('.meter__label').text()).toBe('At least 20 characters')
    expect(wrapper.find('.brief__submit').attributes('disabled')).toBeDefined()
  })

  it('asks about the app, and mentions the business tools as what comes after', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.find('h1').text()).toBe('Brief the agent on a new app')
    expect(wrapper.find('label[for="project-description"]').text()).toBe('What is your app?')
    expect(wrapper.find('label[for="project-details"]').text()).toBe('What does it do?')
    expect(wrapper.find('.brief__name').text()).toBe('Your app')
    expect(wrapper.find('.brief__facts').text()).toContain('Sell, Market and Operate')
  })

  it('moves along the rail and fills the brief card as the answers come in', async () => {
    const wrapper = mountPage()
    await wrapper.find('#project-name').setValue('Little Loaf')
    expect(wrapper.findAll('.step')[0].classes()).toContain('is-done')
    expect(wrapper.findAll('.step')[1].classes()).toContain('is-current')
    expect(wrapper.find('.brief__name').text()).toBe('Little Loaf')

    await wrapper.find('#project-description').setValue('Sourdough bakery')
    expect(wrapper.find('#project-description-meter').text()).toBe('4 more characters')
    expect(wrapper.find('.brief__submit').attributes('disabled')).toBeDefined()

    await wrapper.find('#project-description').setValue(DESCRIPTION)
    expect(wrapper.find('#project-description-meter').text()).toBe('Enough to start')
    expect(wrapper.find('.brief__desc').text()).toBe(DESCRIPTION)
    const facts = wrapper.findAll('.brief__facts dd').map((d) => d.text())
    expect(facts[0]).toBe('Shows up here as you describe it')
    expect(facts[1]).toBe('Imagi picks one')
    // What the app does is required too.
    expect(wrapper.findAll('.step')[2].classes()).toContain('is-current')
    expect(wrapper.find('.brief__submit').attributes('disabled')).toBeDefined()

    await wrapper.find('#project-details').setValue('People order')
    expect(wrapper.find('#project-details-meter').text()).toBe('8 more characters')
    await wrapper.find('#project-details').setValue(DETAILS)
    expect(wrapper.find('#project-details-meter').text()).toBe('Enough to start')
    expect(wrapper.findAll('.step')[2].classes()).toContain('is-done')
    expect(wrapper.find('.brief__submit').attributes('disabled')).toBeUndefined()
  })

  it('sends every answer, trimmed, and opens the new project', async () => {
    store.createProject.mockResolvedValue({ id: 9, name: 'Little Loaf' })
    const wrapper = mountPage()
    await wrapper.find('#project-name').setValue('  Little Loaf ')
    await wrapper.find('#project-description').setValue(DESCRIPTION)
    await wrapper.find('#project-details').setValue(` ${DETAILS} `)
    await wrapper.find('#project-design').setValue('Warm and minimal')
    // The button sits in the brief card, outside the form, and submits it by id.
    expect(wrapper.find('.brief__submit').attributes('form')).toBe('create-project')
    await wrapper.find('form#create-project').trigger('submit')
    await flushPromises()
    expect(store.createProject).toHaveBeenCalledWith({
      name: 'Little Loaf',
      description: DESCRIPTION,
      app_details: DETAILS,
      design_preferences: 'Warm and minimal',
    })
    expect(push).toHaveBeenCalledWith({ name: 'project-hub', params: { projectName: 'little-loaf' } })
  })

  it('won\'t create a project until it says what the app does', async () => {
    const wrapper = mountPage()
    await wrapper.find('#project-name').setValue('Little Loaf')
    await wrapper.find('#project-description').setValue(DESCRIPTION)
    await wrapper.find('form#create-project').trigger('submit')
    await flushPromises()
    expect(store.createProject).not.toHaveBeenCalled()
  })

  it('starts sentences about what the app does with one tap', async () => {
    const wrapper = mountPage()
    const starters = wrapper.findAll('.starters').at(1)!.findAll('button')
    await starters[0].trigger('click')
    expect((wrapper.find('#project-details').element as HTMLTextAreaElement).value).toBe('People can ')
    await wrapper.find('#project-details').setValue('People can book a table')
    await starters[1].trigger('click')
    expect((wrapper.find('#project-details').element as HTMLTextAreaElement).value)
      .toBe('People can book a table. It keeps track of ')
    expect(wrapper.findAll('.step')[2].classes()).toContain('is-done')
  })

  it('asks different questions once a kind of app is picked, and sends the kind', async () => {
    store.createProject.mockResolvedValue({ id: 9, name: 'Wick' })
    const wrapper = mountPage()
    const kind = (name: string) =>
      wrapper.findAll('.starters').at(0)!.findAll('button').find((b) => b.text() === name)!
    const starterLabels = () =>
      wrapper.findAll('.starters').at(1)!.findAll('button').map((b) => b.text())

    expect(starterLabels()[0]).toContain('People can')
    await kind('Online store').trigger('click')
    expect(kind('Online store').attributes('aria-pressed')).toBe('true')
    expect(starterLabels()[0]).toContain('It sells')
    expect(wrapper.find('#project-details-hint').text()).toContain('What do you sell')
    expect(wrapper.find('.brief__facts').text()).toContain('Online store')

    // Tapping it again goes back to the general questions.
    await kind('Online store').trigger('click')
    expect(starterLabels()[0]).toContain('People can')
    await kind('Online store').trigger('click')

    await wrapper.find('#project-name').setValue('Wick')
    await wrapper.find('#project-description').setValue('Handmade candles from my kitchen studio.')
    await wrapper.find('#project-details').setValue('It sells candles in three sizes.')
    await wrapper.find('form#create-project').trigger('submit')
    await flushPromises()
    expect(store.createProject.mock.calls[0][0].app_details)
      .toBe('Kind of app: Online store.\n\nIt sells candles in three sizes.')

  })

  it('builds a starter design from the presets and the notes', async () => {
    store.createProject.mockResolvedValue({ id: 9, name: 'Little Loaf' })
    const wrapper = mountPage()
    const chip = (name: string) =>
      wrapper.find('.design').findAll('button').find((b) => b.text().endsWith(name))!
    await chip('Warm and friendly').trigger('click')
    await chip('Forest').trigger('click')
    await chip('Classic').trigger('click')
    await chip('Light').trigger('click')
    await wrapper.find('#project-design').setValue('Use our green logo')
    expect(chip('Forest').attributes('aria-pressed')).toBe('true')
    expect(wrapper.findAll('.step')[3].classes()).toContain('is-done')
    expect(wrapper.findAll('.brief__facts dd')[1].text())
      .toBe('Warm and friendly, Forest colours, classic type, light mode. Use our green logo')

    // A second tap undoes a preset.
    await chip('Light').trigger('click')
    expect(chip('Light').attributes('aria-pressed')).toBe('false')

    await wrapper.find('#project-name').setValue('Little Loaf')
    await wrapper.find('#project-description').setValue(DESCRIPTION)
    await wrapper.find('#project-details').setValue(DETAILS)
    await wrapper.find('form#create-project').trigger('submit')
    await flushPromises()
    expect(store.createProject.mock.calls[0][0].design_preferences).toBe([
      'Style: Warm and friendly (soft rounded corners, inviting colour, a conversational tone).',
      'Colours: Forest palette, primary #1F4D3A, accent #8FB39A, light background #F5F1E6.',
      'Fonts: serif headings (such as Fraunces or Playfair Display) with a clean sans-serif for body text.',
      'Also: Use our green logo',
    ].join('\n'))
  })

  it('numbers the projects, most recently updated first', async () => {
    store.projects = [
      { id: 1, name: 'Older', updated_at: '2026-10-01T00:00:00Z' },
      { id: 2, name: 'Newer', updated_at: '2026-10-07T00:00:00Z' },
    ]
    const wrapper = mountPage()
    await flushPromises()
    const rows = wrapper.findAll('.project-list .row')
    expect(rows.map((r) => r.find('.row__name').text())).toEqual(['Newer', 'Older'])
    expect(rows.map((r) => r.find('.row__num').text())).toEqual(['01', '02'])
  })
})
