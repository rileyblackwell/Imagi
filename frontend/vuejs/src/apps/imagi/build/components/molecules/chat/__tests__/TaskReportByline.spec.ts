import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TaskReportByline from '../TaskReportByline.vue'
import type { TaskReport } from '@/apps/imagi/build/types/services'

function makeReport(overrides: Partial<TaskReport> = {}): TaskReport {
  return {
    conversationId: 42,
    kind: 'done',
    title: 'Redesign the home page',
    goal: 'Giving your home page a clearer opening.',
    ...overrides,
  }
}

const mountByline = (report: TaskReport) =>
  mount(TaskReportByline, { props: { report } })

const stateOf = (wrapper: ReturnType<typeof mountByline>) =>
  wrapper.find('.report-byline__state').text()

describe('TaskReportByline', () => {
  it('says work that applied itself is already in the app', () => {
    // The whole point of a solo subagent: it merges its own work, so this is
    // news to read, not a decision to make.
    expect(stateOf(mountByline(makeReport()))).toBe(
      'Subagent complete — added to your app'
    )
  })

  it('separates work that is still waiting on the user', () => {
    expect(stateOf(mountByline(makeReport({ kind: 'ready' })))).toBe(
      'Subagent complete — waiting on you'
    )
    expect(stateOf(mountByline(makeReport({ kind: 'question' })))).toBe(
      'Subagent needs an answer'
    )
    expect(stateOf(mountByline(makeReport({ kind: 'error' })))).toBe(
      'Subagent stopped before finishing'
    )
  })

  it('reads the state off the report, not off the subagent today', () => {
    // A line in a transcript has to keep saying what was true when it was
    // written — a week later, and after the subagent has moved on.
    const wrapper = mountByline(makeReport({ kind: 'question' }))
    expect(wrapper.classes()).toContain('report-byline--asking')
  })

  it('names the job so the summary underneath has something to be about', () => {
    const wrapper = mountByline(makeReport())
    expect(wrapper.find('.report-byline__job').text()).toBe(
      'Giving your home page a clearer opening.'
    )
  })

  it('falls back to the task name when the dispatch wrote no goal', () => {
    const wrapper = mountByline(makeReport({ goal: '' }))
    expect(wrapper.find('.report-byline__job').text()).toBe('Redesign the home page')
  })

  it('opens the subagent that wrote it', async () => {
    const wrapper = mountByline(makeReport())
    await wrapper.trigger('click')
    expect(wrapper.emitted('open')).toHaveLength(1)
  })
})
