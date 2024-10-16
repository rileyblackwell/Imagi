$(document).ready(function() {
    // Get CSRF token for AJAX requests
    var csrftoken = Cookies.get('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken); // Set the CSRF token in the header
        }
    });
    
    var websiteTab = null;

    // Click event for the submit button
    $('#submit-btn').click(function(event) {
        event.preventDefault(); // Prevent default form submission
        console.log("Submit Button Clicked!"); // Log submit button click

        // Get the user input and model values
        var userInput = $('#user-input').val();
        var model = $('#model-select').val(); 
        
        console.log("User Input:", userInput); // Log user input
        console.log("Model Selected:", model); // Log selected model

        // Clear the input field immediately
        $('#user-input').val('');

        // Perform the AJAX request
        $.ajax({
            type: 'POST',
            url: '/process-input/',
            data: {
                'user_input': userInput,
                'model': model,
                'csrfmiddlewaretoken': csrftoken // Explicitly include the CSRF token
            },
            success: function(response) {
                console.log("AJAX Success: Response received"); // Log on success
                if (websiteTab === null || websiteTab.closed) {
                    websiteTab = window.open('', '_blank');
                } else {
                    websiteTab.location.href = ''; // Clear the tab
                }
                websiteTab.document.write(response.html); // Write the response HTML to the new tab
                websiteTab.document.close();
            },
            error: function(xhr, status, error) {
                console.error("AJAX Error:", error); // Log errors to console
            }
        });
    });

    // Click event for the clear button
    $('#clear-btn').click(function(event) {
        event.preventDefault(); // Prevent default action
        console.log("Clear Button Clicked: Clearing conversation history"); // Log clear button click
        $.ajax({
            type: 'GET',
            url: '/clear-conversation-history/',
            success: function(response) {
                console.log("Clear History Success:", response.message); // Log on success
            },
            error: function(xhr, status, error) {
                console.error("Clear History Error:", error); // Log errors
            }
        });
    });
});
