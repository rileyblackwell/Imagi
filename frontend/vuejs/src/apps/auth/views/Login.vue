<template>
  <Form @submit="handleSubmit" v-slot="{ errors: formErrors }" class="space-y-6">
    <!-- Username -->
    <div class="form-group">
      <label class="relative block">
        <span class="sr-only">Username</span>
        <span class="absolute inset-y-0 left-0 flex items-center pl-4">
          <i class="fas fa-user text-gray-400"></i>
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
      <ErrorMessage name="username" class="mt-1 text-sm text-red-500" />
    </div>

    <!-- Password -->
    <div class="form-group">
      <label class="relative block">
        <span class="sr-only">Password</span>
        <span class="absolute inset-y-0 left-0 flex items-center pl-4">
          <i class="fas fa-lock text-gray-400"></i>
        </span>
        <Field
          name="password"
          type="password"
          rules="required"
          v-slot="{ field, errorMessage }"
        >
          <input
            v-bind="field"
            :disabled="authStore.isLoading"
            placeholder="Password"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                   disabled:opacity-50 disabled:cursor-not-allowed"
            :class="{ 'border-red-500': errorMessage }"
          >
        </Field>
      </label>
      <ErrorMessage name="password" class="mt-1 text-sm text-red-500" />
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
        <i class="fas fa-circle-notch fa-spin mr-2"></i>
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

const handleSubmit = async (values, actions) => {
  serverError.value = ''
  
  try {
    await authStore.login(values)
    const redirectPath = route.query.redirect || '/'
    await router.push(redirectPath)
  } catch (error) {
    console.error('Login error:', error)
    
    if (error.response?.status === 429) {
      serverError.value = 'Too many login attempts. Please try again later.'
      return
    }

    if (error.response?.status === 401) {
      serverError.value = 'Invalid username or password'
      return
    }

    serverError.value = 'Login failed. Please try again.'
  }
}
</script>