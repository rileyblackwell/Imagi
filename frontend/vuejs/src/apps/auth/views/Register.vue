<template>
  <div class="space-y-6">
    <Form @submit="handleSubmit" v-slot="{ errors: formErrors, submitCount }" class="space-y-6">
      <FormInput
        name="username"
        label="Username"
        icon="fas fa-user"
        rules="required|username"
        placeholder="Create a username"
        :disabled="authStore.isLoading"
        :showError="submitCount > 0"
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
      />

      <div class="space-y-4">
        <PasswordInput
          name="password"
          v-model="formData.password"
          placeholder="Create password"
          :disabled="authStore.isLoading"
          required
        />
        <PasswordRequirements 
          :password="formData.password"
          ref="passwordRequirements"
        />
      </div>

      <PasswordInput
        name="password_confirmation"
        v-model="formData.passwordConfirmation"
        placeholder="Confirm password"
        :disabled="authStore.isLoading"
        required
      />

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

      <!-- Server Error Message -->
      <div v-if="serverError" 
           class="p-4 bg-red-500/10 border border-red-500/20 rounded-xl">
        <p class="text-sm font-medium text-red-400 text-center">{{ serverError }}</p>
      </div>

      <GradientButton
        type="submit"
        :disabled="authStore.isLoading || Object.keys(formErrors).length > 0"
        :loading="authStore.isLoading"
        loading-text="Creating account..."
      >
        Create Account
      </GradientButton>
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

const handleSubmit = async (values) => {
  if (!passwordRequirements.value?.isValid) {
    serverError.value = 'Please ensure your password meets all requirements.'
    return
  }

  serverError.value = ''
  
  try {
    const result = await authStore.register({
      ...values,
      email: formData.email,
      password: formData.password,
      password_confirmation: formData.passwordConfirmation
    })
    
    if (result?.requiresVerification) {
      await router.push({
        name: 'verify-email',
        query: { email: formData.email }
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