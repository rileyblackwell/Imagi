<template>
  <div class="space-y-6">
    <Form v-slot="{ errors: formErrors, submitCount, submitForm }" class="space-y-6" @submit="handleSubmit">
      <!-- Top row - full width fields with enhanced styling -->
      <div class="space-y-5">
        <!-- Username input with micro-interactions -->
        <div class="relative">
          <Field name="username" rules="required|username" :validateOnBlur="false" v-slot="{ errorMessage, field }">
            <FormInput
              v-bind="field"
              name="username"
              label="Username"
              icon="fas fa-user"
              placeholder="Create a username"
              :disabled="authStore.loading || isSubmitting"
              :hasError="!!errorMessage && submitCount > 0"
              v-model="formData.username"
              class="min-h-[42px] sm:min-h-[48px] shadow-sm hover:shadow-md transition-shadow duration-300"
            />
          </Field>
        </div>

        <!-- Email input with micro-interactions -->
        <div class="relative">
          <Field name="email" rules="required|email" :validateOnBlur="false" v-slot="{ errorMessage, field }">
            <FormInput
              v-bind="field"
              name="email"
              label="Email"
              icon="fas fa-envelope"
              placeholder="Enter your email"
              :disabled="authStore.loading || isSubmitting"
              :hasError="!!errorMessage && submitCount > 0"
              v-model="formData.email"
              class="min-h-[42px] sm:min-h-[48px] shadow-sm hover:shadow-md transition-shadow duration-300"
            />
          </Field>
        </div>
      </div>

      <!-- Password section with enhanced styling -->
      <div class="space-y-5">
        <!-- Password inputs with micro-interactions -->
        <div class="space-y-5">
          <div class="relative">
            <Field name="password" rules="required|registration_password" :validateOnBlur="false" v-slot="{ errorMessage, field }">
              <PasswordInput
                v-bind="field"
                name="password"
                v-model="formData.password"
                placeholder="Create password"
                :disabled="authStore.loading || isSubmitting"
                :hasError="!!errorMessage && submitCount > 0"
                class="min-h-[42px] sm:min-h-[48px] shadow-sm hover:shadow-md transition-shadow duration-300"
              />
            </Field>
          </div>

          <div class="relative">
            <Field name="password_confirmation" :rules="{ required: true, password_confirmation: formData.password }" :validateOnBlur="false" v-slot="{ errorMessage, field }">
              <PasswordInput
                v-bind="field"
                name="password_confirmation"
                v-model="formData.passwordConfirmation"
                placeholder="Confirm password"
                :disabled="authStore.loading || isSubmitting"
                :hasError="!!errorMessage && submitCount > 0"
                class="min-h-[42px] sm:min-h-[48px] shadow-sm hover:shadow-md transition-shadow duration-300"
              />
            </Field>
          </div>
        </div>

        <!-- Password requirements with enhanced styling -->
        <div class="px-5 py-4 bg-dark-800/60 backdrop-blur-sm rounded-xl border border-dark-700/50 
                    hover:border-primary-500/20 transition-all duration-300 shadow-inner">
          <PasswordRequirements 
            :password="formData.password || ''"
            ref="passwordRequirements"
            class="text-sm"
          />
        </div>
      </div>

      <!-- Bottom section with enhanced styling -->
      <div class="space-y-5 pt-3">
        <!-- Terms checkbox with enhanced styling -->
        <div class="px-4 py-3 bg-dark-800/40 backdrop-blur-sm rounded-xl border border-dark-700/40 
                    hover:border-primary-500/20 transition-all duration-300 shadow-sm">
          <Field name="agreeToTerms" rules="required|terms" :validateOnBlur="false">
            <FormCheckbox 
              name="agreeToTerms" 
              :disabled="authStore.loading || isSubmitting"
              :showError="false"
            >
              I agree to the 
              <router-link to="/terms" class="text-primary-400 hover:text-primary-300 transition-colors duration-300 font-medium">
                Terms of Service
              </router-link>
              and
              <router-link to="/privacy" class="text-primary-400 hover:text-primary-300 transition-colors duration-300 font-medium">
                Privacy Policy
              </router-link>
            </FormCheckbox>
          </Field>
        </div>

        <!-- Enhanced error message with animation -->
        <transition name="fade-up">
          <div v-if="serverError" 
               class="p-4 bg-red-500/10 border border-red-500/20 rounded-xl backdrop-blur-sm
                      shadow-inner transition-all duration-300">
            <p class="text-sm font-medium text-red-400 text-center whitespace-pre-line">{{ serverError }}</p>
          </div>
        </transition>

        <!-- Elevated button with enhanced styling -->
        <GradientButton
          type="submit"
          :disabled="authStore.loading || isSubmitting"
          :loading="authStore.loading || isSubmitting"
          loading-text="Creating account..."
          class="w-full min-h-[48px] sm:min-h-[52px] mt-4"
        >
          Create Account
        </GradientButton>
      </div>
    </Form>

    <!-- AuthLinks with animations removed -->
    <div class="pt-4">
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Form, Field } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/stores/index'
import { formatAuthError } from '@/apps/auth/plugins/validation'
import type { RegisterFormValues, PasswordRequirementsRef } from '@/apps/auth/types/form'
import { AuthAPI } from '@/apps/auth/services/api'

import { 
  PasswordInput,
  FormInput,
  FormCheckbox,
  PasswordRequirements,
  GradientButton,
  AuthLinks 
} from '@/apps/auth/components' 

const router = useRouter()
const authStore = useAuthStore()
const serverError = ref('')
const isSubmitting = ref(false)
const passwordRequirements = ref<PasswordRequirementsRef | null>(null)

const formData = reactive({
  email: '',
  password: '',
  passwordConfirmation: '',
  username: '',
  agreeToTerms: false
})

defineOptions({
  name: 'Register'
})

// Check backend health when component mounts
onMounted(async () => {
  try {
    await AuthAPI.healthCheck()
  } catch (error: any) {
    console.warn('🚨 Auth API health check failed on register page load:', {
      userMessage: error.userMessage || error.message,
      diagnostics: error.diagnostics,
      originalError: {
        message: error.message,
        stack: error.stack,
        response: error.response
      },
      timestamp: new Date().toISOString()
    })
    
    // Log additional diagnostic information if available
    if (error.diagnostics) {
      console.group('📊 Detailed Diagnostics')
      console.log('Request:', error.diagnostics.request)
      console.log('Response:', error.diagnostics.response)
      console.log('Network:', error.diagnostics.network)
      console.log('Environment:', error.diagnostics.environment)
      console.groupEnd()
    }
  }
})

// Clear error when form fields change
watch(
  [() => formData.email, () => formData.password, () => formData.passwordConfirmation, () => formData.username],
  () => {
    if (serverError.value) {
      serverError.value = ''
    }
  }
)

// Clear any auth errors when component is unmounted
onBeforeUnmount(() => {
  authStore.clearError()
})

const handleSubmit = async (values: RegisterFormValues) => {
  serverError.value = ''
  isSubmitting.value = true

  try {
    // Set form data from values if empty
    if (!formData.username && values.username) {
      formData.username = values.username
    }
    
    if (!formData.email && values.email) {
      formData.email = values.email
    }
    
    if (!formData.password && values.password) {
      formData.password = values.password
    }
    
    // Validate all required fields
    if (!formData.username || !formData.email || !formData.password || !values.agreeToTerms) {
      serverError.value = 'All fields are required'
      isSubmitting.value = false
      return
    }

    // Check password confirmation matches
    if (formData.password !== formData.passwordConfirmation) {
      serverError.value = 'Passwords do not match'
      isSubmitting.value = false
      return
    }

    // Create registration data
    const registerData = {
      username: formData.username.trim(),
      email: formData.email.trim(),
      password: formData.password,
      password_confirmation: formData.passwordConfirmation,
      terms_accepted: values.agreeToTerms
    }

    document.body.style.cursor = 'wait'

    await authStore.register(registerData)
    
    await router.push('/')
  } catch (error: unknown) {
    serverError.value = formatAuthError(error, 'register')
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