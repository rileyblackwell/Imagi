<template>
  <div class="space-y-6">
    <Form v-slot="{ errors: formErrors, submitCount, submitForm, values }" class="space-y-5" @submit="onSubmit">
      <!-- Username input with premium styling -->
      <div class="relative group">
        <Field name="username" rules="login_username" :validateOnBlur="false" v-slot="{ errorMessage, field }">
          <FormInput
            :modelValue="field.value || ''"
            @update:modelValue="field.onChange"
            @blur="field.onBlur"
            name="username"
            label="Username"
            icon="fas fa-user"
            placeholder="Enter your username"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && submitCount > 0"
          />
        </Field>
      </div>

      <!-- Password input with premium styling -->
      <div class="relative group">
        <Field name="password" rules="login_password" :validateOnBlur="false" v-slot="{ errorMessage, field }">
          <PasswordInput
            :modelValue="field.value || ''"
            @update:modelValue="field.onChange"
            @blur="field.onBlur"
            name="password"
            placeholder="Enter your password"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && submitCount > 0"
          />
        </Field>
      </div>

      <!-- Error message display -->
      <div class="space-y-5 pt-2">
        <transition name="fade-up">
          <div v-if="serverError" 
               class="p-4 rounded-xl border border-red-500/20 bg-red-50 dark:bg-red-500/10 backdrop-blur-sm transition-colors duration-300">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-500/20 border border-red-200 dark:border-red-500/30 flex items-center justify-center flex-shrink-0 transition-colors duration-300">
                <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400 text-sm transition-colors duration-300"></i>
              </div>
              <p class="text-sm font-medium text-red-600 dark:text-red-400 whitespace-pre-line transition-colors duration-300">
                {{ serverError }}
              </p>
            </div>
          </div>
        </transition>

        <!-- Premium gradient button -->
        <GradientButton
          type="submit"
          :disabled="authStore.loading || isSubmitting"
          :loading="authStore.loading || isSubmitting"
          loading-text="Signing in..."
          class="w-full"
        >
          Sign In
        </GradientButton>
      </div>
    </Form>

    <!-- Separator -->
    <div class="relative py-4">
      <div class="relative flex items-center justify-center">
        <div class="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300/50 dark:via-white/[0.08] to-transparent transition-colors duration-300"></div>
        <div class="mx-4 text-xs text-gray-400 dark:text-white uppercase tracking-wider transition-colors duration-300">or</div>
        <div class="flex-1 h-px bg-gradient-to-r from-transparent via-gray-300/50 dark:via-white/[0.08] to-transparent transition-colors duration-300"></div>
      </div>
    </div>

    <!-- Auth Links -->
    <div class="text-center">
      <AuthLinks />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
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
} from '@/apps/auth/components'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const serverError = ref('')
const isSubmitting = ref(false)

// Component mounted
onMounted(async () => {
  // Perform health check when component mounts
  try {
    await AuthAPI.healthCheck()
  } catch (error) {
    // Health check failed - silently handle
  }
})

// Clear any auth errors when component is unmounted
onBeforeUnmount(() => {
  authStore.clearError()
})

const onSubmit = async (values: LoginFormValues) => {
  serverError.value = ''
  isSubmitting.value = true
  
  try {
    // Get values from VeeValidate
    const username = values.username?.trim()
    const password = values.password?.trim()
    
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
/* Fade up transition for error messages */
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
