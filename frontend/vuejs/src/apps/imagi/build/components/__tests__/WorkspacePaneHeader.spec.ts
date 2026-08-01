import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import WorkspacePaneHeader from '../molecules/sidebar/WorkspacePaneHeader.vue'

/**
 * The masthead's whole job is to say where a pane stands in the same three
 * tokens the crew cards use. These lock that contract down: the dot and the
 * reading must always agree, and the reading must be able to say nothing.
 */
describe('WorkspacePaneHeader', () => {
  const mountWith = (props: object) =>
    mount(WorkspacePaneHeader, { props: { title: 'Main agent', ...props } })

  it('names the pane', () => {
    expect(mountWith({}).find('.pane-title').text()).toBe('Main agent')
  })

  it('rests idle when no state is given', () => {
    const wrapper = mountWith({ status: 'Ready when you are' })
    expect(wrapper.find('.pane-dot').classes()).toContain('pane-dot--idle')
    expect(wrapper.find('.pane-status').classes()).toContain('pane-status--idle')
  })

  it.each(['working', 'waiting', 'idle'] as const)(
    'marks the dot and the reading with the same state (%s)',
    state => {
      const wrapper = mountWith({ status: 'Something', state })
      expect(wrapper.find('.pane-dot').classes()).toContain(`pane-dot--${state}`)
      expect(wrapper.find('.pane-status').classes()).toContain(`pane-status--${state}`)
    }
  )

  it('drops the status line entirely when there is nothing to report', () => {
    const wrapper = mountWith({})
    expect(wrapper.find('.pane-status-line').exists()).toBe(false)
    expect(wrapper.find('.pane-dot').exists()).toBe(false)
  })

  it('omits the pane switch until it has somewhere to go', () => {
    expect(mountWith({}).find('.pane-switch').exists()).toBe(false)
  })

  it('names its destination on the switch and emits on click', async () => {
    const wrapper = mountWith({ switchLabel: 'Subagents', switchIcon: 'fas fa-layer-group' })
    expect(wrapper.find('.pane-switch-label').text()).toBe('Subagents')
    await wrapper.find('.pane-switch').trigger('click')
    expect(wrapper.emitted('switch')).toHaveLength(1)
  })

  it('badges the switch with what is waiting on the other side', () => {
    expect(mountWith({ switchLabel: 'Subagents', switchCount: 3 }).find('.pane-switch-count').text())
      .toBe('3')
  })

  it('carries no badge when the other pane is empty', () => {
    // 0 is "nothing over there", not a number worth drawing.
    expect(mountWith({ switchLabel: 'Subagents', switchCount: 0 }).find('.pane-switch-count').exists())
      .toBe(false)
  })
})
