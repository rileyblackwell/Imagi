$(document).ready(function() {
    console.log("script.js has been successfully loaded."); // Log when script.js is loaded

    // Get CSRF token for AJAX requests
    var csrftoken = Cookies.get('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken); // Set the CSRF token in the header
        }
    });
    
    var websiteTab = null;
    var currentPages = ['index.html', 'about.html', 'contact.html'];

    // Handle custom page input
    $('#page-select').change(function() {
        if ($(this).val() === 'custom') {
            $('#custom-page-input').show();
        } else {
            $('#custom-page-input').hide();
        }
    });

    // Handle adding new pages
    $('#add-page-btn').click(function(event) {
        event.preventDefault();
        var newPage = $('#custom-page-name').val();
        
        if (!newPage) {
            alert('Please enter a page name');
            return;
        }
        
        if (!newPage.endsWith('.html')) {
            newPage += '.html';
        }
        
        if (currentPages.includes(newPage)) {
            alert('This page already exists');
            return;
        }

        // Add new page to select options
        $('#page-select').append(
            $('<option></option>').val(newPage).html(newPage)
        );
        
        currentPages.push(newPage);
        
        // Reset custom input
        $('#custom-page-name').val('');
        $('#custom-page-input').hide();
        $('#page-select').val(newPage);
    });

    // Modified submit button handler
    $('#submit-btn').click(function(event) {
        event.preventDefault();
        
        var userInput = $('#user-input').val();
        var model = $('#model-select').val();
        var selectedPage = $('#page-select').val();
        
        if (!model) {
            alert('Please select an AI model');
            return;
        }

        $('#user-input').val('');

        $.ajax({
            type: 'POST',
            url: '/builder/process-input/',
            data: {
                'user_input': userInput,
                'model': model,
                'page': selectedPage,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                if (websiteTab === null || websiteTab.closed) {
                    websiteTab = window.open('', '_blank');
                } else {
                    websiteTab.location.href = '';
                }
                websiteTab.document.write(response.html);
                websiteTab.document.close();
            },
            error: function(xhr, status, error) {
                console.error("AJAX Error:", error);
            }
        });
    });

    // Modified undo button handler
    $('#undo-btn').click(function(event) {
        event.preventDefault();
        var selectedPage = $('#page-select').val();

        $.ajax({
            type: 'POST',
            url: '/builder/undo-last-action/',
            data: {
                'page': selectedPage,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                console.log("Undo Success:", response.message);
                if (response.html) {
                    if (websiteTab === null || websiteTab.closed) {
                        websiteTab = window.open('', '_blank');
                    } else {
                        websiteTab.location.href = '';
                    }
                    websiteTab.document.write(response.html);
                    websiteTab.document.close();
                } else {
                    if (websiteTab && !websiteTab.closed) {
                        websiteTab.close();
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error("Undo Error:", error);
            }
        });
    });

    // Click event for the clear button
    $('#clear-btn').click(function(event) {
        event.preventDefault(); // Prevent default action
        console.log("Clear Button Clicked: Clearing conversation history"); // Log clear button click
        $.ajax({
            type: 'POST',
            url: '/builder/clear-conversation-history/',  // Updated URL
            success: function(response) {
                console.log("Clear History Success:", response.message); // Log on success
                if (websiteTab && !websiteTab.closed) {
                    websiteTab.close(); // Close the website tab if open
                }
            },
            error: function(xhr, status, error) {
                console.error("Clear History Error:", error); // Log errors
            }
        });
    });
});
