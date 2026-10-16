import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StarterDesign from '../molecules/brief/StarterDesign.vue'
import { emptyDesign, CUSTOM_SCHEME_ID, type StarterDesign as Design } from '../../utils/projectBrief'

/**
 * Set the look asks two things: a style (tiles that each picture the app) and
 * a colour scheme (a row of dots). Each tap picks, a second tap undoes, and
 * the large preview only appears once something is picked.
 */
describe('StarterDesign', () => {
  const mountWith = (value: Partial<Design> = {}) =>
    mount(StarterDesign, {
      props: { modelValue: { ...emptyDesign(), ...value }, appName: 'Ticker Insights', appDescription: 'A stock tracker. With charts.' },
    })
  const lastValue = (w: ReturnType<typeof mountWith>) => {
    const events = w.emitted('update:modelValue') as Design[][]
    return events[events.length - 1][0]
  }

  it('shows nine style tiles and nine colour choices, with no font or theme picker', () => {
    const w = mountWith()
    expect(w.findAll('.tile')).toHaveLength(9)
    expect(w.findAll('.swatch')).toHaveLength(9)
    expect(w.text()).not.toMatch(/Fonts|Light or dark/)
  })

  it('pictures the app in every tile, using the first sentence of what it is', () => {
    const w = mountWith()
    const tile = w.findAll('.tile')[0]
    expect(tile.find('.pv-title').text()).toBe('Ticker Insights')
    expect(tile.find('.pv-text').text()).toBe('A stock tracker.')
  })

  it('picks a style on tap and undoes it on a second tap', async () => {
    const w = mountWith()
    await w.findAll('.tile')[2].trigger('click')
    expect(lastValue(w).style).toBe('friendly')

    const picked = mountWith({ style: 'friendly' })
    expect(picked.findAll('.tile')[2].attributes('aria-checked')).toBe('true')
    await picked.findAll('.tile')[2].trigger('click')
    expect(lastValue(picked).style).toBeNull()
  })

  it('shows the large preview only once something is picked', () => {
    expect(mountWith().find('.preview').exists()).toBe(false)
    expect(mountWith().text()).toContain('Imagi chooses a look')
    expect(mountWith({ scheme: 'ocean' }).find('.preview').exists()).toBe(true)
  })

  it('leaves the large preview to the page when asked, and drops tile lines when compact', () => {
    const w = mount(StarterDesign, {
      props: { modelValue: { ...emptyDesign(), style: 'bold' }, hidePreview: true, compact: true },
    })
    expect(w.find('.preview').exists()).toBe(false)
    expect(w.text()).not.toContain('Imagi chooses a look')
    expect(w.find('.design').classes()).toContain('design--compact')
    const picked = mount(StarterDesign, { props: { modelValue: { ...emptyDesign(), scheme: 'forest' }, compact: true } })
    expect(picked.find('#design-colour-label').text()).toContain('Forest')
  })

  it('opens the brand colour picker for Your colour', async () => {
    const w = mountWith()
    expect(w.find('.brand').exists()).toBe(false)
    await w.findAll('.swatch')[8].trigger('click')
    expect(lastValue(w).scheme).toBe(CUSTOM_SCHEME_ID)
    expect(mountWith({ scheme: CUSTOM_SCHEME_ID }).find('.brand').exists()).toBe(true)
  })

  it('keeps the note box folded until asked for', async () => {
    const w = mountWith()
    expect(w.find('textarea').exists()).toBe(false)
    await w.find('.note-btn').trigger('click')
    expect(w.find('textarea').exists()).toBe(true)
    expect(mountWith({ notes: 'Earthy' }).find('textarea').exists()).toBe(true)
  })
})
