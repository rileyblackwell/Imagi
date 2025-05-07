<template>
  <BaseCard customClass="flex items-center gap-4 group cursor-pointer hover:bg-emerald-500/10 transition-all">
    <div class="w-8 h-8 rounded-lg bg-emerald-500/15 flex items-center justify-center group-hover:scale-110 transition-all duration-300">
      <BaseIcon :name="icon" class="text-emerald-400" />
    </div>
    <div>
      <h3 class="text-white group-hover:text-emerald-400 transition-colors font-medium">{{ title }}</h3>
      <p class="text-sm text-gray-400">{{ description }}</p>
    </div>
    <BaseIcon name="fas fa-arrow-right" class="text-gray-500 group-hover:text-emerald-400 transition-colors ml-auto" />
  </BaseCard>
</template>

<script setup lang="ts">
import BaseCard from '@/shared/components/atoms/BaseCard.vue'
import BaseIcon from '@/shared/components/atoms/BaseIcon.vue'

const props = defineProps({
  icon: { type: String, required: true },
  title: { type: String, required: true },
  description: { type: String, required: true }
})
</script>
