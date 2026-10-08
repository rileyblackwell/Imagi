import { describe, it, expect } from 'vitest'
import {
  composeAppDetails,
  composeDesignPreferences,
  summarizeDesign,
  designIsSet,
  emptyDesign,
  CUSTOM_PALETTE_ID,
} from '../projectBrief'

describe('projectBrief', () => {
  it('sends nothing for the look when nothing was chosen', () => {
    expect(designIsSet(emptyDesign())).toBe(false)
    expect(composeDesignPreferences(emptyDesign())).toBe('')
    expect(summarizeDesign(emptyDesign())).toBe('')
  })

  it('sends notes on their own when no preset was picked', () => {
    const design = { ...emptyDesign(), notes: '  Earthy colours  ' }
    expect(designIsSet(design)).toBe(true)
    expect(composeDesignPreferences(design)).toBe('Earthy colours')
  })

  it('builds the palette around a custom brand colour', () => {
    const design = { ...emptyDesign(), palette: CUSTOM_PALETTE_ID, brandColor: '#ab12cd', theme: 'dark' }
    expect(composeDesignPreferences(design)).toBe(
      'Colours: build the palette around the brand colour #AB12CD.\nTheme: dark mode.',
    )
    expect(summarizeDesign(design)).toBe('Your brand colour, dark mode')
  })

  it('leaves the light background out of a dark palette', () => {
    const design = { ...emptyDesign(), palette: 'ocean', theme: 'dark' }
    expect(composeDesignPreferences(design)).toBe(
      'Colours: Ocean palette, primary #1E3A8A, accent #38BDF8.\nTheme: dark mode.',
    )
  })

  it('leads what the app does with its kind, except for "something else"', () => {
    expect(composeAppDetails('booking', ' People can book. ')).toBe('Kind of app: Bookings.\n\nPeople can book.')
    expect(composeAppDetails('other', 'People can book.')).toBe('People can book.')
    expect(composeAppDetails(null, 'People can book.')).toBe('People can book.')
  })
})
