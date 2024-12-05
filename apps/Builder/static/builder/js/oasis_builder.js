$(document).ready(function() {
    console.log("✅ Imagi Builder JavaScript loaded successfully");

    var csrftoken = Cookies.get('csrftoken');
    var currentPages = ['index.html', 'about.html', 'styles.css'];

    // Set default file selection on page load
    if (!$('#file-select').val()) {
        $('#file-select').val('index.html');
    }

    // Handle custom page input visibility
    $('#file-select').change(function() {
        var selectedFile = $(this).val();
        if (selectedFile === 'custom') {
            $('#custom-page-input').show();
        } else {
            $('#custom-page-input').hide();
            
            // Just log the file change and update UI
            console.log(`📂 Switched to file: ${selectedFile}`);
            var $responseWindow = $('#response-window');
            $responseWindow.append(`\nSwitched to file: ${selectedFile}\n`);
            $responseWindow.scrollTop($responseWindow[0].scrollHeight);
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
        
        // Update UI
        $('#custom-page-name').val('');
        $('#custom-page-input').hide();
        $('#file-select').val(newPage);
        
        // Show confirmation in response window
        var $responseWindow = $('#response-window');
        $responseWindow.append(`\nAdded new file: ${newPage}\n`);
        $responseWindow.scrollTop($responseWindow[0].scrollHeight);
        
        // Log the new file addition
        console.log(`📄 Added new file: ${newPage}`);
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

    // Submit button handler
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

        // Get conversation history before making request
        $.ajax({
            type: 'POST',
            url: '/builder/get-conversation-history/',
            data: {
                'user_input': userInput,
                'model': model,
                'file': selectedFile,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(historyResponse) {
                // Log conversation history
                console.group('📜 Conversation History');
                historyResponse.messages.forEach(msg => {
                    console.log(`${msg.role.toUpperCase()}:`, msg.content);
                });
                console.groupEnd();
                
                // Now make the actual generate request
                makeGenerateRequest();
            },
            error: function(xhr, status, error) {
                console.error("Error getting conversation history:", error);
                // Continue with generate request even if history fails
                makeGenerateRequest();
            }
        });

        // Make the request
        function makeGenerateRequest() {
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

                    var $responseWindow = $('#response-window');
                    
                    if (mode === 'chat') {
                        // Show chat response
                        var newMessage = 'You: ' + userInput + '\n\nAI: ' + response.message + '\n\n';
                        $responseWindow.append(newMessage);
                    } else {
                        // Show file generation success
                        if (response.success === false) {
                            alert(response.error || 'An error occurred while generating content');
                            return;
                        }
                        
                        // Show success message and file content
                        var successMessage = `\nFile generated successfully: ${selectedFile}\n`;
                        successMessage += `\nContent Preview:\n${response.response || ''}\n`;
                        $responseWindow.append(successMessage);
                        
                        // Log the generated content
                        console.group('📄 Generated File');
                        console.log('File:', selectedFile);
                        console.log('Content:', response.response || response);
                        console.groupEnd();
                    }
                    
                    // Scroll to bottom
                    $responseWindow.scrollTop($responseWindow[0].scrollHeight);
                },
                error: function(xhr, status, error) {
                    console.error("AJAX Error:", error);
                    console.error("Status:", status);
                    console.error("Response:", xhr.responseText);
                    alert("An error occurred. Please try again.");
                },
                complete: function() {
                    // Reset button and placeholder
                    $('#submit-btn').prop('disabled', false);
                    $('#submit-btn').html('<i class="fas fa-magic"></i> ' + (mode === 'chat' ? 'Send' : 'Generate'));
                    $('#user-input').attr('placeholder', mode === 'chat' ? 
                        'Chat with AI about your website ideas...' : 
                        'let your imagination flow...');
                }
            });
        }
    });

    // Clear button handler
    $('#clear-btn').click(function(event) {
        event.preventDefault();
        
        if (!confirm('Are you sure you want to reset this project? This will delete all files and conversation history.')) {
            return;
        }
        
        $.ajax({
            type: 'POST',
            url: '/builder/clear-conversation-history/',
            data: {
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                $('#user-input').val('');
                $('#response-window').empty();
                $('#file-select').val('index.html');
                $('#model-select').val('claude-3-5-sonnet-20241022');
                $('#mode-select').val('build');
                alert('Project has been reset successfully.');
            },
            error: function(xhr, status, error) {
                console.error("Clear History Error:", error);
            }
        });
    });
});
