// Handle floating labels and form input behavior
function initializeFormInputs() {
    const formInputs = document.querySelectorAll('.form-input');
    
    formInputs.forEach(input => {
        const wrapper = input.parentElement;
        const placeholder = input.placeholder;
        
        // Handle focus events
        input.addEventListener('focus', () => {
            wrapper.classList.add('focused');
            input.placeholder = ''; // Clear placeholder on focus
        });
        
        // Handle blur events
        input.addEventListener('blur', () => {
            wrapper.classList.remove('focused');
            if (!input.value) {
                input.placeholder = placeholder; // Restore placeholder if empty
                wrapper.classList.remove('has-value');
            } else {
                wrapper.classList.add('has-value');
            }
        });
        
        // Set initial state if input has value
        if (input.value) {
            wrapper.classList.add('has-value');
        }
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeFormInputs);
