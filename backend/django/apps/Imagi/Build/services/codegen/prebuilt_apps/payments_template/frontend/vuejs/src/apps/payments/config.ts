/**
 * Where this app's payments come from. Imagi writes this file when payments
 * are added from the Sell console, and rewrites it when they change there.
 *
 * Nothing here is secret: the project id and API address only let the pages
 * read the price list and start a Stripe checkout. Stripe keys never live in
 * this app.
 */
export const paymentsConfig = {
  projectId: __IMAGI_PROJECT_ID__,
  apiBase: '__IMAGI_API_BASE__',
  /** Which pages the app has: the plans page and/or the store. */
  pages: __PAYMENT_PAGES__ as { pricing: boolean; store: boolean }
}
