import { describe, it, expect, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useSidebarPane } from '../useSidebarPane'

describe('useSidebarPane', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  describe('the masthead switch works on every layout', () => {
    // The regression this covers: the switch pill wrote only the desktop
    // state, so on a phone — where the rendered pane is named by mobileView —
    // pressing it changed nothing at all.
    it('moves the rendered pane on mobile', () => {
      const { setSidebarView, activeSidebarPane } = useSidebarPane(ref(true))

      expect(activeSidebarPane.value).toBe('chat')
      setSidebarView('manager')
      expect(activeSidebarPane.value).toBe('manager')
      setSidebarView('chat')
      expect(activeSidebarPane.value).toBe('chat')
    })

    it('moves the rendered pane on desktop', () => {
      const { setSidebarView, activeSidebarPane } = useSidebarPane(ref(false))

      expect(activeSidebarPane.value).toBe('chat')
      setSidebarView('manager')
      expect(activeSidebarPane.value).toBe('manager')
      setSidebarView('chat')
      expect(activeSidebarPane.value).toBe('chat')
    })

    it('keeps the navbar switcher in step, so it highlights the pane on screen', () => {
      const { setSidebarView, mobileView } = useSidebarPane(ref(true))

      setSidebarView('manager')
      expect(mobileView.value).toBe('manager')
    })
  })

  it('leaves the preview showing when a pane switch happens behind it', () => {
    // 'browser' means the sidebar is collapsed off-screen. Naming a pane there
    // would light up a navbar tab for something the user cannot see.
    localStorage.setItem('builderWorkspaceSidebarCollapsed', 'true')
    const { setSidebarView, mobileView, sidebarView } = useSidebarPane(ref(true))

    expect(mobileView.value).toBe('browser')
    setSidebarView('manager')
    expect(mobileView.value).toBe('browser')
    // ...but the pane waiting behind it did change.
    expect(sidebarView.value).toBe('manager')
  })

  describe('the navbar switcher', () => {
    it('offers all three views, each named in words', () => {
      // The switcher is the only way across on a phone — including out of the
      // preview, the one view with no masthead of its own — so every view has
      // to be reachable from it, and labelled the way its pane names itself.
      const { mobileViewOptions } = useSidebarPane(ref(true))

      expect(mobileViewOptions.map(o => o.value)).toEqual(['chat', 'manager', 'browser'])
      expect(mobileViewOptions.map(o => o.label)).toEqual(['Main agent', 'Subagents', 'Preview'])
    })

    it('tracks which view is selected, so the switcher can mark it', () => {
      const { selectMobileView, mobileView } = useSidebarPane(ref(true))

      selectMobileView('browser')
      expect(mobileView.value).toBe('browser')
      selectMobileView('manager')
      expect(mobileView.value).toBe('manager')
    })

    it('collapses the sidebar only for the preview', () => {
      const { selectMobileView } = useSidebarPane(ref(true))
      const collapsed: boolean[] = []
      const setCollapsed = (v: boolean) => collapsed.push(v)

      selectMobileView('browser', setCollapsed)
      selectMobileView('manager', setCollapsed)
      selectMobileView('chat', setCollapsed)

      expect(collapsed).toEqual([true, false, false])
    })

    it('keeps the desktop pane in step, so a rotation does not swap panes', () => {
      const { selectMobileView, sidebarView } = useSidebarPane(ref(true))

      selectMobileView('manager')
      expect(sidebarView.value).toBe('manager')

      // The preview is not one of the two panes, so it leaves them alone.
      selectMobileView('browser')
      expect(sidebarView.value).toBe('manager')
    })
  })

  describe('persistence', () => {
    it('reopens on the pane the user left it on', () => {
      const first = useSidebarPane(ref(false))
      first.setSidebarView('manager')

      const reopened = useSidebarPane(ref(false))
      expect(reopened.activeSidebarPane.value).toBe('manager')
    })

    it('starts on the preview when the sidebar was left collapsed', () => {
      localStorage.setItem('builderWorkspaceSidebarCollapsed', 'true')
      const { mobileView } = useSidebarPane(ref(true))
      expect(mobileView.value).toBe('browser')
    })
  })
})
