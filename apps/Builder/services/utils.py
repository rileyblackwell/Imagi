import re

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
    """Extracts CSS content and removes any plain text or non-CSS comments."""
    # Remove markdown code block indicators
    css_content = css_content.replace('```css', '').replace('```', '')
    
    # Split content into lines
    lines = css_content.split('\n')
    css_lines = []
    in_comment = False
    current_selector = None
    current_properties = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip markdown and explanatory text lines
        if any(text in line.lower() for text in [
            'below', 'example', 'here', 'can', 'how', 'incorporate',
            'following', 'create', 'update', 'add', 'style'
        ]):
            continue
            
        # Skip markdown and list markers
        if line.startswith(('#', '>', '-', '1.', '2.', '3.', '*')):
            continue
            
        # Handle CSS comments
        if '/*' in line and '*/' in line:
            css_lines.append(line)
            continue
            
        if '/*' in line:
            in_comment = True
            css_lines.append(line)
            continue
            
        if '*/' in line:
            in_comment = False
            css_lines.append(line)
            continue
            
        if in_comment:
            css_lines.append(line)
            continue
            
        # Handle properties without a selector (add * selector)
        if ':' in line and ';' in line and not current_selector and not line.strip().startswith('@'):
            if not any(char in line for char in ['{', '}']):
                if not current_properties:
                    current_selector = '*'
                    css_lines.append(f'{current_selector} {{')
                current_properties.append(line)
                continue
                
        # Handle rule starts
        if '{' in line:
            # Write previous rule if it exists
            if current_selector and current_properties:
                if not css_lines[-1].endswith('{'):
                    css_lines.append('}')
            current_selector = line.split('{')[0].strip()
            current_properties = []
            css_lines.append(line)
            continue
            
        # Handle rule ends
        if '}' in line:
            current_selector = None
            current_properties = []
            css_lines.append(line)
            continue
            
        # Handle properties inside rules
        if ':' in line:
            css_lines.append(line)
            continue
    
    # Close any open rule
    if current_selector and current_properties:
        css_lines.append('}')
    
    # Join lines back together
    css = '\n'.join(css_lines)
    
    # Clean up the CSS
    css = css.replace(';;', ';')
    css = css.replace('} }', '}}')
    css = css.replace('{ {', '{{')
    
    return css.strip()
