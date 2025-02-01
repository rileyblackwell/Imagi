import { defineStore } from 'pinia'

export const useUIStore = defineStore('ui', {
  state: () => ({
    isSidebarOpen: true,
    isMobileMenuOpen: false,
    activeModals: [],
    screenSize: 'desktop',
    scrollPosition: 0,
    isScrollLocked: false
  }),

  getters: {
    isMobile: (state) => state.screenSize === 'mobile',
    isTablet: (state) => state.screenSize === 'tablet',
    isDesktop: (state) => state.screenSize === 'desktop',
    hasActiveModals: (state) => state.activeModals.length > 0
  },

  actions: {
    toggleSidebar() {
      this.isSidebarOpen = !this.isSidebarOpen
    },

    toggleMobileMenu() {
      this.isMobileMenuOpen = !this.isMobileMenuOpen
    },

    setScreenSize(size) {
      this.screenSize = size
    },

    updateScrollPosition(position) {
      this.scrollPosition = position
    },

    openModal(modalId) {
      if (!this.activeModals.includes(modalId)) {
        this.activeModals.push(modalId)
        this.isScrollLocked = true
      }
    },

    closeModal(modalId) {
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