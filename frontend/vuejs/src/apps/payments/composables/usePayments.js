import { ref, computed } from 'vue';
import axios from 'axios';

const loading = ref(false);
const error = ref(null);
const paymentMethods = ref([]);
const transactions = ref([]);
const currentPlan = ref(null);

export function usePayments() {
  /**
   * Initialize Stripe
   * @param {string} publishableKey - Stripe publishable key
   */
  function initializeStripe(publishableKey) {
    const stripe = window.Stripe(publishableKey);
    return stripe;
  }

  /**
   * Fetch available credit packages
   */
  async function fetchCreditPackages() {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.get('/api/payments/packages/');
      return response.data;
    } catch (err) {
      console.error('Failed to fetch credit packages:', err);
      error.value = err.response?.data?.message || 'Failed to fetch credit packages. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Purchase credits
   * @param {Object} purchaseData - Purchase details
   * @param {string} purchaseData.package_id - ID of the credit package
   * @param {string} purchaseData.payment_method_id - ID of the payment method
   */
  async function purchaseCredits(purchaseData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/payments/purchase/', purchaseData);
      return response.data;
    } catch (err) {
      console.error('Failed to purchase credits:', err);
      error.value = err.response?.data?.message || 'Failed to purchase credits. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Add a new payment method
   * @param {Object} paymentMethodData - Payment method details from Stripe
   */
  async function addPaymentMethod(paymentMethodData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/payments/methods/', paymentMethodData);
      paymentMethods.value.push(response.data);
      return response.data;
    } catch (err) {
      console.error('Failed to add payment method:', err);
      error.value = err.response?.data?.message || 'Failed to add payment method. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Remove a payment method
   * @param {string} paymentMethodId - ID of the payment method to remove
   */
  async function removePaymentMethod(paymentMethodId) {
    loading.value = true;
    error.value = null;

    try {
      await axios.delete(`/api/payments/methods/${paymentMethodId}/`);
      paymentMethods.value = paymentMethods.value.filter(pm => pm.id !== paymentMethodId);
    } catch (err) {
      console.error('Failed to remove payment method:', err);
      error.value = err.response?.data?.message || 'Failed to remove payment method. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fetch user's payment methods
   */
  async function fetchPaymentMethods() {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.get('/api/payments/methods/');
      paymentMethods.value = response.data;
    } catch (err) {
      console.error('Failed to fetch payment methods:', err);
      error.value = err.response?.data?.message || 'Failed to fetch payment methods. Please try again.';
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fetch user's transaction history
   */
  async function fetchTransactions() {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.get('/api/payments/transactions/');
      transactions.value = response.data;
    } catch (err) {
      console.error('Failed to fetch transactions:', err);
      error.value = err.response?.data?.message || 'Failed to fetch transactions. Please try again.';
    } finally {
      loading.value = false;
    }
  }

  /**
   * Subscribe to a plan
   * @param {Object} subscriptionData - Subscription details
   * @param {string} subscriptionData.plan_id - ID of the plan
   * @param {string} subscriptionData.payment_method_id - ID of the payment method
   */
  async function subscribe(subscriptionData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/payments/subscribe/', subscriptionData);
      currentPlan.value = response.data.plan;
      return response.data;
    } catch (err) {
      console.error('Failed to subscribe:', err);
      error.value = err.response?.data?.message || 'Failed to subscribe. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Cancel current subscription
   */
  async function cancelSubscription() {
    loading.value = true;
    error.value = null;

    try {
      await axios.post('/api/payments/cancel-subscription/');
      currentPlan.value = null;
    } catch (err) {
      console.error('Failed to cancel subscription:', err);
      error.value = err.response?.data?.message || 'Failed to cancel subscription. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Update subscription
   * @param {Object} updateData - Update details
   * @param {string} updateData.plan_id - ID of the new plan
   */
  async function updateSubscription(updateData) {
    loading.value = true;
    error.value = null;

    try {
      const response = await axios.post('/api/payments/update-subscription/', updateData);
      currentPlan.value = response.data.plan;
      return response.data;
    } catch (err) {
      console.error('Failed to update subscription:', err);
      error.value = err.response?.data?.message || 'Failed to update subscription. Please try again.';
      throw err;
    } finally {
      loading.value = false;
    }
  }

  // Computed properties
  const isLoading = computed(() => loading.value);
  const paymentError = computed(() => error.value);
  const availablePaymentMethods = computed(() => paymentMethods.value);
  const transactionHistory = computed(() => transactions.value);
  const activePlan = computed(() => currentPlan.value);

  return {
    // State
    isLoading,
    error: paymentError,
    paymentMethods: availablePaymentMethods,
    transactions: transactionHistory,
    currentPlan: activePlan,

    // Methods
    initializeStripe,
    fetchCreditPackages,
    purchaseCredits,
    addPaymentMethod,
    removePaymentMethod,
    fetchPaymentMethods,
    fetchTransactions,
    subscribe,
    cancelSubscription,
    updateSubscription
  };
} 