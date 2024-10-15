$(document).ready(function() {
    var csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });
    var websiteTab = null;
    $('#submit-btn').click(function(event) {
        event.preventDefault();
        var model = $('#model-select').val();
        console.log('Selected Model:', model);
        var userInput = $('#user-input').val();
        if (model !== "" && model !== null) {
            // Send the user input to the server-side view
            $.ajax({
                type: 'POST',
                url: '/process-input/',
                data: {'user_input': userInput, 'model': model},
                beforeSend: function() {
                    // Show a loading animation
                    $('#submit-btn').prop('disabled', true);
                    $('#submit-btn').html('<i class="fas fa-spinner fa-spin"></i> Processing...');
                },
                success: function(response) {
                    // Check if the tab is still open
                    if (websiteTab === null || websiteTab.closed) {
                        websiteTab = window.open('', '_blank');
                    } else {
                        websiteTab.location.href = '';
                    }
                    websiteTab.document.write(response.html);
                    websiteTab.document.close();
                    // Clear the form fields
                    $('#user-input').val('');
                    // Hide the loading animation
                    $('#submit-btn').prop('disabled', false);
                    $('#submit-btn').html('Submit');
                },
                error: function(xhr, status, error) {
                    console.log('Error:', error);
                    // Hide the loading animation
                    $('#submit-btn').prop('disabled', false);
                    $('#submit-btn').html('Submit');
                }
            });
        } else {
            alert("Please select a model");
        }
    });
    $('#clear-btn').click(function(event) {
        event.preventDefault();
        // Send a request to clear the conversation history
        $.ajax({
            type: 'GET',
            url: '/clear-conversation-history/',
            beforeSend: function() {
                // Show a loading animation
                $('#clear-btn').prop('disabled', true);
                $('#clear-btn').html('<i class="fas fa-spinner fa-spin"></i> Clearing...');
            },
            success: function(response) {
                console.log(response.message);
                // Hide the loading animation
                $('#clear-btn').prop('disabled', false);
                $('#clear-btn').html('Clear Conversation History');
            },
            error: function(xhr, status, error) {
                console.log('Error:', error);
                // Hide the loading animation
                $('#clear-btn').prop('disabled', false);
                $('#clear-btn').html('Clear Conversation History');
            }
        });
    });
});