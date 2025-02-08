<template>
  <Form @submit="handleSubmit" v-slot="{ errors: formErrors, submitCount }" class="space-y-6">
    <!-- Username -->
    <div class="form-group">
      <label class="relative block">
        <span class="sr-only">Username</span>
        <span class="absolute inset-y-0 left-0 flex items-center pl-4">
          <font-awesome-icon icon="user" class="text-gray-400" />
        </span>
        <Field
          name="username"
          type="text"
          rules="required|username"
          v-slot="{ field, errorMessage }"
        >
          <input
            v-bind="field"
            :disabled="authStore.isLoading"
            placeholder="Username"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                   disabled:opacity-50 disabled:cursor-not-allowed"
            :class="{ 'border-red-500': errorMessage }"
          >
        </Field>
      </label>
      <ErrorMessage v-if="submitCount > 0" name="username" class="mt-1 text-sm text-red-500" />
    </div>

    <!-- Password -->
    <div class="form-group">
      <label class="relative block">
        <span class="sr-only">Password</span>
        <span class="absolute inset-y-0 left-0 flex items-center pl-4">
          <font-awesome-icon icon="lock" class="text-gray-400" />
        </span>
        <Field
          name="password"
          type="password"
          autocomplete="current-password"
          rules="required"
          v-slot="{ field, errorMessage }"
        >
          <input
            v-bind="field"
            :type="'password'"
            :disabled="authStore.isLoading"
            placeholder="Password"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                   disabled:opacity-50 disabled:cursor-not-allowed"
            :class="{ 'border-red-500': submitCount > 0 && errorMessage }"
          >
        </Field>
      </label>
      <ErrorMessage v-if="submitCount > 0" name="password" class="mt-1 text-sm text-red-500" />
    </div>

    <!-- Server Error Message -->
    <p v-if="serverError" class="text-center text-sm text-red-500">
      {{ serverError }}
    </p>

    <!-- Submit Button -->
    <button
      type="submit"
      :disabled="authStore.isLoading || Object.keys(formErrors).length > 0"
      class="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg
             focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors
             disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <span v-if="authStore.isLoading">
        <font-awesome-icon icon="circle-notch" spin class="mr-2" />
        Signing in...
      </span>
      <span v-else>Sign In</span>
    </button>
  </Form>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Form, Field, ErrorMessage } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/store/auth.js'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const serverError = ref('')

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

const handleSubmit = async (values, actions) => {
  serverError.value = ''
  
  try {
    await authStore.login(values)
    const redirectPath = route.query.redirect || '/'
    await router.push(redirectPath)
  } catch (error) {
    console.error('Login error:', error)
    serverError.value = getErrorMessage(error)
  }
}
</script>