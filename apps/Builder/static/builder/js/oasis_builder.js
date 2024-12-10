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
            
            // Just log the file change
            console.log(`📂 Switched to file: ${selectedFile}`);
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

        // Function to animate loading dots
        function animateLoadingDots($element, baseText) {
            let dots = 0;
            return setInterval(() => {
                $element.attr('placeholder', baseText + '.'.repeat(dots + 1));
                dots = (dots + 1) % 3;
            }, 500);
        }

        // Clear the input textarea and show loading state
        var $textarea = $('#user-input');
        var $submitBtn = $(this);
        $textarea.val('');
        
        // Start loading animation
        const baseText = mode === 'chat' ? 'thinking' : 'building';
        $textarea.attr('placeholder', baseText + '...');
        const loadingAnimation = animateLoadingDots($textarea, baseText);
        
        $submitBtn.prop('disabled', true);
        $submitBtn.html('<i class="fas fa-spinner fa-spin"></i> ' + (mode === 'chat' ? 'Processing...' : 'Generating...'));

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
                makeGenerateRequest();
            },
            error: function(xhr, status, error) {
                console.error("Error getting conversation history:", error);
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
                    var $responseWindow = $('#response-window');
                    
                    if (mode === 'chat') {
                        // Show chat response
                        var newMessage = 'You: ' + userInput + '\n\nAI: ' + response.message + '\n\n';
                        $responseWindow.append(newMessage);
                    } else {
                        // Show only success confirmation for build mode
                        if (response.success === false) {
                            // Add error message with proper spacing
                            const timestamp = new Date().toLocaleTimeString();
                            const currentContent = $responseWindow.text();
                            const newLine = currentContent && !currentContent.endsWith('\n') ? '\n' : '';
                            $responseWindow.text(currentContent + newLine + `❌ ${timestamp} - Error: ${response.error || 'An error occurred while generating content'}\n`);
                        } else {
                            // Add success message with proper spacing
                            const timestamp = new Date().toLocaleTimeString();
                            const fileType = selectedFile.endsWith('.html') ? 'template' : 'stylesheet';
                            const currentContent = $responseWindow.text();
                            const newLine = currentContent && !currentContent.endsWith('\n') ? '\n' : '';
                            $responseWindow.text(currentContent + newLine + `✅ ${timestamp} - Successfully generated ${fileType}: ${selectedFile}\n`);
                        }
                    }
                    
                    // Scroll to bottom
                    $responseWindow.scrollTop($responseWindow[0].scrollHeight);
                },
                error: function(xhr, status, error) {
                    console.error("AJAX Error:", error);
                    var $responseWindow = $('#response-window');
                    const timestamp = new Date().toLocaleTimeString();
                    const currentContent = $responseWindow.text();
                    const newLine = currentContent && !currentContent.endsWith('\n') ? '\n' : '';
                    $responseWindow.text(currentContent + newLine + `❌ ${timestamp} - Error: ${error}\n`);
                    $responseWindow.scrollTop($responseWindow[0].scrollHeight);
                },
                complete: function() {
                    // Reset button and placeholder
                    $submitBtn.prop('disabled', false);
                    $submitBtn.html('<i class="fas fa-magic"></i> ' + (mode === 'chat' ? 'Send' : 'Generate'));
                    // Clear the loading animation
                    clearInterval(loadingAnimation);
                    $textarea.attr('placeholder', mode === 'chat' ? 
                        'Chat with AI about your website ideas...' : 
                        'let your imagination flow...');
                }
            });
        }
    });

    // Clear button handler
    $('#clear-btn').click(function(event) {
        event.preventDefault();
        
        if (!confirm('Are you sure you want to clear the response window? This will not delete any generated files.')) {
            return;
        }
        
        $('#response-window').empty();
    });
});
