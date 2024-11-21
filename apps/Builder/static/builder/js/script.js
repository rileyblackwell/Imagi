$(document).ready(function() {
    console.log("script.js has been successfully loaded.");

    var csrftoken = Cookies.get('csrftoken');
    var websiteTab = null;
    var currentPages = ['index.html', 'about.html', 'contact.html', 'styles.css'];

    // Set default file selection on page load
    if (!$('#file-select').val()) {
        $('#file-select').val('index.html');
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

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

        $('#file-select').append(
            $('<option></option>').val(newPage).html(newPage)
        );
        
        currentPages.push(newPage);
        
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
        
        if (selectedFile === 'custom' || !userInput || !model) {
            alert('Please fill in all required fields');
            return;
        }

        // Log the request details
        console.log('Sending generate request:', {
            user_input: userInput,
            model: model,
            file: selectedFile
        });

        // Clear the user input immediately after capturing it
        $('#user-input').val('');

        // Disable the submit button and show loading state
        var $submitBtn = $(this);
        $submitBtn.prop('disabled', true);
        $submitBtn.html('<i class="fas fa-spinner fa-spin"></i> Generating...');

        $.ajax({
            type: 'POST',
            url: '/builder/process-input/',
            data: {
                'user_input': userInput,
                'model': model,
                'file': selectedFile,
                'csrfmiddlewaretoken': csrftoken
            },
            beforeSend: function() {
                // Get the conversation history from the backend first
                $.ajax({
                    type: 'POST',
                    url: '/builder/get-conversation-history/',
                    async: false,  // Make this synchronous so we get the history before the main request
                    data: {
                        'model': model,
                        'file': selectedFile,
                        'user_input': userInput,
                        'csrfmiddlewaretoken': csrftoken
                    },
                    success: function(historyResponse) {
                        console.group('Conversation History (Being sent to AI):');
                        
                        if (historyResponse.model === 'claude-sonnet') {
                            console.log('SYSTEM MESSAGE:');
                            console.log(historyResponse.system);
                            console.log('-------------------');
                            
                            console.log('MESSAGES:');
                            historyResponse.messages.forEach((msg, index) => {
                                console.log(`${msg.role.toUpperCase()}:`);
                                console.log(msg.content);
                                console.log('-------------------');
                            });
                        } else {
                            historyResponse.messages.forEach((msg, index) => {
                                console.log(`${index + 1}. ${msg.role.toUpperCase()}:`);
                                console.log(msg.content);
                                console.log('-------------------');
                            });
                        }
                        
                        console.groupEnd();
                    }
                });
            },
            success: function(response) {
                console.log('Success response:', response);
                
                if (selectedFile === 'styles.css') {
                    if (response.html) {
                        updateWebsitePreview(response.html);
                    }
                } else {
                    updateWebsitePreview(response.html || response);
                }
            },
            error: handleAjaxError,
            complete: function() {
                // Re-enable the submit button and restore its text
                $submitBtn.prop('disabled', false);
                $submitBtn.html('<i class="fas fa-magic"></i> Generate');
            }
        });
    });

    // New helper functions
    function updateWebsitePreview(html) {
        if (websiteTab === null || websiteTab.closed) {
            websiteTab = window.open('', '_blank');
        }
        if (websiteTab) {
            websiteTab.document.open();
            var htmlWithBase = html.replace('<head>', 
                '<head><base href="/builder/website/">');
            websiteTab.document.write(htmlWithBase);
            websiteTab.document.close();
        }
    }

    function handleAjaxError(xhr, status, error) {
        console.error("AJAX Error:", error);
        console.error("Status:", status);
        console.error("Response:", xhr.responseText);
        
        let errorMessage = "An error occurred. Please try again.";
        
        if (xhr.responseText) {
            try {
                const response = JSON.parse(xhr.responseText);
                if (response.error) {
                    errorMessage = response.error;
                    if (response.detail) {
                        console.error("Error detail:", response.detail);
                    }
                }
            } catch (e) {
                console.error("Error parsing response:", e);
                const textResponse = xhr.responseText;
                if (textResponse.includes('<!DOCTYPE html>')) {
                    errorMessage = "Server error occurred. Please try again later.";
                }
            }
        }
        
        // Show error message to user
        alert(errorMessage);
    }

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
                $('#user-input').val('');
                $('#file-select').val('index.html');
                $('#model-select').val('');
            },
            error: function(xhr, status, error) {
                console.error("Clear History Error:", error);
                console.error("Status:", status);
                console.error("Response:", xhr.responseText);
            }
        });
    });

    // Update the undo button handler
    $('#undo-btn').click(function(event) {
        event.preventDefault();
        
        var selectedFile = $('#file-select').val();
        
        if (selectedFile === 'custom') {
            return;
        }

        $.ajax({
            type: 'POST',
            url: '/builder/undo-last-action/',
            data: {
                'page': selectedFile,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                console.log('Undo Success:', response);
                
                if (selectedFile === 'styles.css') {
                    // Handle styles.css undo the same way as generate
                    if (websiteTab === null || websiteTab.closed) {
                        websiteTab = window.open('', '_blank');
                    }
                    if (websiteTab) {
                        websiteTab.document.open();
                        var htmlWithBase = response.html.replace('<head>', 
                            '<head><base href="/builder/website/">');
                        websiteTab.document.write(htmlWithBase);
                        websiteTab.document.close();
                    }
                } else if (response.html) {
                    if (websiteTab === null || websiteTab.closed) {
                        websiteTab = window.open('', '_blank');
                    }
                    if (websiteTab) {
                        websiteTab.document.open();
                        var htmlWithBase = response.html.replace('<head>', 
                            '<head><base href="/builder/website/">');
                        websiteTab.document.write(htmlWithBase);
                        websiteTab.document.close();
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error("Undo Error:", error);
                console.error("Status:", status);
                console.error("Response:", xhr.responseText);
            }
        });
    });
});
