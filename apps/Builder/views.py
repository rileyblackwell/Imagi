from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
import os
from dotenv import load_dotenv
from openai import OpenAI

def index(request):
    return render(request, 'builder/index.html')  # Make sure this path is correct

@require_http_methods(['POST'])
def process_input(request):
    load_dotenv()  # loads environment variables from .env
    
    user_input = request.POST.get('user_input')
    model = request.POST.get('model')  # Get the selected model from the request

    # Set your OpenAI API key and endpoint URL
    api_key = os.getenv('OPENAI_KEY')

    # Create an OpenAI client
    client = OpenAI(api_key=api_key)

    # Get the conversation history from the session
    conversation_history = request.session.get('conversation_history', [])

    # Add a system message to the conversation history if it's not already there
    system_message = {
        "role": "system",
        "content": (
            "You are a highly skilled web developer with expertise in crafting visually stunning, modern, and highly functional single-page websites. "
            "Your mission is to generate complete, production-ready HTML webpages that adhere to the highest standards of web development and incorporate innovative design elements. "
            
            "Key areas to emphasize:\n\n"
            
            "1. **Aesthetic Design**:\n"
            "   - Utilize vibrant and harmonious color palettes.\n"
            "   - Integrate elegant gradients for backgrounds and buttons.\n"
            "   - Ensure readability with high contrast.\n\n"
            
            "2. **Responsive Layout**:\n"
            "   - Design layouts that seamlessly adapt to various device sizes.\n"
            "   - Employ CSS Grid and Flexbox for efficient layout management.\n\n"
            
            "3. **User Engagement**:\n"
            "   - Incorporate interactive elements to enhance user interaction.\n"
            "   - Ensure accessibility for all users, adhering to WCAG guidelines.\n\n"
            
            "4. **Performance Optimization**:\n"
            "   - Optimize images and assets for swift loading times.\n"
            "   - Minimize the use of heavy scripts and styles.\n\n"
            
            "5. **Code Excellence**:\n"
            "   - Write clean, well-documented, and maintainable code.\n"
            "   - Follow modern best practices for HTML, CSS, and JavaScript.\n\n"
            
            "6. **Advanced Features**:\n"
            "   - Implement sophisticated UI components like carousels and modals.\n"
            "   - Consider adding subtle animations for a dynamic experience.\n\n"
            
            "Ensure your response includes a complete HTML document with embedded CSS and JavaScript. "
            "The webpage should be fully functional, visually impressive, and ready to be rendered in a modern web browser without additional processing. "
            "Focus on creating a cohesive, professional design that effectively communicates the website's purpose while providing an engaging user experience."
        )
    }

    # Add system message only if it's not already present in the history
    if not any(msg['role'] == 'system' for msg in conversation_history):
        conversation_history.insert(0, system_message)

    # Append the user's input to the conversation history
    conversation_history.append({"role": "user", "content": user_input})

    # Store the selected model in the session
    request.session['model'] = model

    # Create a completion using the selected model
    try:
        completion = client.chat.completions.create(
            model=model,  # Use the selected model
            messages=conversation_history
        )
    except Exception as e:
        return JsonResponse({'error': str(e)})

    # Get the AI-generated HTML
    html = completion.choices[0].message.content

    parsed_html = test_html(html)  # Use the test_html function defined below

    # Print the AI-generated HTML to a file
    with open('../output.html', 'w') as f:
        f.write(parsed_html)

    # Append the AI's response to the conversation history
    conversation_history.append({"role": "assistant", "content": parsed_html})

    # Store the conversation history in the session
    request.session['conversation_history'] = conversation_history

    # Return a JSON response with the HTML
    return JsonResponse({'html': parsed_html})

def test_html(html):
    # Parse the HTML to get only the HTML code
    start_idx = html.find('<!DOCTYPE html>')
    if start_idx == -1:
        start_idx = html.find('<html>')

    end_idx = html.find('</html>') + len('</html>')
    if start_idx != -1 and end_idx != -1:
        return html[start_idx:end_idx]
    else:
        return html

@require_http_methods(['POST'])
def undo_last_action(request):
    if 'conversation_history' in request.session:
        conversation_history = request.session['conversation_history']
        if len(conversation_history) >= 2:
            # Remove the last two elements (assistant's response, user's input)
            conversation_history = conversation_history[:-2]
            message = 'Last action undone successfully.'
        else:
            # If less than two elements, clear the conversation history
            conversation_history = []
            message = 'Not enough history to undo last action; conversation history cleared.'

        # Use the same system message as in process_input
        system_message = {
            "role": "system",
            "content": (
                "You are a highly skilled web developer with expertise in crafting visually stunning, modern, and highly functional single-page websites. "
                "Your mission is to generate complete, production-ready HTML webpages that adhere to the highest standards of web development and incorporate innovative design elements. "
                
                "Key areas to emphasize:\n\n"
                
                "1. **Aesthetic Design**:\n"
                "   - Utilize vibrant and harmonious color palettes.\n"
                "   - Integrate elegant gradients for backgrounds and buttons.\n"
                "   - Ensure readability with high contrast.\n\n"
                
                "2. **Responsive Layout**:\n"
                "   - Design layouts that seamlessly adapt to various device sizes.\n"
                "   - Employ CSS Grid and Flexbox for efficient layout management.\n\n"
                
                "3. **User Engagement**:\n"
                "   - Incorporate interactive elements to enhance user interaction.\n"
                "   - Ensure accessibility for all users, adhering to WCAG guidelines.\n\n"
                
                "4. **Performance Optimization**:\n"
                "   - Optimize images and assets for swift loading times.\n"
                "   - Minimize the use of heavy scripts and styles.\n\n"
                
                "5. **Code Excellence**:\n"
                "   - Write clean, well-documented, and maintainable code.\n"
                "   - Follow modern best practices for HTML, CSS, and JavaScript.\n\n"
                
                "6. **Advanced Features**:\n"
                "   - Implement sophisticated UI components like carousels and modals.\n"
                "   - Consider adding subtle animations for a dynamic experience.\n\n"
                
                "Ensure your response includes a complete HTML document with embedded CSS and JavaScript. "
                "The webpage should be fully functional, visually impressive, and ready to be rendered in a modern web browser without additional processing. "
                "Focus on creating a cohesive, professional design that effectively communicates the website's purpose while providing an engaging user experience."
            )
        }

        if not any(msg['role'] == 'system' for msg in conversation_history):
            conversation_history.insert(0, system_message)

        request.session['conversation_history'] = conversation_history

        # Check if there's enough history to retrieve the last HTML
        if len(conversation_history) > 1:
            # Get the previous HTML stored in the conversation history
            previous_html = conversation_history[-1]['content']  # Get the last assistant's response

            # Print the AI-generated HTML to a file
            with open('../output.html', 'w') as f:
                f.write(previous_html)

            return JsonResponse({'message': message, 'html': previous_html})

        else:
            # If no previous HTML is available, return empty response
            return JsonResponse({'message': message, 'html': ''})
    else:
        message = 'Conversation history is already empty.'
        return JsonResponse({'message': message, 'html': ''})

@require_http_methods(['POST'])
def clear_conversation_history(request):
    if 'conversation_history' in request.session:
        del request.session['conversation_history']
    return JsonResponse({'message': 'Conversation history cleared'})

