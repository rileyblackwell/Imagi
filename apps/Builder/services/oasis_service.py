# builder/services/oasis_service.py

import os
from dotenv import load_dotenv
from openai import OpenAI
from ..models import Message, Conversation, Page

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

            "Focus on:\n\n"

            "1. **HTML Structure**:\n"
            "   - Create clean, semantic HTML that links to the shared styles.css file.\n"
            "   - Include inline JavaScript for page-specific functionality.\n"
            "   - Ensure proper linking between pages.\n\n"

            "2. **CSS Management**:\n"
            "   - Maintain a shared styles.css file for consistent styling across all pages.\n"
            "   - Use CSS classes and IDs that work across different pages.\n"
            "   - Create reusable components and styles.\n"
            "   - When asked to modify styles, update the styles.css file appropriately.\n\n"

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
            "1. If creating/updating HTML: Provide complete HTML with inline JavaScript and link to styles.css.\n"
            "2. If updating styles: Provide the complete updated styles.css content.\n"
            "3. Always maintain consistency across pages.\n\n"

            "Example HTML structure:\n"
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            "    <link rel='stylesheet' href='styles.css'>\n"
            "</head>\n"
            "<body>\n"
            "    <!-- Content with inline JavaScript -->\n"
            "</body>\n"
            "</html>"
        )
    }


def process_user_input(user_input, model, conversation, page):
    """Processes user input for a specific page."""
    # Get messages specific to this page
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in page.messages.all()
    ]
    
    # Add system message if it doesn't exist
    if not any(msg['role'] == 'system' for msg in conversation_history):
        conversation_history.insert(0, get_system_message())
    
    conversation_history.append({"role": "user", "content": user_input})
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=conversation_history
        )
        assistant_response = completion.choices[0].message.content

        # Save messages with page reference
        Message.objects.create(
            conversation=conversation,
            page=page,
            role="user",
            content=user_input
        )
        Message.objects.create(
            conversation=conversation,
            page=page,
            role="assistant",
            content=assistant_response
        )

        return assistant_response
    except Exception as e:
        print(f"Error in process_user_input: {e}")
        return str(e)


def test_html(html):
    """Parses the HTML and extracts the main document."""
    start_idx = html.find('<!DOCTYPE html>')
    if start_idx == -1:
        start_idx = html.find('<html>')
    end_idx = html.find('</html>') + len('</html>')
    return html[start_idx:end_idx] if start_idx != -1 and end_idx != -1 else html


def undo_last_action(conversation, page):
    """Removes the last user-assistant exchange from the specific page."""
    messages = page.messages.order_by('-created_at')
    total_messages = messages.count()

    if total_messages >= 2:
        previous_html = messages[2].content if total_messages > 2 else ''
        latest_two = messages[:2]
        Message.objects.filter(id__in=[msg.id for msg in latest_two]).delete()
        return previous_html, 'Last action undone successfully.'
    else:
        messages.all().delete()
        return '', 'Not enough history to undo last action; page history cleared.'
