<template>
  <Form @submit="handleSubmit" v-slot="{ errors: formErrors, submitCount }" class="space-y-6">
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
          :validateOnInput="false"
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

    <!-- Email -->
    <div class="form-group">
      <label class="relative block">
        <span class="sr-only">Email</span>
        <span class="absolute inset-y-0 left-0 flex items-center pl-4">
          <i class="fas fa-envelope text-gray-400"></i>
        </span>
        <Field
          name="email"
          type="email"
          rules="required|email"
          :validateOnInput="false"
          v-slot="{ field, errorMessage }"
        >
          <input
            v-bind="field"
            :disabled="authStore.isLoading"
            placeholder="Email"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                   disabled:opacity-50 disabled:cursor-not-allowed"
            :class="{ 'border-red-500': errorMessage }"
          >
        </Field>
      </label>
      <ErrorMessage v-if="submitCount > 0" name="email" class="mt-1 text-sm text-red-500" />
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
          autocomplete="new-password"
          rules="required"
          :validateOnInput="true"
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

    <!-- Confirm Password -->
    <div class="form-group">
      <label class="relative block">
        <span class="sr-only">Confirm Password</span>
        <span class="absolute inset-y-0 left-0 flex items-center pl-4">
          <i class="fas fa-lock text-gray-400"></i>
        </span>
        <Field
          name="password_confirmation"
          type="password"
          rules="required|confirmed:@password"
          :validateOnInput="true"
          v-slot="{ field, errorMessage }"
        >
          <input
            v-bind="field"
            :type="'password'"
            autocomplete="new-password"
            :disabled="authStore.isLoading"
            placeholder="Confirm Password"
            class="w-full py-3 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-lg text-white placeholder-gray-500
                   focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500
                   disabled:opacity-50 disabled:cursor-not-allowed"
            :class="{ 'border-red-500': errorMessage }"
          >
        </Field>
      </label>
      <ErrorMessage v-if="submitCount > 0" name="password_confirmation" class="mt-1 text-sm text-red-500" />
    </div>

    <!-- Terms Agreement -->
    <div class="flex items-start">
      <div class="flex items-center h-5">
        <Field
          name="agreeToTerms"
          type="checkbox"
          :value="true"
          v-slot="{ field }"
        >
          <input
            type="checkbox"
            :id="field.name"
            :name="field.name"
            :value="true"
            v-model="field.checked"
            @change="field.handleChange"
            :disabled="authStore.isLoading"
            class="w-4 h-4 border border-dark-600 rounded bg-dark-800 text-primary-600 focus:ring-primary-500
                   disabled:opacity-50 disabled:cursor-not-allowed"
          >
        </Field>
      </div>
      <div class="ml-3">
        <label for="agreeToTerms" class="text-sm text-gray-400">
          I agree to the 
          <router-link to="/terms" class="text-primary-400 hover:text-primary-300">Terms of Service</router-link>
          and
          <router-link to="/privacy" class="text-primary-400 hover:text-primary-300">Privacy Policy</router-link>
        </label>
        <ErrorMessage name="agreeToTerms" class="block mt-1 text-sm text-red-500" />
      </div>
    </div>

    <!-- Server Error Message -->
    <p v-if="serverError" class="text-center text-sm text-red-500">
      {{ serverError }}
    </p>

    <!-- Submit Button -->
    <button
      type="submit"
      :disabled="authStore.isLoading"
      class="w-full py-3 px-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg
             focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors
             disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <span v-if="authStore.isLoading">
        <i class="fas fa-circle-notch fa-spin mr-2"></i>
        Creating account...
      </span>
      <span v-else>Create Account</span>
    </button>
  </Form>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Form, Field, ErrorMessage, defineRule } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/store/auth.js'
import { EmailInput, PasswordInput, PasswordRequirements } from '@/apps/auth/components'

// Define custom validation rule
defineRule('confirmed', (value, [target]) => {
  if (value === target) {
    return true;
  }
  return 'Passwords must match';
});

const router = useRouter()
const authStore = useAuthStore()
const serverError = ref('')

const handleSubmit = async (values) => {
  serverError.value = ''
  
  try {
    const registrationData = {
      username: values.username,
      email: values.email,
      password: values.password,
      password_confirmation: values.password_confirmation,
      agreeToTerms: values.agreeToTerms
    }

    const result = await authStore.register(registrationData)
    
    if (result?.requiresVerification) {
      await router.push({
        name: 'verify-email',
        query: { email: values.email }
      })
    } else {
      await router.push('/')
    }
  } catch (error) {
    console.error('Registration error:', error)
    serverError.value = error.response?.data?.error || 'Registration failed. Please try again.'
  }
}
</script>