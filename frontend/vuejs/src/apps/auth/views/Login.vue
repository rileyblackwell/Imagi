<template>
  <div class="space-y-6">
    <Form v-slot="{ submitCount }" class="space-y-5" @submit="onSubmit">
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
            autocomplete="username"
            placeholder="Enter your username"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && submitCount> 0"
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
            autocomplete="current-password"
            placeholder="Enter your password"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && submitCount> 0"
          />
        </Field>
      </div>

      <!-- Error message display -->
      <div class="space-y-5 pt-2">
        <transition name="fade-up">
          <div v-if="serverError"
               class="p-4 rounded-xl border border-red-500/20 dark:border-red-400/25 bg-red-50 dark:bg-red-500/10 backdrop-blur-sm transition-colors duration-300">
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

    <!-- Auth Links -->
    <div class="text-center pt-2">
      <AuthLinks />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Form, Field } from 'vee-validate'
import { useSignInForm } from '@/apps/auth/composables/useSignInForm'

import {
  PasswordInput,
  FormInput,
  GradientButton,
  AuthLinks
} from '@/apps/auth/components'

const { authStore, serverError, isSubmitting, onSubmit } = useSignInForm()
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

@media (prefers-reduced-motion: reduce) {
  .fade-up-enter-active,
  .fade-up-leave-active {
    transition: none;
  }

  .fade-up-enter-from,
  .fade-up-leave-to {
    transform: none;
  }
}
</style>
