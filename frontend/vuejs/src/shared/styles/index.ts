/**
 * The shared style vocabulary, in one import.
 *
 * Three stylesheets and three TypeScript modules make up the design system:
 *
 *   tokens.css     material and motion every page shares — the crisp-card
 *                  shadow ladder, the film grain, the page-load rise, and the
 *                  `--app-surface` variable that focus rings offset against.
 *                  Loaded globally from main.ts.
 *   editorial.css  the public pages' surface (home, docs, legal, auth,
 *                  pricing). Opted into with `class="editorial"` on a page
 *                  root. Also loaded globally from main.ts.
 *   ui.ts          the signed-in app's Tailwind class strings.
 *   forms.ts       the one focus/border treatment for text fields.
 *   accents.ts     each business tool's identity colour.
 *
 * Import the class strings from here (`@/shared/styles`); the stylesheets look
 * after themselves.
 */

export {
  ui,
  accentUi,
  toolUi,
  focusRing,
  disabledState,
  statusTones,
  type AccentUi,
  type StatusTone,
} from './ui'

export {
  accentClasses,
  type ToolAccent,
  type AccentClasses,
} from './accents'

export {
  fieldBorder,
  fieldFocus,
  fieldFocusWithin,
  fieldFocusError,
  controlFocus,
  fieldShell,
} from './forms'
