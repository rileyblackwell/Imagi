// Types for the Home store

export interface ContactForm {
  name: string
  email: string
  subject: string
  message: string
}

export interface HomeState {
  isLoading: boolean
  error: string | null
  showFeatureHighlights: boolean
  contactForm: ContactForm
}
