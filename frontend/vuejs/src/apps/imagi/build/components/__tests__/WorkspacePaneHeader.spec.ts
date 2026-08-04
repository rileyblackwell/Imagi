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

  it('omits the pane switches until it has somewhere to go', () => {
    expect(mountWith({}).find('button.pane-switch').exists()).toBe(false)
  })

  it('keeps the identity in its own centred column, whatever sits beside it', () => {
    const wrapper = mountWith({
      status: 'Ready when you are',
      switches: [{ id: 'manager', icon: 'fas fa-layer-group', label: 'Subagents' }],
    })
    expect(wrapper.find('.pane-identity .pane-title').exists()).toBe(true)
    expect(wrapper.find('.pane-identity .pane-status-line').exists()).toBe(true)
  })

  it('mirrors the whole switch cluster on the empty side, so the name sits at true centre', () => {
    // The ghost exists only to occupy the switches' width on the left. Every
    // switch has to be mirrored (widths must match), and the mirror stays out
    // of the accessibility tree and out of the click path.
    const wrapper = mountWith({
      switches: [
        { id: 'manager', icon: 'fas fa-layer-group', label: 'Subagents', count: 3 },
        { id: 'preview', icon: 'fas fa-globe', label: 'Preview', mobileOnly: true },
      ],
    })
    const gutter = wrapper.find('.pane-header-gutter')

    expect(gutter.attributes('aria-hidden')).toBe('true')
    expect(gutter.findAll('.pane-switch-label').map(l => l.text())).toEqual([
      'Subagents',
      'Preview',
    ])
    expect(gutter.find('.pane-switch-count').text()).toBe('3')
    expect(gutter.find('button').exists()).toBe(false)
    // The mirror has to hide on exactly the widths the real one does, or the
    // gutter reserves room for a button that isn't there.
    expect(gutter.findAll('.pane-switch')[1].classes()).toContain('pane-switch--mobile')
  })

  it('carries no ghost when there is no switch to mirror', () => {
    expect(mountWith({}).find('.pane-header-gutter .pane-switch').exists()).toBe(false)
  })

  it('names its destination on the switch and emits that destination on click', async () => {
    const wrapper = mountWith({
      switches: [{ id: 'manager', icon: 'fas fa-layer-group', label: 'Subagents' }],
    })
    expect(wrapper.find('button.pane-switch .pane-switch-label').text()).toBe('Subagents')
    await wrapper.find('button.pane-switch').trigger('click')
    expect(wrapper.emitted('switch')).toEqual([['manager']])
  })

  it('offers every destination it is given, and says which one was pressed', async () => {
    // The main thread is the workspace's junction — two ways out of it — so the
    // masthead has to tell them apart rather than emitting a bare "switch".
    const wrapper = mountWith({
      switches: [
        { id: 'manager', icon: 'fas fa-layer-group', label: 'Subagents' },
        { id: 'preview', icon: 'fas fa-globe', label: 'Preview' },
      ],
    })
    const buttons = wrapper.findAll('button.pane-switch')

    expect(buttons).toHaveLength(2)
    await buttons[1].trigger('click')
    expect(wrapper.emitted('switch')).toEqual([['preview']])
  })

  it('points a back switch the other way', () => {
    const wrapper = mountWith({
      switches: [{ id: 'chat', icon: 'fas fa-comments', label: 'Main agent', direction: 'back' }],
    })
    const button = wrapper.find('button.pane-switch')

    expect(button.find('.fa-chevron-left').exists()).toBe(true)
    expect(button.find('.fa-chevron-right').exists()).toBe(false)
  })

  it('badges the switch with what is waiting on the other side', () => {
    expect(
      mountWith({
        switches: [{ id: 'manager', icon: 'fas fa-layer-group', label: 'Subagents', count: 3 }],
      }).find('button.pane-switch .pane-switch-count').text()
    ).toBe('3')
  })

  it('carries no badge when the other pane is empty', () => {
    // 0 is "nothing over there", not a number worth drawing.
    expect(
      mountWith({
        switches: [{ id: 'manager', icon: 'fas fa-layer-group', label: 'Subagents', count: 0 }],
      }).find('button.pane-switch .pane-switch-count').exists()
    ).toBe(false)
  })

  it('marks a destination that is only offered on phones', () => {
    // The preview sits beside the panes on desktop, so a button to "go to" it
    // there would be a button to go nowhere. The marker class is what the
    // stylesheet keys the md-and-up hide off.
    const wrapper = mountWith({
      switches: [
        { id: 'manager', icon: 'fas fa-layer-group', label: 'Subagents' },
        { id: 'preview', icon: 'fas fa-globe', label: 'Preview', mobileOnly: true },
      ],
    })
    const buttons = wrapper.findAll('button.pane-switch')

    expect(buttons[0].classes()).not.toContain('pane-switch--mobile')
    expect(buttons[1].classes()).toContain('pane-switch--mobile')
  })
})
