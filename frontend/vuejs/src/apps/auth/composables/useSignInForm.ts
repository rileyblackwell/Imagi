import { ref, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/index'
import { formatAuthError } from '../plugins/validation'
import { safeRedirect } from '../utils/redirect'
import type { LoginFormValues } from '../types/form'

/**
 * Everything the sign-in page does, apart from how it looks.
 *
 * Kept out of the view so the page's markup and styles can be redesigned
 * freely without touching the sign-in flow itself.
 */
export function useSignInForm() {
  const router = useRouter()
  const route = useRoute()
  const authStore = useAuthStore()
  const serverError = ref('')
  const isSubmitting = ref(false)

  // Clear any auth errors when the page goes away
  onBeforeUnmount(() => {
    authStore.clearError()
  })

  const onSubmit = async (values: LoginFormValues) => {
    serverError.value = ''
    isSubmitting.value = true

    try {
      const username = values.username?.trim()
      // Never trimmed: spaces are legal in a password, and registration keeps
      // them, so trimming here would lock those accounts out.
      const password = values.password

      if (!username || !password) {
        serverError.value = 'Username and password are required'
        return
      }

      document.body.style.cursor = 'wait'

      await authStore.login({ username, password })

      // Back to the page that asked for sign-in, if it is one of ours.
      await router.push(safeRedirect(route.query.redirect))
    } catch (error: unknown) {
      serverError.value = formatAuthError(error)
    } finally {
      isSubmitting.value = false
      document.body.style.cursor = 'default'
    }
  }

  return { authStore, serverError, isSubmitting, onSubmit }
}
