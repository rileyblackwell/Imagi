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
        :showError="submitCount > 0"
        class="auth-input min-h-[42px]"
      />

      <PasswordInput
        name="password"
        v-model="password"
        placeholder="Enter your password"
        :disabled="authStore.isLoading"
        required
        class="auth-input min-h-[42px]"
      />

      <!-- Error and button container -->
      <div class="space-y-5 pt-2">
        <div v-if="serverError" 
             class="p-3 bg-red-500/5 border border-red-500/10 rounded-xl">
          <p class="text-sm font-medium text-red-400 text-center">
            {{ serverError }}
          </p>
        </div>

        <GradientButton
          type="submit"
          :disabled="authStore.isLoading || Object.keys(formErrors).length > 0"
          :loading="authStore.isLoading"
          loading-text="Signing in..."
          class="w-full py-3 text-sm font-medium"
        >
          Sign In
        </GradientButton>
      </div>
    </Form>

    <AuthLinks class="pt-2" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Form } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/store/auth.js'
import { 
  PasswordInput,
  FormInput,
  GradientButton,
  AuthLinks 
} from '@/apps/auth/components'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const serverError = ref('')
const password = ref('')

const getErrorMessage = (error) => {
  if (error.response?.status === 429) {
    return 'Too many login attempts. Please try again in a few minutes.'
  }
  
  if (error.response?.status === 401) {
    if (error.response?.data?.detail?.includes('password')) {
      return 'Password is incorrect. Please try again.'
    }
    if (error.response?.data?.detail?.includes('username')) {
      return 'Username not found. Please check your username.'
    }
    return 'Invalid username or password. Please try again.'
  }

  if (error.response?.status === 403) {
    return 'Your account has been temporarily locked. Please try again later or contact support.'
  }

  if (error.response?.status === 400) {
    const errors = error.response.data;
    if (errors.username) return `Username error: ${errors.username[0]}`
    if (errors.password) return `Password error: ${errors.password[0]}`
    return 'Please check your login information and try again.'
  }

  if (error.message?.includes('Network Error')) {
    return 'Unable to connect to server. Please check your internet connection.'
  }

  return 'An error occurred during login. Please try again.'
}

const handleSubmit = async (values) => {
  serverError.value = ''
  
  try {
    await authStore.login({
      ...values,
      password: password.value
    })
    const redirectPath = route.query.redirect || '/'
    await router.push(redirectPath)
  } catch (error) {
    console.error('Login error:', error)
    serverError.value = getErrorMessage(error)
  }
}
</script>