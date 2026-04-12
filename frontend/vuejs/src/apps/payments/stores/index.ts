// Export all stores from the payments module
export { useModuleBalanceStore } from './moduleBalance'
export { usePaymentStore } from './payments'

// Provide backward compatibility with old naming convention
export { usePaymentStore as usePaymentsStore } from './payments'