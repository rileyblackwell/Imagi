# builder/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services.oasis_service import process_user_input, test_html, undo_last_action, get_system_message


@login_required
def index(request):
    return render(request, 'builder/oasis_builder.html')


@require_http_methods(['POST'])
def process_input(request):
    user_input = request.POST.get('user_input')
    model = request.POST.get('model')
    conversation_history = request.session.get('conversation_history', [])

    # Process user input through the service
    html = process_user_input(user_input, model, conversation_history)
    parsed_html = test_html(html)

    with open('../output.html', 'w') as f:
        f.write(parsed_html)

    conversation_history.append({"role": "assistant", "content": parsed_html})
    request.session['conversation_history'] = conversation_history

    return JsonResponse({'html': parsed_html})


@require_http_methods(['POST'])
def undo_last_action_view(request):
    conversation_history = request.session.get('conversation_history', [])
    conversation_history, message = undo_last_action(conversation_history)
    request.session['conversation_history'] = conversation_history

    # Retrieve previous HTML if it exists
    previous_html = conversation_history[-1]['content'] if len(conversation_history) > 1 else ''
    with open('../output.html', 'w') as f:
        f.write(previous_html)

    return JsonResponse({'message': message, 'html': previous_html})


@require_http_methods(['POST'])
def clear_conversation_history(request):
    if 'conversation_history' in request.session:
        del request.session['conversation_history']
    return JsonResponse({'message': 'Conversation history cleared'})
