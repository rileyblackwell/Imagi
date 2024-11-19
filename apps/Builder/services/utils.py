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
    import re
    
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

 