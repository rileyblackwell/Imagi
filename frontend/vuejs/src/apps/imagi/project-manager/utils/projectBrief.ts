/**
 * projectBrief.ts — the questions behind the projects page's create form.
 *
 * The form asks what the app is, what it does, and how it should look. Two
 * answers here shape the rest of it:
 *
 * - The kind of app (a booking app, an online store, ...) is the form's one
 *   branch. It changes what step 3 asks: its hint, its sentence starters and
 *   its example, so someone describing a store is asked about orders and
 *   someone describing a booking app is asked about bookings.
 * - The starter design (style, colours, fonts, theme, notes) is the app's
 *   first design system. It is sent as plain text in `design_preferences`,
 *   written so the build agent can act on it directly (named colours with
 *   hex values, font suggestions), with no schema change on the backend.
 */

export interface AppKind {
  id: string
  label: string
  /** Step 3's hint once this kind is picked: the questions worth answering. */
  hint: string
  /** One-tap first words for step 3. */
  starters: readonly string[]
  /** Step 3's example answer. */
  example: string
}

export const GENERIC_KIND: AppKind = {
  id: 'other',
  label: 'Something else',
  hint: 'In everyday words: what people can do on it, what it needs to keep track of, and anything that matters to you.',
  starters: ['People can', 'It keeps track of', 'It should'],
  example: 'People can sign up and save their favourites. It keeps track of each person’s list. It should work well on phones.',
}

export const APP_KINDS: readonly AppKind[] = [
  {
    id: 'booking',
    label: 'Bookings',
    hint: 'What can people book, how far ahead, and do they pay when they book? What do you need to see each day?',
    starters: ['People can book', 'Each booking needs', 'I can see'],
    example: 'People can book a class up to two weeks ahead and pay when they book. Each booking needs a name and phone number. I can see the day’s bookings and cancel a class.',
  },
  {
    id: 'store',
    label: 'Online store',
    hint: 'What do you sell, how do people find and order it, and what does each order need?',
    starters: ['It sells', 'Customers can', 'Each order needs'],
    example: 'It sells handmade candles in three sizes. Customers can browse by scent, add to a cart and pay online. Each order needs a delivery address.',
  },
  {
    id: 'community',
    label: 'Community',
    hint: 'Who joins, what can members do, and what is only for members?',
    starters: ['People join by', 'Members can', 'Only members see'],
    example: 'People join by signing up with email. Members can post questions and reply to each other. Only members see the event calendar.',
  },
  {
    id: 'tool',
    label: 'Tool or tracker',
    hint: 'What do people put in, what do they get back, and what does it keep track of over time?',
    starters: ['People can add', 'It keeps track of', 'It shows'],
    example: 'People can add their workouts with sets and weights. It keeps track of every session. It shows progress for each exercise as a chart.',
  },
  {
    id: 'content',
    label: 'Portfolio or blog',
    hint: 'What do you want to show, how is it organised, and how do people get in touch?',
    starters: ['It shows', 'Each post has', 'Visitors can'],
    example: 'It shows my photography grouped into weddings, portraits and travel. Each post has a title and a short story. Visitors can send me an enquiry.',
  },
  GENERIC_KIND,
]

export const kindById = (id: string | null): AppKind | null =>
  APP_KINDS.find(kind => kind.id === id) ?? null

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

/**
 * What the app does, as sent in `app_details`. A picked kind leads it, so the
 * build knows the shape of app before it reads the details.
 */
export function composeAppDetails(kindId: string | null, details: string): string {
  const text = details.trim()
  const kind = kindById(kindId)
  if (!kind || kind.id === GENERIC_KIND.id) return text
  return `Kind of app: ${kind.label}.\n\n${text}`
}
