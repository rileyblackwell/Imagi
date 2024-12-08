// Wait for the window to load
window.addEventListener('load', function() {
    const stripeKey = window.stripePublishableKey;
    const creditsPerDollar = window.creditsPerDollar;

    console.log('Init.js - Checking configuration:', {
        hasStripeKey: !!stripeKey,
        hasCreditsPerDollar: !!creditsPerDollar
    });

    if (stripeKey && creditsPerDollar) {
        initializePayment(stripeKey, creditsPerDollar);
    } else {
        console.error('Missing payment configuration:', {
            stripeKey: !!stripeKey,
            creditsPerDollar: !!creditsPerDollar
        });
    }
}); 