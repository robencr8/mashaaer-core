"""
Create Sound Files for Mashaaer

This script creates required sound files for the Mashaaer application
using text-to-speech technology and copies them to the appropriate location.
"""

import os
import sys
import json
import shutil
import requests
from pathlib import Path

# Set up paths
CURRENT_DIR = Path(__file__).parent
STATIC_SOUNDS_DIR = CURRENT_DIR / "static" / "sounds"
TEMP_DIR = CURRENT_DIR / "temp_sounds"
TTS_CACHE_DIR = CURRENT_DIR / "tts_cache"

# Make sure necessary directories exist
STATIC_SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Sound definitions - mapping sound types to text prompts
SOUND_DEFINITIONS = {
    # For interaction sounds
    "click": {"en": "click", "ar": "نقرة"},
    "hover": {"en": "hover", "ar": "تحويم"},
    "listen_start": {"en": "start listening", "ar": "بدء الاستماع"},
    "listen_stop": {"en": "stop listening", "ar": "إيقاف الاستماع"},
    # For voice notifications
    "welcome": {"en": "Welcome to Mashaaer, Create the future, I hear you", 
                "ar": "مرحبا بك في مشاعر، اصنع المستقبل، أنا أسمعك"},
    "greeting": {"en": "I'm listening to you", "ar": "أنا أستمع إليك"}
}

# Background music file (we'll use a TTS-generated ambient sound for now)
BACKGROUND_MUSIC = {"en": "cosmic ambient music", "ar": "موسيقى كونية"}

def generate_sound_with_tts(text, language, filename):
    """Generate a sound file using the application's TTS API"""
    print(f"Generating sound for: {text} ({language}) -> {filename}")
    
    # Call the TTS API endpoint
    api_url = "http://localhost:5000/api/speak"
    headers = {'Content-Type': 'application/json'}
    data = {
        'text': text,
        'language': language,
        'cache': True  # Use cache if available
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and 'audio_url' in result:
                # Parse the relative URL path
                audio_path = result['audio_url'].split('/')[-1]
                audio_source = TTS_CACHE_DIR / audio_path
                
                if audio_source.exists():
                    # Copy the generated file to our destination
                    shutil.copy(audio_source, filename)
                    print(f"  ✓ Created sound file: {filename}")
                    return True
                else:
                    print(f"  ✗ TTS generated audio file not found at: {audio_source}")
            else:
                print(f"  ✗ TTS API error: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ✗ TTS API returned error status: {response.status_code}")
            print(f"  Response: {response.text}")
    
    except Exception as e:
        print(f"  ✗ Error calling TTS API: {str(e)}")
    
    return False

def create_sound(sound_type, language="en"):
    """Create a sound file for the specified type and language"""
    if sound_type == "cosmic":
        text = BACKGROUND_MUSIC[language]
        out_filename = STATIC_SOUNDS_DIR / f"cosmic.mp3"
    else:
        text = SOUND_DEFINITIONS.get(sound_type, {}).get(language, sound_type)
        out_filename = STATIC_SOUNDS_DIR / f"{sound_type}.mp3"
    
    return generate_sound_with_tts(text, language, out_filename)

def main():
    """Main function to create all required sound files"""
    print("Creating sound files for Mashaaer...")
    
    # Create all the basic interaction sounds (using English for simplicity)
    for sound_type in ["click", "hover", "listen_start", "listen_stop"]:
        create_sound(sound_type, "en")
    
    # Create welcome and greeting sounds in both languages
    for sound_type in ["welcome", "greeting"]:
        # Arabic version for primary use
        create_sound(sound_type, "ar")
    
    # Create the cosmic background audio
    create_sound("cosmic", "en")
    
    print("\nSound file creation complete!")
    print(f"Sound files location: {STATIC_SOUNDS_DIR}")

if __name__ == "__main__":
    main()