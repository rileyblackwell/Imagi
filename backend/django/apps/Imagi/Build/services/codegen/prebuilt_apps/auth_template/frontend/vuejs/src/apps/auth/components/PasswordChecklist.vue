<!-- Live checklist under the new-password field. The rules match the
     registration_password rule in plugins/validation.ts; the server applies
     Django's password validators on top. -->
<template>
  <ul class="auth-checklist" aria-label="Password requirements">
    <li
      v-for="rule in rules"
      :key="rule.label"
      class="auth-check"
      :class="{ 'auth-check--met': rule.met }"
    >
      <span class="auth-check-mark" aria-hidden="true"></span>
      {{ rule.label }}
      <span class="sr-only">{{ rule.met ? '(done)' : '(not yet)' }}</span>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{ password?: string }>(), { password: '' })

const rules = computed(() => [
  { label: '8+ characters', met: props.password.length >= 8 },
  { label: 'One uppercase letter', met: /[A-Z]/.test(props.password) },
  { label: 'One lowercase letter', met: /[a-z]/.test(props.password) },
  { label: 'One number', met: /[0-9]/.test(props.password) }
])
</script>
