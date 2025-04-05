#!/usr/bin/env python3
"""
Simple utility to check TTS functionality.
Tests both ElevenLabs and Google TTS providers.
"""
import os
import sys
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_elevenlabs():
    """Check if ElevenLabs TTS is accessible and working."""
    print("\n=== Testing ElevenLabs TTS ===")
    
    # Get API key
    api_key = os.environ.get('ELEVENLABS_API_KEY')
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found in environment variables.")
        return False
    
    # Check key length and format
    print(f"API key length: {len(api_key)}")
    sanitized_key = f"{api_key[:3]}...{api_key[-4:]}"
    print(f"Using API key (sanitized): {sanitized_key}")
    
    # Check available voices
    try:
        print("Checking available voices...")
        url = "https://api.elevenlabs.io/v1/voices"
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            voices = response.json().get('voices', [])
            print(f"✅ Found {len(voices)} available voices.")
            
            # Print a sample of voices
            for i, voice in enumerate(voices[:5], 1):
                print(f"  {i}. {voice.get('name')} (ID: {voice.get('voice_id')})")
            
            if len(voices) > 5:
                print(f"  ... and {len(voices) - 5} more voices")
            
            return True
        else:
            print(f"❌ Failed to get voices: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error checking ElevenLabs: {str(e)}")
        return False

def test_elevenlabs_generation():
    """Test generating audio with ElevenLabs."""
    print("\n=== Testing ElevenLabs TTS Generation ===")
    
    # Get API key
    api_key = os.environ.get('ELEVENLABS_API_KEY')
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found in environment variables.")
        return False
    
    # Default voice ID
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice
    
    # Test message in both English and Arabic
    messages = {
        "en": "Testing text to speech for Mashaaer Feelings. This is working correctly.",
        "ar": "اختبار تحويل النص إلى كلام لمشاعر. هذا يعمل بشكل صحيح."
    }
    
    success = True
    for lang, text in messages.items():
        try:
            print(f"\nGenerating TTS for {lang} text: '{text}'")
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                # Save the audio to a file
                output_file = f"test_tts_output_{lang}.mp3"
                with open(output_file, "wb") as f:
                    f.write(response.content)
                print(f"✅ TTS generation successful for {lang}. Audio saved to {output_file}")
            else:
                print(f"❌ TTS generation failed for {lang}: {response.text}")
                success = False
        except Exception as e:
            print(f"❌ Error generating TTS for {lang}: {str(e)}")
            success = False
    
    return success

def check_google_tts():
    """Check if Google TTS is accessible and working as a fallback."""
    print("\n=== Testing Google TTS (Fallback) ===")
    
    try:
        # Try to import gtts
        from gtts import gTTS
        print("✅ Google TTS library (gtts) is available.")
        
        # Test generating audio
        print("Generating test audio...")
        tts = gTTS("This is a test of Google Text to Speech for Mashaaer Feelings.", lang='en')
        output_file = "test_google_tts.mp3"
        tts.save(output_file)
        
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✅ Successfully generated Google TTS audio ({file_size} bytes saved to {output_file}).")
            return True
        else:
            print(f"❌ Failed to save Google TTS audio to {output_file}.")
            return False
    except ImportError:
        print("❌ Google TTS library (gtts) is not installed.")
        return False
    except Exception as e:
        print(f"❌ Error testing Google TTS: {str(e)}")
        return False

def check_cache_directory():
    """Check if the TTS cache directory exists and is writable."""
    print("\n=== Checking TTS Cache Directory ===")
    
    cache_dir = "tts_cache"
    
    if not os.path.exists(cache_dir):
        try:
            os.makedirs(cache_dir)
            print(f"✅ Created TTS cache directory: {cache_dir}")
        except Exception as e:
            print(f"❌ Failed to create TTS cache directory: {str(e)}")
            return False
    else:
        print(f"✅ TTS cache directory exists: {cache_dir}")
    
    # Check if directory is writable
    test_file = os.path.join(cache_dir, "test_write.tmp")
    try:
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print(f"✅ TTS cache directory is writable.")
        return True
    except Exception as e:
        print(f"❌ TTS cache directory is not writable: {str(e)}")
        return False

def main():
    """Run all TTS checks."""
    print("=== Mashaaer TTS System Check ===")
    print(f"Current directory: {os.getcwd()}")
    
    # Check environment variables
    print("\n=== Checking Environment Variables ===")
    elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY')
    print(f"ELEVENLABS_API_KEY: {'Present' if elevenlabs_key else 'Missing'}")
    if elevenlabs_key:
        print(f"  Length: {len(elevenlabs_key)}")
        print(f"  First few chars: {elevenlabs_key[:3]}...")
        print(f"  Last few chars: ...{elevenlabs_key[-4:]}")
    
    # Run TTS checks
    elevenlabs_available = check_elevenlabs()
    if elevenlabs_available:
        tts_generation_ok = test_elevenlabs_generation()
    else:
        tts_generation_ok = False
    
    google_tts_available = check_google_tts()
    cache_ok = check_cache_directory()
    
    # Summary
    print("\n=== TTS Check Summary ===")
    print(f"ElevenLabs API: {'✅ Available' if elevenlabs_available else '❌ Unavailable'}")
    print(f"ElevenLabs TTS Generation: {'✅ Working' if tts_generation_ok else '❌ Failed'}")
    print(f"Google TTS (Fallback): {'✅ Available' if google_tts_available else '❌ Unavailable'}")
    print(f"TTS Cache Directory: {'✅ OK' if cache_ok else '❌ Issue'}")
    
    overall_status = elevenlabs_available and (tts_generation_ok or google_tts_available) and cache_ok
    print(f"\nOverall TTS Status: {'✅ OPERATIONAL' if overall_status else '❌ ISSUES DETECTED'}")
    
    return 0 if overall_status else 1

if __name__ == "__main__":
    sys.exit(main())