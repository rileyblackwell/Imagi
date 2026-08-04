/**
 * forms.ts — the canonical focus/outline treatment for form fields.
 *
 * A field draws exactly ONE edge: its border. It stays the same neutral ink
 * hairline at every state and simply deepens — 12% at rest, 25% on hover,
 * 45% on focus. No accent colour, and nothing ever layered outside it.
 *
 * Both halves of that rule came from watching the alternatives fail:
 *
 *   - `ring-*` gives a second edge, always. A ring is a box-shadow drawn
 *     outside the element, so it composites over the *page* background while
 *     the border composites over the *field's* background. Even a `ring-1`
 *     declaring the identical colour as the border lands as a visibly
 *     different tone — a grey edge inside a blue one.
 *   - Turning that single border blue on focus still read as two outlines,
 *     because a saturated accent edge doesn't belong to the same family as
 *     the calm hairline it replaces; the eye separates them.
 *
 * Buttons, cards and links still use an offset ring — those fire on
 * `focus-visible` (keyboard only), where a detached ring is the point.
 */

/** The one edge, at rest: a hairline that warms slightly on hover. */
export const fieldBorder =
  'border border-blue-950/[0.12] dark:border-white/[0.14] ' +
  'hover:border-blue-950/25 dark:hover:border-white/25'

/** Focus: the same hairline, one step deeper. No accent, no ring, no halo. */
export const fieldFocus =
  'focus:outline-none focus:border-blue-950/45 dark:focus:border-white/45'

/**
 * Same treatment for a wrapper that hosts a field it doesn't own — the Stripe
 * card element, for instance, which mounts its own iframe inside our shell.
 */
export const fieldFocusWithin =
  'focus-within:border-blue-950/45 dark:focus-within:border-white/45'

/** Error state: still one border, red instead of ink. */
export const fieldFocusError =
  'focus:outline-none ' +
  'border-red-500/50 dark:border-red-400/40 ' +
  'focus:border-red-500 dark:focus:border-red-400'

/**
 * Checkboxes, radios and sliders are too small to carry an edge treatment, so
 * they keep an offset ring — but in ink rather than stock blue, and only for
 * keyboard focus.
 */
export const controlFocus = 'focus-ring'

/** Everything a standard text field needs apart from its own sizing/colour. */
export const fieldShell = `${fieldBorder} ${fieldFocus} transition-colors duration-200`
