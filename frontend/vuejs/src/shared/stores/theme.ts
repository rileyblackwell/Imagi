import { defineStore } from 'pinia'

interface ThemeState {
  currentTheme: 'light' | 'dark' | 'system'
  effectiveTheme: 'light' | 'dark'
  availableThemes: string[]
}

export const useThemeStore = defineStore('theme', {
  state: (): ThemeState => ({
    currentTheme: 'system',
    effectiveTheme: 'dark',
    availableThemes: ['light', 'dark', 'system']
  }),

  actions: {
    setTheme(theme: 'light' | 'dark' | 'system') {
      if (this.availableThemes.includes(theme)) {
        this.currentTheme = theme
        localStorage.setItem('theme', theme)
        this.applyTheme()
      }
    },

    initializeTheme() {
      // Check for saved theme preference, default to system
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme && this.availableThemes.includes(savedTheme)) {
        this.currentTheme = savedTheme as 'light' | 'dark' | 'system'
      } else {
        this.currentTheme = 'system'
      }
      
      // Set up system theme listener
      this.setupSystemThemeListener()
      
      // Apply the theme
      this.applyTheme()
    },

    setupSystemThemeListener() {
      // Listen for system theme changes
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
      
      const handleSystemThemeChange = (e: MediaQueryListEvent | MediaQueryList) => {
        if (this.currentTheme === 'system') {
          this.effectiveTheme = e.matches ? 'dark' : 'light'
          this.updateDOMTheme()
        }
      }

      // Initial check
      handleSystemThemeChange(mediaQuery)
      
      // Listen for changes
      mediaQuery.addEventListener('change', handleSystemThemeChange)
    },

    getSystemTheme(): 'light' | 'dark' {
      // Check system preference
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark'
      }
      return 'light'
    },

    applyTheme() {
      // Determine the effective theme
      if (this.currentTheme === 'system') {
        this.effectiveTheme = this.getSystemTheme()
      } else {
        this.effectiveTheme = this.currentTheme
      }
      
      this.updateDOMTheme()
    },

    updateDOMTheme() {
      // Apply the theme to the DOM
      const html = document.documentElement
      
      if (this.effectiveTheme === 'dark') {
        html.classList.add('dark')
        html.classList.remove('light')
      } else {
        html.classList.add('light')
        html.classList.remove('dark')
      }

      // Keep native UI (scrollbars, form controls) in sync with the theme
      html.style.colorScheme = this.effectiveTheme

      // Set data attribute for reference
      html.setAttribute('data-theme', this.currentTheme)
    }
  }
})