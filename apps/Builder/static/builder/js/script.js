$(document).ready(function() {
    console.log("script.js has been successfully loaded.");

    var csrftoken = Cookies.get('csrftoken');
    var websiteTab = null;
    var currentPages = ['index.html', 'about.html', 'contact.html', 'styles.css'];

    // Set default file selection on page load
    if (!$('#file-select').val()) {
        $('#file-select').val('index.html');
    }

    // Handle custom page input visibility
    $('#file-select').change(function() {
        if ($(this).val() === 'custom') {
            $('#custom-page-input').show();
        } else {
            $('#custom-page-input').hide();
        }
    });

    // Handle adding new pages
    $('#add-page-btn').click(function(event) {
        event.preventDefault();
        var newPage = $('#custom-page-name').val().trim();
        
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
        $('#file-select').append(
            $('<option></option>').val(newPage).html(newPage)
        );
        
        currentPages.push(newPage);
        
        // Reset custom input
        $('#custom-page-name').val('');
        $('#custom-page-input').hide();
        $('#file-select').val(newPage);
    });

    // Modified submit button handler
    $('#submit-btn').click(function(event) {
        event.preventDefault();
        
        var userInput = $('#user-input').val().trim();
        var model = $('#model-select').val();
        var selectedFile = $('#file-select').val();
        
        // Don't proceed if 'custom' is selected without adding a new page
        if (selectedFile === 'custom') {
            alert('Please add a new page or select an existing one');
            return;
        }

        console.log('Attempting to send:', {
            user_input: userInput,
            model: model,
            file: selectedFile
        });

        if (!userInput) {
            alert('Please enter your vision');
            return;
        }

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
                'file': selectedFile,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                console.log('Success response:', response);
                
                if (selectedFile === 'styles.css') {
                    console.log('Updated styles.css, fetching index.html');
                    // After styles.css is updated, fetch and render index.html
                    $.ajax({
                        type: 'POST',
                        url: '/builder/get-page/',
                        data: {
                            'file': 'index.html',
                            'csrfmiddlewaretoken': csrftoken
                        },
                        success: function(htmlResponse) {
                            if (websiteTab === null || websiteTab.closed) {
                                websiteTab = window.open('', '_blank');
                            } else {
                                websiteTab.location.href = '';
                            }
                            var htmlWithBase = htmlResponse.html.replace('<head>', 
                                '<head><base href="/builder/website/">');
                            websiteTab.document.write(htmlWithBase);
                            websiteTab.document.close();
                        },
                        error: function(xhr, status, error) {
                            console.error("Error fetching index.html:", error);
                        }
                    });
                } else {
                    // For HTML pages, show the preview of the current page
                    if (websiteTab === null || websiteTab.closed) {
                        websiteTab = window.open('', '_blank');
                    } else {
                        websiteTab.location.href = '';
                    }
                    var htmlWithBase = response.html.replace('<head>', 
                        '<head><base href="/builder/website/">');
                    websiteTab.document.write(htmlWithBase);
                    websiteTab.document.close();
                }
            },
            error: function(xhr, status, error) {
                console.error("AJAX Error:", error);
                console.error("Status:", status);
                console.error("Response:", xhr.responseText);
                alert('Error: ' + (xhr.responseJSON?.error || 'Something went wrong. Please try again.'));
            }
        });
    });

    // Click event for the clear button
    $('#clear-btn').click(function(event) {
        event.preventDefault();
        console.log("Clear Button Clicked: Clearing conversation history");
        
        $.ajax({
            type: 'POST',
            url: '/builder/clear-conversation-history/',
            data: {
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                console.log("Clear History Success:", response.message);
                if (websiteTab && !websiteTab.closed) {
                    websiteTab.close();
                }
                // Clear the input field
                $('#user-input').val('');
                // Reset file select to index.html
                $('#file-select').val('index.html');
                // Reset model select
                $('#model-select').val('');
            },
            error: function(xhr, status, error) {
                console.error("Clear History Error:", error);
                console.error("Status:", status);
                console.error("Response:", xhr.responseText);
                alert('Error clearing history. Please try again.');
            }
        });
    });

    // Rest of your existing code...
});
