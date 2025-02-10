<template>
  <div class="space-y-5">
    <Form @submit="handleSubmit" v-slot="{ errors: formErrors, submitCount }" class="space-y-5">
      <!-- Top row - full width fields -->
      <div class="space-y-5">
        <FormInput
          name="username"
          label="Username"
          icon="fas fa-user"
          rules="required"
          placeholder="Create a username"
          :disabled="authStore.isLoading"
          :showError="submitCount > 0"
          class="min-h-[42px]"
        />

        <FormInput
          name="email"
          label="Email"
          icon="fas fa-envelope"
          rules="required|email"
          placeholder="Enter your email"
          :disabled="authStore.isLoading"
          :showError="submitCount > 0"
          v-model="formData.email"
          class="min-h-[42px]"
        />
      </div>

      <!-- Password section with full-width requirements -->
      <div class="space-y-4">
        <!-- Password inputs stacked vertically -->
        <div class="space-y-5">
          <PasswordInput
            name="password"
            v-model="formData.password"
            placeholder="Create password"
            :disabled="authStore.isLoading"
            required
            class="min-h-[42px]"
          />

          <PasswordInput
            name="password_confirmation"
            v-model="formData.passwordConfirmation"
            placeholder="Confirm password"
            :disabled="authStore.isLoading"
            required
            class="min-h-[42px]"
          />
        </div>

        <!-- Password requirements with simplified styling -->
        <div class="px-4 py-3 bg-dark-800/50 rounded-lg border border-dark-700/50">
          <PasswordRequirements 
            :password="formData.password || ''"
            ref="passwordRequirements"
            class="text-sm"
          />
        </div>
      </div>

      <!-- Bottom section - full width -->
      <div class="space-y-5 pt-2">
        <FormCheckbox name="agreeToTerms" :disabled="authStore.isLoading">
          I agree to the 
          <router-link to="/terms" class="text-primary-400 hover:text-primary-300 transition-colors duration-300">
            Terms of Service
          </router-link>
          and
          <router-link to="/privacy" class="text-primary-400 hover:text-primary-300 transition-colors duration-300">
            Privacy Policy
          </router-link>
        </FormCheckbox>

        <div v-if="serverError" 
             class="p-3 bg-red-500/10 border border-red-500/20 rounded-xl">
          <p class="text-sm font-medium text-red-400 text-center">{{ serverError }}</p>
        </div>

        <GradientButton
          type="submit"
          :disabled="authStore.isLoading || Object.keys(formErrors).length > 0"
          :loading="authStore.isLoading"
          loading-text="Creating account..."
          class="w-full"
        >
          Create Account
        </GradientButton>
      </div>
    </Form>

    <AuthLinks />
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Form } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/store/auth.js'
import { 
  EmailInput, 
  PasswordInput, 
  PasswordRequirements,
  FormInput,
  FormCheckbox,
  GradientButton,
  AuthLinks 
} from '@/apps/auth/components'

const router = useRouter()
const authStore = useAuthStore()
const serverError = ref('')
const passwordRequirements = ref(null)

const formData = reactive({
  email: '',
  password: '',
  passwordConfirmation: ''
})

defineOptions({
  name: 'Register'
})

const handleSubmit = async (values) => {
  if (!passwordRequirements.value?.isValid) {
    serverError.value = 'Please ensure your password meets all requirements.'
    return
  }

  serverError.value = ''
  
  try {
    const registerData = {
      username: values.username?.trim(),
      email: (values.email || formData.email)?.trim(),
      password: formData.password,
      password_confirmation: formData.passwordConfirmation
    }

    const result = await authStore.register(registerData)
    
    // Check if we have a result before trying to access properties
    if (result) {
      if (result.requiresVerification) {
        await router.push({
          name: 'verify-email',
          query: { email: registerData.email }
        })
      } else {
        await router.push('/')
      }
    } else {
      throw new Error('Registration failed')
    }
  } catch (error) {
    console.error('Registration error:', error)
    serverError.value = error.response?.data?.detail || 
                       error.message || 
                       'Registration failed. Please try again.'
  }
}
</script>