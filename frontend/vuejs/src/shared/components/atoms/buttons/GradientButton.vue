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
        : 'bg-gradient-to-r from-indigo-500 via-violet-500 to-fuchsia-500 hover:from-indigo-400 hover:via-violet-400 hover:to-fuchsia-400 text-white shadow-indigo-500/25 hover:shadow-indigo-500/35',
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
}>(), {
  to: null,
  disabled: false,
  size: 'base',
  block: false,
  icon: '',
  iconRight: ''
})

const emit = defineEmits<{ (e: 'click', ev: MouseEvent): void }>()

const componentTag = computed(() => (props.to ? 'router-link' : 'button'))

const sizeClass = computed(() => ({
  sm: 'px-3 py-1.5 text-sm',
  base: 'px-4 py-2 text-sm',
  lg: 'px-5 py-3 text-base'
}[props.size]))

function onClick(ev: MouseEvent) {
  if (props.disabled) {
    ev.preventDefault()
    ev.stopPropagation()
    return
  }
  emit('click', ev)
}
</script>
