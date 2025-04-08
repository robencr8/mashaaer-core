#!/usr/bin/env python3
"""Add accessibility API routes to main.py"""

import re

# Read the main.py file
with open('main.py', 'r') as f:
    content = f.read()

# Find the position after the emotion test registration code
pattern = r"(register_emotion_test_routes\(app\)\n\s+logger\.info\(\"Emotion test routes registered successfully\"\)\n\s+)except ImportError as e:\n\s+logger\.error\(f\"Could not import emotion test routes: \{str\(e\)\}\"\)\n\s+except Exception as e:\n\s+logger\.error\(f\"Error registering emotion test routes: \{str\(e\)\}\"\)"

# Replacement text that adds our accessibility API registration
replacement = r"\1except ImportError as e:\n    logger.error(f\"Could not import emotion test routes: {str(e)}\")\nexcept Exception as e:\n    logger.error(f\"Error registering emotion test routes: {str(e)}\")\n\n# Register Accessibility Narrator API routes\ntry:\n    # Initialize accessibility narrator API\n    accessibility_narrator = register_accessibility_routes(app, tts_manager, voice_tone_modulator)\n    logger.info(\"Accessibility Narrator API routes registered successfully\")\nexcept ImportError as e:\n    logger.error(f\"Could not import accessibility narrator routes: {str(e)}\")\nexcept Exception as e:\n    logger.error(f\"Error registering accessibility narrator routes: {str(e)}\")"

# Make the replacement
new_content = re.sub(pattern, replacement, content)

# Write back to main.py
with open('main.py', 'w') as f:
    f.write(new_content)

print("Added accessibility API routes to main.py")
