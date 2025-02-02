<template>
  <div class="change-password">
    <div class="section-header">
      <h2>Change Password</h2>
      <p class="subtitle">Update your account password</p>
    </div>

    <form class="password-form" @submit.prevent="handleSubmit">
      <div class="form-group">
        <FormInput
          v-model="currentPassword"
          type="password"
          name="current_password"
          placeholder="Current Password"
          :error="errors.current_password"
          icon="fa-lock"
          required
        />
      </div>

      <div class="form-group">
        <FormInput
          v-model="newPassword"
          type="password"
          name="new_password"
          placeholder="New Password"
          :error="errors.new_password"
          icon="fa-lock"
          required
        />
      </div>

      <div class="form-group">
        <FormInput
          v-model="confirmPassword"
          type="password"
          name="confirm_password"
          placeholder="Confirm New Password"
          :error="errors.confirm_password"
          icon="fa-lock"
          required
        />
      </div>

      <div class="password-requirements">
        <h4>Password Requirements:</h4>
        <ul>
          <li :class="{ valid: passwordLength }">
            <i :class="getValidationIcon(passwordLength)"></i>
            At least 8 characters long
          </li>
          <li :class="{ valid: hasUpperCase }">
            <i :class="getValidationIcon(hasUpperCase)"></i>
            Contains uppercase letter
          </li>
          <li :class="{ valid: hasLowerCase }">
            <i :class="getValidationIcon(hasLowerCase)"></i>
            Contains lowercase letter
          </li>
          <li :class="{ valid: hasNumber }">
            <i :class="getValidationIcon(hasNumber)"></i>
            Contains number
          </li>
          <li :class="{ valid: hasSpecialChar }">
            <i :class="getValidationIcon(hasSpecialChar)"></i>
            Contains special character
          </li>
        </ul>
      </div>

      <div class="form-actions">
        <BaseButton
          type="submit"
          variant="primary"
          :loading="isLoading"
          :disabled="isLoading || !isFormValid"
          block
        >
          Update Password
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/apps/auth/store'
import { useNotificationsStore } from '../store/notifications'
import FormInput from '@/components/common/FormInput.vue'
import BaseButton from '@/components/common/BaseButton.vue'

const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const errors = ref({})
const isLoading = ref(false)

// Password validation computed properties
const passwordLength = computed(() => newPassword.value.length >= 8)
const hasUpperCase = computed(() => /[A-Z]/.test(newPassword.value))
const hasLowerCase = computed(() => /[a-z]/.test(newPassword.value))
const hasNumber = computed(() => /\d/.test(newPassword.value))
const hasSpecialChar = computed(() => /[!@#$%^&*(),.?":{}|<>]/.test(newPassword.value))

const isFormValid = computed(() => {
  return currentPassword.value &&
         newPassword.value &&
         confirmPassword.value &&
         passwordLength.value &&
         hasUpperCase.value &&
         hasLowerCase.value &&
         hasNumber.value &&
         hasSpecialChar.value &&
         newPassword.value === confirmPassword.value
})

const getValidationIcon = (isValid) => {
  return isValid ? 'fas fa-check text-success' : 'fas fa-times text-muted'
}

const handleSubmit = async () => {
  try {
    isLoading.value = true
    errors.value = {}

    // Basic validation
    if (!currentPassword.value) {
      errors.value.current_password = 'Current password is required'
      return
    }

    if (!isFormValid.value) {
      errors.value.new_password = 'Please meet all password requirements'
      return
    }

    if (newPassword.value !== confirmPassword.value) {
      errors.value.confirm_password = 'Passwords do not match'
      return
    }

    await authStore.changePassword({
      old_password: currentPassword.value,
      new_password: newPassword.value
    })
    
    notificationsStore.showNotification({
      type: 'success',
      message: 'Your password has been successfully updated'
    })

    // Clear form
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    
  } catch (error) {
    if (error.response?.data?.errors) {
      errors.value = error.response.data.errors
    } else {
      notificationsStore.showNotification({
        type: 'error',
        message: 'Failed to update password. Please try again.'
      })
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.change-password {
  max-width: 600px;
  margin: 0 auto;
  padding: var(--spacing-lg);
}

.section-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.section-header h2 {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text);
  margin-bottom: var(--spacing-sm);
}

.subtitle {
  font-size: var(--font-size-md);
  color: var(--color-text-muted);
}

.password-form {
  background: var(--color-background-light);
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.password-requirements {
  margin: var(--spacing-xl) 0;
  padding: var(--spacing-lg);
  background: var(--color-background);
  border-radius: var(--border-radius-md);
}

.password-requirements h4 {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
  margin-bottom: var(--spacing-md);
}

.password-requirements ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.password-requirements li {
  display: flex;
  align-items: center;
  margin-bottom: var(--spacing-sm);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.password-requirements li i {
  margin-right: var(--spacing-sm);
  width: 16px;
}

.password-requirements li.valid {
  color: var(--color-text);
}

.text-success {
  color: var(--color-success);
}

.text-muted {
  color: var(--color-text-muted);
}

.form-actions {
  margin-top: var(--spacing-xl);
}
</style> 