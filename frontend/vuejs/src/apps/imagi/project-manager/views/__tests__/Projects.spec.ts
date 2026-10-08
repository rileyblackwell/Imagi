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

/**
 * The create form is a three-step brief. What matters is that the steps and
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

  it('moves along the rail and fills the brief card as the answers come in', async () => {
    const wrapper = mountPage()
    await wrapper.find('#project-name').setValue('Little Loaf')
    expect(wrapper.findAll('.step')[0].classes()).toContain('is-done')
    expect(wrapper.findAll('.step')[1].classes()).toContain('is-current')
    expect(wrapper.find('.brief__name').text()).toBe('Little Loaf')

    await wrapper.find('#project-description').setValue('Sourdough bakery')
    expect(wrapper.find('.meter__label').text()).toBe('4 more characters')
    expect(wrapper.find('.brief__submit').attributes('disabled')).toBeDefined()

    await wrapper.find('#project-description').setValue(DESCRIPTION)
    expect(wrapper.find('.meter__label').text()).toBe('Enough to start')
    expect(wrapper.find('.brief__desc').text()).toBe(DESCRIPTION)
    const facts = wrapper.findAll('.brief__facts dd').map((d) => d.text())
    expect(facts[0]).toBe('Imagi works it out from the description')
    expect(facts[1]).toBe('Imagi picks one')
    expect(wrapper.find('.brief__submit').attributes('disabled')).toBeUndefined()
  })

  it('sends every answer, trimmed, and opens the new project', async () => {
    store.createProject.mockResolvedValue({ id: 9, name: 'Little Loaf' })
    const wrapper = mountPage()
    await wrapper.find('#project-name').setValue('  Little Loaf ')
    await wrapper.find('#project-description').setValue(DESCRIPTION)
    await wrapper.find('#project-details').setValue(' People can order bread for Saturday. ')
    await wrapper.find('#project-design').setValue('Warm and minimal')
    // The button sits in the brief card, outside the form, and submits it by id.
    expect(wrapper.find('.brief__submit').attributes('form')).toBe('create-project')
    await wrapper.find('form#create-project').trigger('submit')
    await flushPromises()
    expect(store.createProject).toHaveBeenCalledWith({
      name: 'Little Loaf',
      description: DESCRIPTION,
      app_details: 'People can order bread for Saturday.',
      design_preferences: 'Warm and minimal',
    })
    expect(push).toHaveBeenCalledWith({ name: 'project-hub', params: { projectName: 'little-loaf' } })
  })

  it('starts sentences about how the app works with one tap', async () => {
    const wrapper = mountPage()
    const starters = wrapper.findAll('.starters').at(0)!.findAll('button')
    await starters[0].trigger('click')
    expect((wrapper.find('#project-details').element as HTMLTextAreaElement).value).toBe('People can ')
    await wrapper.find('#project-details').setValue('People can book a table')
    await starters[1].trigger('click')
    expect((wrapper.find('#project-details').element as HTMLTextAreaElement).value)
      .toBe('People can book a table. It keeps track of ')
    expect(wrapper.findAll('.step')[2].classes()).toContain('is-done')
  })

  it('toggles moods into the design direction and back out', async () => {
    const wrapper = mountPage()
    const design = () => (wrapper.find('#project-design').element as HTMLTextAreaElement).value
    const mood = (name: string) =>
      wrapper.findAll('.starters').at(1)!.findAll('button').find((b) => b.text() === name)!
    await wrapper.find('#project-design').setValue('Earthy colours')
    await mood('Fun').trigger('click')
    expect(design()).toBe('Earthy colours, fun')
    expect(mood('Fun').attributes('aria-pressed')).toBe('true')
    await mood('Calm').trigger('click')
    expect(design()).toBe('Earthy colours, fun, calm')
    await mood('Fun').trigger('click')
    expect(design()).toBe('Earthy colours, calm')
    expect(mood('Fun').attributes('aria-pressed')).toBe('false')
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
