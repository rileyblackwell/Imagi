<template>
  <Form @submit="handleSubmit" v-slot="{ errors: formErrors, submitCount }" class="space-y-6">
    <!-- Username -->
    <div class="form-group">
      <label class="relative block">
        <span class="sr-only">Username</span>
        <span class="absolute inset-y-0 left-0 flex items-center pl-4">
          <i class="fas fa-user text-gray-400 group-hover:text-primary-300 
                   group-focus-within:text-primary-300 transition-colors duration-500"></i>
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
            placeholder="Create a username"
            class="w-full py-3.5 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-xl 
                   text-white placeholder-gray-500 outline-none focus:ring-0
                   focus:border-primary-400 disabled:opacity-50 disabled:cursor-not-allowed 
                   transition-all duration-500 ease-out hover:border-primary-400/50
                   hover:bg-dark-800/80"
            :class="{ 'border-red-500': errorMessage }"
          >
        </Field>
      </label>
      <ErrorMessage v-if="submitCount > 0" name="username" class="mt-2 text-sm text-red-400" />
    </div>

    <!-- Email -->
    <div class="form-group">
      <label class="relative block">
        <span class="sr-only">Email</span>
        <span class="absolute inset-y-0 left-0 flex items-center pl-4">
          <i class="fas fa-envelope text-gray-400 group-hover:text-primary-300 
                   group-focus-within:text-primary-300 transition-colors duration-500"></i>
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
            placeholder="Enter your email"
            class="w-full py-3.5 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-xl 
                   text-white placeholder-gray-500 outline-none focus:ring-0
                   focus:border-primary-400 disabled:opacity-50 disabled:cursor-not-allowed 
                   transition-all duration-500 ease-out hover:border-primary-400/50
                   hover:bg-dark-800/80"
            :class="{ 'border-red-500': errorMessage }"
          >
        </Field>
      </label>
      <ErrorMessage v-if="submitCount > 0" name="email" class="mt-2 text-sm text-red-400" />
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
            class="w-full py-3.5 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-xl 
                   text-white placeholder-gray-500 outline-none focus:ring-0
                   focus:border-primary-400 disabled:opacity-50 disabled:cursor-not-allowed 
                   transition-all duration-500 ease-out hover:border-primary-400/50
                   hover:bg-dark-800/80"
            :class="{ 'border-red-500': submitCount > 0 && errorMessage }"
          >
        </Field>
      </label>
      <ErrorMessage v-if="submitCount > 0" name="password" class="mt-2 text-sm text-red-400" />
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
            class="w-full py-3.5 pl-11 pr-4 bg-dark-800 border border-dark-700 rounded-xl 
                   text-white placeholder-gray-500 outline-none focus:ring-0
                   focus:border-primary-400 disabled:opacity-50 disabled:cursor-not-allowed 
                   transition-all duration-500 ease-out hover:border-primary-400/50
                   hover:bg-dark-800/80"
            :class="{ 'border-red-500': errorMessage }"
          >
        </Field>
      </label>
      <ErrorMessage v-if="submitCount > 0" name="password_confirmation" class="mt-2 text-sm text-red-400" />
    </div>

    <!-- Terms Agreement -->
    <div class="flex items-start p-4 rounded-xl bg-dark-800/50 border border-dark-700 
                hover:border-primary-400/30 transition-duration-300">
      <div class="flex items-center h-5">
        <Field
          name="agreeToTerms"
          type="checkbox"
          :value="true"
          v-slot="{ field }"
        >
          <input
            type="checkbox"
            v-bind="field"
            :disabled="authStore.isLoading"
            class="w-4 h-4 border border-dark-600 rounded bg-dark-800 text-primary-500 
                   focus:ring-primary-400/50 focus:ring-offset-0 focus:ring-2
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-all duration-300"
          >
        </Field>
      </div>
      <div class="ml-3">
        <label class="text-sm text-gray-300">
          I agree to the 
          <router-link to="/terms" class="text-primary-400 hover:text-primary-300 transition-colors duration-300">
            Terms of Service
          </router-link>
          and
          <router-link to="/privacy" class="text-primary-400 hover:text-primary-300 transition-colors duration-300">
            Privacy Policy
          </router-link>
        </label>
        <ErrorMessage name="agreeToTerms" class="block mt-1 text-sm text-red-400" />
      </div>
    </div>

    <!-- Server Error Message -->
    <div v-if="serverError" 
         class="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
      <p class="text-sm font-medium text-red-400 text-center">{{ serverError }}</p>
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
        <span class="font-medium">Creating account...</span>
      </span>
      <span v-else class="flex items-center justify-center space-x-2 relative z-10">
        <span class="font-medium">Create Account</span>
        <i class="fas fa-arrow-right transform transition-transform duration-500 
                  group-hover:translate-x-1"></i>
      </span>
    </button>
  </Form>

  <!-- Navigation Links -->
  <div class="mt-6 sm:mt-8 space-y-4 sm:space-y-6">
    <!-- Divider -->
    <div class="relative">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t border-dark-700/50"></div>
      </div>
      <div class="relative flex justify-center text-sm">
        <span class="px-4 bg-dark-800/50 text-gray-400">or</span>
      </div>
    </div>

    <!-- Links Section -->
    <div class="text-center space-y-4 sm:space-y-6">
      <!-- Login Link -->
      <div>
        <p class="text-gray-300 text-sm sm:text-base">
          Already have an account?
          <router-link 
            to="/auth/login" 
            class="text-primary-400 hover:text-primary-300 font-medium transition-colors duration-300"
          >
            Sign in here
          </router-link>
        </p>
      </div>

      <!-- Home Link -->
      <router-link 
        to="/" 
        class="inline-flex items-center gap-2 px-3 sm:px-4 py-2 rounded-lg text-gray-400 
               hover:text-white transition-all duration-300 group hover:bg-dark-700/50
               text-sm sm:text-base"
      >
        <i class="fas fa-arrow-left text-xs sm:text-sm transform group-hover:-translate-x-1 transition-transform"></i>
        Back to Home
      </router-link>
    </div>
  </div>
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