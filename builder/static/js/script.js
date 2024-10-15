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
        var userInput = $('#user-input').val();
        // Send the user input to the server-side view
        $.ajax({
            type: 'POST',
            url: '/process-input/',
            data: {'user_input': userInput},
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
            }
        });
    });
    $('#clear-btn').click(function(event) {
        event.preventDefault();
        // Send a request to clear the conversation history
        $.ajax({
            type: 'GET',
            url: '/clear-conversation-history/',
            success: function(response) {
                console.log(response.message);
            }
        });
    });
});