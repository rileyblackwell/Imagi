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
        var selectedFile = $(this).val();
        if (selectedFile === 'custom') {
            $('#custom-page-input').show();
        } else {
            $('#custom-page-input').hide();
            
            // Load and display the selected file
            if (selectedFile !== 'styles.css') {
                $.ajax({
                    type: 'GET',
                    url: '/builder/website/' + selectedFile,
                    success: function(response) {
                        if (websiteTab === null || websiteTab.closed) {
                            websiteTab = window.open('', '_blank');
                        }
                        if (websiteTab) {
                            websiteTab.location.href = '/builder/website/' + selectedFile;
                        }
                    },
                    error: function(xhr, status, error) {
                        console.error('Error loading file:', error);
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
        
        // Log the request details
        console.group('🚀 Generate Request');
        console.log('Mode:', mode);
        console.log('Model:', model);
        console.log('File:', selectedFile);
        console.log('User Input:', userInput);
        console.groupEnd();

        // Validate input based on mode
        if (mode === 'build') {
            if (selectedFile === 'custom' || !userInput || !model) {
                alert('Please fill in all required fields');
                return;
            }
        } else if (mode === 'chat') {
            if (!userInput || !model || selectedFile === 'custom') {
                alert('Please enter your message, select an AI model, and choose a file to discuss');
                return;
            }
        }

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
            beforeSend: function() {
                $.ajax({
                    type: 'POST',
                    url: '/builder/get-conversation-history/',
                    async: false,
                    data: {
                        'model': model,
                        'file': selectedFile,
                        'user_input': userInput,
                        'csrfmiddlewaretoken': csrftoken
                    },
                    success: function(historyResponse) {
                        console.group('📜 Conversation History (Being sent to AI)');
                        
                        // Common function to handle message logging
                        function logMessage(msg) {
                            if (msg.content.includes('=== SYSTEM PROMPT ===')) {
                                console.group('🤖 System Prompt');
                                console.log(msg.content.split('===')[2]?.trim() || msg.content);
                                console.groupEnd();
                            } else if (msg.content.includes('=== CURRENT WEBSITE FILES ===')) {
                                console.group('📄 Website Files');
                                console.log(msg.content.split('===')[2]?.trim() || msg.content);
                            } else if (msg.content.includes('=== CHAT HISTORY FOR')) {
                                console.group('💬 Chat History');
                                console.log(msg.content.split('===')[2]?.trim() || msg.content);
                            } else if (msg.content.includes('=== BUILD HISTORY FOR')) {
                                console.group('🏗️ Build History');
                                console.log(msg.content.split('===')[2]?.trim() || msg.content);
                            } else if (msg.content.includes('=== CURRENT TASK ===')) {
                                console.group('🎯 Current Task');
                                console.log(msg.content.split('===')[2]?.trim() || msg.content);
                            } else {
                                // Regular message content
                                console.log(`${msg.role.toUpperCase()}:`);
                                console.log(msg.content);
                                console.log('-------------------');
                            }
                            
                            // Close group for section headers
                            if (msg.content.includes('===') && 
                                !msg.content.includes('=== SYSTEM PROMPT ===')) {
                                console.groupEnd();
                            }
                        }
                        
                        if (historyResponse.model === 'claude-sonnet') {
                            // For Claude, first log the system message in the same format
                            console.group('🤖 System Prompt');
                            console.log(historyResponse.system);
                            console.groupEnd();
                            
                            // Create a messages array that includes section headers
                            let messages = [];
                            let hasFiles = false;
                            let hasChat = false;
                            let hasBuild = false;
                            
                            // Process messages to identify sections
                            historyResponse.messages.forEach(msg => {
                                if (msg.content.startsWith('[File:') && !hasFiles) {
                                    messages.push({
                                        role: 'system',
                                        content: '=== CURRENT WEBSITE FILES ==='
                                    });
                                    hasFiles = true;
                                } else if (msg.content.startsWith('[Chat]') && !hasChat) {
                                    messages.push({
                                        role: 'system',
                                        content: '=== CHAT HISTORY ==='
                                    });
                                    hasChat = true;
                                } else if (!msg.content.startsWith('[Chat]') && 
                                         msg.content.startsWith('[File:') && !hasBuild) {
                                    messages.push({
                                        role: 'system',
                                        content: '=== BUILD HISTORY ==='
                                    });
                                    hasBuild = true;
                                }
                                messages.push(msg);
                            });
                            
                            // Log all messages with proper sections
                            messages.forEach(logMessage);
                        } else {
                            // For GPT models, log all messages including system message
                            historyResponse.messages.forEach(logMessage);
                        }
                        
                        console.groupEnd();
                    }
                });
            },
            success: function(response) {
                console.group('✨ AI Response');
                console.log('Response:', response);
                
                // Clear the ripple effect
                if (window.rippleInterval) {
                    clearInterval(window.rippleInterval);
                }

                if (mode === 'chat') {
                    // For chat mode, append the conversation to the response window
                    var $responseWindow = $('#response-window');
                    var newMessage = 'You: ' + originalInput + '\n\nAI: ' + response.message + '\n\n';
                    $responseWindow.append(newMessage);
                    
                    // Scroll to bottom of response window
                    $responseWindow.scrollTop($responseWindow[0].scrollHeight);
                    
                    // Reset input placeholder
                    $textarea.attr('placeholder', 'Chat with AI about your website ideas...');
                } else {
                    // For build mode, show the generated content in the response window
                    var $responseWindow = $('#response-window');
                    $responseWindow.text('Generated content has been applied to: ' + selectedFile);
                    
                    // Reset input placeholder
                    $textarea.attr('placeholder', 'let your imagination flow...');
                    
                    // Update website preview
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
                console.group('❌ Error');
                console.error("AJAX Error:", error);
                console.error("Status:", status);
                console.error("Response:", xhr.responseText);
                console.groupEnd();
                
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
            
            // Add click event handlers for navigation
            htmlWithBase = htmlWithBase.replace('</body>', `
                <script>
                    document.addEventListener('click', function(e) {
                        if (e.target.tagName === 'A') {
                            e.preventDefault();
                            var href = e.target.getAttribute('href');
                            if (href) {
                                window.location.href = '/builder/website/' + href;
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
                    // Update the website preview with the previous version
                    if (websiteTab === null || websiteTab.closed) {
                        websiteTab = window.open('', '_blank');
                    }
                    if (websiteTab) {
                        updateWebsitePreview(response.html);
                    }
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
});
