import { describe, it, expect } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import ToolCategoryCard from '../organisms/hub/ToolCategoryCard.vue'
import { businessTools } from '../../utils/businessTools'

/**
 * The hub's four modules. Three of them are always a link; Build is the one
 * that can be busy, because the agent is still writing the app the moment the
 * project is created — and while it is, the module must not be openable.
 */
describe('ToolCategoryCard', () => {
  const tool = (id: string) => businessTools.find(t => t.id === id)!

  const mountWith = (props: object) =>
    mount(ToolCategoryCard, {
      props: { projectSlug: 'ticker-insights', ...props },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })

  it('names the module, says what it is for, and lists what it holds', () => {
    const wrapper = mountWith({ tool: tool('sell') })
    expect(wrapper.find('.sl-card__title').text()).toBe('Sell')
    expect(wrapper.find('.sl-card__body').text()).toBe('Turn visitors into customers')
    expect(wrapper.findAll('.module__features li')).toHaveLength(3)
  })

  it('draws the same mark the home page uses for the same module', () => {
    // Both read from LineIcon's set — the hub's marks are not a second
    // vocabulary that can drift away from the one a visitor arrives with.
    expect(mountWith({ tool: tool('operate') }).find('svg.line-icon').exists()).toBe(true)
  })

  it('opens an available tool at its own workspace route', () => {
    expect(mountWith({ tool: tool('market') }).findComponent(RouterLinkStub).props('to')).toEqual({
      name: 'marketing-overview',
      params: { projectName: 'ticker-insights' },
    })
  })

  it('locks Build while the first build is still running', () => {
    const wrapper = mountWith({ tool: tool('build'), buildStatus: 'generating' })

    expect(wrapper.findComponent(RouterLinkStub).exists()).toBe(false)
    expect(wrapper.attributes('aria-disabled')).toBe('true')
    expect(wrapper.classes()).toContain('module--building')
    expect(wrapper.find('.module__cta--waiting').text()).toBe('Building')
  })

  it.each(['pending', 'completed', 'failed', null, undefined] as const)(
    'leaves Build open at every other status (%s)',
    buildStatus => {
      const wrapper = mountWith({ tool: tool('build'), buildStatus })
      expect(wrapper.findComponent(RouterLinkStub).props('to')).toEqual({
        name: 'builder-workspace',
        params: { projectName: 'ticker-insights' },
      })
      expect(wrapper.find('.module--building').exists()).toBe(false)
    }
  )

  it('never locks a module other than Build', () => {
    // Only the app is half-written during a build; the business tools around it
    // are perfectly usable.
    const wrapper = mountWith({ tool: tool('operate'), buildStatus: 'generating' })
    expect(wrapper.findComponent(RouterLinkStub).exists()).toBe(true)
    expect(wrapper.classes()).not.toContain('module--building')
  })

  describe('as the Build half of the hub', () => {
    it('shows the workspace sketch, the capabilities and the one lit button', () => {
      const wrapper = mountWith({ tool: tool('build'), layout: 'feature' })

      expect(wrapper.classes()).toContain('module--feature')
      expect(wrapper.find('.module__window').exists()).toBe(true)
      expect(wrapper.findAll('.module__chips li').map(li => li.text())).toEqual([
        'AI agents',
        'Live workspace',
        'Instant preview',
      ])
      expect(wrapper.find('.module__open').text()).toBe('Open workspace')
      expect(wrapper.findComponent(RouterLinkStub).props('to')).toEqual({
        name: 'builder-workspace',
        params: { projectName: 'ticker-insights' },
      })
    })

    it('swaps the button for the building state while the first build runs', () => {
      const wrapper = mountWith({ tool: tool('build'), layout: 'feature', buildStatus: 'generating' })

      expect(wrapper.findComponent(RouterLinkStub).exists()).toBe(false)
      expect(wrapper.attributes('aria-disabled')).toBe('true')
      expect(wrapper.find('.module__open').exists()).toBe(false)
      expect(wrapper.find('.module__track').exists()).toBe(true)
      expect(wrapper.find('.module__cta--waiting').text()).toBe('Building')
    })
  })

  it('draws a Run tool as a row by default', () => {
    const wrapper = mountWith({ tool: tool('sell') })
    expect(wrapper.classes()).toContain('module--row')
    expect(wrapper.find('.module__window').exists()).toBe(false)
  })
})
