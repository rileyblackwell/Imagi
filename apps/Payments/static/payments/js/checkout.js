// Initialize payment processing
function initializePayment(stripeKey, creditsPerDollar) {
    console.log('Initializing payment with:', { 
        stripeKeyLength: stripeKey ? stripeKey.length : 0,
        creditsPerDollar 
    });
    
    if (!stripeKey) {
        console.error('Stripe key is missing or invalid');
        return;
    }

    // Initialize Stripe immediately, not inside DOMContentLoaded
    try {
        const stripe = Stripe(stripeKey);
        let elements;

        // Get CSRF token from the cookie
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        initialize();

        document
            .querySelector("#payment-form")
            .addEventListener("submit", handleSubmit);

        // Initialize Stripe and elements
        async function initialize() {
            try {
                const amount = parseFloat(document.getElementById('credit_amount').value);
                const validation = validateAmount(amount);
                
                if (!validation.valid) {
                    throw new Error(validation.message);
                }

                const csrftoken = getCookie('csrftoken');
                if (!csrftoken) {
                    throw new Error('CSRF token not found');
                }

                const response = await fetch("/payments/create-payment-intent/", {
                    method: "POST",
                    headers: { 
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrftoken
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify({ 
                        credit_amount: amount
                    }),
                });
                
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Network response was not ok');
                }

                const { clientSecret } = await response.json();
                console.log('Got client secret');

                const appearance = {
                    theme: 'night',
                    variables: {
                        colorPrimary: '#00ffc6',
                        colorBackground: 'rgba(13, 12, 34, 0.95)',
                        colorText: '#ffffff',
                        colorDanger: '#ff4d4d',
                        fontFamily: 'system-ui, sans-serif',
                        spacingUnit: '6px',
                        borderRadius: '12px',
                        fontSizeBase: '15px',
                        fontWeightNormal: '400',
                        fontWeightMedium: '500',
                        fontLineHeight: '1.6',
                        colorTextPlaceholder: 'rgba(255, 255, 255, 0.5)',
                        colorLogo: 'light',
                        colorIcon: '#ffffff',
                        colorIconHover: '#ffffff',
                        colorIconSelected: '#ffffff'
                    },
                    rules: {
                        '.Input': {
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            boxShadow: 'none',
                            backgroundColor: 'rgba(255, 255, 255, 0.05)',
                            color: '#ffffff'
                        },
                        '.Label': {
                            color: 'rgba(255, 255, 255, 0.8)',
                            fontSize: '14px'
                        },
                        '.Tab': {
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            backgroundColor: 'rgba(255, 255, 255, 0.05)',
                            color: '#ffffff'
                        },
                        '.Tab:hover': {
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            color: '#ffffff'
                        },
                        '.Tab--selected': {
                            border: '1px solid #00ffc6',
                            backgroundColor: 'rgba(0, 255, 198, 0.1)',
                            color: '#ffffff'
                        },
                        '.TabLabel': {
                            color: '#ffffff'
                        },
                        '.TabIcon': {
                            color: '#ffffff'
                        },
                        '.Input::placeholder': {
                            color: 'rgba(255, 255, 255, 0.5)'
                        },
                        '.Block': {
                            backgroundColor: 'rgba(255, 255, 255, 0.05)',
                            borderColor: 'rgba(255, 255, 255, 0.1)',
                            color: '#ffffff'
                        },
                        '.Block:hover': {
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            borderColor: 'rgba(255, 255, 255, 0.2)',
                            color: '#ffffff'
                        },
                        '.Block--selected': {
                            backgroundColor: 'rgba(0, 255, 198, 0.1)',
                            borderColor: '#00ffc6',
                            color: '#ffffff'
                        },
                        '[class*="Icon"]': {
                            color: '#ffffff !important',
                            fill: '#ffffff !important'
                        },
                        '.PaymentElement [class*="Icon"]': {
                            color: '#ffffff !important',
                            fill: '#ffffff !important'
                        },
                        '.PaymentElement .Card [class*="Icon"]': {
                            color: '#ffffff !important',
                            fill: '#ffffff !important'
                        }
                    }
                };
                
                const paymentElementOptions = {
                    layout: "tabs",
                    defaultValues: {
                        billingDetails: {
                            name: '{{ user.get_full_name }}',
                            email: '{{ user.email }}'
                        }
                    }
                };

                elements = stripe.elements({ 
                    appearance, 
                    clientSecret,
                    loader: 'auto' 
                });

                const paymentElement = elements.create("payment", paymentElementOptions);
                console.log('Created payment element');

                await paymentElement.mount("#payment-element");
                console.log('Mounted payment element');
                
                document.querySelector("#submit").disabled = false;
            } catch (error) {
                console.error('Initialization error:', error);
                showMessage(error.message || "Failed to initialize payment form.");
            }
        }

        // Handle form submission
        async function handleSubmit(e) {
            e.preventDefault();
            setLoading(true);

            try {
                const { error } = await stripe.confirmPayment({
                    elements,
                    confirmParams: {
                        return_url: window.location.origin + "/payments/success/"
                    }
                });

                if (error) {
                    if (error.type === "card_error" || error.type === "validation_error") {
                        showMessage(error.message);
                    } else {
                        showMessage("An unexpected error occurred.");
                    }
                    setLoading(false);
                }
            } catch (error) {
                console.error('Error:', error);
                showMessage("Payment failed. Please try again.");
                setLoading(false);
            }
        }

        // Update payment intent when credit amount changes
        document.getElementById('credit_amount').addEventListener('change', async () => {
            const amount = parseFloat(document.getElementById('credit_amount').value);
            const validation = validateAmount(amount);
            
            if (validation.valid) {
                setLoading(true);
                await initialize();
                setLoading(false);
            }
        });

        // UI helpers
        function showMessage(messageText) {
            const messageContainer = document.querySelector("#payment-message");
            messageContainer.classList.remove("hidden");
            messageContainer.textContent = messageText;
            setTimeout(function () {
                messageContainer.classList.add("hidden");
                messageContainer.textContent = "";
            }, 4000);
        }

        function setLoading(isLoading) {
            const submitButton = document.querySelector("#submit");
            const spinner = document.querySelector("#spinner");
            const buttonText = document.querySelector("#button-text");
            
            if (isLoading) {
                submitButton.disabled = true;
                spinner.classList.remove("hidden");
                buttonText.classList.add("hidden");
            } else {
                submitButton.disabled = false;
                spinner.classList.add("hidden");
                buttonText.classList.remove("hidden");
            }
        }

        // Add input validation
        const creditInput = document.getElementById('credit_amount');
        const errorDiv = document.getElementById('amount-error');
        const creditsPreview = document.getElementById('credits-amount');

        function validateAmount(amount) {
            const numAmount = parseFloat(amount);
            if (isNaN(numAmount)) {
                return { valid: false, message: 'Please enter a valid amount' };
            }
            if (numAmount < 5) {
                return { valid: false, message: 'Minimum amount is $5.00' };
            }
            if (numAmount > 100) {
                return { valid: false, message: 'Maximum amount is $100.00' };
            }
            return { valid: true };
        }

        function updateCreditsPreview(amount) {
            const numAmount = parseFloat(amount);
            if (!isNaN(numAmount)) {
                const credits = numAmount * creditsPerDollar;
                creditsPreview.textContent = credits.toFixed(2);
            }
        }

        creditInput.addEventListener('input', function(e) {
            const amount = e.target.value;
            const validation = validateAmount(amount);
            
            if (!validation.valid) {
                errorDiv.textContent = validation.message;
                errorDiv.classList.remove('hidden');
                creditInput.classList.add('error');
                document.querySelector("#submit").disabled = true;
            } else {
                errorDiv.classList.add('hidden');
                creditInput.classList.remove('error');
                document.querySelector("#submit").disabled = false;
                updateCreditsPreview(amount);
            }
        });

        // Initialize the credits preview with the default value
        updateCreditsPreview(creditInput.value);
    } catch (error) {
        console.error('Stripe initialization error:', error);
        showMessage("Failed to initialize payment system. Please try again later.");
    }
}
