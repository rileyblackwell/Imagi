"""
Coding Agent using OpenAI Agents SDK.

This module provides a specialized coding agent that can both chat with the user
AND edit files in their Imagi project using function tools.
"""

import json
import os
import logging
from typing import Optional

from agents import Agent, RunContextWrapper, function_tool

from apps.Products.Imagi.ProjectManager.models import Project
from apps.Products.Imagi.Builder.services.view_file_service import ViewFileService
from apps.Products.Imagi.Builder.services.create_file_service import CreateFileService
from apps.Products.Imagi.Builder.services.delete_file_service import DeleteFileService
from apps.Products.Imagi.Builder.services.directory_service import DirectoryService

# Configure logging
logger = logging.getLogger(__name__)

# Default model
DEFAULT_MODEL = "gpt-5.5"

# Coding agent system instructions
CODING_AGENT_INSTRUCTIONS = """You are Imagi, an expert AI coding assistant for building web applications. You can both chat with users AND directly edit files in their project.

You have access to tools that let you browse the project structure, list files, read, create, update, and delete project files. Use them when the user asks you to make code changes. When the user just asks a question or wants guidance, respond conversationally without using tools.

Key Responsibilities:
1. ALWAYS call get_project_tree FIRST when you need to make changes — it shows the full directory structure so you know exactly where files live.
2. Read files before making changes to understand existing code and context.
3. Make targeted, minimal edits — change only what's needed.
4. When creating or updating files, always provide the complete file content.
5. After making changes, briefly summarize what you did and why.

Project Structure (CRITICAL — read carefully):
- This is a dual-stack project with TWO separate codebases:
  * Frontend (Vue.js): lives under 'frontend/vuejs/'
  * Backend (Django):  lives under 'backend/django/'
- The frontend uses an APP-BASED architecture under 'frontend/vuejs/src/apps/':
  * Each app (e.g. home, auth, payments) has its own directory
  * App structure: src/apps/{app_name}/views/, src/apps/{app_name}/router/, src/apps/{app_name}/stores/, src/apps/{app_name}/components/
  * Example: the home app's views are at 'frontend/vuejs/src/apps/home/views/'
  * Each app has a router/index.ts that defines its routes
- The root router at 'frontend/vuejs/src/router/index.js' auto-imports app routes via import.meta.glob
- Shared code lives under 'frontend/vuejs/src/shared/'

File Paths (CRITICAL):
- ALL paths must be relative to the project root and include the full stack prefix.
- Frontend paths MUST start with 'frontend/vuejs/' (e.g. 'frontend/vuejs/src/apps/home/views/About.vue')
- Backend paths MUST start with 'backend/django/' (e.g. 'backend/django/templates/base.html')
- NEVER use bare paths like 'src/views/About.vue' — always include the full prefix.
- When adding a new view to an app, place it in 'frontend/vuejs/src/apps/{app_name}/views/'
- When adding a new route, update 'frontend/vuejs/src/apps/{app_name}/router/index.ts'

Workflow for Creating New Views:
1. Call get_project_tree to see the directory structure
2. Identify the correct app directory (e.g. src/apps/home/)
3. Read the app's existing router (e.g. frontend/vuejs/src/apps/home/router/index.ts) to understand route patterns
4. Create the view file at the correct path (e.g. frontend/vuejs/src/apps/home/views/NewView.vue)
5. Update the app's router to add the new route
6. If needed, update the app's views/index.ts barrel export

Error Handling:
- If a tool returns an error or "success": false, you MUST inform the user that the operation failed. NEVER claim success when a tool reported an error.

Technology Stack:
- Backend: Django with REST framework
- Frontend: Vue.js 3 with Composition API and TypeScript
- Styling: TailwindCSS
- Build tools: Vite
- State management: Pinia
- HTTP client: Axios
"""

# File extension to type mapping
_EXT_TYPE_MAP = {
    '.vue': 'vue', '.ts': 'typescript', '.tsx': 'typescript',
    '.js': 'javascript', '.jsx': 'javascript', '.css': 'css',
    '.html': 'html', '.py': 'python', '.json': 'json',
    '.md': 'markdown', '.txt': 'text',
}

# Patterns indicating a frontend file path
_FRONTEND_PATH_PREFIXES = (
    'src/', 'public/', 'package.json', 'vite.config', 'tsconfig',
    'tailwind.config', 'postcss.config', 'index.html', 'env.d.ts',
)
_FRONTEND_EXTENSIONS = {'.vue', '.ts', '.tsx', '.jsx'}

# Patterns indicating a backend file path
_BACKEND_PATH_PREFIXES = (
    'templates/', 'static/', 'apps/', 'api/', 'manage.py', 'Pipfile',
)


def _is_dual_stack(project):
    """Check if project has both frontend/vuejs and backend/django directories."""
    pp = project.project_path
    return (
        os.path.isdir(os.path.join(pp, 'frontend', 'vuejs'))
        and os.path.isdir(os.path.join(pp, 'backend', 'django'))
    )


def _normalize_file_path(project, file_path: str) -> str:
    """Normalize a file path for dual-stack projects.

    The LLM may omit the 'frontend/vuejs/' or 'backend/django/' prefix.
    This function detects that and adds the correct prefix so files are
    written to the location that list_project_files actually scans.
    """
    file_path = file_path.strip().lstrip('/')

    if not _is_dual_stack(project):
        return file_path

    # Already has the correct prefix — leave it alone
    if file_path.startswith('frontend/') or file_path.startswith('backend/'):
        return file_path

    # Check for frontend patterns
    ext = os.path.splitext(file_path)[1].lower()
    if any(file_path.startswith(p) for p in _FRONTEND_PATH_PREFIXES) or ext in _FRONTEND_EXTENSIONS:
        normalized = f'frontend/vuejs/{file_path}'
        logger.info(f"Path normalized (frontend): '{file_path}' -> '{normalized}'")
        return normalized

    # Check for backend patterns
    if any(file_path.startswith(p) for p in _BACKEND_PATH_PREFIXES) or ext == '.py':
        normalized = f'backend/django/{file_path}'
        logger.info(f"Path normalized (backend): '{file_path}' -> '{normalized}'")
        return normalized

    # Ambiguous — return as-is and let the service handle it
    return file_path


def _infer_file_type(file_path: str) -> str:
    """Infer file type from extension for CreateFileService."""
    ext = os.path.splitext(file_path)[1].lower()
    return _EXT_TYPE_MAP.get(ext, '')


def _error_result(message: str) -> str:
    """Build a JSON error result that instructs the LLM to report failure."""
    return json.dumps({
        "success": False,
        "error": message,
        "instruction": "Tell the user this operation FAILED. Do NOT say the file was created or updated.",
    })


def _get_project(ctx):
    """Resolve the Project model from agent context."""
    try:
        return Project.objects.get(id=ctx.project_id, user_id=ctx.user_id, is_active=True)
    except Project.DoesNotExist:
        raise ValueError(f"Project {ctx.project_id} not found for user {ctx.user_id}")


@function_tool
def get_project_tree(ctx: RunContextWrapper) -> str:
    """Get the directory tree of the user's project. Shows all directories and files organised hierarchically.

    ALWAYS call this tool first before creating or modifying files so you know the exact directory structure.
    This helps you find where views, routers, components, and other files live.
    """
    try:
        project = _get_project(ctx.context)
        service = ViewFileService(project=project)
        tree = service.get_directory_tree()
        return json.dumps(tree, indent=2)
    except Exception as e:
        logger.error(f"Error getting project tree: {e}")
        return _error_result(str(e))


@function_tool
def list_project_files(ctx: RunContextWrapper) -> str:
    """List all files in the user's project (both frontend and backend). Returns file paths and types."""
    try:
        project = _get_project(ctx.context)
        service = ViewFileService(project=project)
        files = service.list_all_project_files()
        # Return a simplified list for the agent
        file_list = [{"path": f["path"], "type": f.get("type", "unknown")} for f in files]
        return json.dumps(file_list, indent=2)
    except Exception as e:
        logger.error(f"Error listing project files: {e}")
        return _error_result(str(e))


@function_tool
def read_file(ctx: RunContextWrapper, file_path: str) -> str:
    """Read the content of a file in the user's project. Use this to understand existing code before making changes.

    Args:
        file_path: The relative path to the file within the project (e.g. 'frontend/vuejs/src/App.vue').
    """
    try:
        project = _get_project(ctx.context)
        file_path = _normalize_file_path(project, file_path)

        # Check if path is a directory rather than a file
        full_path = os.path.join(project.project_path, file_path)
        if os.path.isdir(full_path):
            # List directory contents to be helpful
            entries = sorted(os.listdir(full_path))
            dirs = [e for e in entries if os.path.isdir(os.path.join(full_path, e)) and not e.startswith('.')]
            files = [e for e in entries if os.path.isfile(os.path.join(full_path, e)) and not e.startswith('.')]
            return json.dumps({
                "error": f"'{file_path}' is a directory, not a file. Use get_project_tree to browse directories.",
                "directory_contents": {"dirs": dirs, "files": files},
            })

        service = ViewFileService(project=project)
        content = service.get_file_content(file_path)
        return content
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return _error_result(str(e))


@function_tool
def update_file(ctx: RunContextWrapper, file_path: str, content: str) -> str:
    """Update an existing file in the user's project with new content. Always read the file first to understand the current content.

    Args:
        file_path: The relative path to the file within the project.
        content: The complete new content for the file.
    """
    try:
        project = _get_project(ctx.context)
        file_path = _normalize_file_path(project, file_path)
        service = ViewFileService(project=project)
        result = service.update_file(file_path, content)

        # Verify the file was actually written
        full_path = os.path.join(project.project_path, file_path)
        if not os.path.isfile(full_path):
            return _error_result(f"update_file appeared to succeed but file not found at {file_path}")

        return json.dumps({"success": True, "path": file_path, "message": result.get("message", "File updated successfully")})
    except Exception as e:
        logger.error(f"Error updating file {file_path}: {e}")
        return _error_result(str(e))


@function_tool
def create_file(ctx: RunContextWrapper, file_path: str, content: str) -> str:
    """Create a new file in the user's project.

    Args:
        file_path: The relative path for the new file within the project (e.g. 'frontend/vuejs/src/components/MyComponent.vue').
        content: The content for the new file.
    """
    try:
        project = _get_project(ctx.context)
        file_path = _normalize_file_path(project, file_path)
        file_type = _infer_file_type(file_path)
        service = CreateFileService(project=project)
        result = service.create_file({"name": file_path, "content": content, "type": file_type})

        # Verify the file was actually written
        full_path = os.path.join(project.project_path, file_path)
        if not os.path.isfile(full_path):
            return _error_result(f"create_file appeared to succeed but file not found at {file_path}")

        actual_path = result.get("path", file_path)
        return json.dumps({"success": True, "path": actual_path, "message": f"File created at {actual_path}"})
    except Exception as e:
        logger.error(f"Error creating file {file_path}: {e}")
        return _error_result(str(e))


@function_tool
def delete_file(ctx: RunContextWrapper, file_path: str) -> str:
    """Delete a file from the user's project.

    Args:
        file_path: The relative path to the file within the project (e.g. 'frontend/vuejs/src/components/OldComponent.vue').
    """
    try:
        project = _get_project(ctx.context)
        file_path = _normalize_file_path(project, file_path)
        service = DeleteFileService(project=project)
        result = service.delete_file(file_path)

        # Verify the file was actually removed
        full_path = os.path.join(project.project_path, file_path)
        if os.path.isfile(full_path):
            return _error_result(f"delete_file appeared to succeed but file still exists at {file_path}")

        return json.dumps({"success": True, "path": file_path, "message": result.get("message", "File deleted successfully")})
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return _error_result(str(e))


@function_tool
def create_directory(ctx: RunContextWrapper, dir_path: str) -> str:
    """Create a new directory in the user's project.

    Args:
        dir_path: The relative path for the new directory within the project (e.g. 'frontend/vuejs/src/components/NewFeature').
    """
    try:
        project = _get_project(ctx.context)
        dir_path = _normalize_file_path(project, dir_path)
        service = DirectoryService(project=project)
        result = service.create_directory(dir_path)
        return json.dumps({"success": True, "path": dir_path, "message": result.get("message", "Directory created successfully")})
    except Exception as e:
        logger.error(f"Error creating directory {dir_path}: {e}")
        return _error_result(str(e))


@function_tool
def delete_directory(ctx: RunContextWrapper, dir_path: str) -> str:
    """Delete a directory from the user's project. This will recursively delete the directory and all its contents.

    Args:
        dir_path: The relative path to the directory within the project (e.g. 'frontend/vuejs/src/components/OldFeature').
    """
    try:
        project = _get_project(ctx.context)
        dir_path = _normalize_file_path(project, dir_path)
        service = DirectoryService(project=project)
        result = service.delete_directory(dir_path, recursive=True)
        return json.dumps({"success": True, "path": dir_path, "message": result.get("message", "Directory deleted successfully")})
    except Exception as e:
        logger.error(f"Error deleting directory {dir_path}: {e}")
        return _error_result(str(e))


def get_dynamic_coding_instructions(context: RunContextWrapper, agent: Agent) -> str:
    """Generate dynamic instructions for the coding agent based on context."""
    ctx = context.context
    instructions = CODING_AGENT_INSTRUCTIONS

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
            if file_path:
                additional_context.append(f"\nThe user is currently viewing file: {file_path}")

        if additional_context:
            instructions += "\n\nCurrent Context:\n" + "\n".join(additional_context)

    return instructions


def create_coding_agent(model: str = DEFAULT_MODEL) -> Agent:
    """
    Create a coding agent that can chat and edit project files.

    Args:
        model: The OpenAI model to use

    Returns:
        Agent: The configured coding agent with file tools
    """
    return Agent(
        name="Coding Agent",
        instructions=get_dynamic_coding_instructions,
        model=model,
        tools=[get_project_tree, list_project_files, read_file, update_file, create_file, delete_file, create_directory, delete_directory],
        handoff_description="A coding assistant that can chat about web development "
                           "and directly edit files in the user's project."
    )
