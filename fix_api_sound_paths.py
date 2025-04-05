#!/usr/bin/env python3

import os

with open('api_routes.py', 'r') as file:
    content = file.read()

# Fix audio paths to use static/sounds instead of static/audio
content = content.replace(
    "sound_path = f\"/static/audio/{sound_file}\"",
    "sound_path = f\"/static/sounds/{sound_file}\""
)

content = content.replace(
    "full_path = os.path.join('static', 'audio', sound_file)",
    "full_path = os.path.join('static', 'sounds', sound_file)"
)

content = content.replace(
    "'sound_path': '/static/audio/click.mp3'",
    "'sound_path': '/static/sounds/click.mp3'"
)

# Write more audio files to make sure all resources are available
os.makedirs('static/sounds', exist_ok=True)

# Create the basic sound files if they don't exist
for sound in ['click', 'hover', 'listen_start', 'listen_stop']:
    if not os.path.exists(f'static/sounds/{sound}.mp3'):
        with open(f'static/sounds/{sound}.mp3', 'wb') as audio_file:
            # Write minimal MP3 file (empty but valid)
            audio_file.write(b'\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

with open('api_routes.py', 'w') as file:
    file.write(content)

print("Fixed API sound paths and created necessary audio files")
