#!/usr/bin/env python3
"""Add accessibility route to main.py"""

import re

# Read the main.py file
with open('main.py', 'r') as f:
    content = f.read()

# Find the position after the voice_tone_test_page function
pattern = r"(@app\.route\('/voice-tone-test', methods=\['GET'\])\n(def voice_tone_test_page\(\):\n\s+\"\"\"Serve a test page for voice tone modulation\"\"\"\n\s+logger\.debug\(\"Voice tone test page accessed\"\)\n\s+return send_from_directory\('static_test', 'voice_tone_test\.html'\))"

# Replacement text that adds our accessibility test page route
replacement = r"\1\n\2\n\n@app.route('/accessibility-test', methods=['GET'])\ndef accessibility_test_page():\n    \"\"\"Serve a test page for accessibility features\"\"\"\n    logger.debug(\"Accessibility test page accessed\")\n    return render_template('accessibility_settings.html')"

# Make the replacement
new_content = re.sub(pattern, replacement, content)

# Write back to main.py
with open('main.py', 'w') as f:
    f.write(new_content)

print("Added accessibility test route to main.py")
