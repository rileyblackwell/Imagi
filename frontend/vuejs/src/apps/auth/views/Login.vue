<template>
  <div class="space-y-5 sm:space-y-6">
    <Form @submit="handleSubmit" v-slot="{ errors: formErrors, submitCount }" class="space-y-5">
      <!-- Username -->
      <div class="form-group">
        <label class="relative block">
          <span class="sr-only">Username</span>
          <span class="absolute inset-y-0 left-0 flex items-center pl-4">
            <i class="fas fa-user text-gray-400 group-hover:text-primary-400 transition-colors duration-300"></i>
          </span>
          <Field
            name="username"
            type="text"
            rules="required|username"
            :validateOnInput="false"
            v-slot="{ field, errorMessage }"
          >
            <input
              v-bind="field"
              :disabled="authStore.isLoading"
              placeholder="Username"
              class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg 
                     text-white placeholder-gray-500 outline-none focus:ring-0
                     focus:border-primary-400 disabled:opacity-50 disabled:cursor-not-allowed 
                     transition-all duration-500 ease-out hover:border-primary-400/50
                     hover:bg-dark-800/80"
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
            <i class="fas fa-lock text-gray-400 group-hover:text-primary-400 transition-colors duration-300"></i>
          </span>
          <Field
            name="password"
            type="password"
            :rules="passwordRules"
            :validateOnInput="false"
            v-slot="{ field, errorMessage }"
          >
            <input
              v-bind="field"
              type="password"
              :disabled="authStore.isLoading"
              placeholder="Password"
              class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg 
                     text-white placeholder-gray-500 outline-none focus:ring-0
                     focus:border-primary-400 disabled:opacity-50 disabled:cursor-not-allowed 
                     transition-all duration-500 ease-out hover:border-primary-400/50
                     hover:bg-dark-800/80"
              :class="{ 'border-red-500': submitCount > 0 && errorMessage }"
            >
          </Field>
        </label>
        <ErrorMessage v-if="submitCount > 0" name="password" class="mt-1 text-sm text-red-500" />
      </div>

      <!-- Server Error Message -->
      <div v-if="serverError" 
           class="p-3 sm:p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
        <p class="text-xs sm:text-sm font-medium text-red-400 text-center">
          {{ serverError }}
        </p>
      </div>

      <!-- Submit Button -->
      <button
        type="submit"
        :disabled="authStore.isLoading || Object.keys(formErrors).length > 0"
        class="w-full bg-gradient-to-r from-primary-600 via-primary-500 to-primary-400 
               hover:from-primary-500 hover:via-primary-400 hover:to-primary-300 
               text-white font-semibold py-4 px-6 rounded-xl 
               transition-all duration-500 transform hover:-translate-y-0.5 hover:scale-[1.02] 
               flex items-center justify-center text-base disabled:opacity-50 
               disabled:cursor-not-allowed disabled:hover:translate-y-0 disabled:hover:scale-100
               shadow-[0_8px_16px_-6px_rgba(59,130,246,0.3)] 
               hover:shadow-[0_12px_20px_-6px_rgba(59,130,246,0.4)]
               border border-primary-500/20 hover:border-primary-400/40
               backdrop-blur-sm relative overflow-hidden group"
      >
        <div class="absolute inset-0 bg-gradient-to-r from-primary-400/10 to-violet-400/10 
                    group-hover:from-primary-400/20 group-hover:to-violet-400/20 
                    transition-all duration-500"></div>
        <span v-if="authStore.isLoading" class="flex items-center justify-center relative z-10">
          <i class="fas fa-circle-notch fa-spin mr-2"></i>
          <span class="font-medium">Signing in...</span>
        </span>
        <span v-else class="flex items-center justify-center space-x-2 relative z-10">
          <span class="font-medium">Sign In</span>
          <i class="fas fa-arrow-right transform transition-transform duration-500 
                    group-hover:translate-x-1"></i>
        </span>
      </button>
    </Form>

    <!-- Navigation Links -->
    <AuthLinks class="mt-6 sm:mt-8" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Form, Field, ErrorMessage } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/store/auth.js'
import { EmailInput, PasswordInput, AuthLinks } from '@/apps/auth/components'

// Change the validation rule for password field
const passwordRules = 'required' // Remove the |password part since we don't need password validation on login

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