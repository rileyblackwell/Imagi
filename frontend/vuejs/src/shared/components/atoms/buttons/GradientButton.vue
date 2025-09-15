<template>
  <component
    :is="componentTag"
    :to="to"
    :disabled="disabled"
    class="inline-flex items-center justify-center rounded-xl font-medium transition-all duration-300 shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-0 focus:ring-violet-400/40"
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
  variant?: 'primary' | 'oasis'
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

const variantClass = computed(() => {
  // Default (primary) matches existing gradient to avoid breaking styles elsewhere
  if (props.variant === 'primary') {
    return 'bg-gradient-to-r from-indigo-500 via-violet-500 to-fuchsia-500 hover:from-indigo-400 hover:via-violet-400 hover:to-fuchsia-400 text-white shadow-indigo-500/25 hover:shadow-indigo-500/35'
  }
  // Oasis variant: tuned to Imagi site palette with primary + violet/indigo accents
  if (props.variant === 'oasis') {
    return 'bg-gradient-to-r from-primary-500 via-violet-500 to-indigo-500 hover:from-primary-400 hover:via-violet-400 hover:to-indigo-400 text-white shadow-violet-500/20 hover:shadow-violet-500/30'
  }
  return 'bg-gradient-to-r from-indigo-500 via-violet-500 to-fuchsia-500 hover:from-indigo-400 hover:via-violet-400 hover:to-fuchsia-400 text-white shadow-indigo-500/25 hover:shadow-indigo-500/35'
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
