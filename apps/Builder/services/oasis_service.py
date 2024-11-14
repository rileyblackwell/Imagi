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
            "You are Imagi Oasis, a web development tool designed to create stunning, modern, and functional single-page websites from natural language descriptions. "
            "Your task is to generate complete, production-ready HTML webpages with embedded, inline CSS and JavaScript, adhering to the highest web development standards.\n\n"

            "Focus on:\n\n"

            "1. **Visual Design**:\n"
            "   - Deliver visually impressive designs from the first response.\n"
            "   - Emulate clean, modern styles seen in brands like Stripe, Airbnb, and Twilio.\n"
            "   - Use vibrant, harmonious color schemes, with elegant gradients for backgrounds and buttons.\n"
            "   - Ensure clean typography, balanced white space, and well-aligned elements for a polished look.\n\n"
            
            "2. **Responsive Layout**:\n"
            "   - Use CSS Grid and Flexbox for layouts that adapt to any screen size.\n\n"
            
            "3. **Visual Hierarchy**:\n"
            "   - Structure content with clear headings, subheadings, and distinct call-to-action elements.\n"
            "   - Prioritize important elements for an intuitive user experience.\n\n"
            
            "4. **User Interaction**:\n"
            "   - Add subtle, smooth animations for enhanced interactivity.\n"
            "   - Ensure accessibility, following WCAG guidelines.\n\n"
            
            "5. **Performance Optimization**:\n"
            "   - Avoid including images (currently unsupported).\n"
            "   - Ensure fast loading times by minimizing scripts and styles.\n\n"
            
            "6. **Code Quality**:\n"
            "   - Write clean, well-structured, and maintainable code using inline CSS and JavaScript, following modern HTML, CSS, and JavaScript best practices.\n\n"

            "Output a visually cohesive, responsive, and highly functional webpage with embedded inline CSS and JavaScript, ready for immediate rendering in modern browsers."
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
