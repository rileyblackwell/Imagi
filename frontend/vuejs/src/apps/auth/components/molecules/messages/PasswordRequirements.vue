<template>
  <div class="w-full">
    <!-- Requirements Grid -->
    <div class="grid grid-cols-2 gap-x-8 gap-y-2">
      <!-- Left column -->
      <div class="space-y-2">
        <RequirementItem
          :checked="hasMinLength"
          text="8+ characters"
        />
        <RequirementItem
          :checked="hasUpperCase"
          text="One uppercase"
        />
        <RequirementItem
          :checked="hasLowerCase"
          text="One lowercase"
        />
      </div>

      <!-- Right column -->
      <div class="space-y-2">
        <RequirementItem
          :checked="hasNumber"
          text="One number"
        />
        <RequirementItem
          :checked="hasSpecialChar"
          text="One symbol"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RequirementItem } from '@/apps/auth/components'

const props = defineProps({
  password: {
    type: String,
    required: true,
    default: ''
  }
})

const hasMinLength = computed(() => (props.password || '').length >= 8)
const hasUpperCase = computed(() => /[A-Z]/.test(props.password || ''))
const hasLowerCase = computed(() => /[a-z]/.test(props.password || ''))
const hasNumber = computed(() => /\d/.test(props.password || ''))
const hasSpecialChar = computed(() => /[!@#$%^&*(),.?":{}|<>]/.test(props.password || ''))

const isValid = computed(() => 
  hasMinLength.value && 
  hasUpperCase.value && 
  hasLowerCase.value && 
  hasNumber.value && 
  hasSpecialChar.value
)

defineExpose({ isValid })
</script>