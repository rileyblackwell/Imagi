/**
 * The business idea a visitor typed into the home page's prompt, carried over
 * to the "Start a project" form on the projects page.
 *
 * Signed-out visitors detour through sign-in (or registration, which lands
 * back on the home page) on the way, so the idea can't ride along in component
 * state. sessionStorage keeps it for the tab and drops it when the tab closes.
 * Storage can be unavailable (private mode, blocked site data); every call
 * fails soft, and the worst case is an empty form.
 */
const KEY = 'imagi:pending-idea'

export function savePendingIdea(idea: string): void {
  const value = idea.trim()
  try {
    if (value) sessionStorage.setItem(KEY, value)
    else sessionStorage.removeItem(KEY)
  } catch {
    /* storage unavailable — nothing to carry */
  }
}

export function peekPendingIdea(): string {
  try {
    return sessionStorage.getItem(KEY) ?? ''
  } catch {
    return ''
  }
}

/** Read the idea and forget it, so it fills the form exactly once. */
export function takePendingIdea(): string {
  const value = peekPendingIdea()
  try {
    sessionStorage.removeItem(KEY)
  } catch {
    /* nothing to clear */
  }
  return value
}
