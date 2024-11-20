# builder/services/oasis_service.py

import os
from dotenv import load_dotenv
from openai import OpenAI
from ..models import Message, Conversation, Page
from .utils import test_html, test_css

# Load environment variables from .env
load_dotenv()
api_key = os.getenv('OPENAI_KEY')
client = OpenAI(api_key=api_key)


def get_system_message():
    """Generates the system message content for the assistant."""
    return {
        "role": "system",
        "content": (
            "You are Imagi Oasis, a web development tool designed to create stunning, modern, and functional multi-page websites from natural language descriptions. "
            "Your task is to generate HTML pages with inline JavaScript and maintain a separate styles.css file for consistent styling across all pages.\n\n"

            "IMPORTANT - Message Format:\n"
            "Each message includes a [File: filename] prefix indicating which file is being discussed or modified. "
            "This helps you track which file each message relates to and ensures you maintain context across the conversation. "
            "When you see a message like '[File: about.html] Add a contact form', you should focus on modifying the about.html file.\n\n"

            "Focus on:\n\n"

            "1. **HTML Structure**:\n"
            "   - When editing any HTML file, ALWAYS provide the complete HTML document including ALL existing content.\n"
            "   - Never provide partial HTML updates - always include the entire document.\n"
            "   - Create clean, semantic HTML that links to the shared styles.css file.\n"
            "   - Include inline JavaScript for page-specific functionality.\n"
            "   - Ensure proper linking between pages.\n\n"

            "2. **CSS Management**:\n"
            "   - When editing styles.css, ALWAYS provide the complete CSS file including ALL existing styles.\n"
            "   - Never provide partial CSS updates - always include the entire stylesheet.\n"
            "   - Maintain consistent styling across all pages through the shared styles.css file.\n"
            "   - Use CSS classes and IDs that work across different pages.\n"
            "   - Create reusable components and styles.\n\n"

            "3. **Visual Design**:\n"
            "   - Create cohesive designs that work across all pages.\n"
            "   - Use consistent color schemes and typography.\n"
            "   - Ensure responsive layouts using CSS Grid and Flexbox.\n\n"

            "4. **User Interaction**:\n"
            "   - Add smooth animations and transitions via CSS.\n"
            "   - Ensure accessibility following WCAG guidelines.\n\n"

            "5. **Performance**:\n"
            "   - Optimize CSS for reusability and performance.\n"
            "   - Minimize redundant styles.\n"
            "   - Avoid including images (currently unsupported).\n\n"

            "When responding:\n"
            "1. Always check the [File: filename] prefix to know which file you're working on.\n"
            "2. If creating/updating HTML: ALWAYS provide the COMPLETE HTML document with ALL existing content, not just the changes.\n"
            "3. If updating styles.css: ALWAYS provide the COMPLETE stylesheet with ALL styles, not just the changes.\n"
            "4. Always maintain consistency across pages.\n\n"

            "Required HTML structure (always include ALL parts):\n"
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            "    <meta charset='UTF-8'>\n"
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
            "    <title>Page Title</title>\n"
            "    <link rel='stylesheet' href='styles.css'>\n"
            "</head>\n"
            "<body>\n"
            "    <!-- ALL existing content must be preserved and modified as needed -->\n"
            "    <!-- Include inline JavaScript within the body -->\n"
            "</body>\n"
            "</html>"
        )
    }


def process_user_input(user_input, model, conversation, page):
    """Processes user input for a specific page."""
    # Start with system message
    conversation_history = [get_system_message()]
    
    # Get all messages from the conversation, ordered by creation time
    all_messages = conversation.messages.all().order_by('created_at')
    
    if page.filename == 'styles.css':
        # For styles.css, include the most recent HTML content of each page
        html_pages = Page.objects.filter(
            conversation=conversation
        ).exclude(filename='styles.css')
        
        for html_page in html_pages:
            latest_html = html_page.messages.filter(
                role='assistant'
            ).order_by('-created_at').first()
            
            if latest_html:
                conversation_history.append({
                    "role": "assistant",
                    "content": f"[File: {html_page.filename}]\nCurrent HTML content:\n{latest_html.content}"
                })
    
    # Process each message
    for msg in all_messages:
        if msg.role == 'user':
            # Store the original user prompt
            conversation_history.append({
                "role": "user",
                "content": f"[File: {msg.page.filename}]\n{msg.content}"
            })
        elif msg.role == 'assistant' and msg.page == page:
            # Store the complete HTML/CSS response without repeating the file name
            conversation_history.append({
                "role": "assistant",
                "content": msg.content  # Only store the content without the file name
            })
    
    # Add current file context
    conversation_history.append({
        "role": "system",
        "content": f"You are now working on file: {page.filename}"
    })
    
    # Add the current user input with file context
    conversation_history.append({
        "role": "user",
        "content": f"[File: {page.filename}]\n{user_input}"
    })
    
    try:
        # Get response from OpenAI
        completion = client.chat.completions.create(
            model=model,
            messages=conversation_history
        )
        assistant_response = completion.choices[0].message.content

        # Validate and clean the response based on file type
        if page.filename.endswith('.html'):
            cleaned_response = test_html(assistant_response)
        elif page.filename == 'styles.css':
            cleaned_response = test_css(assistant_response)
        else:
            cleaned_response = assistant_response

        # If validation failed (empty response), return error
        if not cleaned_response:
            raise ValueError(f"Invalid {page.filename.split('.')[-1].upper()} content received")

        # Save the user's original prompt
        Message.objects.create(
            conversation=conversation,
            page=page,
            role="user",
            content=user_input
        )

        # Save the validated response from the assistant
        Message.objects.create(
            conversation=conversation,
            page=page,
            role="assistant",
            content=cleaned_response  # Store the validated response
        )

        return cleaned_response
    except Exception as e:
        print(f"Error in process_user_input: {e}")
        return str(e)


def undo_last_action(conversation, page):
    """Removes the last user-assistant exchange from the specific page."""
    messages = page.messages.order_by('-created_at')
    total_messages = messages.count()

    if total_messages >= 2:
        # Get the previous content (before the last change)
        previous_content = messages[2].content if total_messages > 2 else ''
        
        # Delete only the last exchange (last two messages)
        latest_two = messages[:2]
        Message.objects.filter(id__in=[msg.id for msg in latest_two]).delete()

        # For styles.css, we need to ensure we return valid CSS
        if page.filename == 'styles.css':
            previous_content = test_css(previous_content)
            if not previous_content:
                # If no previous CSS exists, return empty string but don't delete file
                return '', 'No previous CSS version available.'
        else:
            previous_content = test_html(previous_content) if previous_content else ''

        return previous_content, 'Last action undone successfully.'
    else:
        # Don't delete all messages for styles.css when there's not enough history
        if page.filename == 'styles.css':
            return '', 'Not enough history to undo last action.'
        else:
            messages.all().delete()
            return '', 'Not enough history to undo last action; page history cleared.'
