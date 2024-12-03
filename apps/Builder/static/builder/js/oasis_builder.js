$(document).ready(function() {
    console.log("✅ Imagi Builder JavaScript loaded successfully");

    var csrftoken = Cookies.get('csrftoken');
    var websiteTab = null;
    var currentPages = ['index.html', 'about.html', 'styles.css'];

    // Set default file selection on page load
    if (!$('#file-select').val()) {
        $('#file-select').val('index.html');
    }

    // Updated AJAX setup to handle errors silently for specific endpoints
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        error: function(xhr, status, error) {
            // Get the URL from the XHR object
            var url = xhr.url || xhr?.responseURL || '';
            
            // Completely suppress errors for get-page endpoint
            if (url.includes('/builder/get-page/')) {
                return;
            }
            
            // For other endpoints, only log non-404 errors in development
            if (xhr.status !== 404 && 
                (window.location.hostname === 'localhost' || 
                 window.location.hostname === '127.0.0.1')) {
                console.group('Debug Info');
                console.log('Status:', status);
                console.log('Error:', error);
                console.groupEnd();
            }
        }
    });

    // Handle custom page input visibility
    $('#file-select').change(function() {
        var selectedFile = $(this).val();
        if (selectedFile === 'custom') {
            $('#custom-page-input').show();
        } else {
            $('#custom-page-input').hide();
            
            // Only check existing files if it's not styles.css
            if (selectedFile !== 'styles.css') {
                $.ajax({
                    type: 'POST',
                    url: '/builder/get-page/',
                    data: {
                        'file': selectedFile,
                        'csrfmiddlewaretoken': csrftoken
                    },
                    success: function(response) {
                        // Only open the file if it exists and has content
                        if (response.html) {
                            if (websiteTab === null || websiteTab.closed) {
                                websiteTab = window.open('/builder/oasis/' + selectedFile, '_blank');
                            } else {
                                websiteTab.location.href = '/builder/oasis/' + selectedFile;
                            }
                        }
                    },
                    statusCode: {
                        404: function(response) {
                            // File doesn't exist yet - handle silently
                            if (response.responseJSON && response.responseJSON.message) {
                                console.log(response.responseJSON.message);
                            } else {
                                console.log("Waiting for file to be generated:", selectedFile);
                            }
                        }
                    },
                    error: function(xhr, status, error) {
                        // Only log errors that aren't 404
                        if (xhr.status !== 404) {
                            console.error("Error getting page:", error);
                        }
                    }
                });
            }
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
        } else {
            $textarea.attr('placeholder', 'let your imagination flow...');
            $('#file-select').parent().show();
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
            if (!userInput) {
                alert('Please enter your instructions for building the website');
                return;
            }
            if (!model) {
                alert('Please select an AI model');
                return;
            }
            if (selectedFile === 'custom') {
                alert('Please select a valid file to edit');
                return;
            }
        } else if (mode === 'chat') {
            if (!userInput) {
                alert('Please enter your message');
                return;
            }
            if (!model) {
                alert('Please select an AI model');
                return;
            }
            if (selectedFile === 'custom') {
                alert('Please select a file to discuss');
                return;
            }
        }

        // Log the request details
        console.group('🚀 Generate Request');
        console.log('Mode:', mode);
        console.log('Model:', model);
        console.log('File:', selectedFile);
        console.log('User Input:', userInput);
        console.groupEnd();

        // First, get conversation history
        $.ajax({
            type: 'POST',
            url: '/builder/get-conversation-history/',
            data: {
                'model': model,
                'file': selectedFile,
                'user_input': userInput,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(historyResponse) {
                console.group('📜 Conversation History');
                console.log('History:', historyResponse);
                console.groupEnd();
                
                // Now make the main request
                makeGenerateRequest(userInput, model, mode, selectedFile);
            },
            error: function(xhr, status, error) {
                console.error('Failed to get conversation history:', error);
                // Continue with generate request anyway
                makeGenerateRequest(userInput, model, mode, selectedFile);
            }
        });
    });

    function makeGenerateRequest(userInput, model, mode, selectedFile) {
        // Clear only the input textarea, not the response window
        var $textarea = $('#user-input');
        var originalInput = userInput;
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
        var $submitBtn = $('#submit-btn');
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
                console.group('✨ AI Response');
                console.log('Response:', response);
                console.groupEnd();
                
                // Clear the ripple effect
                if (window.rippleInterval) {
                    clearInterval(window.rippleInterval);
                }

                handleGenerateResponse(response, mode, selectedFile, originalInput);
            },
            error: handleAjaxError,
            complete: function() {
                // Re-enable the submit button and restore its text
                $submitBtn.prop('disabled', false);
                $submitBtn.html('<i class="fas fa-magic"></i> ' + (mode === 'chat' ? 'Send' : 'Generate'));
                
                // Reset input placeholder
                $textarea.attr('placeholder', mode === 'chat' ? 
                    'Chat with AI about your website ideas...' : 
                    'let your imagination flow...');
            }
        });
    }

    function handleGenerateResponse(response, mode, selectedFile, originalInput) {
        var $textarea = $('#user-input');
        var $responseWindow = $('#response-window');

        if (mode === 'chat') {
            var newMessage = 'You: ' + originalInput + '\n\nAI: ' + response.message + '\n\n';
            $responseWindow.append(newMessage);
            $responseWindow.scrollTop($responseWindow[0].scrollHeight);
        } else {
            $responseWindow.text('Generated content has been applied to: ' + selectedFile);
            
            if (response.success === false) {
                alert(response.error || 'An error occurred while generating content');
                return;
            }
            
            if (selectedFile === 'styles.css') {
                if (response.html) {
                    updateWebsitePreview(response.html);
                }
            } else {
                updateWebsitePreview(response.response || response);
            }
        }
    }

    // New helper functions
    function updateWebsitePreview(response, filename) {
        // Handle case where response is an object with html property
        const html = typeof response === 'object' ? response.html : response;
        
        // If no valid HTML content, return early
        if (!html || typeof html !== 'string') {
            console.log('No valid HTML content to preview');
            return;
        }
        
        // Default to index.html if filename is not provided or is styles.css
        filename = (!filename || filename === 'styles.css') ? 'index.html' : filename;
        
        if (websiteTab === null || websiteTab.closed) {
            websiteTab = window.open('/builder/oasis/' + filename, '_blank');
        } else {
            websiteTab.location.href = '/builder/oasis/' + filename;
        }
        
        if (websiteTab) {
            websiteTab.document.open();
            var htmlWithBase = html.replace('<head>', 
                '<head><base href="/builder/oasis/">');
            
            // Add click event handlers for navigation
            htmlWithBase = htmlWithBase.replace('</body>', `
                <script>
                    document.addEventListener('click', function(e) {
                        if (e.target.tagName === 'A') {
                            e.preventDefault();
                            var href = e.target.getAttribute('href');
                            if (href) {
                                window.location.href = '/builder/oasis/' + href;
                            }
                        }
                    });
                </script>
            </body>`);
            
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
        
        if (!confirm('Are you sure you want to reset this project? This will delete all files and conversation history.')) {
            return;
        }
        
        console.log("Clear Button Clicked: Clearing conversation history and files");
        
        $.ajax({
            type: 'POST',
            url: '/builder/clear-conversation-history/',
            data: {
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                console.log("Clear History Success:", response.message);
                
                // Close the website preview tab if it's open
                if (websiteTab && !websiteTab.closed) {
                    websiteTab.close();
                    websiteTab = null;
                }
                
                // Clear the UI
                $('#user-input').val('');
                $('#response-window').empty();
                $('#file-select').val('index.html');
                
                // Set the model select to Claude Sonnet
                $('#model-select').val('claude-3-5-sonnet-20241022').trigger('change');
                
                $('#mode-select').val('build');
                $('#file-select').parent().show();
                
                // Show success message
                alert('Project has been reset successfully.');
            },
            error: function(xhr, status, error) {
                console.error("Clear History Error:", error);
                // Don't show error to user, just log it
                console.log("Reset note:", error);
            }
        });
    });

    // Update the undo button handler
    $('#undo-btn').click(function(event) {
        event.preventDefault();
        
        var selectedFile = $('#file-select').val();
        
        if (selectedFile === 'custom') {
            return;  // Silently do nothing for custom pages
        }

        $.ajax({
            type: 'POST',
            url: '/builder/undo-last-action/',
            data: {
                'page': selectedFile,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                console.log('Undo Response:', response);
                
                if (response.html) {
                    // Pass the current filename to updateWebsitePreview
                    var currentFile = selectedFile === 'styles.css' ? 'index.html' : selectedFile;
                    updateWebsitePreview(response.html, currentFile);
                }
                
                // Only show message if something was actually undone
                if (response.message && response.message !== 'Nothing to undo') {
                    alert(response.message);
                }
            },
            error: function(xhr, status, error) {
                // Silently log error but don't show to user
                console.log("Undo note:", error);
            }
        });
    });

    // Add this to your existing JavaScript
    $('#preview-btn').click(function() {
        $.ajax({
            type: 'POST',
            url: '/builder/preview-project/',
            data: {
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                if (response.url) {
                    window.open(response.url, '_blank');
                } else {
                    alert('Failed to start preview server');
                }
            },
            error: function(xhr, status, error) {
                alert('Failed to start preview server: ' + error);
            }
        });
    });
});
