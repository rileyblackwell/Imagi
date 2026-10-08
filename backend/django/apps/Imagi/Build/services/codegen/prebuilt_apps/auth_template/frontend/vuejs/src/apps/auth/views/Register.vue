<template>
  <div class="auth-view">
    <Form v-slot="{ submitCount }" class="auth-form" @submit="onSubmit">
      <Field name="username" rules="required|username" :validateOnBlur="false" v-slot="{ errorMessage, field }">
        <TextField
          :modelValue="field.value || ''"
          @update:modelValue="field.onChange"
          @blur="field.onBlur"
          name="username"
          label="Username"
          icon="user"
          autocomplete="username"
          placeholder="At least 3 characters"
          :disabled="busy"
          :hasError="!!errorMessage && submitCount > 0"
          :error="submitCount > 0 ? errorMessage : ''"
        />
      </Field>

      <Field name="email" rules="required|email" :validateOnBlur="false" v-slot="{ errorMessage, field }">
        <TextField
          :modelValue="field.value || ''"
          @update:modelValue="field.onChange"
          @blur="field.onBlur"
          name="email"
          type="email"
          label="Email"
          icon="mail"
          autocomplete="email"
          placeholder="you@example.com"
          :disabled="busy"
          :hasError="!!errorMessage && submitCount > 0"
          :error="submitCount > 0 ? errorMessage : ''"
        />
      </Field>

      <Field name="password" rules="required|registration_password" :validateOnBlur="false" v-slot="{ errorMessage, field, value }">
        <PasswordField
          :modelValue="field.value || ''"
          @update:modelValue="field.onChange"
          @blur="field.onBlur"
          name="password"
          label="Password"
          autocomplete="new-password"
          placeholder="Create a password"
          :disabled="busy"
          :hasError="!!errorMessage && submitCount > 0"
          :error="submitCount > 0 ? errorMessage : ''"
        />
        <PasswordChecklist :password="value || ''" />
      </Field>

      <Field name="password_confirmation" rules="required|password_confirmation:@password" :validateOnBlur="false" v-slot="{ errorMessage, field }">
        <PasswordField
          :modelValue="field.value || ''"
          @update:modelValue="field.onChange"
          @blur="field.onBlur"
          name="password_confirmation"
          label="Confirm password"
          autocomplete="new-password"
          placeholder="Type it again"
          :disabled="busy"
          :hasError="!!errorMessage && submitCount > 0"
          :error="submitCount > 0 ? errorMessage : ''"
        />
      </Field>

      <p v-if="serverError" class="auth-alert" role="alert">{{ serverError }}</p>

      <SubmitButton :loading="busy" loading-text="Creating account…">Create account</SubmitButton>
    </Form>

    <p class="auth-switch">
      Already have an account?
      <router-link to="/auth/signin">Sign in</router-link>
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Form, Field } from 'vee-validate'
import { useRegisterForm } from '@/apps/auth/composables/useRegisterForm'
import { TextField, PasswordField, PasswordChecklist, SubmitButton } from '@/apps/auth/components'

// No terms checkbox: a new business has no terms page to link to yet.
const { authStore, serverError, isSubmitting, onSubmit } = useRegisterForm({ requireTerms: false })
const busy = computed(() => authStore.loading || isSubmitting.value)

defineOptions({
  name: 'Register'
})
</script>
