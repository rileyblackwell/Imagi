import { ref, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/index'
import { formatAuthError } from '../plugins/validation'
import type { RegisterFormValues } from '../types/form'

interface RegisterFormOptions {
  /** Whether the form carries a terms-of-service checkbox that must be ticked. */
  requireTerms?: boolean
}

/**
 * Everything the register page does, apart from how it looks.
 *
 * Kept out of the view so the page's markup and styles can be redesigned
 * freely without touching account creation itself.
 */
export function useRegisterForm({ requireTerms = true }: RegisterFormOptions = {}) {
  const router = useRouter()
  const authStore = useAuthStore()
  const serverError = ref('')
  const isSubmitting = ref(false)
  const hasAcceptedTerms = ref(false)

  // Clear any auth errors when the page goes away
  onBeforeUnmount(() => {
    authStore.clearError()
  })

  const onSubmit = async (values: RegisterFormValues) => {
    serverError.value = ''
    isSubmitting.value = true

    try {
      const username = values.username?.trim()
      const email = values.email?.trim()
      const password = values.password
      const passwordConfirmation = values.password_confirmation
      const agreeToTerms = values.agreeToTerms === true
      hasAcceptedTerms.value = agreeToTerms

      if (!username || !email || !password) {
        serverError.value = 'Please fill in all required fields'
        return
      }

      if (requireTerms && !agreeToTerms) {
        serverError.value = 'You must accept the Terms of Service and Privacy Policy to continue'
        return
      }

      if (password !== passwordConfirmation) {
        serverError.value = 'Passwords do not match'
        return
      }

      if (password.length < 8) {
        serverError.value = 'Password must be at least 8 characters long'
        return
      }

      document.body.style.cursor = 'wait'

      await authStore.register({
        username,
        email,
        password,
        password_confirmation: passwordConfirmation,
        terms_accepted: agreeToTerms
      })

      await router.push('/')
    } catch (error: unknown) {
      serverError.value = formatAuthError(error)
    } finally {
      isSubmitting.value = false
      document.body.style.cursor = 'default'
    }
  }

  return { authStore, serverError, isSubmitting, hasAcceptedTerms, onSubmit }
}
