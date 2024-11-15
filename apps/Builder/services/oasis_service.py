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
    # Start with system message
    conversation_history = [get_system_message()]
    
    # Get all messages from the conversation, ordered by creation time
    all_messages = conversation.messages.all().order_by('created_at')
    
    # Process each message
    for msg in all_messages:
        if msg.role == 'user':
            # Include all user messages regardless of page
            conversation_history.append({
                "role": "user",
                "content": msg.content
            })
        elif msg.role == 'assistant' and msg.page == page:
            # Only include assistant messages for the current page
            conversation_history.append({
                "role": "assistant",
                "content": msg.content
            })
    
    # Add the current user input
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    try:
        # Get response from OpenAI
        completion = client.chat.completions.create(
            model=model,
            messages=conversation_history
        )
        assistant_response = completion.choices[0].message.content

        # Save the new messages
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


def test_css(css_content):
    """Extracts CSS content and removes any plain text or non-CSS comments."""
    # Remove markdown code block indicators
    css_content = css_content.replace('```css', '').replace('```', '')
    
    # Split content into lines
    lines = css_content.split('\n')
    css_lines = []
    in_comment = False
    current_selector = None
    current_properties = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip markdown and explanatory text lines
        if any(text in line.lower() for text in [
            'below', 'example', 'here', 'can', 'how', 'incorporate',
            'following', 'create', 'update', 'add', 'style'
        ]):
            continue
            
        # Skip markdown and list markers
        if line.startswith(('#', '>', '-', '1.', '2.', '3.', '*')):
            continue
            
        # Handle CSS comments
        if '/*' in line and '*/' in line:
            css_lines.append(line)
            continue
            
        if '/*' in line:
            in_comment = True
            css_lines.append(line)
            continue
            
        if '*/' in line:
            in_comment = False
            css_lines.append(line)
            continue
            
        if in_comment:
            css_lines.append(line)
            continue
            
        # Handle properties without a selector (add * selector)
        if ':' in line and ';' in line and not current_selector and not line.strip().startswith('@'):
            if not any(char in line for char in ['{', '}']):
                if not current_properties:
                    current_selector = '*'
                    css_lines.append(f'{current_selector} {{')
                current_properties.append(line)
                continue
                
        # Handle rule starts
        if '{' in line:
            # Write previous rule if it exists
            if current_selector and current_properties:
                if not css_lines[-1].endswith('{'):
                    css_lines.append('}')
            current_selector = line.split('{')[0].strip()
            current_properties = []
            css_lines.append(line)
            continue
            
        # Handle rule ends
        if '}' in line:
            current_selector = None
            current_properties = []
            css_lines.append(line)
            continue
            
        # Handle properties inside rules
        if ':' in line:
            css_lines.append(line)
            continue
    
    # Close any open rule
    if current_selector and current_properties:
        css_lines.append('}')
    
    # Join lines back together
    css = '\n'.join(css_lines)
    
    # Clean up the CSS
    css = css.replace(';;', ';')
    css = css.replace('} }', '}}')
    css = css.replace('{ {', '{{')
    
    return css.strip()


def test_html(html):
    """Ensures only valid HTML content is returned."""
    # Look for complete HTML document
    start_idx = html.find('<!DOCTYPE html>')
    if start_idx == -1:
        start_idx = html.find('<html')
    
    if start_idx == -1:
        return ''
        
    end_idx = html.find('</html>')
    if end_idx == -1:
        return ''
        
    return html[start_idx:end_idx + 7]  # 7 is the length of '</html>'


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
