# views.py

import requests
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
import os
from dotenv import load_dotenv

def index(request):
    return render(request, 'index.html')

@require_http_methods(['POST'])
def process_input(request):
    load_dotenv()  # loads environment variables from .env
    
    user_input = request.POST.get('user_input')
    # Set your OpenAI API key and endpoint URL
    api_key = os.getenv('OPENAI_KEY')
    endpoint_url = 'https://api.openai.com/v1/completions'

    # Set the API request headers and data
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {'model': 'gpt-4', 'prompt': user_input, 'max_tokens': 2048}

    # Send the API request and get the response
    response = requests.post(endpoint_url, headers=headers, json=data)

    # Print out the API response
    print(response.json())

    # Get the returned HTML from the API response
    # returned_html = response.json()['choices'][0]['text']

    # Return the HTML as a response
    return HttpResponse('API response: ' + str(response.json()))