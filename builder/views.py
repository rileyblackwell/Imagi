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

    # Add a system message to the conversation history
    system_message = {
        "role": "system",
        "content": (
            "You are a skilled web developer with expertise in HTML, CSS, and JavaScript. "
            "Your task is to generate complete, well-structured, and visually appealing HTML webpages. "
            "Ensure that your responses include a doctype declaration, HTML tags, and a basic structure. "
            "Use semantic HTML elements, CSS selectors, and JavaScript functions to create interactive and responsive webpages. "
            "Consider accessibility, usability, and web standards when crafting your responses. "
            "Respond with a fully functional HTML webpage that is ready to be rendered in a web browser. "
            "Use inline CSS or JavaScript if necessary. "
            "Your goal is to create professional-looking webpages that are easy to use, efficient, and effective. "
        )
    }
    
    conversation_history.append(system_message)

    # Append the user's input to the conversation history
    conversation_history.append({"role": "user", "content": user_input})

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

    parsed_html = test_html(html)

    # Print the AI-generated HTML to a file
    with open('../output.html', 'w') as f:
        f.write(parsed_html)
    
    # Append the AI's response to the conversation history
    conversation_history.append({"role": "assistant", "content": parsed_html})

    # Store the conversation history in the session
    request.session['conversation_history'] = conversation_history

    # Return a JSON response with the HTML
    return JsonResponse({'html': parsed_html})

def clear_conversation_history(request):
    if 'conversation_history' in request.session:
        del request.session['conversation_history']
    return JsonResponse({'message': 'Conversation history cleared'})