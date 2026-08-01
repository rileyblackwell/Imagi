import { computed, ref, type Ref } from 'vue'

/**
 * Which pane the workspace sidebar shows, across both layouts.
 *
 * There are two of these panes — the agent manager and the active instance's
 * chat — and never both at once. Desktop toggles between them; mobile adds the
 * preview as a third full-screen view, driven by the navbar switcher.
 *
 * The two layouts read different state (`sidebarView` on desktop, `mobileView`
 * on mobile), which is the trap this composable exists to close: a switch made
 * from inside a pane has to move both, or it changes the pane on one layout and
 * silently does nothing on the other.
 */

export type SidebarView = 'manager' | 'chat'
export type MobileView = SidebarView | 'browser'

// Persisted so the workspace reopens on the pane you left it on. Tolerates the
// old 'builderAgentManagerOpen' key's absence; that key is no longer written.
const SIDEBAR_VIEW_STORAGE_KEY = 'builderSidebarView'
// Owned by BuilderLayout (see its storage-key prop); read here only to pick the
// mobile view that matches it on first paint.
const SIDEBAR_COLLAPSED_STORAGE_KEY = 'builderWorkspaceSidebarCollapsed'

function readStored(key: string): string | null {
  try {
    return typeof localStorage !== 'undefined' ? localStorage.getItem(key) : null
  } catch {
    return null
  }
}

export const mobileViewOptions: Array<{ value: MobileView; label: string; icon: string }> = [
  { value: 'manager', label: 'Subagents', icon: 'fas fa-layer-group' },
  { value: 'chat', label: 'Chat', icon: 'fas fa-comment-dots' },
  { value: 'browser', label: 'Preview', icon: 'fas fa-globe' },
]

export function useSidebarPane(isMobile: Ref<boolean>) {
  const sidebarView = ref<SidebarView>(
    readStored(SIDEBAR_VIEW_STORAGE_KEY) === 'manager' ? 'manager' : 'chat'
  )

  // Start on the view matching the persisted collapsed state, otherwise a
  // reload after choosing the browser would highlight "chat" while showing it.
  const mobileView = ref<MobileView>(
    readStored(SIDEBAR_COLLAPSED_STORAGE_KEY) === 'true' ? 'browser' : 'chat'
  )

  /** Swap the pane the sidebar shows. The single writer for both pieces of
   *  state, so a switch made from inside a pane — the masthead's switch pill,
   *  picking a thread in the manager, opening a subagent from a dispatch card —
   *  lands on whichever one the current layout is rendering.
   *  'browser' is left alone: it means the sidebar is collapsed off-screen, and
   *  naming a pane the user can't see would light up the wrong navbar tab. */
  function setSidebarView(view: SidebarView) {
    sidebarView.value = view
    if (mobileView.value !== 'browser') mobileView.value = view
    try {
      localStorage.setItem(SIDEBAR_VIEW_STORAGE_KEY, view)
    } catch {}
  }

  /** The navbar switcher picked a view. `setSidebarCollapsed` comes from the
   *  layout: the browser lives in the main content area, so it shows when the
   *  sidebar is collapsed off-screen and the two panes show when it is open. */
  function selectMobileView(
    view: MobileView,
    setSidebarCollapsed?: (collapsed: boolean) => void
  ) {
    mobileView.value = view
    // Manager/chat are the same panes desktop toggles between; keep the
    // persisted desktop view in step so a rotation doesn't swap panes.
    if (view !== 'browser') setSidebarView(view)
    setSidebarCollapsed?.(view === 'browser')
  }

  /** The single pane the sidebar renders right now. On mobile 'browser' means
   *  the sidebar is collapsed and neither pane is visible, so it falls through
   *  to chat — what the user returns to when they reopen the sidebar. */
  const activeSidebarPane = computed<SidebarView>(() =>
    isMobile.value ? (mobileView.value === 'manager' ? 'manager' : 'chat') : sidebarView.value
  )

  return {
    sidebarView,
    mobileView,
    mobileViewOptions,
    setSidebarView,
    selectMobileView,
    activeSidebarPane,
  }
}
