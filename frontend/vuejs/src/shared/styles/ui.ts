/**
 * ui.ts — the signed-in app's Tailwind vocabulary, written down once.
 *
 * Every workspace (Build, Sell, Market, Operate, the project hub) draws from
 * this: one card, one label, one input, one primary button, one hairline
 * secondary, one danger, one focus ring. The public pages have their own
 * language in editorial.css; this is the tool half.
 *
 * There were three copies of this object — marketing/, sell/ and operate/ each
 * kept their own `utils/ui.ts` — and they had already drifted: buttons were
 * px-4 in one and px-5 in the others, labels sat at 60% ink in one and 70% in
 * the others, cards were translucent-with-blur in two and opaque in the third.
 * None of those differences meant anything; they were just three files aging
 * apart. The values below take the majority reading in each case.
 *
 * Two rules for editing this file:
 *
 *   1. Every class name must appear here in full, literal form. The Tailwind
 *      JIT compiler scans source text, so `text-ink/70` written out
 *      survives the production build and `text-ink/${n}` does not.
 *   2. Surfaces come from the theme, not from hex literals. `bg-paper` and
 *      `bg-canvas` read tokens.css and are already theme-aware, so they need
 *      no `dark:` twin — see tailwind.config.js.
 */

import { fieldShell } from './forms'
import { accentClasses, type ToolAccent } from './accents'

/**
 * The one focus ring — keyboard-only, offset from whatever surface the element
 * is sitting on. Defined in tokens.css so a static `class="…"` attribute can
 * use it too; this constant exists so class strings built in TypeScript read
 * the same as the ones written in templates.
 *
 * Never applied to text fields: those draw a single deepening border instead
 * (see forms.ts for why).
 */
export const focusRing = 'focus-ring'

/** Applied to any control that can be switched off. */
export const disabledState = 'disabled:opacity-50 disabled:cursor-not-allowed'

/** Shared geometry for the pill buttons, so all three stay the same size. */
const pill = 'inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors duration-200'

export const ui = {
  /**
   * A panel. White paper lifted off the page, an ink hairline, and the shared
   * `crisp-card` shadow ladder from tokens.css.
   */
  card: 'crisp-card rounded-2xl bg-white dark:bg-white/[0.035] border border-ink/[0.08] dark:border-white/[0.08] transition-colors duration-300',

  /** Field label: small, tracked, uppercase — quiet enough to stay out of the way. */
  label: 'block text-xs font-semibold uppercase tracking-[0.14em] text-ink/55 dark:text-bone/55 mb-1.5 transition-colors duration-300',

  /** Text input, select and textarea. Borrows its edge treatment from forms.ts. */
  input: `w-full px-3.5 py-2.5 rounded-xl bg-white dark:bg-white/[0.06] text-ink dark:text-bone text-sm placeholder-ink/40 dark:placeholder-bone/30 ${fieldShell}`,

  /**
   * The page's one strong action: flat ink in light, bone in dark — the home
   * page's btn-primary, without a drop shadow.
   */
  primaryBtn: `${pill} border border-ink bg-ink text-paper hover:bg-ink/90 dark:border-bone dark:bg-bone dark:text-ink dark:hover:bg-white ${focusRing} ${disabledState}`,

  /** Everything else: a hairline outline that warms on hover. */
  secondaryBtn: `${pill} border border-ink/[0.14] text-ink/80 hover:text-ink hover:border-ink/30 hover:bg-ink/[0.03] dark:border-white/[0.16] dark:text-bone/80 dark:hover:text-bone dark:hover:border-white/30 dark:hover:bg-white/[0.06] ${focusRing} ${disabledState}`,

  /** Destructive actions. Same hairline shape, red ink — never a solid red fill. */
  dangerBtn: `${pill} border border-red-200/80 dark:border-red-400/25 text-red-600 dark:text-red-300 hover:bg-red-50 dark:hover:bg-red-500/10 hover:border-red-300 dark:hover:border-red-400/40 ${focusRing} ${disabledState}`,

  /**
   * A quiet square icon button — toolbar and table-row actions. Size stays on
   * the element (`w-8 h-8`, `w-9 h-9`, …) because it varies by context; only
   * the ink and the hover wash are shared.
   */
  iconBtn: `inline-flex items-center justify-center rounded-lg text-ink/50 dark:text-bone/50 hover:text-ink dark:hover:text-bone hover:bg-ink/[0.04] dark:hover:bg-white/[0.08] transition-colors duration-200 ${focusRing}`,

  /** The destructive twin: the same button, reddening on hover. */
  dangerIconBtn: `inline-flex items-center justify-center rounded-lg text-ink/50 dark:text-bone/50 hover:text-red-600 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors duration-200 ${focusRing}`,

  /** Inline feedback boxes. */
  errorBox: 'p-3.5 rounded-xl border border-red-200/80 dark:border-red-400/25 bg-red-50/80 dark:bg-red-500/10 text-sm text-red-700 dark:text-red-300',
  infoBox: 'p-3.5 rounded-xl border border-ink/10 dark:border-blue-400/25 bg-ink/[0.03] dark:bg-blue-400/10 text-sm text-blue-800 dark:text-blue-200',
  successBox: 'p-3.5 rounded-xl border border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-sm text-emerald-700 dark:text-emerald-300',

  /** Table furniture: a tracked uppercase header row over a hairline. */
  tableHead: 'px-4 py-3.5 text-xs font-semibold uppercase tracking-[0.14em] text-ink/50 dark:text-bone/50',
  tableCell: 'px-4 py-3.5 text-sm text-ink/80 dark:text-bone/80',

  /**
   * The type scale inside a panel, top to bottom. Three sizes and two ink
   * levels cover every label, note and heading in the four workspaces — they
   * were being written out as utility triples a hundred and sixteen times.
   */
  headingText: 'text-lg font-semibold text-ink dark:text-bone',
  panelHeading: 'text-base font-semibold text-ink dark:text-bone',
  bodyText: 'text-sm text-ink/60 dark:text-bone/60',
  hintText: 'text-xs text-ink/50 dark:text-bone/50',
}

/** Class strings that carry a workspace's identity colour. */
export interface AccentUi {
  /** The tile an icon sits on — sized by the caller (w-14 h-14, w-9 h-9, …). */
  iconTile: string
  /** The tracked pill that titles a section. */
  sectionBadge: string
}

/**
 * The accent-tinted half of a workspace's vocabulary.
 *
 * Composed from whole literal strings in accents.ts rather than assembled from
 * colour fragments, so the JIT compiler still sees every class name.
 */
export function accentUi(accent: ToolAccent): AccentUi {
  const a = accentClasses[accent]
  return {
    iconTile: `rounded-xl flex items-center justify-center border ${a.iconWrap} ${a.iconText} transition-colors duration-300`,
    sectionBadge: `inline-flex items-center px-3.5 py-1.5 rounded-full border ${a.badge} text-xs font-semibold uppercase tracking-[0.18em] transition-colors duration-300`,
  }
}

/**
 * Everything a workspace needs: the shared vocabulary plus its own accent.
 *
 * A tool's `utils/ui.ts` is now a single line — `export const ui =
 * toolUi('violet')` — so its templates keep reading `ui.card` and `ui.iconTile`
 * while there is only one definition of either.
 */
export function toolUi(accent: ToolAccent): typeof ui & AccentUi {
  return { ...ui, ...accentUi(accent) }
}

/**
 * Semantic status tones, shared by every status pill in the product.
 *
 * Keyed by meaning rather than by colour so a caller maps its own vocabulary
 * ('paid', 'delivered', 'done') onto a tone and never onto emerald directly.
 */
export type StatusTone = 'success' | 'danger' | 'info' | 'pending' | 'neutral'

export const statusTones: Record<StatusTone, string> = {
  success: 'border-emerald-200/80 dark:border-emerald-400/25 bg-emerald-50/80 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-300',
  danger: 'border-red-200/80 dark:border-red-400/25 bg-red-50/80 dark:bg-red-500/10 text-red-600 dark:text-red-300',
  info: 'border-ink/10 dark:border-blue-400/25 bg-ink/[0.03] dark:bg-blue-400/10 text-blue-700 dark:text-blue-300',
  pending: 'border-amber-200/80 dark:border-amber-400/25 bg-amber-50/80 dark:bg-amber-400/10 text-amber-700 dark:text-amber-300',
  neutral: 'border-ink/10 dark:border-white/15 bg-ink/[0.03] dark:bg-white/[0.04] text-ink/60 dark:text-bone/60',
}
