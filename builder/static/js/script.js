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
        var model = $('#model-select').val(); 
        $.ajax({
            type: 'POST',
            url: '/process-input/',
            data: {'user_input': userInput, 'model': model},
            success: function(response) {
                if (websiteTab === null || websiteTab.closed) {
                    websiteTab = window.open('', '_blank');
                } else {
                    websiteTab.location.href = '';
                }
                websiteTab.document.write(response.html);
                websiteTab.document.close();
                $('#user-input').val('');
            }
        });
    });
    $('#clear-btn').click(function(event) {
        event.preventDefault();
        $.ajax({
            type: 'GET',
            url: '/clear-conversation-history/',
            success: function(response) {
                console.log(response.message);
            }
        });
    });
});