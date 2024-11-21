import re
import os

def get_system_message():
    """Generates the system message content for the assistant."""
    return {
        "role": "system",
        "content": (
            "You are Imagi Oasis, a web development tool designed to create stunning, modern, and functional multi-page websites from natural language descriptions. "
            "Your task is to generate complete HTML pages and maintain a complete styles.css file.\n\n"

            "CRITICAL - Response Rules:\n"
            "1. When editing HTML files:\n"
            "   - ALWAYS return a COMPLETE HTML document starting with <!DOCTYPE html>\n"
            "   - Include ALL required tags: <html>, <head>, <meta>, <title>, <link>, <body>\n"
            "   - Preserve ALL existing content unless explicitly told to remove it\n"
            "   - Return ONLY the HTML document - no explanations or markdown\n\n"

            "2. When editing CSS files:\n"
            "   - ALWAYS return the COMPLETE CSS file\n"
            "   - Include ALL existing styles unless explicitly told to remove them\n"
            "   - Return ONLY valid CSS - no explanations or markdown\n\n"

            "IMPORTANT - File Generation Rules:\n"
            "1. NEVER provide partial updates - ALWAYS generate the complete file\n"
            "2. NEVER include explanatory text or markdown in your response\n"
            "3. ONLY return valid file content (HTML or CSS)\n"
            "4. Preserve all existing content unless explicitly asked to remove it\n"
            "5. Maintain proper formatting and structure\n\n"

            "Examples:\n"
            "1. Creating index.html - Return complete HTML:\n"
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            "    <meta charset='UTF-8'>\n"
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
            "    <title>Page Title</title>\n"
            "    <link rel='stylesheet' href='styles.css'>\n"
            "</head>\n"
            "<body>\n"
            "    <!-- Content here -->\n"
            "</body>\n"
            "</html>\n\n"

            "2. Creating styles.css - Return complete CSS:\n"
            "/* Global Variables */\n"
            ":root {\n"
            "    --primary-color: #3498db;\n"
            "}\n\n"
            "/* Base Styles */\n"
            "body {\n"
            "    font-family: 'Open Sans', sans-serif;\n"
            "    color: #333;\n"
            "}\n\n"

            "3. Editing existing files:\n"
            "- When asked to 'add a contact form' - Return the complete HTML document with the new form added\n"
            "- When asked to 'change background color' - Return the complete CSS file with the color updated\n\n"

            "IMPORTANT - Message Format:\n"
            "Each message includes a [File: filename] prefix indicating which file is being modified.\n\n"
        )
    }

def test_html(html):
    """Ensures only valid HTML content is returned."""
    # Look for complete HTML document
    start_idx = html.find('<!DOCTYPE html>')
    if start_idx == -1:
        start_idx = html.find('<html')
    
    if start_idx == -1:
        return ''
        
    end_idx = html.find('</html>')
    if end_idx == -1:
        return ''
        
    return html[start_idx:end_idx + 7]  # 7 is the length of '</html>'

def get_file_context(filename):
    """Generates the file-specific context message."""
    if filename.endswith('.html'):
        return (
            f"You are working on file: {filename}\n"
            "CRITICAL REQUIREMENTS:\n"
            "1. Return a COMPLETE HTML document\n"
            "2. Start with <!DOCTYPE html>\n"
            "3. Include ALL required tags: <html>, <head>, <meta>, <title>, <link>, <body>\n"
            "4. Preserve ALL existing content\n"
            "5. Return ONLY the HTML document - no explanations\n"
            "6. Ensure proper linking to styles.css\n"
            "7. Maintain consistent styling with other pages\n\n"
            "IMPORTANT INSTRUCTIONS:\n"
            "1. Always include the complete existing content in your response\n"
            "2. Never remove or modify content unless explicitly asked\n"
            "3. Your response must be a complete, valid HTML document\n"
        )
    elif filename == 'styles.css':
        return (
            f"You are working on file: {filename}\n"
            "CRITICAL REQUIREMENTS:\n"
            "1. Return the COMPLETE CSS file\n"
            "2. Include ALL existing styles\n"
            "3. Return ONLY valid CSS - no explanations\n"
            "4. Use proper CSS syntax and formatting\n"
            "5. Maintain consistency across all pages\n"
            "6. Group related styles together\n"
            "7. Use CSS variables in :root {}\n\n"
            "IMPORTANT INSTRUCTIONS:\n"
            "1. Always include all existing styles in your response\n"
            "2. Never remove or modify styles unless explicitly asked\n"
            "3. Your response must be complete, valid CSS\n"
        )
    return f"You are working on file: {filename}"

def ensure_website_directory(base_dir):
    """Ensures the website directory exists and returns its path."""
    output_dir = os.path.join(base_dir, 'website')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

 