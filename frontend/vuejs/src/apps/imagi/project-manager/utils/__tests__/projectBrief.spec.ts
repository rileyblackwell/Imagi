import { describe, it, expect } from 'vitest'
import {
  composeDesignPreferences,
  customScheme,
  designIsSet,
  emptyDesign,
  inkOn,
  previewTextFor,
  schemeFor,
  CUSTOM_SCHEME_ID,
  SCHEMES,
  STYLES,
} from '../projectBrief'

describe('projectBrief', () => {
  it('sends nothing for the look when nothing was chosen', () => {
    expect(designIsSet(emptyDesign())).toBe(false)
    expect(composeDesignPreferences(emptyDesign())).toBe('')
  })

  it('sends notes on their own when no preset was picked', () => {
    const design = { ...emptyDesign(), notes: '  Earthy colours  ' }
    expect(designIsSet(design)).toBe(true)
    expect(composeDesignPreferences(design)).toBe('Earthy colours')
  })

  it('sends a style with the fonts that come with it', () => {
    const design = { ...emptyDesign(), style: 'friendly' }
    expect(composeDesignPreferences(design)).toBe(
      'Style: Friendly (soft rounded corners, pill buttons, gentle shadows, centred welcoming headings).\n' +
        'Fonts: a rounded sans-serif (such as Nunito or Quicksand).',
    )
  })

  it('sends a scheme with all its colours and whether it is light or dark', () => {
    expect(composeDesignPreferences({ ...emptyDesign(), scheme: 'ocean' })).toBe(
      'Colours: Ocean scheme, primary #1E4FD8, accent #38BDF8, background #F3F6FA, text #0F1B33.\nTheme: light mode.',
    )
    expect(composeDesignPreferences({ ...emptyDesign(), scheme: 'midnight' })).toContain('Theme: dark mode.')
  })

  it('builds the palette around a custom brand colour', () => {
    const design = { ...emptyDesign(), scheme: CUSTOM_SCHEME_ID, brandColor: '#ab12cd', notes: 'Logo is a fox' }
    expect(composeDesignPreferences(design)).toBe(
      'Colours: build the palette around the brand colour #AB12CD.\nAlso: Logo is a fox',
    )
    expect(schemeFor(design)?.primary).toBe('#AB12CD')
  })

  it('previews a brand colour as a light scheme', () => {
    const scheme = customScheme('#1E4FD8')
    expect(scheme.dark).toBeFalsy()
    expect(scheme.background).toMatch(/^#[0-9A-F]{6}$/)
    expect(scheme.text).toMatch(/^#[0-9A-F]{6}$/)
  })

  it('picks readable ink for each scheme’s buttons', () => {
    expect(inkOn('#111111')).toBe('#FFFFFF')
    expect(inkOn('#F2A541')).toBe('#111318')
  })

  it('offers nine styles and eight schemes, two of them dark', () => {
    expect(STYLES).toHaveLength(9)
    expect(SCHEMES).toHaveLength(8)
    expect(SCHEMES.filter((s) => s.dark).map((s) => s.id)).toEqual(['midnight', 'ember'])
  })

  it('previews the first sentence of what the app is, cut short', () => {
    expect(previewTextFor('  A stock tracker. With charts. ')).toBe('A stock tracker.')
    expect(previewTextFor('')).toBe('')
    expect(previewTextFor(undefined)).toBe('')
    const long = previewTextFor('a'.repeat(200))
    expect(long).toHaveLength(110)
    expect(long.endsWith('…')).toBe(true)
  })
})
