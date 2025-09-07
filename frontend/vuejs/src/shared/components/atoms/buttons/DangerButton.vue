<template>
  <component
    :is="componentTag"
    :to="to"
    :disabled="disabled"
    class="inline-flex items-center justify-center rounded-xl font-medium transition-all duration-300 shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-0 focus:ring-rose-400/30"
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
  size?: 'sm' | 'base' | 'lg'
  block?: boolean
  icon?: string
  iconRight?: string
  variant?: 'solid' | 'outline' | 'subtle'
}>(), {
  to: null,
  disabled: false,
  size: 'base',
  block: false,
  icon: '',
  iconRight: '',
  variant: 'solid'
})

const emit = defineEmits<{ (e: 'click', ev: MouseEvent): void }>()

const componentTag = computed(() => (props.to ? 'router-link' : 'button'))

const sizeClass = computed(() => ({
  sm: 'px-3 py-1.5 text-sm',
  base: 'px-4 py-2 text-sm',
  lg: 'px-5 py-3 text-base'
}[props.size]))

const variantClass = computed(() => ({
  solid: 'bg-gradient-to-r from-red-500 via-rose-500 to-orange-500 text-white hover:from-red-400 hover:via-rose-400 hover:to-orange-400 shadow-red-500/25 hover:shadow-red-500/35',
  outline: 'border border-red-400/50 text-red-300 hover:text-white hover:bg-red-500/15',
  subtle: 'bg-red-500/10 text-red-300 hover:bg-red-500/15 border border-white/10'
}[props.variant]))

function onClick(ev: MouseEvent) {
  if (props.disabled) {
    ev.preventDefault()
    ev.stopPropagation()
    return
  }
  emit('click', ev)
}
</script>
