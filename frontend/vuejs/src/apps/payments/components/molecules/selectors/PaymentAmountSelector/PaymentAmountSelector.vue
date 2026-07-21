<template>
  <div class="payment-amount-selector">
    <h3 class="text-lg font-medium tracking-tight text-blue-950 dark:text-white mb-4 transition-colors duration-300">Select Amount</h3>

    <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
      <button
        v-for="amount in presetAmounts"
        :key="amount"
        @click="selectAmount(amount)"
        class="amount-btn py-3 px-4 text-center rounded-full border font-medium transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:ring-offset-2 focus-visible:ring-offset-white dark:focus-visible:ring-offset-[#0a0a0a]"
        :class="{
          'border-blue-950 bg-blue-950 text-[#fdf9f2] dark:border-[#f3ede2] dark:bg-[#f3ede2] dark:text-blue-950': selectedAmount === amount,
          'border-blue-950/[0.14] bg-white/85 text-blue-950/80 hover:text-blue-950 hover:border-blue-950/30 hover:bg-blue-950/[0.03] dark:border-white/[0.16] dark:bg-white/[0.05] dark:text-blue-100/80 dark:hover:text-white dark:hover:border-white/30 dark:hover:bg-white/[0.06]': selectedAmount !== amount
        }"
      >
        ${{ amount }}
      </button>

      <div class="custom-amount col-span-2 md:col-span-3 mt-2">
        <label class="block text-sm text-blue-950/70 dark:text-blue-100/55 mb-1 transition-colors duration-300">Custom Amount</label>
        <div class="flex items-center">
          <span class="text-blue-950/60 dark:text-blue-100/55 mr-2">$</span>
          <input
            type="number"
            min="5"
            :value="customAmount"
            @input="onCustomAmountChange"
            @focus="selectCustomAmount"
            class="bg-white dark:bg-white/[0.05] border border-blue-950/[0.12] dark:border-white/[0.14] rounded-xl px-3 py-2 w-full text-blue-950 dark:text-white placeholder-blue-950/40 dark:placeholder-blue-100/30 transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500/40 dark:focus-visible:ring-blue-300/50 focus-visible:border-blue-500/50 dark:focus-visible:border-blue-300/50"
            placeholder="Enter amount"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PaymentAmountSelector',
  props: {
    value: {
      type: Number,
      default: 50
    },
    presetAmounts: {
      type: Array,
      default: () => [20, 50, 100, 200, 500]
    }
  },
  data() {
    return {
      selectedAmount: null,
      customAmount: null
    }
  },
  created() {
    // Initialize with the provided value
    if (this.presetAmounts.includes(this.value)) {
      this.selectedAmount = this.value
    } else {
      this.customAmount = this.value
    }
  },
  methods: {
    selectAmount(amount) {
      this.selectedAmount = amount
      this.customAmount = null
      this.$emit('input', amount)
    },
    selectCustomAmount() {
      this.selectedAmount = null
      if (!this.customAmount) {
        this.customAmount = ''
      }
    },
    onCustomAmountChange(e) {
      const value = parseFloat(e.target.value)
      this.customAmount = e.target.value
      this.selectedAmount = null
      
      if (!isNaN(value) && value > 0) {
        this.$emit('input', value)
      }
    }
  }
}
</script>

<style scoped>
.amount-btn {
  transition: all 0.2s ease;
}

input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style> 