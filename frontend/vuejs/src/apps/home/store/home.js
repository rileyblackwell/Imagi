import { defineStore } from 'pinia'

export const useHomeStore = defineStore('home', {
  state: () => ({
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
    hasError: (state) => !!state.error,
    isContactFormValid: (state) => {
      const { name, email, subject, message } = state.contactForm
      return name && email && subject && message
    }
  },

  actions: {
    setLoading(loading) {
      this.isLoading = loading
    },

    setError(error) {
      this.error = error
    },

    clearError() {
      this.error = null
    },

    toggleFeatureHighlights() {
      this.showFeatureHighlights = !this.showFeatureHighlights
    },

    // Contact form actions
    updateContactForm(field, value) {
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

    async submitContactForm() {
      try {
        this.setLoading(true)
        this.clearError()
        
        // TODO: Implement API call to submit form
        // const response = await homeService.submitContactForm(this.contactForm)
        
        this.resetContactForm()
        return true
      } catch (error) {
        this.setError(error.message || 'Failed to submit contact form')
        return false
      } finally {
        this.setLoading(false)
      }
    }
  }
}) 