import { describe, it, expect } from 'vitest'
import { mount, RouterLinkStub } from '@vue/test-utils'
import ProjectCard from '../molecules/cards/ProjectCard.vue'
import type { Project } from '@/apps/imagi/build/types/components'

/**
 * A row in the projects list carries two actions in one strip: open the
 * project, and delete it. The row is clickable end to end, which is what makes
 * the arrangement worth pinning down — the delete button must stay outside the
 * link that covers the row, or pressing it would open the project it just asked
 * to remove (and nest a <button> inside an <a> while doing it).
 */
describe('ProjectCard', () => {
  const project = {
    id: '7',
    name: 'Ticker Insights',
    description: 'A stock tracker with AI-written summaries',
  } as unknown as Project

  const mountWith = (props: object = {}) =>
    mount(ProjectCard, {
      props: { project, ...props },
      global: { stubs: { RouterLink: RouterLinkStub } },
    })

  it('names the project and its business', () => {
    const wrapper = mountWith()
    expect(wrapper.find('.row__name').text()).toBe('Ticker Insights')
    expect(wrapper.find('.row__desc').text()).toBe('A stock tracker with AI-written summaries')
  })

  it('drops the description line rather than leaving an empty one', () => {
    expect(mountWith({ project: { id: '7', name: 'Untitled' } }).find('.row__desc').exists()).toBe(false)
  })

  it('opens the project hub, keyed by slug', () => {
    expect(mountWith().findComponent(RouterLinkStub).props('to')).toEqual({
      name: 'project-hub',
      params: { projectName: 'ticker-insights' },
    })
  })

  it('asks to delete the project it is showing', async () => {
    const wrapper = mountWith()
    await wrapper.find('.row__delete').trigger('click')
    expect(wrapper.emitted('delete')).toEqual([[project]])
  })

  it('keeps the delete button out of the link that covers the row', () => {
    const wrapper = mountWith()
    expect(wrapper.find('.row__link .row__delete').exists()).toBe(false)
    expect(wrapper.find('.row__delete').attributes('aria-label')).toBe('Delete Ticker Insights')
  })

  it('renders nothing at all without a project', () => {
    expect(mount(ProjectCard, { global: { stubs: { RouterLink: RouterLinkStub } } }).find('.row').exists()).toBe(false)
  })
})
