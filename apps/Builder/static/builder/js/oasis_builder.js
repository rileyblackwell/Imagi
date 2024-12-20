$(document).ready(function() {
    console.log("✅ Imagi Builder JavaScript loaded successfully");

    var csrftoken = Cookies.get('csrftoken');
    var currentPages = ['index.html', 'about.html', 'styles.css'];

    // Create hidden div for measuring text height
    $('body').append('<div class="hidden-div"></div>');
    const $hiddenDiv = $('.hidden-div');
    const $textarea = $('#user-input');

    // Function to auto-expand textarea
    function autoExpand() {
        // Copy the textarea's content to the hidden div
        $hiddenDiv.text($textarea.val() + '\n');
        
        // Get the height of the hidden div
        let newHeight = $hiddenDiv.height();
        
        // Ensure minimum height
        newHeight = Math.max(60, newHeight);
        
        // Ensure maximum height
        newHeight = Math.min(200, newHeight);
        
        // Set the textarea height
        $textarea.height(newHeight);
    }

    // Bind auto-expand to input events
    $textarea.on('input', autoExpand);

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

    // Function to format chat messages
    function formatChatMessage(role, content) {
        const roleClass = role === 'user' ? 'user' : 'assistant';
        const roleText = role === 'user' ? 'You' : 'AI';
        return `<div class="chat-message ${roleClass}">
            <div class="role">${roleText}</div>
            <div class="content">${content}</div>
        </div>`;
    }

    // Wrap the textarea in an input container
    $('#user-input').wrap('<div class="input-container"></div>');

    // Move the submit button inside the input container
    const $submitBtn = $('#submit-btn');
    $submitBtn.appendTo('.input-container');

    // Handle Enter key in textarea
    $('#user-input').on('keydown', function(e) {
        // Check if Enter is pressed without Shift
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            $submitBtn.click();
        }
    });

    // Update the submit button handler
    $('#submit-btn').click(function(event) {
        event.preventDefault();
        
        var userInput = $('#user-input').val().trim();
        if (!userInput) return;
        
        var model = $('#model-select').val();
        var mode = $('#mode-select').val();
        var selectedFile = $('#file-select').val();
        
        // Clear the input and reset its height
        $('#user-input').val('').height(60);
        
        // Show loading state
        $(this).prop('disabled', true)
               .html('<i class="fas fa-spinner"></i>');
        
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
                // Log conversation history
                console.group('📜 Conversation History');
                historyResponse.messages.forEach(msg => {
                    console.log(`[${msg.role.toUpperCase()}]:`);
                    console.log(msg.content);
                    console.log('---');
                });
                console.groupEnd();
                
                makeGenerateRequest();
            },
            error: function(xhr, status, error) {
                console.error("Error getting conversation history:", error);
                makeGenerateRequest();
            }
        });

        // Function to handle insufficient credits
        function handleInsufficientCredits(response) {
            const requiredCredits = response.required_credits || 1.0;
            if (confirm(`You need ${requiredCredits} credits for this request. Would you like to purchase credits now?`)) {
                window.location.href = response.redirect_url;
            }
        }

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
                    
                    // Log AI response
                    console.group('🤖 AI Response');
                    console.log(response.response || response.message);
                    console.groupEnd();
                    
                    if (mode === 'chat') {
                        // Show chat response
                        var userMessage = formatChatMessage('user', userInput);
                        var aiMessage = formatChatMessage('assistant', response.message);
                        $responseWindow.append(userMessage + aiMessage);
                        $responseWindow.scrollTop($responseWindow[0].scrollHeight);
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
                    
                    // Handle insufficient credits
                    if (xhr.status === 402) {
                        try {
                            const response = JSON.parse(xhr.responseText);
                            handleInsufficientCredits(response);
                            return;
                        } catch (e) {
                            console.error("Error parsing response:", e);
                        }
                    }
                    
                    // Handle other errors
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

    // Undo button handler
    $('#undo-btn').click(function(event) {
        event.preventDefault();
        
        // Get the currently selected file
        var selectedFile = $('#file-select').val();
        if (selectedFile === 'custom') {
            alert('Please select a valid file to undo');
            return;
        }
        
        // Show loading state
        const $undoBtn = $(this);
        $undoBtn.prop('disabled', true);
        $undoBtn.html('<i class="fas fa-spinner fa-spin"></i> Undoing...');
        
        // Make request to undo last action
        $.ajax({
            type: 'POST',
            url: '/builder/undo-last-action/',
            data: {
                'page': selectedFile,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                // Add success message to response window
                const timestamp = new Date().toLocaleTimeString();
                const $responseWindow = $('#response-window');
                const currentContent = $responseWindow.text();
                const newLine = currentContent && !currentContent.endsWith('\n') ? '\n' : '';
                $responseWindow.text(currentContent + newLine + `✅ ${timestamp} - ${response.message}\n`);
                $responseWindow.scrollTop($responseWindow[0].scrollHeight);
                
                // If HTML content was returned, update the preview
                if (response.html) {
                    // TODO: Update preview if needed
                }
            },
            error: function(xhr, status, error) {
                console.error("Undo Error:", error);
                
                // Add error message to response window
                const timestamp = new Date().toLocaleTimeString();
                const $responseWindow = $('#response-window');
                const currentContent = $responseWindow.text();
                const newLine = currentContent && !currentContent.endsWith('\n') ? '\n' : '';
                $responseWindow.text(currentContent + newLine + `❌ ${timestamp} - Error undoing last action: ${error}\n`);
                $responseWindow.scrollTop($responseWindow[0].scrollHeight);
            },
            complete: function() {
                // Reset button state
                $undoBtn.prop('disabled', false);
                $undoBtn.html('<i class="fas fa-undo"></i> Undo');
            }
        });
    });

    // Preview button handler
    $('#preview-btn').click(function(event) {
        event.preventDefault();
        
        // Show loading state
        const $previewBtn = $(this);
        $previewBtn.prop('disabled', true);
        $previewBtn.html('<i class="fas fa-spinner fa-spin"></i> Starting Preview...');
        
        // Make request to start preview server
        $.ajax({
            type: 'POST',
            url: '/builder/preview-project/',
            data: {
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                if (response.url) {
                    // Open preview in new tab
                    window.open(response.url, '_blank');
                    
                    // Add success message to response window
                    const timestamp = new Date().toLocaleTimeString();
                    const $responseWindow = $('#response-window');
                    const currentContent = $responseWindow.text();
                    const newLine = currentContent && !currentContent.endsWith('\n') ? '\n' : '';
                    $responseWindow.text(currentContent + newLine + `✅ ${timestamp} - Preview server started at ${response.url}\n`);
                    $responseWindow.scrollTop($responseWindow[0].scrollHeight);
                } else {
                    alert('Error starting preview server');
                }
            },
            error: function(xhr, status, error) {
                console.error("Preview Error:", error);
                alert('Error starting preview server: ' + error);
                
                // Add error message to response window
                const timestamp = new Date().toLocaleTimeString();
                const $responseWindow = $('#response-window');
                const currentContent = $responseWindow.text();
                const newLine = currentContent && !currentContent.endsWith('\n') ? '\n' : '';
                $responseWindow.text(currentContent + newLine + `❌ ${timestamp} - Error starting preview: ${error}\n`);
                $responseWindow.scrollTop($responseWindow[0].scrollHeight);
            },
            complete: function() {
                // Reset button state
                $previewBtn.prop('disabled', false);
                $previewBtn.html('<i class="fas fa-eye"></i> Preview');
            }
        });
    });
});
