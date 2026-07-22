<template>
  <component
    :is="componentTag"
    :to="to"
    :disabled="disabled"
    class="inline-flex items-center justify-center rounded-full font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-[#fdf9f2] dark:focus-visible:ring-offset-[#0c0c0e]"
    :class="[
      sizeClass,
      disabled
        ? 'opacity-60 cursor-not-allowed'
        : variantClass,
      block ? 'w-full' : 'w-auto'
    ]"
    @click="onClick"
  >
    <i v-if="icon && !iconRight" :class="[icon, 'mr-2']"></i>
    <slot />
    <i v-if="iconRight" :class="[iconRight, 'ml-2']"></i>
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  to?: string | Record<string, any> | null
  disabled?: boolean
  size?: 'xs' | 'sm' | 'base' | 'lg'
  block?: boolean
  icon?: string
  iconRight?: string
  variant?: 'primary' | 'imagi'
}>(), {
  to: null,
  disabled: false,
  size: 'base',
  block: false,
  icon: '',
  iconRight: '',
  variant: 'primary'
})

const emit = defineEmits<{ (e: 'click', ev: MouseEvent): void }>()

const componentTag = computed(() => (props.to ? 'router-link' : 'button'))

const sizeClass = computed(() => ({
  xs: 'px-2 py-1 text-xs',
  sm: 'px-3 py-1.5 text-sm',
  base: 'px-4 py-2 text-sm',
  lg: 'px-5 py-3 text-base'
}[props.size]))

// Both variants share the navy ink pill from the home page button system
const variantClass = computed(() => {
  return 'bg-blue-950 text-[#fdf9f2] hover:bg-blue-900 dark:bg-[#f3ede2] dark:text-blue-950 dark:hover:bg-white shadow-[0_1px_2px_rgba(23,37,84,0.2),0_3px_8px_-2px_rgba(23,37,84,0.25)] dark:shadow-[0_1px_2px_rgba(0,0,0,0.4),0_3px_8px_-2px_rgba(0,0,0,0.45)]'
})

function onClick(ev: MouseEvent) {
  if (props.disabled) {
    ev.preventDefault()
    ev.stopPropagation()
    return
  }
  emit('click', ev)
}
</script>
