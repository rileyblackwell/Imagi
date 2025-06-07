import { defineStore } from 'pinia'

import type { ContactForm, HomeState } from '../types/home'

export const useHomeStore = defineStore('home', {
  state: (): HomeState => ({
    // UI state
    isLoading: false,
    error: null,
    // Feature flags and preferences
    showFeatureHighlights: true,
    // Contact form state
    contactForm: {
      name: '',
      email: '',
      subject: '',
      message: ''
    }
  }),

  getters: {
    hasError: (state: HomeState): boolean => !!state.error,
    isContactFormValid: (state: HomeState): boolean => {
      const { name, email, subject, message } = state.contactForm
      return !!(name && email && subject && message)
    }
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
    },

    // Contact form actions
    updateContactForm(field: keyof ContactForm, value: string) {
      this.contactForm[field] = value
    },

    resetContactForm() {
      this.contactForm = {
        name: '',
        email: '',
        subject: '',
        message: ''
      }
    },

    async submitContactForm(): Promise<boolean> {
      try {
        this.setLoading(true)
        this.clearError()
        // TODO: Implement API call to submit form
        // const response = await homeService.submitContactForm(this.contactForm)
        this.resetContactForm()
        return true
      } catch (error: any) {
        this.setError(error.message || 'Failed to submit contact form')
        return false
      } finally {
        this.setLoading(false)
      }
    }
  }
})
