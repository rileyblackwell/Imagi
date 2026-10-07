import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatsSection from '../StatsSection.vue'

const stubs = { LineIcon: true, ProductShot: true }
const directives = { reveal: {} }

describe('StatsSection (Why Imagi)', () => {
  const wrapper = () => mount(StatsSection, { global: { stubs, directives } })

  it('spells out the two halves: tools to build the app and tools to run the business', () => {
    const titles = wrapper().findAll('.half__title').map((h) => h.text())
    expect(titles).toEqual(['Tools to build the app', 'Tools to run the business'])
  })

  it('names the run-half workspaces', () => {
    const run = wrapper().find('.half--run').text()
    for (const name of ['Sell', 'Market', 'Operate']) expect(run).toContain(name)
  })

  it('still shows the project hub screenshot', () => {
    expect(wrapper().findComponent({ name: 'ProductShot' }).exists()).toBe(true)
  })
})
