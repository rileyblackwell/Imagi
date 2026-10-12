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
// The plan as the usage endpoint reports it; null until loaded. The limit
// check mirrors the real store's canCreateProject.
const usage = reactive({
  plan: null as null | { id: string; name: string; maxActiveProjects: number | null; earlyAccess: boolean },
  fetchUsage: vi.fn().mockResolvedValue(undefined),
  canCreateProject(active: number) {
    const limit = usage.plan?.maxActiveProjects ?? null
    return limit === null || active < limit
  },
})
vi.mock('@/shared/stores/usage', () => ({ useUsageStore: () => usage }))
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
 * The create form is a four-step brief. What matters is that the steps
 * follow what is typed, and that the Create app button under them still sends
 * the same fields under the same rules as before.
 */
describe('Projects (Brief)', () => {
  beforeEach(() => {
    store.projects = []
    store.createProject.mockReset()
    push.mockReset()
    usage.plan = null
  })

  it('starts on the first step with nothing done and the button off', async () => {
    const wrapper = mountPage()
    await flushPromises()
    const steps = wrapper.findAll('.step')
    expect(steps).toHaveLength(4)
    expect(steps[0].classes()).toContain('is-current')
    expect(wrapper.findAll('.step.is-done')).toHaveLength(0)
    expect(wrapper.find('.meter__label').text()).toBe('At least 20 characters')
    expect(wrapper.find('.create-submit').attributes('disabled')).toBeDefined()
  })

  it('asks about the app, with one Create app button and no summary card', async () => {
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.find('h1').text()).toBe('Brief the agent on a new app')
    expect(wrapper.find('label[for="project-description"]').text()).toBe('What is your app?')
    expect(wrapper.find('label[for="project-details"]').text()).toBe('How does it work?')
    expect(wrapper.find('.create-submit').text()).toBe('Create app')
    expect(wrapper.text()).not.toContain('What the agent receives')
  })

  it('moves along the rail as the answers come in', async () => {
    const wrapper = mountPage()
    await wrapper.find('#project-name').setValue('Little Loaf')
    expect(wrapper.findAll('.step')[0].classes()).toContain('is-done')
    expect(wrapper.findAll('.step')[1].classes()).toContain('is-current')

    await wrapper.find('#project-description').setValue('Sourdough bakery')
    expect(wrapper.find('#project-description-meter').text()).toBe('4 more characters')
    expect(wrapper.find('.create-submit').attributes('disabled')).toBeDefined()

    await wrapper.find('#project-description').setValue(DESCRIPTION)
    expect(wrapper.find('#project-description-meter').text()).toBe('Enough to start')
    // What the app does is required too.
    expect(wrapper.findAll('.step')[2].classes()).toContain('is-current')
    expect(wrapper.find('.create-submit').attributes('disabled')).toBeDefined()

    await wrapper.find('#project-details').setValue('People order')
    expect(wrapper.find('#project-details-meter').text()).toBe('8 more characters')
    await wrapper.find('#project-details').setValue(DETAILS)
    expect(wrapper.find('#project-details-meter').text()).toBe('Enough to start')
    expect(wrapper.findAll('.step')[2].classes()).toContain('is-done')
    expect(wrapper.find('.create-submit').attributes('disabled')).toBeUndefined()
  })

  it('sends every answer, trimmed, and opens the new project', async () => {
    store.createProject.mockResolvedValue({ id: 9, name: 'Little Loaf' })
    const wrapper = mountPage()
    await wrapper.find('#project-name').setValue('  Little Loaf ')
    await wrapper.find('#project-description').setValue(DESCRIPTION)
    await wrapper.find('#project-details').setValue(` ${DETAILS} `)
    await wrapper.find('#project-design').setValue('Warm and minimal')
    // The button sits inside the form, under the last step.
    expect(wrapper.find('form#create-project button[type="submit"].create-submit').exists()).toBe(true)
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

  it('won\'t create a project until it says how the app works', async () => {
    const wrapper = mountPage()
    await wrapper.find('#project-name').setValue('Little Loaf')
    await wrapper.find('#project-description').setValue(DESCRIPTION)
    await wrapper.find('form#create-project').trigger('submit')
    await flushPromises()
    expect(store.createProject).not.toHaveBeenCalled()
  })

  it('previews the starter design with the app\'s own name and description', async () => {
    const wrapper = mountPage()
    expect(wrapper.find('.preview__title').text()).toBe('Your app’s name')
    await wrapper.find('#project-name').setValue('Little Loaf')
    await wrapper.find('#project-description').setValue('A pre-order site for my bakery. Customers pick loaves for Saturday.')
    expect(wrapper.find('.preview__brand').text()).toBe('Little Loaf')
    expect(wrapper.find('.preview__title').text()).toBe('Little Loaf')
    expect(wrapper.find('.preview__text').text()).toBe('A pre-order site for my bakery.')
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

  it('offers an upgrade instead of a create once Free holds its one project', async () => {
    usage.plan = { id: 'free', name: 'Free', maxActiveProjects: 1, earlyAccess: false }
    store.projects = [{ id: 1, name: 'Little Loaf', updated_at: '2026-10-01T00:00:00Z' }]
    const wrapper = mountPage()
    await flushPromises()
    expect(wrapper.find('button.create-submit').exists()).toBe(false)
    const link = wrapper.findComponent(RouterLinkStub)
    expect(link.props('to')).toBe('/payments/pricing')
    expect(link.text()).toBe('See plans')
    expect(wrapper.find('.create-note--limit').text()).toBe(
      'Your Free plan includes one project. Pro and Max include unlimited projects.',
    )
  })

  it('lets Free create its first project, and paid plans create any number', async () => {
    usage.plan = { id: 'free', name: 'Free', maxActiveProjects: 1, earlyAccess: false }
    let wrapper = mountPage()
    await flushPromises()
    expect(wrapper.find('button.create-submit').exists()).toBe(true)

    usage.plan = { id: 'pro', name: 'Pro', maxActiveProjects: null, earlyAccess: false }
    store.projects = [1, 2, 3].map((id) => ({ id, name: `App ${id}`, updated_at: '2026-10-01T00:00:00Z' }))
    wrapper = mountPage()
    await flushPromises()
    expect(wrapper.find('button.create-submit').exists()).toBe(true)
    expect(wrapper.find('.create-note--limit').exists()).toBe(false)
  })
})
