"""
View agent service for Imagi.

This module provides a specialized agent service for generating Vue 3 view/page
Single File Components (SFCs). Views are route-level components that compose
atoms/molecules/organisms and orchestrate page layout, state wiring, and UX
flows while remaining clean and idiomatic.
"""

from dotenv import load_dotenv
import logging
from .agent_service import BaseAgentService
from apps.Products.Imagi.Builder.services.models_service import model_supports_temperature
import os

# Load environment variables from .env
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)


class ViewAgentService(BaseAgentService):
    """Specialized agent service for Vue 3 route-level view/page generation."""

    def __init__(self):
        super().__init__()
        self.current_view_name = None
        # Override default timeout for view generation if needed
        self.request_timeout = 45
        self.BASE_SYSTEM_PROMPT = self.get_system_prompt()["content"]

    def get_system_prompt(self, project_name: str | None = None):
        """
        Get a concise, optimized system prompt for Vue 3 view/page generation.
        """
        if not project_name:
            project_name = "your project"

        return {
            "role": "system",
            "content": (
                f"You are an expert Vue 3 engineer generating clean, production-ready route-level views for {project_name} using Tailwind CSS."
                "\n\nOutput rules:"
                "\n- Output exactly one complete .vue Single File Component (SFC) with <template>, <script setup> (TS preferred when obvious), and optional <style>."
                "\n- Use the Composition API with <script setup> and keep business logic minimal; views orchestrate components and data wiring."
                "\n- No external CSS imports; prefer Tailwind utilities."
                "\n- Provide accessible markup, proper labels, landmarks, and keyboard navigation."
                "\n- Include data-testid attributes on key regions (e.g., page container, primary actions)."
                "\n\nArchitecture & UX:"
                "\n- Treat this file as a route-level view under src/apps/.../views."
                "\n- Compose smaller components (atoms/molecules/organisms) rather than implementing raw UI repeatedly."
                "\n- Handle loading/empty/error states when data is present in context."
                "\n- Keep network calls minimal; when necessary, abstract via services or stores and show placeholders for wiring."
                "\n- Respect minimalist, responsive design inspired by Stripe/Airbnb/Apple/Twilio."
                "\n\nConventions:"
                "\n- Use Tailwind for layout (container, grid, flex, gap, space, responsive prefixes)."
                "\n- Expose well-typed props only when needed; views typically receive params from router."
                "\n- Use useRoute/useRouter when interacting with routing."
                "\n- Dark mode friendly (use neutral palettes and Tailwind dark: variants)."
            )
        }

    def validate_response(self, content: str):
        """Validate that the generated view is a non-empty Vue SFC with template/script."""
        if not content or not isinstance(content, str):
            return False, "Generated content is empty or invalid."
        has_template = "<template>" in content and "</template>" in content
        has_script = "<script setup" in content and "</script>" in content
        if not (has_template and has_script):
            return False, "View must include <template> and <script setup>."
        return True, None

    def get_additional_context(self, **kwargs):
        """Assemble additional system context for the specific view/page."""
        context_parts: list[str] = []
        file_path = kwargs.get("file_path")
        project_id = kwargs.get("project_id")

        if file_path:
            context_parts.append(f"You are creating/editing the view file: {file_path}")

        if project_id:
            try:
                from apps.Products.Imagi.ProjectManager.models import Project
                project = Project.objects.get(id=project_id)
                context_parts.append(f"Project name: {project.name}")
                if hasattr(project, 'description') and project.description:
                    context_parts.append(f"Project description: {project.description}")
            except Exception as e:
                logger.warning(f"Could not get project details for context: {str(e)}")

        # Include .vue files present in project for better context
        if hasattr(self, 'project_files') and self.project_files:
            vue_files = [f["path"] for f in self.project_files if f["path"].endswith('.vue')]
            if vue_files:
                context_parts.append(
                    f"Project contains the following Vue components/views: {', '.join(vue_files[:50])}"
                )

        return "\n".join(context_parts) if context_parts else None

    def process_view(self, prompt: str, model: str, user, project_id: str | None = None,
                     file_name: str | None = None, conversation_id: int | None = None):
        """
        Process a view/page generation request and return the generated code.
        Ensures .vue target and uses BaseAgentService conversation flow.
        """
        try:
            if not prompt:
                return self.error_response("Prompt is required")
            if not model:
                return self.error_response("Model is required")

            # Ensure .vue extension
            if file_name:
                if not file_name.endswith('.vue'):
                    file_name = file_name + '.vue'
                    logger.info(f"Added .vue extension to file name: {file_name}")
                self.current_view_name = file_name

            # Build additional context and full system prompt
            view_context = self.get_additional_context(
                project_id=project_id,
                file_path=file_name,
            )
            system_prompt = f"{self.BASE_SYSTEM_PROMPT}\n\n{view_context}".strip()

            logger.info("==================================================================")
            logger.info("==================== VIEW AGENT SYSTEM PROMPT ====================")
            logger.info("==================================================================")
            logger.info(system_prompt)
            logger.info("==================================================================")
            logger.info("==================== END OF SYSTEM PROMPT ========================")
            logger.info("==================================================================")

            # Prepare project context (optional best-effort)
            project_path = None
            project_files = []
            if project_id:
                try:
                    from apps.Products.Imagi.ProjectManager.models import Project
                    project = Project.objects.get(id=project_id, user=user)
                    project_path = project.project_path
                    project_files = self.load_project_files(project_path)
                    logger.info(f"Loaded {len(project_files)} project files for context")
                except Exception as e:
                    logger.warning(f"Could not load project files: {str(e)}")

            # Prepare current file if exists
            current_file = None
            if file_name and project_path:
                try:
                    full_path = os.path.join(project_path, file_name)
                    if os.path.exists(full_path):
                        with open(full_path, 'r') as f:
                            file_content = f.read()
                            current_file = {
                                'path': file_name,
                                'content': file_content,
                                'type': 'vue'
                            }
                    else:
                        current_file = {
                            'path': file_name,
                            'content': f"<!-- New file: {file_name} -->",
                            'type': 'vue'
                        }
                except Exception as e:
                    logger.warning(f"Could not read file {file_name}: {str(e)}")

            # Build conversation
            messages_result = self.process_conversation(
                user_input=prompt,
                model=model,
                user=user,
                project_id=project_id,
                system_prompt=system_prompt,
                conversation_id=conversation_id,
                is_build_mode=True,
                current_file=current_file,
                project_path=project_path,
                project_files=project_files,
            )

            # Validate and annotate
            if not messages_result:
                return {"success": False, "error": "No response from AI model"}

            if messages_result.get('success'):
                content = messages_result.get('response', '')
                is_valid, err = self.validate_response(content)
                if not is_valid:
                    return {"success": False, "error": f"Invalid response: {err}"}

            return messages_result

        except Exception as e:
            logger.error(f"Error processing view: {str(e)}")
            return {"success": False, "error": str(e)}
