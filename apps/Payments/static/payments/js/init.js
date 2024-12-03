(function() {
    const script = document.currentScript;
    const stripeKey = script.getAttribute('data-stripe-key');
    const creditsPerDollar = parseFloat(script.getAttribute('data-credits-per-dollar'));
    
    if (stripeKey && !isNaN(creditsPerDollar)) {
        initializePayment(stripeKey, creditsPerDollar);
    } else {
        console.error('Missing or invalid payment configuration');
    }
})(); 