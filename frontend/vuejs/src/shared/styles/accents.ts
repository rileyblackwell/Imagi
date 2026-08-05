/**
 * accents.ts — the identity colour of each business tool, in one place.
 *
 * Build, Sell, Market and Operate each get an accent. It is the only colour
 * that varies between the four workspaces: the ink, the paper, the buttons,
 * the hairlines and the focus ring are identical everywhere (see ui.ts), and
 * the accent is what tells you which tool you are standing in.
 *
 * These used to live in three places that disagreed with each other. The
 * project hub declared Market as violet and Operate as amber; the Market
 * workspace styled itself blue and the Operate workspace orange — so a tool's
 * card and the tool it opened were different colours. The hub's declaration
 * wins, because it is the one a user sees first, and because blue is already
 * the app's chrome colour (focus rings, selection) and reads as "system"
 * rather than "Market".
 *
 * NOTE: every class name below is written out in full and never assembled from
 * fragments at runtime, so the Tailwind JIT compiler can see it in the source.
 * Composing whole literal strings together (as `iconTile` and `sectionBadge`
 * do) is fine — building `text-${color}-600` is not.
 */

export type ToolAccent = 'blue' | 'emerald' | 'violet' | 'amber'

/** The roles an accent fills. Each is a complete, static Tailwind string. */
export interface AccentClasses {
  /** Card edge, with its hover state — for cards that link somewhere. */
  cardBorder: string
  /** Background + border of the tile an icon sits on. */
  iconWrap: string
  /** The icon glyph itself. */
  iconText: string
  /** Border + background + text of a small pill. */
  badge: string
  /** A call-to-action link inside an accent-tinted card. */
  link: string
  /** Gradient stop for an ambient wash. */
  glow: string
}

export const accentClasses: Record<ToolAccent, AccentClasses> = {
  blue: {
    cardBorder: 'border-blue-200/70 dark:border-blue-300/[0.16] hover:border-blue-300 dark:hover:border-blue-300/40',
    iconWrap: 'bg-blue-50 dark:bg-blue-400/10 border-blue-200/60 dark:border-blue-400/25',
    iconText: 'text-blue-600 dark:text-blue-300',
    badge: 'border-blue-200/70 dark:border-blue-400/25 bg-blue-50/80 dark:bg-blue-400/10 text-blue-700 dark:text-blue-300',
    link: 'text-blue-700 dark:text-blue-300 group-hover:text-blue-800 dark:group-hover:text-blue-200',
    glow: 'from-blue-400/20',
  },
  emerald: {
    cardBorder: 'border-emerald-200/70 dark:border-emerald-300/[0.16] hover:border-emerald-300 dark:hover:border-emerald-300/40',
    iconWrap: 'bg-emerald-50 dark:bg-emerald-400/10 border-emerald-200/60 dark:border-emerald-400/25',
    iconText: 'text-emerald-600 dark:text-emerald-300',
    badge: 'border-emerald-200/70 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-400/10 text-emerald-700 dark:text-emerald-300',
    link: 'text-emerald-700 dark:text-emerald-300 group-hover:text-emerald-800 dark:group-hover:text-emerald-200',
    glow: 'from-emerald-400/20',
  },
  violet: {
    cardBorder: 'border-violet-200/70 dark:border-violet-300/[0.16] hover:border-violet-300 dark:hover:border-violet-300/40',
    iconWrap: 'bg-violet-50 dark:bg-violet-400/10 border-violet-200/60 dark:border-violet-400/25',
    iconText: 'text-violet-600 dark:text-violet-300',
    badge: 'border-violet-200/70 dark:border-violet-400/25 bg-violet-50/80 dark:bg-violet-400/10 text-violet-700 dark:text-violet-300',
    link: 'text-violet-700 dark:text-violet-300 group-hover:text-violet-800 dark:group-hover:text-violet-200',
    glow: 'from-violet-400/20',
  },
  amber: {
    cardBorder: 'border-amber-200/70 dark:border-amber-300/[0.16] hover:border-amber-300 dark:hover:border-amber-300/40',
    iconWrap: 'bg-amber-50 dark:bg-amber-400/10 border-amber-200/60 dark:border-amber-400/25',
    iconText: 'text-amber-600 dark:text-amber-300',
    badge: 'border-amber-200/70 dark:border-amber-400/25 bg-amber-50/80 dark:bg-amber-400/10 text-amber-700 dark:text-amber-300',
    link: 'text-amber-700 dark:text-amber-300 group-hover:text-amber-800 dark:group-hover:text-amber-200',
    glow: 'from-amber-400/20',
  },
}

/**
 * Static treatment for the project-hub cards.
 *
 * The hub is the most utilitarian surface in the product, so it wears the
 * brand's most restrained face: navy ink on porcelain — the same ink as the
 * `Imagi.` wordmark — rather than a warm accent. Each card carries a solid ink
 * icon chip with a porcelain glyph, and the blue brand colour is held back to
 * a whisper on hover. This keeps four repeated cards calm instead of loud.
 */
export const hubCardTone = {
  /** Card border, with its hover accent. */
  card: 'border-blue-950/[0.08] dark:border-white/[0.08] group-hover:border-blue-300/60 dark:group-hover:border-blue-300/25',
  /** Icon chip background + ring. */
  tile: 'bg-blue-950 dark:bg-white ring-1 ring-blue-950/10 dark:ring-white/10',
  /** Icon glyph colour, sitting on the chip. */
  glyph: 'text-paper dark:text-blue-950',
}
