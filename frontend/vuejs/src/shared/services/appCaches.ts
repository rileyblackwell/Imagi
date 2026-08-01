/**
 * Session-scoped app data caches held in localStorage.
 *
 * These caches hold data fetched for one signed-in user — project names,
 * descriptions, and server-side paths — on an origin that any later visitor to
 * the same browser profile also loads. They are therefore cleared as part of
 * the auth teardown, alongside the token and user blob.
 *
 * Kept in `shared` rather than in the build app so the auth store can clear
 * them without depending on an app module.
 */

/** Base key for the cached project list; per-user keys append `:<user id>`. */
export const PROJECTS_CACHE_PREFIX = 'imagi_cached_projects'

const CACHE_PREFIXES = [PROJECTS_CACHE_PREFIX]

/**
 * Remove every cached app data entry in this browser profile.
 *
 * Sweeps the unsuffixed legacy keys as well as the per-user ones, so a cache
 * written by an older build is cleaned up rather than left behind forever.
 */
export function clearAppDataCaches(): void {
  try {
    const doomed: string[] = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (!key) continue
      if (CACHE_PREFIXES.some(prefix => key === prefix || key.startsWith(`${prefix}:`))) {
        doomed.push(key)
      }
    }
    doomed.forEach(key => localStorage.removeItem(key))
  } catch (e) {
    console.warn('Error clearing app data caches:', e)
  }
}
