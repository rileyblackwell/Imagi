import re
import os

def get_system_message():
    """Generates the system message content for the assistant."""
    return {
        "role": "system",
        "content": (
            "You are Imagi Oasis, a web development tool designed to create stunning, modern, and functional multi-page websites from natural language descriptions. "
            "Your task is to generate HTML pages with inline JavaScript and maintain a separate styles.css file for consistent styling across all pages.\n\n"

            "IMPORTANT - Message Format:\n"
            "Each message includes a [File: filename] prefix indicating which file is being discussed or modified. "
            "This helps you track which file each message relates to and ensures you maintain context across the conversation. "
            "When you see a message like '[File: about.html] Add a contact form', you should focus on modifying the about.html file.\n\n"

            "Focus on:\n\n"

            "1. **HTML Structure**:\n"
            "   - When editing any HTML file, ALWAYS provide the complete HTML document including ALL existing content.\n"
            "   - Never provide partial HTML updates - always include the entire document.\n"
            "   - Create clean, semantic HTML that links to the shared styles.css file.\n"
            "   - Include inline JavaScript for page-specific functionality.\n"
            "   - Ensure proper linking between pages.\n\n"

            "2. **CSS Management**:\n"
            "   - When editing styles.css, ALWAYS provide the complete CSS file including ALL existing styles.\n"
            "   - Never provide partial CSS updates - always include the entire stylesheet.\n"
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

            "When responding:\n"
            "1. Always check the [File: filename] prefix to know which file you're working on.\n"
            "2. If creating/updating HTML: ALWAYS provide the COMPLETE HTML document with ALL existing content, not just the changes.\n"
            "3. If updating styles.css: ALWAYS provide the COMPLETE stylesheet with ALL styles, not just the changes.\n"
            "4. Always maintain consistency across pages.\n\n"

            "Required HTML structure (always include ALL parts):\n"
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
            "</html>"
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
       All plain text and non-CSS comments are removed."""
    # Remove markdown code block indicators and extra whitespace
    css_content = css_content.replace('```css', '').replace('```', '').strip()
    
    # Remove file headers and descriptive text before CSS content
    css_start = css_content.find('/*')
    if css_start == -1:
        # If no comment, look for first CSS rule
        match = re.search(r'[\w\s\#\.\[\]]+\s*\{', css_content)
        if match:
            css_start = match.start()
        else:
            return ''
    
    css_content = css_content[css_start:]
    
    # Count opening and closing braces
    open_braces = css_content.count('{')
    close_braces = css_content.count('}')
    
    # Add missing closing braces if needed
    if open_braces > close_braces:
        css_content += '\n}' * (open_braces - close_braces)
    
    # Pattern to match valid CSS constructs
    css_pattern = re.compile(
        r"""
        (?P<comments>/\*[^*]*\*+(?:[^/*][^*]*\*+)*/)|    # CSS comments
        (?P<atrules>@[^{]+\{[^}]*\})|                    # At-rules with blocks
        (?P<simpleimports>@[\w-]+[^;]*;)|                # Simple at-rules
        (?P<rules>                                        # Style rules
            [^@/\s][^{]*\{
                [^}]*
            \}
        )
        """,
        re.VERBOSE | re.MULTILINE
    )
    
    # Find all valid CSS parts
    matches = css_pattern.finditer(css_content)
    valid_parts = []
    
    for match in matches:
        # Get the matched content
        if match.group('comments'):
            valid_parts.append(match.group('comments'))
        elif match.group('atrules'):
            valid_parts.append(match.group('atrules'))
        elif match.group('simpleimports'):
            valid_parts.append(match.group('simpleimports'))
        elif match.group('rules'):
            valid_parts.append(match.group('rules'))
    
    # Join valid parts with newlines and add a blank line between rules
    result = '\n\n'.join(valid_parts)  # Two newlines for spacing
    
    # Clean up any double newlines and extra whitespace
    result = re.sub(r'\n\s*\n', '\n\n', result)
    
    # Final brace count validation
    final_open_braces = result.count('{')
    final_close_braces = result.count('}')
    if final_open_braces > final_close_braces:
        result += '\n}' * (final_open_braces - final_close_braces)
    
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

 