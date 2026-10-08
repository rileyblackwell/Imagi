<template>
  <div class="auth-view">
    <Form v-slot="{ submitCount }" class="auth-form" @submit="onSubmit">
      <Field name="username" rules="login_username" :validateOnBlur="false" v-slot="{ errorMessage, field }">
        <TextField
          :modelValue="field.value || ''"
          @update:modelValue="field.onChange"
          @blur="field.onBlur"
          name="username"
          label="Username"
          icon="user"
          autocomplete="username"
          placeholder="Your username"
          :disabled="busy"
          :hasError="!!errorMessage && submitCount > 0"
        />
      </Field>

      <Field name="password" rules="login_password" :validateOnBlur="false" v-slot="{ errorMessage, field }">
        <PasswordField
          :modelValue="field.value || ''"
          @update:modelValue="field.onChange"
          @blur="field.onBlur"
          name="password"
          label="Password"
          autocomplete="current-password"
          placeholder="Your password"
          :disabled="busy"
          :hasError="!!errorMessage && submitCount > 0"
        />
      </Field>

      <p v-if="serverError" class="auth-alert" role="alert">{{ serverError }}</p>

      <SubmitButton :loading="busy" loading-text="Signing in…">Sign in</SubmitButton>
    </Form>

    <p class="auth-switch">
      New here?
      <router-link to="/auth/register">Create an account</router-link>
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Form, Field } from 'vee-validate'
import { useSignInForm } from '@/apps/auth/composables/useSignInForm'
import { TextField, PasswordField, SubmitButton } from '@/apps/auth/components'

const { authStore, serverError, isSubmitting, onSubmit } = useSignInForm()
const busy = computed(() => authStore.loading || isSubmitting.value)
</script>
