#!/usr/bin/env python3
"""Fix the accessibility test route in main.py"""

import re

# Read the main.py file
with open('main.py', 'r') as f:
    content = f.read()

# Find the position after the voice_tone_test_page function
voice_tone_pattern = r"@app\.route\('/voice-tone-test', methods=\['GET'\]\)\ndef voice_tone_test_page\(\):[^}]*?\)"

# Match the voice_tone_test_page function
match = re.search(voice_tone_pattern, content)
if match:
    func_end_pos = match.end()
    
    # Add our new route after the voice_tone_test_page function
    new_route = """

@app.route('/accessibility-test', methods=['GET'])
def accessibility_test_page():
    """Serve a test page for accessibility features"""
    logger.debug("Accessibility test page accessed")
    return render_template('accessibility_settings.html')
"""
    
    # Insert the new route 
    new_content = content[:func_end_pos] + new_route + content[func_end_pos:]
    
    # Write back to main.py
    with open('main.py', 'w') as f:
        f.write(new_content)
    
    print("Fixed accessibility test route in main.py")
else:
    print("Could not find voice_tone_test_page function in main.py")
