import { describe, it, expect, vi } from 'vitest'
import { ref } from 'vue'
import { mount, flushPromises, RouterLinkStub } from '@vue/test-utils'

vi.mock('@/apps/imagi/shared', () => ({
  useProjectFromSlug: () => ({
    project: ref({ id: 7, name: 'Ticker Insights', description: 'A stock tracker.' }),
    isLoading: ref(false),
  }),
}))

vi.mock('@/apps/imagi/build/services/projectService', () => ({
  ProjectService: { getProjectStatus: vi.fn().mockResolvedValue({ generation_status: 'completed' }) },
}))

vi.mock('@/shared/layouts', () => ({
  DefaultLayout: { template: '<div><slot /></div>' },
}))

import ProjectHub from '../ProjectHub.vue'

/**
 * The hub lays the modules out in the product's two halves: Build the app,
 * and the three tools that run it as a business.
 */
describe('ProjectHub', () => {
  it('puts Build in its own half and Sell, Market and Operate under Run', async () => {
    const wrapper = mount(ProjectHub, {
      props: { projectName: 'ticker-insights' },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })
    await flushPromises()

    const [build, run] = wrapper.findAll('.hub-half')
    expect(build.find('.hub-half__label').text()).toContain('Build')
    expect(build.find('.hub-half__label').text()).toContain('the app')
    expect(build.findAll('.module--feature .sl-card__title').map(t => t.text())).toEqual(['Build'])

    expect(run.find('.hub-half__label').text()).toContain('Run')
    expect(run.find('.hub-half__label').text()).toContain('it as a business')
    expect(run.findAll('.module--row .sl-card__title').map(t => t.text())).toEqual([
      'Sell',
      'Market',
      'Operate',
    ])
    wrapper.unmount()
  })
})
