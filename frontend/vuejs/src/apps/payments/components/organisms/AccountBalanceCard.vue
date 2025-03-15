<template>
  <PaymentCard hoverable contentClass="p-8">
    <h2 class="text-xl font-semibold mb-6 bg-gradient-to-r from-primary-300 to-primary-500 bg-clip-text text-transparent">
      {{ title }}
    </h2>
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
      <div>
        <BalanceDisplay 
          :balance="credits" 
          :loading="loading"
          :label="balanceLabel"
          :last-updated="lastUpdated"
          :show-last-updated="true"
          type="credits"
        />
      </div>
      <div v-if="showActions" class="flex flex-col sm:flex-row gap-3">
        <slot name="actions"></slot>
      </div>
    </div>
  </PaymentCard>
</template>

<script setup lang="ts">
import PaymentCard from '../atoms/Card.vue';
import BalanceDisplay from '../atoms/BalanceDisplay.vue';

defineProps({
  title: {
    type: String,
    default: 'Your Account'
  },
  balanceLabel: {
    type: String,
    default: 'Current Balance'
  },
  credits: {
    type: Number,
    default: 0
  },
  loading: {
    type: Boolean,
    default: false
  },
  lastUpdated: {
    type: [Date, String],
    default: null
  },
  showActions: {
    type: Boolean,
    default: false
  }
});
</script> 