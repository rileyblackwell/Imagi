import { defineStore } from 'pinia'

interface UIState {
  isSidebarOpen: boolean
  isMobileMenuOpen: boolean
  activeModals: string[]
  screenSize: 'mobile' | 'tablet' | 'desktop'
  scrollPosition: number
  isScrollLocked: boolean
}

export const useUIStore = defineStore('ui', {
  state: (): UIState => ({
    isSidebarOpen: true,
    isMobileMenuOpen: false,
    activeModals: [],
    screenSize: 'desktop',
    scrollPosition: 0,
    isScrollLocked: false
  }),

  getters: {
    isMobile: (state): boolean => state.screenSize === 'mobile',
    isTablet: (state): boolean => state.screenSize === 'tablet',
    isDesktop: (state): boolean => state.screenSize === 'desktop',
    hasActiveModals: (state): boolean => state.activeModals.length > 0
  },

  actions: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen
    },

    toggleMobileMenu() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen
    },

    setScreenSize(size: 'mobile' | 'tablet' | 'desktop') {
      this.screenSize = size
    },

    updateScrollPosition(position: number) {
      this.scrollPosition = position
    },

    openModal(modalId: string) {
      if (!this.activeModals.includes(modalId)) {
        this.activeModals.push(modalId)
        this.isScrollLocked = true
      }
    },

    closeModal(modalId: string) {
      this.activeModals = this.activeModals.filter(id => id !== modalId)
      if (this.activeModals.length === 0) {
        this.isScrollLocked = false
      }
    },

    closeAllModals() {
      this.activeModals = []
      this.isScrollLocked = false
    }
  }
}) 