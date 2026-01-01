<template>
  <div class="space-y-6">
    <Form v-slot="{ errors: formErrors, submitCount, submitForm }" class="space-y-5" @submit="handleSubmit">
      <!-- Username input with premium styling -->
      <div class="relative group">
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
          />
        </Field>
      </div>

      <!-- Email input with premium styling -->
      <div class="relative group">
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
          />
        </Field>
      </div>

      <!-- Password section -->
      <div class="space-y-4">
        <!-- Password input -->
        <div class="relative group">
          <Field name="password" rules="required|registration_password" :validateOnBlur="false" v-slot="{ errorMessage, field }">
            <PasswordInput
              v-bind="field"
              name="password"
              v-model="formData.password"
              placeholder="Create password"
              :disabled="authStore.loading || isSubmitting"
              :hasError="!!errorMessage && submitCount > 0"
            />
          </Field>
        </div>

        <!-- Confirm password input -->
        <div class="relative group">
          <Field name="password_confirmation" :rules="{ required: true, password_confirmation: formData.password }" :validateOnBlur="false" v-slot="{ errorMessage, field }">
            <PasswordInput
              v-bind="field"
              name="password_confirmation"
              v-model="formData.passwordConfirmation"
              placeholder="Confirm password"
              :disabled="authStore.loading || isSubmitting"
              :hasError="!!errorMessage && submitCount > 0"
            />
          </Field>
        </div>

        <!-- Password requirements with premium glass styling -->
        <div class="p-4 rounded-xl border border-white/[0.08] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.12] transition-all duration-300">
          <PasswordRequirements 
            :password="formData.password || ''"
            ref="passwordRequirements"
            class="text-sm"
          />
        </div>
      </div>

      <!-- Bottom section -->
      <div class="space-y-5 pt-2">
        <!-- Terms checkbox with premium styling -->
        <div class="p-4 rounded-xl border border-white/[0.08] bg-white/[0.02] backdrop-blur-sm hover:bg-white/[0.04] hover:border-white/[0.12] transition-all duration-300">
          <Field name="agreeToTerms" rules="required|terms" :validateOnBlur="false">
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

// Component lifecycle
onMounted(async () => {
  // Perform health check when component mounts
  try {
    const healthResponse = await AuthAPI.healthCheck()
    console.log('Auth service health check:', healthResponse.data)
  } catch (error) {
    console.error('Auth service health check failed:', error)
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
