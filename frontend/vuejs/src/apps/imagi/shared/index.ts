/**
 * Code shared by the Imagi business tools — Build, Sell, Market and Operate.
 *
 * These four are siblings that share a domain (a project and the business
 * behind it) but nothing with the public marketing site, so their common code
 * belongs here rather than in the site-wide `shared/`.
 */
export { useProjectFromSlug } from './composables/useProjectFromSlug'
export { default as ToolWorkspaceShell } from './components/ToolWorkspaceShell.vue'
export type { ToolTab } from './components/ToolWorkspaceShell.vue'
