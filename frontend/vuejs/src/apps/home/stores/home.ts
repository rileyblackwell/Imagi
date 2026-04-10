import { defineStore } from 'pinia'

import type { HomeState } from '../types/home'

export const useHomeStore = defineStore('home', {
  state: (): HomeState => ({
    // UI state
    isLoading: false,
    error: null,
    // Feature flags and preferences
    showFeatureHighlights: true
  }),

  getters: {
    hasError: (state: HomeState): boolean => !!state.error
  },

  actions: {
    setLoading(loading: boolean) {
      this.isLoading = loading
    },

    setError(error: string) {
      this.error = error
    },

    clearError() {
      this.error = null
    },

    toggleFeatureHighlights() {
      this.showFeatureHighlights = !this.showFeatureHighlights
    }
  }
})
