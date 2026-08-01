/**
 * Utility functions for URL-safe project name slugs
 */

/**
 * Convert a project name to a URL-safe slug
 * - Converts to lowercase
 * - Replaces spaces and underscores with hyphens
 * - Removes special characters except hyphens
 * - Removes leading/trailing hyphens
 * - Collapses multiple hyphens into one
 * 
 * @param name - The project name to convert
 * @returns URL-safe slug
 */
export function toSlug(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/[\s_]+/g, '-')           // Replace spaces and underscores with hyphens
    .replace(/[^a-z0-9-]/g, '')        // Remove special characters except hyphens
    .replace(/-+/g, '-')                // Collapse multiple hyphens
    .replace(/^-|-$/g, '')              // Remove leading/trailing hyphens
}

/**
 * Check if a project name matches a slug
 * Used to find a project by its URL slug
 *
 * @param projectName - The project name to check
 * @param slug - The URL slug to match against
 * @returns True if the project name matches the slug
 */
export function matchesSlug(projectName: string, slug: string): boolean {
  return toSlug(projectName) === slug.toLowerCase()
}

/** The shape every slug helper below needs — a project from the API. */
interface SluggableProject {
  name: string
  slug?: string
}

/**
 * The slug to route a project on.
 *
 * Prefers the backend's slug, which is unique across projects and is what the
 * project's directory on disk is named. Falls back to deriving one from the
 * name for a project that predates the API exposing it (an entry still in the
 * local cache, say) — for most names the two agree anyway.
 *
 * @param project - Project to get the slug for
 * @returns URL-safe slug
 */
export function projectSlug(project: SluggableProject): string {
  return project.slug || toSlug(project.name)
}

/**
 * Find the project a URL slug addresses.
 *
 * Matches on the backend slug first so that names colliding under `toSlug`
 * ("My App" and "My-App") stay separately addressable — the backend hands out
 * `my-app` and `my-app-1`. Only if nothing matches does it fall back to the
 * name-derived slug, which keeps URLs minted before the backend slug was
 * exposed working. Because exact matches win, that fallback cannot steal a
 * link away from the project that actually owns the slug.
 *
 * @param projects - Projects to search
 * @param slug - URL slug to resolve
 * @returns The matching project or undefined
 */
export function findProjectBySlug<T extends SluggableProject>(
  projects: T[],
  slug: string
): T | undefined {
  const target = (slug || '').toLowerCase()
  if (!target) return undefined
  return (
    projects.find(project => project.slug?.toLowerCase() === target) ??
    projects.find(project => matchesSlug(project.name, target))
  )
}
