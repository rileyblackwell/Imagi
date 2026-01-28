import { defineStore } from 'pinia'

interface ThemeState {
  currentTheme: 'light' | 'dark' | 'system'
  effectiveTheme: 'light' | 'dark'
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
    currentTheme: 'system',
    effectiveTheme: 'dark',
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
    isDarkMode: (state): boolean => state.effectiveTheme === 'dark',
    isLightMode: (state): boolean => state.effectiveTheme === 'light',
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
      
      // Set data attribute for reference
      html.setAttribute('data-theme', this.currentTheme)
    },

    toggleTheme() {
      // Cycle through: system -> light -> dark -> system
      const themes: Array<'light' | 'dark' | 'system'> = ['system', 'light', 'dark']
      const currentIndex = themes.indexOf(this.currentTheme)
      const nextIndex = (currentIndex + 1) % themes.length
      this.setTheme(themes[nextIndex])
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