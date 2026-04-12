"""
Chat Agent using OpenAI Agents SDK.

This module provides a specialized chat agent for natural language conversations
about web development and the user's projects.
"""

import logging
from typing import Optional

from agents import Agent, RunContextWrapper

# Configure logging
logger = logging.getLogger(__name__)

# Default model
DEFAULT_MODEL = "gpt-5.2"

# Chat agent system instructions
CHAT_AGENT_INSTRUCTIONS = """You are an expert web designer and developer called Imagi, a powerful AI platform for building web applications. You assist users with understanding their project code, explaining concepts, and providing guidance on web development using Django, Vue.js, and modern frontend technologies.

Key Responsibilities:
1. Help users understand their current website structure and design choices.
2. Provide clear explanations about Django templates, CSS styling, and web design best practices.
3. Suggest improvements and answer questions about the user's web application.
4. Maintain context of the entire project while discussing specific files.

Guidelines for your responses:
1. Be concise, clear, and focused on providing actionable information.
2. When explaining code, focus on the most important concepts first.
3. If asked about a specific file, focus your answer on that file's content.
4. Use code examples when helpful, but keep them brief and targeted.
5. When suggesting improvements, explain the rationale briefly.
6. For technical questions, provide specific, practical guidance.
7. Remember that users may be at different skill levels - adjust accordingly.

Technology Stack:
- Backend: Django with REST framework
- Frontend: Vue.js 3 with Composition API
- Styling: TailwindCSS
- Build tools: Vite
- State management: Pinia
- HTTP client: Axios

Remember:
- You don't need to prefix your responses with 'As a web development assistant' or similar phrases.
- Give direct, practical advice rather than general platitudes.
- If you're not sure about something, say so rather than making up information.
- When responding, prioritize being helpful, accurate, and concise.
"""


def get_dynamic_chat_instructions(context: RunContextWrapper, agent: Agent) -> str:
    """
    Generate dynamic instructions for the chat agent based on context.
    
    Args:
        context: The run context with user/project information
        agent: The agent instance
        
    Returns:
        str: The system instructions for the chat agent
    """
    ctx = context.context
    
    # Start with base instructions
    instructions = CHAT_AGENT_INSTRUCTIONS
    
    # Add project-specific context if available
    if ctx:
        project_name = getattr(ctx, 'project_name', None)
        project_description = getattr(ctx, 'project_description', None)
        current_file = getattr(ctx, 'current_file', None)
        
        additional_context = []
        
        if project_name:
            additional_context.append(f"\nYou are currently helping with a project called '{project_name}'.")
        
        if project_description:
            additional_context.append(f"Project Description: {project_description}")
        
        if current_file:
            file_path = current_file.get('path')
            file_type = current_file.get('type', '').lower()
            
            if file_path:
                additional_context.append(f"\nThe user is currently working with file: {file_path}")
                
                file_type_descriptions = {
                    'html': "This is a Django HTML template file.",
                    'vue': "This is a Vue.js component file.",
                    'css': "This is a CSS stylesheet file.",
                    'js': "This is a JavaScript file.",
                    'ts': "This is a TypeScript file.",
                    'python': "This is a Python file.",
                    'py': "This is a Python file.",
                }
                if file_type in file_type_descriptions:
                    additional_context.append(file_type_descriptions[file_type])
        
        if additional_context:
            instructions += "\n\nCurrent Context:\n" + "\n".join(additional_context)
    
    return instructions


def create_chat_agent(model: str = DEFAULT_MODEL) -> Agent:
    """
    Create a chat agent for natural language conversations.
    
    Args:
        model: The OpenAI model to use
        
    Returns:
        Agent: The configured chat agent
    """
    return Agent(
        name="Chat Agent",
        instructions=get_dynamic_chat_instructions,
        model=model,
        handoff_description="A helpful assistant for chatting about web development, "
                           "answering questions, and providing guidance."
    )


def create_simple_chat_agent(model: str = DEFAULT_MODEL) -> Agent:
    """
    Create a simple chat agent with static instructions.
    
    Use this when you don't have context to pass to the agent.
    
    Args:
        model: The OpenAI model to use
        
    Returns:
        Agent: The configured chat agent
    """
    return Agent(
        name="Chat Agent",
        instructions=CHAT_AGENT_INSTRUCTIONS,
        model=model,
        handoff_description="A helpful assistant for chatting about web development, "
                           "answering questions, and providing guidance."
    )
