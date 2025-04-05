#!/usr/bin/env python3

import os
import requests
import time

# Ensure the sounds directory exists
os.makedirs('static/sounds', exist_ok=True)

# List of sound files we need to create
sound_files = [
    'welcome.mp3',
    'cosmic.mp3',
    'click.mp3',
    'hover.mp3',
    'listen_start.mp3',
    'listen_stop.mp3',
    'greeting.mp3'
]

# Sample audio URLs (short audio files)
sample_urls = [
    "https://github.com/duncantl/SampleAudio/raw/master/audio/file1.mp3",
    "https://github.com/duncantl/SampleAudio/raw/master/audio/file2.mp3",
    "https://github.com/duncantl/SampleAudio/raw/master/audio/file3.mp3"
]

# Download or create each file
for i, sound_file in enumerate(sound_files):
    file_path = os.path.join('static', 'sounds', sound_file)
    
    # Check if the file already exists and has content
    if os.path.exists(file_path) and os.path.getsize(file_path) > 100:
        print(f"Skipping {sound_file} - already exists with content")
        continue
    
    try:
        # Use a different sample URL for each file (cycling through the available ones)
        url = sample_urls[i % len(sample_urls)]
        print(f"Downloading audio for {sound_file} from {url}")
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(file_path, 'wb') as audio_file:
                audio_file.write(response.content)
            print(f"Created {sound_file}, size: {os.path.getsize(file_path)} bytes")
        else:
            print(f"Failed to download audio for {sound_file}, status: {response.status_code}")
            # Create a minimal valid MP3 file if download fails
            with open(file_path, 'wb') as audio_file:
                audio_file.write(b'\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            print(f"Created minimal MP3 for {sound_file}")
    except Exception as e:
        print(f"Error creating {sound_file}: {str(e)}")
        # Create a minimal valid MP3 file in case of any error
        with open(file_path, 'wb') as audio_file:
            audio_file.write(b'\xFF\xFB\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        print(f"Created minimal MP3 for {sound_file} after error")
    
    # Delay to avoid rate limiting
    time.sleep(0.5)

print("\nSummary of sound files:")
for sound_file in sound_files:
    file_path = os.path.join('static', 'sounds', sound_file)
    if os.path.exists(file_path):
        print(f"{sound_file}: {os.path.getsize(file_path)} bytes")
    else:
        print(f"{sound_file}: MISSING")
