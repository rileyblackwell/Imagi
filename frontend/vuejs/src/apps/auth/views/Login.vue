<template>
  <div class="space-y-5">
    <Form @submit="handleSubmit" v-slot="{ errors: formErrors, submitCount }" class="space-y-5">
      <FormInput
        name="username"
        label="Username"
        icon="fas fa-user"
        rules="required"
        placeholder="Enter your username"
        :disabled="authStore.isLoading"
        :showError="submitCount > 0 && hasAttemptedSubmit"
        v-model="username"
        class="auth-input min-h-[42px]"
      />

      <PasswordInput
        name="password"
        v-model="password"
        placeholder="Enter your password"
        :disabled="authStore.isLoading"
        required
        rules="required"
        :showError="submitCount > 0 && hasAttemptedSubmit"
        class="auth-input min-h-[42px]"
      />

      <!-- Error message display -->
      <div class="space-y-5 pt-2">
        <div v-if="serverError && hasAttemptedSubmit" 
             class="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p class="text-sm font-medium text-red-400 text-center whitespace-pre-line">
            {{ serverError }}
          </p>
        </div>

        <GradientButton
          type="submit"
          :disabled="authStore.isLoading || (Object.keys(formErrors).length > 0 && hasAttemptedSubmit)"
          :loading="authStore.isLoading"
          loading-text="Signing in..."
          class="w-full"
        >
          Sign In
        </GradientButton>
      </div>
    </Form>

    <AuthLinks class="pt-2" />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Form } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/store/auth.js'
import { 
  PasswordInput,
  FormInput,
  GradientButton,
  AuthLinks 
} from '@/apps/auth/components'
import { formatAuthError } from '../utils/errorHandling'

interface LoginFormValues {
  username?: string;
  password?: string;
  [key: string]: unknown;
}

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const serverError = ref('')
const hasAttemptedSubmit = ref(false)
const password = ref('')
const username = ref('')

const handleSubmit = async (values: LoginFormValues) => {
  hasAttemptedSubmit.value = true
  serverError.value = ''
  
  try {
    const credentials = {
      username: values.username?.trim(),
      password: values.password?.trim() || password.value?.trim()
    }

    if (!credentials.username || !credentials.password) {
      serverError.value = `Missing ${!credentials.username ? 'username' : 'password'}`
      return
    }

    await authStore.login(credentials)
    const redirectPath = (route.query.redirect as string) || '/'
    await router.push(redirectPath)
  } catch (error: unknown) {
    console.error('Login error:', error)
    if (error instanceof Error) {
      serverError.value = error.message
    } else {
      serverError.value = 'Login failed'
    }
  }
}

// Clear error when user starts typing again
watch([username, password], () => {
  if (hasAttemptedSubmit.value && serverError.value) {
    serverError.value = ''
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>