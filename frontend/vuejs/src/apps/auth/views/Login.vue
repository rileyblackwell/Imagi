<template>
  <div class="space-y-5">
    <Form @submit="handleSubmit" v-slot="{ errors: formErrors, submitCount }" class="space-y-5">
      <FormInput
        name="username"
        label="Username"
        icon="fas fa-user"
        rules="login_username"
        placeholder="Enter your username"
        :disabled="authStore.loading"
        :showError="submitCount > 0 && hasAttemptedSubmit"
        v-model="formData.username"
        class="auth-input min-h-[42px]"
      />

      <PasswordInput
        name="password"
        v-model="formData.password"
        placeholder="Enter your password"
        :disabled="authStore.loading"
        rules="login_password"
        :showError="submitCount > 0 && hasAttemptedSubmit"
        class="auth-input min-h-[42px]"
      />

      <!-- Error message display -->
      <div class="space-y-5 pt-2">
        <div v-if="serverError && hasAttemptedSubmit" 
             class="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
          <p class="text-sm font-medium text-red-400 text-center whitespace-pre-line">
            {{ serverError }}
          </p>
        </div>

        <GradientButton
          type="submit"
          :disabled="authStore.loading || (Object.keys(formErrors).length > 0 && hasAttemptedSubmit)"
          :loading="authStore.loading"
          loading-text="Signing in..."
          class="w-full"
        >
          Sign In
        </GradientButton>
      </div>
    </Form>

    <AuthLinks class="pt-2" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Form } from 'vee-validate'
import { useAuthStore } from '@/apps/auth/store/index'
import { formatAuthError } from '@/apps/auth/plugins/validation'

import { 
  PasswordInput,
  FormInput,
  GradientButton,
  AuthLinks 
} from '@/apps/auth/components'

interface LoginFormValues {
  username?: string;
  password?: string;
  [key: string]: unknown;
}

const router = useRouter()
const authStore = useAuthStore()
const serverError = ref('')
const hasAttemptedSubmit = ref(false)

const formData = reactive({
  username: '',
  password: ''
})

const handleSubmit = async (values: LoginFormValues) => {
  hasAttemptedSubmit.value = true
  serverError.value = ''
  
  try {
    const loginData = {
      username: values.username?.trim() || formData.username.trim(),
      password: values.password?.trim() || formData.password.trim()
    }

    await authStore.login(loginData)
    
    // Once login is successful, redirect to home
    await router.push({ path: '/' })
  } catch (error: unknown) {
    console.error('Login error:', error)
    serverError.value = formatAuthError(error, 'login')
  }
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>