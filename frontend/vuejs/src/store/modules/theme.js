import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: 'dark',
    userPreferences: {
      fontSize: 'base',
      contrast: 'default',
      reducedMotion: false,
      customColors: null
    },
    availableThemes: ['light', 'dark', 'system'],
    fontSizes: ['sm', 'base', 'lg', 'xl'],
    contrastModes: ['default', 'high', 'low']
  }),

  getters: {
    isDarkMode: (state) => state.currentTheme === 'dark',
    isLightMode: (state) => state.currentTheme === 'light',
    isSystemTheme: (state) => state.currentTheme === 'system',
    currentFontSize: (state) => state.userPreferences.fontSize,
    currentContrast: (state) => state.userPreferences.contrast
  },

  actions: {
    setTheme(theme) {
      if (this.availableThemes.includes(theme)) {
        this.currentTheme = theme
        localStorage.setItem('theme', theme)
        this.applyTheme()
      }
    },

    initializeTheme() {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme && this.availableThemes.includes(savedTheme)) {
        this.currentTheme = savedTheme
      } else {
        // Default to system preference
        this.currentTheme = 'system'
      }
      this.applyTheme()
    },

    setFontSize(size) {
      if (this.fontSizes.includes(size)) {
        this.userPreferences.fontSize = size
        localStorage.setItem('fontSize', size)
        document.documentElement.setAttribute('data-font-size', size)
      }
    },

    setContrast(contrast) {
      if (this.contrastModes.includes(contrast)) {
        this.userPreferences.contrast = contrast
        localStorage.setItem('contrast', contrast)
        document.documentElement.setAttribute('data-contrast', contrast)
      }
    },

    setReducedMotion(enabled) {
      this.userPreferences.reducedMotion = enabled
      localStorage.setItem('reducedMotion', String(enabled))
      document.documentElement.setAttribute('data-reduced-motion', String(enabled))
    },

    setCustomColors(colors) {
      this.userPreferences.customColors = colors
      if (colors) {
        localStorage.setItem('customColors', JSON.stringify(colors))
        this.applyCustomColors()
      } else {
        localStorage.removeItem('customColors')
        this.removeCustomColors()
      }
    },

    applyTheme() {
      document.documentElement.setAttribute('data-theme', this.currentTheme)
      if (this.currentTheme === 'system') {
        // Remove explicit theme to follow system
        document.documentElement.removeAttribute('data-theme')
      }
    },

    applyCustomColors() {
      const colors = this.userPreferences.customColors
      if (colors) {
        Object.entries(colors).forEach(([key, value]) => {
          document.documentElement.style.setProperty(`--color-${key}`, value)
        })
      }
    },

    removeCustomColors() {
      const colors = this.userPreferences.customColors
      if (colors) {
        Object.keys(colors).forEach(key => {
          document.documentElement.style.removeProperty(`--color-${key}`)
        })
      }
    }
  }
}) 