<template>
  <div class="space-y-6">
    <Form v-slot="{ submitCount: formSubmitCount }" class="space-y-5" @submit="handleSubmit">
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
            autocomplete="username"
            placeholder="Create a username (min. 3 characters)"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && formSubmitCount> 0"
          />
          <transition v-bind="fadeUp">
            <div v-if="errorMessage && formSubmitCount> 0" class="mt-2 text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
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
            autocomplete="email"
            placeholder="Enter your email address"
            :disabled="authStore.loading || isSubmitting"
            :hasError="!!errorMessage && formSubmitCount> 0"
          />
          <transition v-bind="fadeUp">
            <div v-if="errorMessage && formSubmitCount> 0" class="mt-2 text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
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
              autocomplete="new-password"
              placeholder="Create password"
              :disabled="authStore.loading || isSubmitting"
              :hasError="!!errorMessage && formSubmitCount> 0"
            />
            <!-- Password requirements on an inset chip panel -->
            <div class="mt-4 p-4 rounded-xl border border-sl-line bg-sl-chip-bg backdrop-blur-sm transition-all duration-300">
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
              autocomplete="new-password"
              placeholder="Confirm password"
              :disabled="authStore.loading || isSubmitting"
              :hasError="!!errorMessage && formSubmitCount> 0"
            />
            <transition v-bind="fadeUp">
              <div v-if="errorMessage && formSubmitCount> 0" class="mt-2 text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
                <i class="fas fa-exclamation-circle text-xs"></i>
                <span>{{ errorMessage }}</span>
              </div>
            </transition>
          </Field>
        </div>
      </div>

      <!-- Bottom section -->
      <div class="space-y-5 pt-2">
        <!-- Terms checkbox on an inset chip panel -->
        <div class="p-4 rounded-xl border border-sl-line bg-sl-chip-bg backdrop-blur-sm transition-all duration-300">
          <Field name="agreeToTerms" :rules="{ required: { allowFalse: false } }" :validateOnBlur="false" v-slot="{ errorMessage }">
            <FormCheckbox 
              name="agreeToTerms" 
              :disabled="authStore.loading || isSubmitting"
            >
              I agree to the
              <router-link to="/terms" class="font-medium text-sl-text border-b border-sl-line-strong hover:border-sl-focus pb-0.5 transition-colors duration-200 rounded-sm focus-ring">
                Terms of Service
              </router-link>
              and
              <router-link to="/privacy" class="font-medium text-sl-text border-b border-sl-line-strong hover:border-sl-focus pb-0.5 transition-colors duration-200 rounded-sm focus-ring">
                Privacy Policy
              </router-link>
            </FormCheckbox>
            <div v-if="(errorMessage || !hasAcceptedTerms) && formSubmitCount> 0" class="mt-2 text-sm text-red-600 dark:text-red-400 flex items-center gap-2">
              <i class="fas fa-exclamation-circle text-xs"></i>
              <span>You must accept the terms to continue</span>
            </div>
          </Field>
        </div>

        <!-- Error message with premium styling -->
        <transition v-bind="fadeUp">
          <div v-if="serverError"
               class="p-4 rounded-xl border border-red-500/20 dark:border-red-400/25 bg-red-50 dark:bg-red-500/10 backdrop-blur-sm transition-colors duration-300">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-500/20 border border-red-200 dark:border-red-500/30 flex items-center justify-center flex-shrink-0 transition-colors duration-300">
                <i class="fas fa-exclamation-triangle text-red-600 dark:text-red-400 text-sm transition-colors duration-300"></i>
              </div>
              <p class="text-sm font-medium text-red-600 dark:text-red-400 whitespace-pre-line transition-colors duration-300">{{ serverError }}</p>
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

    <!-- Auth Links -->
    <div class="pt-2">
      <AuthLinks />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Form, Field } from 'vee-validate'
import { useRegisterForm } from '@/apps/auth/composables/useRegisterForm'
import type { PasswordRequirementsRef } from '@/apps/auth/types/form'

import {
  AuthLinks,
  PasswordInput,
  FormInput,
  FormCheckbox,
  PasswordRequirements,
  GradientButton,
} from '@/apps/auth/components'

const { authStore, serverError, isSubmitting, hasAcceptedTerms, onSubmit: handleSubmit } = useRegisterForm()
const passwordRequirements = ref<PasswordRequirementsRef | null>(null)

defineOptions({
  name: 'Register'
})
// Error messages fade up into place. `!` because the server-error box carries
// its own transition-colors, which the enter/leave transition must replace.
const fadeUp = {
  enterActiveClass: '![transition:all_0.4s_cubic-bezier(0.4,0,0.2,1)] motion-reduce:![transition:none]',
  leaveActiveClass: '![transition:all_0.4s_cubic-bezier(0.4,0,0.2,1)] motion-reduce:![transition:none]',
  enterFromClass: 'opacity-0 translate-y-[10px] motion-reduce:transform-none',
  leaveToClass: 'opacity-0 translate-y-[10px] motion-reduce:transform-none',
}
</script>
