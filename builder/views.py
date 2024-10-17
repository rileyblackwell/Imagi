from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
import os
from dotenv import load_dotenv
from openai import OpenAI

def index(request):
    return render(request, 'index.html')

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
            "You are a skilled web developer with expertise in HTML, CSS, and JavaScript, tasked with crafting professional, elegant, and sleek single-page websites that evoke the minimalist sophistication of Apple products. "
            "Your task is to generate complete, well-structured, and visually appealing HTML webpages. "
            "Aim to create comprehensive, feature-rich single-page websites with interactive elements, dynamic functionality, and responsive design. "
            "Maximize token generation to create detailed and polished outputs, incorporating various features such as: "
            "  - JavaScript-enhanced interactions "
            "  - CSS-driven layouts and animations "
            "  - Accessibility features "
            "Ensure that your responses include a doctype declaration, HTML tags, and a basic structure. "
            "Use semantic HTML elements, CSS selectors, and JavaScript functions to create interactive and responsive webpages. "
            "Consider accessibility, usability, and web standards when crafting your responses, ensuring clear typography and readable content layout, with sufficient line height, font sizes, and organized headings. "
            "Respond with a fully functional HTML webpage that is ready to be rendered in a web browser. "
            "Use inline CSS or JavaScript if necessary. "
            "Your goal is to create professional-looking webpages that are easy to use, efficient, and effective."
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

        # Ensure the system message is present
        system_message = {
            "role": "system",
            "content": (
                "You are a skilled web developer with expertise in HTML, CSS, and JavaScript, tasked with crafting professional, elegant, and sleek single-page websites that evoke the minimalist sophistication of Apple products. "
                "Your task is to generate complete, well-structured, and visually appealing HTML webpages. "
                "Aim to create comprehensive, feature-rich single-page websites with interactive elements, dynamic functionality, and responsive design. "
                "Maximize token generation to create detailed and polished outputs, incorporating various features such as: "
                "  - JavaScript-enhanced interactions "
                "  - CSS-driven layouts and animations "
                "  - Accessibility features "
                "Ensure that your responses include a doctype declaration, HTML tags, and a basic structure. "
                "Use semantic HTML elements, CSS selectors, and JavaScript functions to create interactive and responsive webpages. "
                "Consider accessibility, usability, and web standards when crafting your responses, ensuring clear typography and readable content layout, with sufficient line height, font sizes, and organized headings. "
                "Respond with a fully functional HTML webpage that is ready to be rendered in a web browser. "
                "Use inline CSS or JavaScript if necessary. "
                "Your goal is to create professional-looking webpages that are easy to use, efficient, and effective."
            )
        }

        if not any(msg['role'] == 'system' for msg in conversation_history):
            conversation_history.insert(0, system_message)

        request.session['conversation_history'] = conversation_history

        # Check if there's enough history to retrieve the last HTML
        if len(conversation_history) > 1:
            # Get the previous HTML stored in the conversation history
            previous_html = conversation_history[-1]['content']  # Get the last assistant's response

            return JsonResponse({'message': message, 'html': previous_html})

        else:
            # If no previous HTML is available, return empty response
            return JsonResponse({'message': message, 'html': ''})
    else:
        message = 'Conversation history is already empty.'
        return JsonResponse({'message': message, 'html': ''})

def clear_conversation_history(request):
    if 'conversation_history' in request.session:
        del request.session['conversation_history']
    return JsonResponse({'message': 'Conversation history cleared'})
