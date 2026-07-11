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

/**
 * Get the slug from a project object
 * 
 * @param project - Project object with a name property
 * @returns URL-safe slug for the project
 */
export function getProjectSlug(project: { name: string }): string {
  return toSlug(project.name)
}
