/**
 * projectBrief.ts — the starter design behind the projects page's create form.
 *
 * The form's last step, "Set the look", is the app's first design system:
 * style, colours, fonts, theme and notes. It is sent as plain text in
 * `design_preferences`, written so the build agent can act on it directly
 * (named colours with hex values, font suggestions), with no schema change on
 * the backend.
 */

export interface DesignStyle {
  id: string
  label: string
  /** What the style means, for the agent. */
  brief: string
}

export const STYLES: readonly DesignStyle[] = [
  { id: 'minimal', label: 'Clean and minimal', brief: 'lots of white space, restrained colour, simple shapes' },
  { id: 'friendly', label: 'Warm and friendly', brief: 'soft rounded corners, inviting colour, a conversational tone' },
  { id: 'bold', label: 'Bold and energetic', brief: 'big type, strong contrast, confident colour' },
  { id: 'premium', label: 'Elegant and premium', brief: 'refined type, generous spacing, understated detail' },
  { id: 'playful', label: 'Playful', brief: 'bright colour, rounded shapes, a little fun in the details' },
  { id: 'professional', label: 'Professional', brief: 'clear structure, calm colour, businesslike and trustworthy' },
]

export interface Palette {
  id: string
  label: string
  primary: string
  accent: string
  background: string
}

export const PALETTES: readonly Palette[] = [
  { id: 'ocean', label: 'Ocean', primary: '#1E3A8A', accent: '#38BDF8', background: '#F1F5F9' },
  { id: 'forest', label: 'Forest', primary: '#1F4D3A', accent: '#8FB39A', background: '#F5F1E6' },
  { id: 'sunset', label: 'Sunset', primary: '#E8553E', accent: '#F5A524', background: '#FFF7ED' },
  { id: 'berry', label: 'Berry', primary: '#9D174D', accent: '#C084FC', background: '#FDF2F8' },
  { id: 'earth', label: 'Earth', primary: '#9A4A2C', accent: '#C9A66B', background: '#F4EDE4' },
  { id: 'mono', label: 'Black and white', primary: '#111111', accent: '#6B7280', background: '#F5F5F5' },
]

/** The palette option that is the founder's own brand colour. */
export const CUSTOM_PALETTE_ID = 'custom'

export interface FontPairing {
  id: string
  label: string
  /** CSS stack for the sample "Aa" on the picker. */
  sample: string
  brief: string
}

export const FONTS: readonly FontPairing[] = [
  { id: 'modern', label: 'Modern', sample: "'Hanken Grotesk', ui-sans-serif, system-ui, sans-serif", brief: 'a modern sans-serif throughout (such as Inter or Manrope)' },
  { id: 'classic', label: 'Classic', sample: "'Fraunces', Georgia, serif", brief: 'serif headings (such as Fraunces or Playfair Display) with a clean sans-serif for body text' },
  { id: 'display', label: 'Bold', sample: "'Bricolage Grotesque', ui-sans-serif, system-ui, sans-serif", brief: 'a heavy display sans-serif for headings (such as Bricolage Grotesque or Archivo Black) with a plain sans-serif for body text' },
  { id: 'rounded', label: 'Rounded', sample: "ui-rounded, 'SF Pro Rounded', 'Nunito', system-ui, sans-serif", brief: 'a rounded sans-serif (such as Nunito or Quicksand)' },
]

export const THEMES = [
  { id: 'light', label: 'Light' },
  { id: 'dark', label: 'Dark' },
] as const

export interface StarterDesign {
  style: string | null
  palette: string | null
  /** Hex brand colour, used when `palette` is CUSTOM_PALETTE_ID. */
  brandColor: string
  font: string | null
  theme: string | null
  notes: string
}

export const emptyDesign = (): StarterDesign => ({
  style: null,
  palette: null,
  brandColor: '#4F46E5',
  font: null,
  theme: null,
  notes: '',
})

export const designIsSet = (d: StarterDesign): boolean =>
  Boolean(d.style || d.palette || d.font || d.theme || d.notes.trim())

/**
 * The starter design as the text the build reads, one line per answer. Empty
 * when nothing was chosen, so the build picks a look itself.
 */
export function composeDesignPreferences(d: StarterDesign): string {
  const lines: string[] = []
  const style = STYLES.find(s => s.id === d.style)
  if (style) lines.push(`Style: ${style.label} (${style.brief}).`)

  if (d.palette === CUSTOM_PALETTE_ID) {
    lines.push(`Colours: build the palette around the brand colour ${d.brandColor.toUpperCase()}.`)
  } else {
    const palette = PALETTES.find(p => p.id === d.palette)
    if (palette) {
      // A dark theme makes its own background, so the light one is left out.
      const background = d.theme === 'dark' ? '' : `, light background ${palette.background}`
      lines.push(`Colours: ${palette.label} palette, primary ${palette.primary}, accent ${palette.accent}${background}.`)
    }
  }

  const font = FONTS.find(f => f.id === d.font)
  if (font) lines.push(`Fonts: ${font.brief}.`)

  const theme = THEMES.find(t => t.id === d.theme)
  if (theme) lines.push(`Theme: ${theme.label.toLowerCase()} mode.`)

  const notes = d.notes.trim()
  if (notes) lines.push(lines.length ? `Also: ${notes}` : notes)
  return lines.join('\n')
}

/** A short, readable summary of the starter design for the brief card. */
export function summarizeDesign(d: StarterDesign): string {
  const font = FONTS.find(f => f.id === d.font)
  const palette = PALETTES.find(p => p.id === d.palette)
  const theme = THEMES.find(t => t.id === d.theme)
  const parts = [
    STYLES.find(s => s.id === d.style)?.label,
    d.palette === CUSTOM_PALETTE_ID ? 'your brand colour' : palette && `${palette.label} colours`,
    font && `${font.label.toLowerCase()} type`,
    theme && `${theme.label.toLowerCase()} mode`,
  ].filter(Boolean) as string[]
  const summary = parts.join(', ')
  const notes = d.notes.trim()
  if (!summary) return notes
  const sentence = summary.charAt(0).toUpperCase() + summary.slice(1)
  return notes ? `${sentence}. ${notes}` : sentence
}
