import re
import os

def get_system_message():
    """Generates the system message content for the assistant."""
    return {
        "role": "system",
        "content": (
            "You are Imagi Oasis, a web development tool designed to create stunning, modern, and functional multi-page websites from natural language descriptions. "
            "Your task is to generate HTML pages with inline JavaScript and maintain a separate styles.css file for consistent styling across all pages.\n\n"

            "IMPORTANT - File Generation Rules:\n"
            "1. ALWAYS generate the COMPLETE file content for the file you are working on.\n"
            "2. When creating a new file, generate the entire file with all necessary content.\n"
            "3. When editing an existing file, generate the entire file again with your changes incorporated.\n"
            "4. Never provide partial updates or snippets - always provide the complete file.\n"
            "5. Preserve all existing content unless explicitly asked to remove it.\n"
            "6. Use valid comments and ensure proper formatting and structure.\n\n"

            "IMPORTANT - Response Format:\n"
            "1. Include ONLY valid comments (HTML: <!-- comment -->, CSS: /* comment */).\n"
            "2. Never include markdown, plain text, or explanations.\n"
            "3. Maintain proper spacing and formatting.\n"
            "4. Ensure all elements and rules are complete and properly closed.\n\n"

            "IMPORTANT - Message Format:\n"
            "Each message includes a [File: filename] prefix indicating which file is being discussed or modified. "
            "This helps you track which file each message relates to and ensures you maintain context across the conversation.\n\n"

            "Focus on:\n\n"

            "1. **HTML Structure**:\n"
            "   - Create clean, semantic HTML that links to the shared styles.css file.\n"
            "   - Include inline JavaScript for page-specific functionality.\n"
            "   - Ensure proper linking between pages.\n\n"

            "2. **CSS Management**:\n"
            "   - Maintain consistent styling across all pages through the shared styles.css file.\n"
            "   - Use CSS classes and IDs that work across different pages.\n"
            "   - Create reusable components and styles.\n\n"

            "3. **Visual Design**:\n"
            "   - Create cohesive designs that work across all pages.\n"
            "   - Use consistent color schemes and typography.\n"
            "   - Ensure responsive layouts using CSS Grid and Flexbox.\n\n"

            "4. **User Interaction**:\n"
            "   - Add smooth animations and transitions via CSS.\n"
            "   - Ensure accessibility following WCAG guidelines.\n\n"

            "5. **Performance**:\n"
            "   - Optimize CSS for reusability and performance.\n"
            "   - Minimize redundant styles.\n"
            "   - Avoid including images (currently unsupported).\n\n"
            
            "Examples:\n"
            "1. If asked to 'create styles.css' - Generate a complete CSS file with all necessary styles.\n"
            "2. If then asked to 'change background to blue' - Generate the complete CSS file again, including ALL existing styles, with the background color updated.\n"
            "3. If asked to 'create index.html' - Generate a complete HTML document with all necessary content.\n"
            "4. If then asked to 'add a contact form' - Generate the complete HTML document again, including ALL existing content, with the new form added.\n\n"

            "Sample HTML Structure:\n"
            "<!DOCTYPE html>\n"
            "<html>\n"
            "<head>\n"
            "    <meta charset='UTF-8'>\n"
            "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
            "    <title>Page Title</title>\n"
            "    <link rel='stylesheet' href='styles.css'>\n"
            "</head>\n"
            "<body>\n"
            "    <!-- ALL existing content must be preserved and modified as needed -->\n"
            "    <!-- Include inline JavaScript within the body -->\n"
            "</body>\n"
            "</html>\n\n"

            "Sample CSS Structure:\n"
            ":root {\n"
            "    --primary-color: #3498db;\n"
            "    --secondary-color: #2ecc71;\n"
            "}\n\n"
            "body {\n"
            "    font-family: 'Open Sans', sans-serif;\n"
            "    background-color: var(--primary-color);\n"
            "    color: #333;\n"
            "}\n\n"
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

def test_css(css_content):
    """Ensures that only valid CSS content is returned.
    Purpose: Remove non-CSS comments and plain text while preserving valid CSS exactly as formatted.
    Does NOT modify or reformat valid CSS content."""
    
    # Remove markdown code block indicators if present
    css_content = css_content.replace('```css', '').replace('```', '').strip()
    
    # Pattern to match valid CSS constructs (including comments and whitespace)
    css_pattern = re.compile(
        r"""
        (?P<comments>/\*[^*]*\*+(?:[^/*][^*]*\*+)*/)|    # CSS comments
        (?P<imports>@import\s+[^;]+;)|                    # @import statements
        (?P<media>@media[^{]+\{(?:[^{}]|\{[^{}]*\})*\})|  # @media with nested rules
        (?P<keyframes>
            @keyframes\s+[\w-]+\s*\{
                (?:[^{}]|\{[^{}]*\})*
            \}
        )|                                                # @keyframes with nested rules
        (?P<rules>
            [^@/\s][^{]*\{
                [^{}]*
            \}
        )|                                               # Regular CSS rules
        (?P<whitespace>\s+)                              # Preserve whitespace
        """,
        re.VERBOSE | re.MULTILINE | re.DOTALL
    )
    
    # Find all valid CSS parts while preserving their order and formatting
    matches = css_pattern.finditer(css_content)
    result = ''
    last_end = 0
    
    for match in matches:
        # Check if we have any non-whitespace content between matches
        gap = css_content[last_end:match.start()].strip()
        if gap and not gap.startswith('/*') and not gap.endswith('*/'):
            # There's non-CSS content between matches - skip it
            pass
        
        # Add any valid CSS construct exactly as it appears
        if match.group('comments'):
            result += match.group('comments')
        elif match.group('imports'):
            result += match.group('imports')
        elif match.group('media'):
            result += match.group('media')
        elif match.group('keyframes'):
            result += match.group('keyframes')
        elif match.group('rules'):
            result += match.group('rules')
        elif match.group('whitespace'):
            result += match.group('whitespace')
        
        last_end = match.end()
    
    # If no valid CSS was found, return empty string
    if not result.strip():
        return ''
    
    return result.strip()

def get_file_context(filename):
    """Generates the file-specific context message."""
    file_context = (
        f"You are working on file: {filename}\n"
        f"Remember to maintain consistency with all existing files.\n"
    )
    if filename.endswith('.html'):
        file_context += (
            "Provide a complete, valid HTML document with all required elements.\n"
            "Include <!DOCTYPE html>, <html>, <head>, and <body> tags.\n"
        )
    elif filename == 'styles.css':
        file_context += (
            "Provide complete CSS content.\n"
            "Ensure styles are compatible with all HTML files.\n"
        )
    return file_context

def ensure_website_directory(base_dir):
    """Ensures the website directory exists and returns its path."""
    output_dir = os.path.join(base_dir, 'website')
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

 