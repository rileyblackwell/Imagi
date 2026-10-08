/**
 * The words on the payment pages.
 *
 * Imagi writes this file for each business, together with
 * styles/payments.css, which decides how the pages look. Everything else in
 * this folder is the payment flow itself, maintained by Imagi.
 */
export const brand = {
  pricing: {
    eyebrow: 'Pricing',
    title: 'Plans and pricing',
    subtitle: 'Pick a plan and subscribe through secure checkout. Cancel anytime.',
    subscribe: 'Subscribe',
    signInNote: 'You will be asked to sign in first, so your plan is tied to your account.'
  },
  store: {
    eyebrow: 'Store',
    title: 'Shop',
    subtitle: 'Secure checkout powered by Stripe.',
    buy: 'Buy now',
    empty: 'Nothing for sale just yet. Check back soon.'
  },
  checkout: {
    paidTitle: 'Thank you',
    paidBody: 'Your payment was received. A receipt is on its way to your email.',
    subscribedTitle: 'You are subscribed',
    subscribedBody: 'Your plan is active. A receipt is on its way to your email.',
    canceledTitle: 'Checkout canceled',
    canceledBody: 'No charge was made. You can pick up where you left off.',
    pendingTitle: 'Payment still processing',
    pendingBody: 'We have not received confirmation yet. If you completed the payment, it will show up shortly.'
  },
  secureNote: 'Payments are handled by Stripe. Card details never touch this site.'
}
