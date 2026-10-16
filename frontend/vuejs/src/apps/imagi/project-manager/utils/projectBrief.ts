/**
 * projectBrief.ts — the starter design behind the projects page's create form.
 *
 * The form's last step, "Set the look", is the app's first design system, and
 * it asks for two things only: a style and a colour scheme. A style carries
 * its own fonts, corners and card treatment; a scheme carries its colours and
 * whether the app is light or dark. The choice is sent as plain text in
 * `design_preferences`, written so the build agent can act on it directly
 * (named colours with hex values, font suggestions), with no schema change on
 * the backend.
 */

export interface DesignStyle {
  id: string
  label: string
  /** One line under the style's tile, in the founder's words. */
  line: string
  /** What the style means for the build: shapes, spacing, type. */
  brief: string
  /** Fonts for the build to use. */
  fonts: string
  /** The preview's look for this style (StarterPreview.vue). */
  preview: {
    head: string
    body: string
    weight: number
    tracking: string
    radius: number
    buttonRadius: number
    hero: 'left' | 'center'
    card: 'line' | 'none' | 'shadow' | 'fill' | 'offset'
    titleSize: number
    eyebrow?: string
  }
}

export const STYLES: readonly DesignStyle[] = [
  {
    id: 'professional',
    label: 'Professional',
    line: 'Clear, calm and trustworthy',
    brief: 'clear structure, calm colour, businesslike and trustworthy, softly rounded corners',
    fonts: 'a clean modern sans-serif throughout (such as Inter or Hanken Grotesk)',
    preview: { head: "'Hanken Grotesk', system-ui, sans-serif", body: "'Hanken Grotesk', system-ui, sans-serif", weight: 700, tracking: '-0.02em', radius: 10, buttonRadius: 8, hero: 'left', card: 'line', titleSize: 44 },
  },
  {
    id: 'minimal',
    label: 'Minimal',
    line: 'Lots of space, very little decoration',
    brief: 'lots of white space, restrained colour, thin rules instead of boxes, nearly square corners',
    fonts: 'a light, neutral sans-serif (such as Instrument Sans or Inter)',
    preview: { head: "'Instrument Sans', system-ui, sans-serif", body: "'Instrument Sans', system-ui, sans-serif", weight: 500, tracking: '-0.03em', radius: 4, buttonRadius: 4, hero: 'left', card: 'none', titleSize: 46 },
  },
  {
    id: 'friendly',
    label: 'Friendly',
    line: 'Soft, rounded and welcoming',
    brief: 'soft rounded corners, pill buttons, gentle shadows, centred welcoming headings',
    fonts: 'a rounded sans-serif (such as Nunito or Quicksand)',
    preview: { head: "'Nunito', ui-rounded, system-ui, sans-serif", body: "'Nunito', ui-rounded, system-ui, sans-serif", weight: 800, tracking: '-0.01em', radius: 18, buttonRadius: 999, hero: 'center', card: 'shadow', titleSize: 44 },
  },
  {
    id: 'bold',
    label: 'Bold',
    line: 'Big type and strong contrast',
    brief: 'big heavy headings, strong contrast, blocks of solid colour, sharp corners',
    fonts: 'a heavy display sans-serif for headings (such as Bricolage Grotesque or Archivo Black) with a plain sans-serif for body text',
    preview: { head: "'Bricolage Grotesque', system-ui, sans-serif", body: "'Hanken Grotesk', system-ui, sans-serif", weight: 800, tracking: '-0.045em', radius: 3, buttonRadius: 3, hero: 'left', card: 'fill', titleSize: 54 },
  },
  {
    id: 'elegant',
    label: 'Elegant',
    line: 'Refined, quiet and premium',
    brief: 'refined and understated, generous spacing, hairline borders, square corners, small letter-spaced labels',
    fonts: 'serif headings (such as Fraunces or Playfair Display) with a clean sans-serif for body text',
    preview: { head: "'Fraunces', Georgia, serif", body: "'Instrument Sans', system-ui, sans-serif", weight: 500, tracking: '-0.01em', radius: 0, buttonRadius: 0, hero: 'center', card: 'line', titleSize: 46, eyebrow: 'Welcome' },
  },
  {
    id: 'playful',
    label: 'Playful',
    line: 'Bright shapes and a sense of fun',
    brief: 'bright colour, very rounded shapes, pill buttons, cards in tinted colours, a little fun in the details',
    fonts: 'a friendly rounded display font for headings (such as Fredoka) with a rounded sans-serif for body text (such as Nunito)',
    preview: { head: "'Fredoka', ui-rounded, system-ui, sans-serif", body: "'Nunito', ui-rounded, system-ui, sans-serif", weight: 600, tracking: '0', radius: 22, buttonRadius: 999, hero: 'center', card: 'fill', titleSize: 46 },
  },
  {
    id: 'colourful',
    label: 'Colourful',
    line: 'Rich colour from edge to edge',
    brief: 'rich colour, a gradient hero from the primary to the accent colour, pill buttons, confident and lively',
    fonts: 'a bold modern sans-serif for headings (such as Bricolage Grotesque or Plus Jakarta Sans) with a plain sans-serif for body text',
    preview: { head: "'Bricolage Grotesque', system-ui, sans-serif", body: "'Hanken Grotesk', system-ui, sans-serif", weight: 700, tracking: '-0.03em', radius: 16, buttonRadius: 999, hero: 'left', card: 'shadow', titleSize: 42 },
  },
  {
    id: 'retro',
    label: 'Retro',
    line: 'Thick outlines and a vintage feel',
    brief: 'a vintage feel, thick dark outlines with hard offset shadows on cards and buttons',
    fonts: 'a classic display serif for headings (such as DM Serif Display) with a monospace or typewriter face for body text (such as Space Mono)',
    preview: { head: "'DM Serif Display', Georgia, serif", body: "'Space Mono', ui-monospace, monospace", weight: 400, tracking: '-0.01em', radius: 6, buttonRadius: 6, hero: 'left', card: 'offset', titleSize: 46 },
  },
  {
    id: 'techy',
    label: 'Techy',
    line: 'Sharp, precise and modern',
    brief: 'sharp and precise, a faint grid in the background, small monospace labels, crisp thin borders',
    fonts: 'a geometric sans-serif (such as Sora or Geist) with a monospace face for small labels (such as JetBrains Mono)',
    preview: { head: "'Sora', system-ui, sans-serif", body: "'Sora', system-ui, sans-serif", weight: 600, tracking: '-0.035em', radius: 8, buttonRadius: 6, hero: 'left', card: 'line', titleSize: 42, eyebrow: 'Now live' },
  },
]

export interface ColourScheme {
  id: string
  label: string
  /** A dark scheme makes the whole app dark. */
  dark?: boolean
  background: string
  surface: string
  text: string
  primary: string
  accent: string
}

export const SCHEMES: readonly ColourScheme[] = [
  { id: 'ocean', label: 'Ocean', background: '#F3F6FA', surface: '#FFFFFF', text: '#0F1B33', primary: '#1E4FD8', accent: '#38BDF8' },
  { id: 'forest', label: 'Forest', background: '#F4F1E8', surface: '#FBFAF5', text: '#1B2A22', primary: '#1F5A40', accent: '#8DBF96' },
  { id: 'sunset', label: 'Sunset', background: '#FFF6EE', surface: '#FFFFFF', text: '#2A1712', primary: '#E1462F', accent: '#F5A524' },
  { id: 'berry', label: 'Berry', background: '#FCF2F7', surface: '#FFFFFF', text: '#2B0F1E', primary: '#A3195B', accent: '#C084FC' },
  { id: 'earth', label: 'Earth', background: '#F4EDE4', surface: '#FBF7F1', text: '#2E1F16', primary: '#9A4A2C', accent: '#C9A66B' },
  { id: 'mono', label: 'Mono', background: '#F6F6F5', surface: '#FFFFFF', text: '#111111', primary: '#111111', accent: '#A3A3A3' },
  { id: 'midnight', label: 'Midnight', dark: true, background: '#0D1220', surface: '#151C2E', text: '#EAF0FF', primary: '#6EA8FF', accent: '#7FE0D4' },
  { id: 'ember', label: 'Ember', dark: true, background: '#15110F', surface: '#201A17', text: '#F6EEE8', primary: '#F2A541', accent: '#E8644A' },
]

/** The scheme option that is the founder's own brand colour. */
export const CUSTOM_SCHEME_ID = 'custom'

export interface StarterDesign {
  style: string | null
  scheme: string | null
  /** Hex brand colour, used when `scheme` is CUSTOM_SCHEME_ID. */
  brandColor: string
  notes: string
}

export const emptyDesign = (): StarterDesign => ({
  style: null,
  scheme: null,
  brandColor: '#4F46E5',
  notes: '',
})

export const designIsSet = (d: StarterDesign): boolean =>
  Boolean(d.style || d.scheme || d.notes.trim())

// --- Colour helpers --------------------------------------------------------

type Triple = [number, number, number]

const hexToRgb = (hex: string): Triple => {
  const n = parseInt(hex.replace('#', ''), 16)
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
}

const mapTriple = ([a, b, c]: Triple, f: (v: number) => number): Triple => [f(a), f(b), f(c)]

/** Relative luminance, 0 (black) to 1 (white). */
export const luminance = (hex: string): number => {
  const [r, g, b] = mapTriple(hexToRgb(hex), (v) => {
    const c = v / 255
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
  })
  return 0.2126 * r + 0.7152 * g + 0.0722 * b
}

/** Ink that reads on a filled button of this colour. */
export const inkOn = (hex: string): string => (luminance(hex) > 0.42 ? '#111318' : '#FFFFFF')

const hexToHsl = (hex: string): Triple => {
  const [r, g, b] = mapTriple(hexToRgb(hex), (v) => v / 255)
  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  const l = (max + min) / 2
  let h = 0
  let s = 0
  if (max !== min) {
    const d = max - min
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
    if (max === r) h = (g - b) / d + (g < b ? 6 : 0)
    else if (max === g) h = (b - r) / d + 2
    else h = (r - g) / d + 4
    h *= 60
  }
  return [h, s * 100, l * 100]
}

const hslToHex = (h: number, s: number, l: number): string => {
  const sat = s / 100
  const light = l / 100
  const a = sat * Math.min(light, 1 - light)
  const f = (n: number) => {
    const k = (n + h / 30) % 12
    return light - a * Math.max(-1, Math.min(k - 3, 9 - k, 1))
  }
  return `#${[f(0), f(8), f(4)].map((x) => Math.round(x * 255).toString(16).padStart(2, '0')).join('')}`.toUpperCase()
}

/** A light scheme built around one brand colour, for the preview. */
export const customScheme = (brandColor: string): ColourScheme => {
  const [h, s] = hexToHsl(brandColor)
  return {
    id: CUSTOM_SCHEME_ID,
    label: 'Your colour',
    background: hslToHex(h, Math.min(s, 40), 97),
    surface: '#FFFFFF',
    text: hslToHex(h, Math.min(s, 35), 12),
    primary: brandColor.toUpperCase(),
    accent: hslToHex((h + 35) % 360, Math.max(55, s), 62),
  }
}

/** The scheme a design points at, or null when none is picked. */
export const schemeFor = (d: Pick<StarterDesign, 'scheme' | 'brandColor'>): ColourScheme | null => {
  if (d.scheme === CUSTOM_SCHEME_ID) return customScheme(d.brandColor)
  return SCHEMES.find((s) => s.id === d.scheme) ?? null
}

/**
 * The starter design as the text the build reads, one line per answer. Empty
 * when nothing was chosen, so the build picks a look itself.
 */
export function composeDesignPreferences(d: StarterDesign): string {
  const lines: string[] = []
  const style = STYLES.find((s) => s.id === d.style)
  if (style) {
    lines.push(`Style: ${style.label} (${style.brief}).`)
    lines.push(`Fonts: ${style.fonts}.`)
  }

  if (d.scheme === CUSTOM_SCHEME_ID) {
    lines.push(`Colours: build the palette around the brand colour ${d.brandColor.toUpperCase()}.`)
  } else {
    const scheme = SCHEMES.find((s) => s.id === d.scheme)
    if (scheme) {
      lines.push(
        `Colours: ${scheme.label} scheme, primary ${scheme.primary}, accent ${scheme.accent}, ` +
          `background ${scheme.background}, text ${scheme.text}.`,
      )
      lines.push(`Theme: ${scheme.dark ? 'dark' : 'light'} mode.`)
    }
  }

  const notes = d.notes.trim()
  if (notes) lines.push(lines.length ? `Also: ${notes}` : notes)
  return lines.join('\n')
}
