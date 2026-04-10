<!-- Section Pill Badge Component - Clean & Elegant Design -->
<template>
  <div
    class="group inline-flex items-center gap-2 px-4 py-2 rounded-full relative overflow-hidden transition-all duration-300 hover:scale-[1.02]"
  >
    <!-- Soft gradient border -->
    <div
      class="absolute inset-0 rounded-full opacity-60 group-hover:opacity-100 transition-opacity duration-300"
      :class="borderGradientClass"
    ></div>

    <!-- Inner background with subtle gradient -->
    <div
      class="absolute inset-[1px] rounded-full"
      :class="backgroundClass"
    ></div>

    <!-- Icon -->
    <i
      v-if="icon"
      :class="[icon, 'relative z-10 text-xs', iconClass, { 'animate-pulse': iconPulse }]"
      aria-hidden="true"
    ></i>

    <!-- Label with refined typography -->
    <span
      class="relative z-10 text-[13px] font-medium tracking-wide"
      :class="labelClass"
    >
      {{ label }}
    </span>
  </div>
</template>

<script>
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'SectionPill',
  props: {
    label: { type: String, required: true },
    icon: { type: String, default: '' },
    tone: {
      type: String,
      default: 'violet' // violet | fuchsia | amber | emerald | blue | rose
    },
    labelColor: {
      type: String,
      default: 'default' // default | tone
    },
    iconPulse: { type: Boolean, default: false }
  },
  setup(props) {
    const borderGradientClass = computed(() => {
      const map = {
        violet: 'bg-gradient-to-r from-violet-500/30 via-violet-400/40 to-violet-500/30',
        fuchsia: 'bg-gradient-to-r from-fuchsia-500/30 via-fuchsia-400/40 to-fuchsia-500/30',
        amber: 'bg-gradient-to-r from-amber-500/35 via-amber-400/45 to-amber-500/35',
        emerald: 'bg-gradient-to-r from-emerald-500/30 via-emerald-400/40 to-emerald-500/30',
        blue: 'bg-gradient-to-r from-blue-500/30 via-blue-400/40 to-blue-500/30',
        rose: 'bg-gradient-to-r from-rose-500/30 via-rose-400/40 to-rose-500/30'
      }
      return map[props.tone] || map.violet
    })

    const backgroundClass = computed(() => {
      const map = {
        violet: 'bg-gradient-to-br from-violet-950/90 via-[#0a0a14] to-violet-950/80',
        fuchsia: 'bg-gradient-to-br from-fuchsia-950/90 via-[#0a0a14] to-fuchsia-950/80',
        amber: 'bg-gradient-to-br from-amber-950/90 via-[#0a0a14] to-amber-950/80',
        emerald: 'bg-gradient-to-br from-emerald-950/90 via-[#0a0a14] to-emerald-950/80',
        blue: 'bg-gradient-to-br from-blue-950/90 via-[#0a0a14] to-blue-950/80',
        rose: 'bg-gradient-to-br from-rose-950/90 via-[#0a0a14] to-rose-950/80'
      }
      return map[props.tone] || map.violet
    })

    const iconClass = computed(() => {
      const map = {
        violet: 'text-violet-400',
        fuchsia: 'text-fuchsia-400',
        amber: 'text-amber-400',
        emerald: 'text-emerald-400',
        blue: 'text-blue-400',
        rose: 'text-rose-400'
      }
      return map[props.tone] || map.violet
    })

    const labelClass = computed(() => {
      const toneMap = {
        violet: 'text-violet-300',
        fuchsia: 'text-fuchsia-300',
        amber: 'text-amber-300',
        emerald: 'text-emerald-300',
        blue: 'text-blue-300',
        rose: 'text-rose-300'
      }

      return props.labelColor === 'tone' ? (toneMap[props.tone] || toneMap.violet) : 'text-white/90'
    })

    return {
      borderGradientClass,
      backgroundClass,
      iconClass,
      labelClass
    }
  }
})
</script>
