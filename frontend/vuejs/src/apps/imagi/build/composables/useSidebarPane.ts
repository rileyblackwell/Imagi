import { ref } from 'vue'

/**
 * Which pane the workspace sidebar shows, and how the preview relates to it.
 *
 * There are two panes — the agent manager and the active instance's chat — and
 * never both at once. The preview is not a third pane: it lives in the main
 * content area, so it is simply what you see when the sidebar is collapsed. On
 * desktop the sidebar is open beside it; on a phone the sidebar covers it, so
 * "go to the preview" and "collapse the sidebar" are the same act.
 *
 * That is the whole model, and it is deliberately the same one at every width:
 * mobile used to carry a second piece of state (a navbar switcher naming one of
 * three views) which had to be kept in lockstep with this one, and any writer
 * that forgot changed the pane on one layout while doing nothing on the other.
 */

export type SidebarView = 'manager' | 'chat'

/** Persisted so the workspace reopens on the pane you left it on. Tolerates the
 *  old 'builderAgentManagerOpen' key's absence; that key is no longer written. */
const SIDEBAR_VIEW_STORAGE_KEY = 'builderSidebarView'

function readStored(key: string): string | null {
  try {
    return typeof localStorage !== 'undefined' ? localStorage.getItem(key) : null
  } catch {
    return null
  }
}

/** Collapse state is owned by BuilderLayout (see its storage-key prop) and
 *  handed to us as a setter, so the preview stays one thing the layout knows
 *  about rather than a view this composable has to mirror. */
type SetCollapsed = (collapsed: boolean) => void

export function useSidebarPane() {
  const sidebarView = ref<SidebarView>(
    readStored(SIDEBAR_VIEW_STORAGE_KEY) === 'manager' ? 'manager' : 'chat'
  )

  /** Swap the pane the sidebar shows. The single writer, so a switch made from
   *  inside a pane — the masthead's switch pill, picking a thread in the
   *  manager, opening a subagent from a dispatch card — always lands. */
  function setSidebarView(view: SidebarView) {
    sidebarView.value = view
    try {
      localStorage.setItem(SIDEBAR_VIEW_STORAGE_KEY, view)
    } catch {}
  }

  /** Go and watch the app being built. The pane underneath is left alone: it is
   *  what you come back to, and coming back should not have moved it. */
  function showPreview(setSidebarCollapsed: SetCollapsed) {
    setSidebarCollapsed(true)
  }

  /** Come back from the preview to a pane — the preview's return pill, and the
   *  desktop case where the sidebar was collapsed. Naming the pane and opening
   *  the sidebar are one act: either alone lands you somewhere you didn't ask
   *  for. */
  function showPane(view: SidebarView, setSidebarCollapsed: SetCollapsed) {
    setSidebarView(view)
    setSidebarCollapsed(false)
  }

  return {
    sidebarView,
    setSidebarView,
    showPreview,
    showPane,
  }
}
