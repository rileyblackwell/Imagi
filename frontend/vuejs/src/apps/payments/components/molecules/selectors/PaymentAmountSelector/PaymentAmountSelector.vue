<template>
  <div class="payment-amount-selector">
    <h3 class="text-lg font-medium text-white mb-4">Select Amount</h3>
    
    <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
      <button
        v-for="amount in presetAmounts"
        :key="amount"
        @click="selectAmount(amount)"
        class="amount-btn py-3 px-4 text-center rounded-lg border transition-all duration-200"
        :class="{ 
          'border-primary-500 bg-primary-500/10': selectedAmount === amount,
          'border-gray-700 bg-dark-800 hover:border-gray-500': selectedAmount !== amount 
        }"
      >
        ${{ amount }}
      </button>
      
      <div class="custom-amount col-span-2 md:col-span-3 mt-2">
        <label class="block text-sm text-gray-400 mb-1">Custom Amount</label>
        <div class="flex items-center">
          <span class="text-gray-400 mr-2">$</span>
          <input
            type="number"
            min="5"
            :value="customAmount"
            @input="onCustomAmountChange"
            @focus="selectCustomAmount"
            class="bg-dark-800 border border-gray-700 rounded-lg px-3 py-2 w-full text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
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