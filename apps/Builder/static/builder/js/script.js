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
            return;
        }

        // Log the request details
        console.log('Sending generate request:', {
            user_input: userInput,
            model: model,
            file: selectedFile
        });

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
                
                // Log the conversation history in a more readable format
                console.group('Submitted conversation history:');
                response.conversation_history.forEach((message, index) => {
                    console.log(`${index + 1}. ${message.role.toUpperCase()}:`);
                    console.log(message.content);
                    console.log('-------------------');
                });
                console.groupEnd();
                
                if (selectedFile === 'styles.css') {
                    console.log('Updated styles.css, fetching index.html');
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
                            }
                            if (websiteTab) {
                                websiteTab.document.open();
                                var htmlWithBase = htmlResponse.html.replace('<head>', 
                                    '<head><base href="/builder/website/">');
                                websiteTab.document.write(htmlWithBase);
                                websiteTab.document.close();
                            }
                        },
                        error: function(xhr, status, error) {
                            console.error("Error fetching index.html:", error);
                        }
                    });
                } else {
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
                console.error("AJAX Error:", error);
                console.error("Status:", status);
                console.error("Response:", xhr.responseText);
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

    // Add undo button handler
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
                
                if (response.html) {
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
                } else if (websiteTab && !websiteTab.closed) {
                    websiteTab.close();
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
