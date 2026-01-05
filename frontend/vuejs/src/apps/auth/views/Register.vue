<template>
  <div class="space-y-6">
    <Form v-slot="{ errors: formErrors, submitCount: formSubmitCount }" class="space-y-5" @submit="handleSubmit">
      <!-- Username input with premium styling -->
      <div class="relative group">
        <Field name="username" rules="required|username" :validateOnBlur="false" v-slot="{ errorMessage, field }">
          <FormInput
            :modelValue="field.value || ''"
            @update:modelValue="field.onChange"
            @blur="field.onBlur"
            name="username"
            label="Username"
            icon="fas fa-user"
            placeholder="Create a username (min. 3 characters)"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && formSubmitCount > 0"
          />
          <transition name="fade-up">
            <div v-if="errorMessage && formSubmitCount > 0" class="mt-2 text-sm text-red-400 flex items-center gap-2">
              <i class="fas fa-exclamation-circle text-xs"></i>
              <span>{{ errorMessage }}</span>
            </div>
          </transition>
        </Field>
      </div>

      <!-- Email input with premium styling -->
      <div class="relative group">
        <Field name="email" rules="required|email" :validateOnBlur="false" v-slot="{ errorMessage, field }">
          <FormInput
            :modelValue="field.value || ''"
            @update:modelValue="field.onChange"
            @blur="field.onBlur"
            name="email"
            label="Email"
            icon="fas fa-envelope"
            placeholder="Enter your email address"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && formSubmitCount > 0"
          />
          <transition name="fade-up">
            <div v-if="errorMessage && formSubmitCount > 0" class="mt-2 text-sm text-red-400 flex items-center gap-2">
              <i class="fas fa-exclamation-circle text-xs"></i>
              <span>{{ errorMessage }}</span>
            </div>
          </transition>
        </Field>
      </div>

      <!-- Password section -->
      <div class="space-y-4">
        <!-- Password input -->
        <div class="relative group">
          <Field name="password" rules="required|registration_password" :validateOnBlur="false" v-slot="{ errorMessage, field, value }">
            <PasswordInput
              :modelValue="field.value || ''"
              @update:modelValue="field.onChange"
              @blur="field.onBlur"
              name="password"
              placeholder="Create password"
              :disabled="authStore.loading || isSubmitting"
              :hasError="!!errorMessage && formSubmitCount > 0"
            />
            <!-- Password requirements with premium glass styling -->
            <div class="mt-4 p-4 rounded-xl border border-white/[0.08] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.12] transition-all duration-300">
              <PasswordRequirements 
                :password="value || ''"
                ref="passwordRequirements"
                class="text-sm"
              />
            </div>
          </Field>
        </div>

        <!-- Confirm password input -->
        <div class="relative group">
          <Field name="password_confirmation" rules="required|password_confirmation:@password" :validateOnBlur="false" v-slot="{ errorMessage, field }">
            <PasswordInput
              :modelValue="field.value || ''"
              @update:modelValue="field.onChange"
              @blur="field.onBlur"
              name="password_confirmation"
              placeholder="Confirm password"
              :disabled="authStore.loading || isSubmitting"
              :hasError="!!errorMessage && formSubmitCount > 0"
            />
            <transition name="fade-up">
              <div v-if="errorMessage && formSubmitCount > 0" class="mt-2 text-sm text-red-400 flex items-center gap-2">
                <i class="fas fa-exclamation-circle text-xs"></i>
                <span>{{ errorMessage }}</span>
              </div>
            </transition>
          </Field>
        </div>
      </div>

      <!-- Bottom section -->
      <div class="space-y-5 pt-2">
        <!-- Terms checkbox with premium styling -->
        <div class="p-4 rounded-xl border border-white/[0.08] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.12] transition-all duration-300">
          <Field name="agreeToTerms" :rules="{ required: { allowFalse: false } }" :validateOnBlur="false" v-slot="{ errorMessage }">
            <FormCheckbox 
              name="agreeToTerms" 
              :disabled="authStore.loading || isSubmitting"
              :showError="false"
            >
              I agree to the 
              <router-link to="/terms" class="text-violet-400 hover:text-violet-300 transition-colors duration-300 font-medium">
                Terms of Service
              </router-link>
              and
              <router-link to="/privacy" class="text-violet-400 hover:text-violet-300 transition-colors duration-300 font-medium">
                Privacy Policy
              </router-link>
            </FormCheckbox>
            <div v-if="(errorMessage || !hasAcceptedTerms) && formSubmitCount > 0" class="mt-2 text-sm text-red-400 flex items-center gap-2">
              <i class="fas fa-exclamation-circle text-xs"></i>
              <span>You must accept the terms to continue</span>
            </div>
          </Field>
        </div>

        <!-- Error message with premium styling -->
        <transition name="fade-up">
          <div v-if="serverError" 
               class="p-4 rounded-xl border border-red-500/20 bg-red-500/10 backdrop-blur-sm">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-red-500/20 border border-red-500/30 flex items-center justify-center flex-shrink-0">
                <i class="fas fa-exclamation-triangle text-red-400 text-sm"></i>
              </div>
              <p class="text-sm font-medium text-red-400 whitespace-pre-line">{{ serverError }}</p>
            </div>
          </div>
        </transition>

        <!-- Premium gradient button -->
        <GradientButton
          type="submit"
          :disabled="authStore.loading || isSubmitting"
          :loading="authStore.loading || isSubmitting"
          loading-text="Creating account..."
          class="w-full"
        >
          Create Account
        </GradientButton>
      </div>
    </Form>

    <!-- Separator -->
    <div class="relative py-4">
      <div class="relative flex items-center justify-center">
        <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
        <div class="mx-4 text-xs text-white/30 uppercase tracking-wider">or</div>
        <div class="flex-1 h-px bg-gradient-to-r from-transparent via-white/[0.08] to-transparent"></div>
      </div>
    </div>

    <!-- Auth Links -->
    <div class="text-center">
      <p class="text-white/50 text-sm">
        Already have an account?
        <router-link to="/auth/login" class="text-violet-400 hover:text-violet-300 font-medium transition-colors duration-300 ml-1">
          Sign in
        </router-link>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
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
} from '@/apps/auth/components' 

const router = useRouter()
const authStore = useAuthStore()
const serverError = ref('')
const isSubmitting = ref(false)
const passwordRequirements = ref<PasswordRequirementsRef | null>(null)
const hasAcceptedTerms = ref(false)

defineOptions({
  name: 'Register'
})

// Component lifecycle
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

const handleSubmit = async (values: RegisterFormValues) => {
  serverError.value = ''
  isSubmitting.value = true

  try {
    // Get values from VeeValidate
    const username = values.username?.trim()
    const email = values.email?.trim()
    const password = values.password
    const passwordConfirmation = values.password_confirmation
    const agreeToTerms = values.agreeToTerms === true
    
    // Update terms acceptance state
    hasAcceptedTerms.value = agreeToTerms
    
    // Validate all required fields
    if (!username || !email || !password) {
      serverError.value = 'Please fill in all required fields'
      isSubmitting.value = false
      return
    }
    
    // Check terms acceptance first
    if (!agreeToTerms) {
      serverError.value = 'You must accept the Terms of Service and Privacy Policy to continue'
      isSubmitting.value = false
      return
    }

    // Check password confirmation matches
    if (password !== passwordConfirmation) {
      serverError.value = 'Passwords do not match'
      isSubmitting.value = false
      return
    }
    
    // Validate password length
    if (password.length < 8) {
      serverError.value = 'Password must be at least 8 characters long'
      isSubmitting.value = false
      return
    }

    // Create registration data
    const registerData = {
      username,
      email,
      password,
      password_confirmation: passwordConfirmation,
      terms_accepted: agreeToTerms
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
