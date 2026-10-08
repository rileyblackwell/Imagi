/**
 * Where to send someone after they sign in.
 *
 * The sign-in page honours a `?redirect=` query so a guarded page can send a
 * visitor to sign in and bring them back. Anyone can craft that link, so only
 * a path on this site is accepted: it must start with a single '/', which
 * rules out absolute URLs ('https://…'), protocol-relative ones ('//evil.com')
 * and the backslash variant browsers treat the same way ('/\evil.com').
 * Anything else falls back to the home page.
 */
export function safeRedirect(target: unknown, fallback = '/'): string {
  if (typeof target !== 'string') return fallback
  if (!target.startsWith('/')) return fallback
  if (target.startsWith('//') || target.startsWith('/\\')) return fallback
  return target
}
