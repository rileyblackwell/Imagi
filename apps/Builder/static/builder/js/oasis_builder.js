$(document).ready(function() {
    console.log("✅ Imagi Builder JavaScript loaded successfully");

    // Elements
    const $userInput = $('#user-input');
    const $submitBtn = $('#submit-btn');
    const $responseWindow = $('#response-window');
    const $modeSelect = $('#mode-select');
    const $fileSelect = $('#file-select');
    const $modelSelect = $('#model-select');
    
    var csrftoken = Cookies.get('csrftoken');
    var currentPages = ['index.html', 'about.html', 'styles.css'];

    // Auto-resize textarea
    function autoResizeTextarea() {
        $userInput.css('height', 'auto');
        $userInput.css('height', $userInput[0].scrollHeight + 'px');
        
        // Enable/disable submit button based on input
        $submitBtn.prop('disabled', !$userInput.val().trim());
    }

    // Handle input changes
    $userInput.on('input', autoResizeTextarea);

    // Handle key press
    $userInput.on('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!$submitBtn.prop('disabled')) {
                handleSubmit();
            }
        }
    });

    // Handle form submission
    $submitBtn.on('click', handleSubmit);

    async function handleSubmit() {
        const userMessage = $userInput.val().trim();
        if (!userMessage) return;

        // Disable input and button while processing
        $userInput.prop('disabled', true);
        $submitBtn.prop('disabled', true);

        // Add user message to chat
        addMessageToChat('user', userMessage);

        try {
            // Get current mode and file
            const mode = $modeSelect.val();
            const currentFile = $fileSelect.val();
            const model = $modelSelect.val();

            // Send message to backend
            const response = await fetch('/builder/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({
                    message: userMessage,
                    mode: mode,
                    file: currentFile,
                    model: model
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            // Add AI response to chat
            addMessageToChat('assistant', data.response);

        } catch (error) {
            console.error('Error:', error);
            addMessageToChat('error', 'Sorry, there was an error processing your request.');
        } finally {
            // Re-enable input and button
            $userInput.prop('disabled', false);
            $submitBtn.prop('disabled', false);
            
            // Clear and reset input
            $userInput.val('');
            $userInput.css('height', 'auto');
            $userInput.focus();
        }
    }

    function addMessageToChat(role, content) {
        const messageDiv = $('<div>').addClass(`chat-message ${role}-message`);
        
        // Add icon based on role
        const iconDiv = $('<div>').addClass('message-icon').html(getIconForRole(role));
        messageDiv.append(iconDiv);

        // Add content
        const contentDiv = $('<div>').addClass('message-content').html(formatMessage(content));
        messageDiv.append(contentDiv);

        $responseWindow.append(messageDiv);
        
        // Scroll to bottom
        $responseWindow.scrollTop($responseWindow[0].scrollHeight);

        // Add fade-in animation
        messageDiv.css({
            'opacity': '0',
            'transform': 'translateY(20px)'
        });
        
        requestAnimationFrame(() => {
            messageDiv.css({
                'transition': 'opacity 0.3s ease, transform 0.3s ease',
                'opacity': '1',
                'transform': 'translateY(0)'
            });
        });
    }

    function getIconForRole(role) {
        switch (role) {
            case 'user':
                return '<i class="fas fa-user"></i>';
            case 'assistant':
                return '<i class="fas fa-robot"></i>';
            case 'error':
                return '<i class="fas fa-exclamation-circle"></i>';
            default:
                return '';
        }
    }

    function formatMessage(content) {
        // Convert markdown-style code blocks
        content = content.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code class="$1">$2</code></pre>');
        
        // Convert inline code
        content = content.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Convert URLs to links
        content = content.replace(
            /(https?:\/\/[^\s<]+[^<.,:;"')\]\s])/g, 
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        return content;
    }

    // Handle mobile menu toggle
    const menuToggle = $('<button>')
        .addClass('menu-toggle')
        .html('<i class="fas fa-bars"></i>')
        .prependTo('.main-chat-area');

    menuToggle.on('click', () => {
        $('.side-controls').toggleClass('active');
    });

    // Handle custom page input visibility
    $fileSelect.change(function() {
        var selectedFile = $(this).val();
        if (selectedFile === 'custom') {
            $('#custom-page-input').show();
        } else {
            $('#custom-page-input').hide();
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

        $fileSelect.append(
            $('<option></option>').val(newPage).html(newPage)
        );
        
        currentPages.push(newPage);
        
        // Update UI
        $('#custom-page-name').val('');
        $('#custom-page-input').hide();
        $fileSelect.val(newPage);
        
        // Show confirmation
        addMessageToChat('system', `Added new file: ${newPage}`);
        
        console.log(`📄 Added new file: ${newPage}`);
    });

    // Handle mode selection changes
    $modeSelect.change(function() {
        var mode = $(this).val();
        
        if (mode === 'chat') {
            $userInput.attr('placeholder', 'Chat with AI about your website ideas...');
        } else {
            $userInput.attr('placeholder', 'let your imagination flow...');
            $fileSelect.parent().show();
        }
    });

    // Clear button handler
    $('#clear-btn').click(function(event) {
        event.preventDefault();
        
        if (!confirm('Are you sure you want to clear the response window? This will not delete any generated files.')) {
            return;
        }
        
        $responseWindow.empty();
    });

    // Undo button handler
    $('#undo-btn').click(function(event) {
        event.preventDefault();
        
        var selectedFile = $fileSelect.val();
        if (selectedFile === 'custom') {
            alert('Please select a valid file to undo');
            return;
        }
        
        const $undoBtn = $(this);
        $undoBtn.prop('disabled', true)
               .html('<i class="fas fa-spinner fa-spin"></i> Undoing...');
        
        $.ajax({
            type: 'POST',
            url: '/builder/undo-last-action/',
            data: {
                'page': selectedFile,
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                addMessageToChat('system', `✅ ${response.message}`);
                
                if (response.html) {
                    // TODO: Update preview if needed
                }
            },
            error: function(xhr, status, error) {
                console.error("Undo Error:", error);
                addMessageToChat('error', `Error undoing last action: ${error}`);
            },
            complete: function() {
                $undoBtn.prop('disabled', false)
                       .html('<i class="fas fa-undo"></i> Undo');
            }
        });
    });

    // Preview button handler
    $('#preview-btn').click(function(event) {
        event.preventDefault();
        
        const $previewBtn = $(this);
        $previewBtn.prop('disabled', true)
                  .html('<i class="fas fa-spinner fa-spin"></i> Starting Preview...');
        
        $.ajax({
            type: 'POST',
            url: '/builder/preview-project/',
            data: {
                'csrfmiddlewaretoken': csrftoken
            },
            success: function(response) {
                if (response.url) {
                    window.open(response.url, '_blank');
                    addMessageToChat('system', `✅ Preview server started at ${response.url}`);
                } else {
                    alert('Error starting preview server');
                }
            },
            error: function(xhr, status, error) {
                console.error("Preview Error:", error);
                addMessageToChat('error', `Error starting preview: ${error}`);
            },
            complete: function() {
                $previewBtn.prop('disabled', false)
                          .html('<i class="fas fa-eye"></i> Preview');
            }
        });
    });

    // Initialize
    autoResizeTextarea();
});
