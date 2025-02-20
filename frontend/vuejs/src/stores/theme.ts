import { defineStore } from 'pinia'

interface ThemeState {
  currentTheme: 'light' | 'dark' | 'system'
  userPreferences: {
    fontSize: 'sm' | 'base' | 'lg' | 'xl'
    contrast: 'default' | 'high' | 'low'
    reducedMotion: boolean
    customColors: Record<string, string> | null
  }
  availableThemes: string[]
  fontSizes: string[]
  contrastModes: string[]
}

export const useThemeStore = defineStore('theme', {
  state: (): ThemeState => ({
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
    isDarkMode: (state): boolean => state.currentTheme === 'dark',
    isLightMode: (state): boolean => state.currentTheme === 'light',
    isSystemTheme: (state): boolean => state.currentTheme === 'system',
    currentFontSize: (state): string => state.userPreferences.fontSize,
    currentContrast: (state): string => state.userPreferences.contrast
  },

  actions: {
    setTheme(theme: 'light' | 'dark' | 'system') {
      if (this.availableThemes.includes(theme)) {
        this.currentTheme = theme
        localStorage.setItem('theme', theme)
        this.applyTheme()
      }
    },

    initializeTheme() {
      const savedTheme = localStorage.getItem('theme')
      if (savedTheme && this.availableThemes.includes(savedTheme)) {
        this.currentTheme = savedTheme as 'light' | 'dark' | 'system'
      } else {
        this.currentTheme = 'system'
      }
      this.applyTheme()
    },

    setFontSize(size: 'sm' | 'base' | 'lg' | 'xl') {
      if (this.fontSizes.includes(size)) {
        this.userPreferences.fontSize = size
        localStorage.setItem('fontSize', size)
        document.documentElement.setAttribute('data-font-size', size)
      }
    },

    setContrast(contrast: 'default' | 'high' | 'low') {
      if (this.contrastModes.includes(contrast)) {
        this.userPreferences.contrast = contrast
        localStorage.setItem('contrast', contrast)
        document.documentElement.setAttribute('data-contrast', contrast)
      }
    },

    setReducedMotion(enabled: boolean) {
      this.userPreferences.reducedMotion = enabled
      localStorage.setItem('reducedMotion', String(enabled))
      document.documentElement.setAttribute('data-reduced-motion', String(enabled))
    },

    setCustomColors(colors: Record<string, string> | null) {
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