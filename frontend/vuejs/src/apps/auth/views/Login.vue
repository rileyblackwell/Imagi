<template>
  <div class="space-y-5">
    <Form v-slot="{ errors: formErrors, submitCount, submitForm, values }" class="space-y-6" @submit="onSubmit">
      <!-- Username input with enhanced styling -->
      <div class="relative">
        <Field name="username" rules="login_username" :validateOnBlur="false" v-slot="{ errorMessage, field }">
          <FormInput
            v-bind="field"
            name="username"
            label="Username"
            icon="fas fa-user"
            placeholder="Enter your username"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && submitCount > 0"
            v-model="formData.username"
            class="auth-input min-h-[42px] sm:min-h-[48px] shadow-sm hover:shadow-md transition-shadow duration-300"
          />
        </Field>
      </div>

      <!-- Password input with enhanced styling -->
      <div class="relative">
        <Field name="password" rules="login_password" :validateOnBlur="false" v-slot="{ errorMessage, field }">
          <PasswordInput
            v-bind="field"
            name="password"
            v-model="formData.password"
            placeholder="Enter your password"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && submitCount > 0"
            class="auth-input min-h-[42px] sm:min-h-[48px] shadow-sm hover:shadow-md transition-shadow duration-300"
          />
        </Field>
      </div>

      <!-- Enhanced error message display with animation -->
      <div class="space-y-5 pt-2">
        <transition name="fade-up">
          <div v-if="serverError" 
               class="p-4 bg-red-500/10 border border-red-500/20 rounded-xl backdrop-blur-sm
                      shadow-inner transition-all duration-300">
            <p class="text-sm font-medium text-red-400 text-center whitespace-pre-line">
              {{ serverError }}
            </p>
          </div>
        </transition>

        <!-- Elevated button with enhanced styling -->
        <GradientButton
          type="submit"
          :disabled="authStore.loading || isSubmitting"
          :loading="authStore.loading || isSubmitting"
          loading-text="Signing in..."
          class="w-full min-h-[48px] sm:min-h-[52px] mt-4"
        >
          Sign In
        </GradientButton>
      </div>
    </Form>

    <!-- AuthLinks with animations removed -->
    <div class="pt-4">
      <AuthLinks />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Form, Field, ErrorMessage } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/stores/index'
import { formatAuthError } from '@/apps/auth/plugins/validation'
import type { LoginFormValues } from '@/apps/auth/types/form'
import { AuthAPI } from '@/apps/auth/services/api'

import { 
  PasswordInput,
  FormInput,
  GradientButton,
  AuthLinks 
} from '@/apps/auth/components' // Barrel already updated, so this is fine

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const serverError = ref('')
const hasAttemptedSubmit = ref(false)
const isSubmitting = ref(false)

const formData = reactive({
  username: '',
  password: ''
})

// Check backend health when component mounts
onMounted(async () => {
  try {
    await AuthAPI.healthCheck()
  } catch (error: any) {
    console.warn('🚨 Auth API health check failed on login page load:', {
      error: error.message,
      stack: error.stack,
      response: error.response,
      timestamp: new Date().toISOString()
    })
  }
})

// Clear error when username or password changes
watch([() => formData.username, () => formData.password], () => {
  if (serverError.value) {
    serverError.value = ''
  }
})

// Clear any auth errors when component is unmounted
onBeforeUnmount(() => {
  authStore.clearError()
})

const onSubmit = async (values: LoginFormValues) => {
  // Set form data from values if empty
  if (!formData.username && values.username) {
    formData.username = values.username
  }
  
  if (!formData.password && values.password) {
    formData.password = values.password
  }
  
  serverError.value = ''
  isSubmitting.value = true
  
  try {
    // Get values either from form values or from local formData
    const username = formData.username.trim()
    const password = formData.password.trim()
    
    // Validate input - ensure both fields are filled
    if (!username || !password) {
      serverError.value = 'Username and password are required'
      isSubmitting.value = false
      return
    }

    const loginData = {
      username,
      password
    }

    // Show loading state in UI
    document.body.style.cursor = 'wait'
    
    await authStore.login(loginData)
    
    // Check if there's a redirect parameter to navigate to
    const redirectPath = route.query.redirect as string
    if (redirectPath) {
      await router.push(redirectPath)
    } else {
      // Default redirect to home
      await router.push({ path: '/' })
    }
  } catch (error: unknown) {
    serverError.value = formatAuthError(error, 'login')
  } finally {
    isSubmitting.value = false
    document.body.style.cursor = 'default'
  }
}
</script>

<style scoped>
/* Only keeping essential transitions for error messages */
.fade-up-enter-active,
.fade-up-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-up-enter-from,
.fade-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>