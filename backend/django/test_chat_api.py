#!/usr/bin/env python
"""
Test script for the Imagi Oasis chat API.
This script sends a test request to the chat API endpoint.
"""

import os
import sys
import json
import requests
from datetime import datetime

def setup_environment():
    """Set up Django environment."""
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    # Import Django settings
    from django.conf import settings
    print(f"DEBUG = {settings.DEBUG}")
    print(f"SECRET_KEY set = {'Yes' if settings.SECRET_KEY else 'No'}")
    
    # Check if we're in the correct Django project
    print(f"INSTALLED_APPS: {', '.join(settings.INSTALLED_APPS[:5])}...")

def get_auth_token(username='admin', password='admin'):
    """Get authentication token."""
    response = requests.post(
        "http://localhost:8000/api/v1/auth/token/",
        json={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        return response.json().get('token')
    else:
        print(f"Failed to get token: {response.status_code} - {response.text}")
        return None

def test_chat_api(token):
    """Test the chat API endpoint."""
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    # Prepare a minimal test payload
    payload = {
        'message': 'Hello, testing the chat API',
        'model': 'gpt-4o',
        'project_id': 'test-project',
        'mode': 'chat'
    }
    
    print(f"Sending payload: {json.dumps(payload, indent=2)}")
    
    # Make the request
    response = requests.post(
        "http://localhost:8000/api/v1/agents/chat/",
        headers=headers,
        json=payload
    )
    
    # Print response information
    print(f"Status code: {response.status_code}")
    print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
    
    try:
        content = response.json()
        print(f"Response: {json.dumps(content, indent=2)}")
    except:
        print(f"Raw response: {response.text[:500]}...")

def test_streaming_api(token):
    """Test the chat API endpoint with streaming enabled."""
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    # Prepare a minimal test payload
    payload = {
        'message': 'Hello, testing the streaming chat API',
        'model': 'gpt-4o',
        'project_id': 'test-project',
        'mode': 'chat',
        'stream': True
    }
    
    print(f"Sending streaming payload: {json.dumps(payload, indent=2)}")
    
    # Make the request
    response = requests.post(
        "http://localhost:8000/api/v1/agents/chat/",
        headers=headers,
        json=payload,
        stream=True
    )
    
    # Print response information
    print(f"Status code: {response.status_code}")
    print(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
    
    if response.status_code == 200:
        print("Streaming response chunks:")
        for chunk in response.iter_lines():
            if chunk:
                print(f"Chunk: {chunk.decode('utf-8')}")
    else:
        try:
            content = response.json()
            print(f"Error response: {json.dumps(content, indent=2)}")
        except:
            print(f"Raw error response: {response.text[:500]}...")

def main():
    """Main function to run the tests."""
    print(f"=== Starting chat API test at {datetime.now().isoformat()} ===")
    
    # Try to set up Django environment for direct API testing
    try:
        setup_environment()
        print("Django environment set up successfully")
    except Exception as e:
        print(f"Failed to set up Django environment: {e}")
        print("Continuing with HTTP tests only...")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("Failed to get authentication token. Exiting.")
        sys.exit(1)
    
    print("\n=== Testing regular chat API ===")
    test_chat_api(token)
    
    print("\n=== Testing streaming chat API ===")
    test_streaming_api(token)
    
    print("\n=== Test completed ===")

if __name__ == "__main__":
    main() 