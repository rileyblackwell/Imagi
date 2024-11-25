$(document).ready(function() {
    console.log("script.js has been successfully loaded.");

    var csrftoken = Cookies.get('csrftoken');
    var websiteTab = null;
    var currentPages = ['index.html', 'about.html', 'styles.css'];

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

    // Handle mode selection changes
    $('#mode-select').change(function() {
        var mode = $(this).val();
        var $textarea = $('#user-input');
        
        if (mode === 'chat') {
            $textarea.attr('placeholder', 'Chat with AI about your website ideas...');
            $('#file-select').parent().hide(); // Hide file selection in chat mode
        } else {
            $textarea.attr('placeholder', 'let your imagination flow...');
            $('#file-select').parent().show(); // Show file selection in build mode
        }
    });

    // Modified submit button handler
    $('#submit-btn').click(function(event) {
        event.preventDefault();
        
        var userInput = $('#user-input').val().trim();
        var model = $('#model-select').val();
        var mode = $('#mode-select').val();
        var selectedFile = $('#file-select').val();
        
        // Validate input based on mode
        if (mode === 'build') {
            if (selectedFile === 'custom' || !userInput || !model) {
                alert('Please fill in all required fields');
                return;
            }
        } else if (mode === 'chat') {
            if (!userInput || !model) {
                alert('Please enter your message and select an AI model');
                return;
            }
        }

        // Clear the textarea and start ripple effect
        var $textarea = $('#user-input');
        var originalInput = userInput; // Store original input for chat mode
        $textarea.val('');
        
        // Set initial state with placeholder
        $textarea.attr('placeholder', mode === 'chat' ? 'thinking...' : 'building...');
        
        // Make sure to clear any existing intervals
        if (window.rippleInterval) {
            clearInterval(window.rippleInterval);
        }
        
        // Start new ripple effect with dots
        var dots = 0;
        window.rippleInterval = setInterval(function() {
            var placeholder = (mode === 'chat' ? 'thinking' : 'building') + '.'.repeat(dots);
            $textarea.attr('placeholder', placeholder);
            dots = (dots + 1) % 4;
        }, 500);

        // Disable the submit button and show loading state
        var $submitBtn = $(this);
        $submitBtn.prop('disabled', true);
        $submitBtn.html('<i class="fas fa-spinner fa-spin"></i> ' + (mode === 'chat' ? 'Processing...' : 'Generating...'));

        $.ajax({
            type: 'POST',
            url: mode === 'chat' ? '/builder/chat/' : '/builder/process-input/',
            data: {
                'user_input': userInput,
                'model': model,
                'file': selectedFile,
                'mode': mode,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                console.log('Success response:', response);
                
                // Clear the ripple effect
                if (window.rippleInterval) {
                    clearInterval(window.rippleInterval);
                }

                if (mode === 'chat') {
                    // For chat mode, display the conversation in the textarea
                    $textarea.val('You: ' + originalInput + '\n\nAI: ' + response.message);
                    $textarea.attr('placeholder', 'Chat with AI about your website ideas...');
                } else {
                    // For build mode, handle as before
                    $textarea.attr('placeholder', 'let your imagination flow...');
                    if (selectedFile === 'styles.css') {
                        if (response.html) {
                            updateWebsitePreview(response.html);
                        }
                    } else {
                        updateWebsitePreview(response.html || response);
                    }
                }
            },
            error: function(xhr, status, error) {
                // Handle errors as before
                handleAjaxError(xhr, status, error);
            },
            complete: function() {
                // Re-enable the submit button and restore its text
                $submitBtn.prop('disabled', false);
                $submitBtn.html('<i class="fas fa-magic"></i> ' + (mode === 'chat' ? 'Send' : 'Generate'));
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

    // Modified clear button handler
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
                $('#model-select').val('claude-sonnet');
                $('#mode-select').val('build'); // Reset mode to build
                $('#file-select').parent().show(); // Show file selection
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
