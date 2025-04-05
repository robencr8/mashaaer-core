"""
Standalone script to test the TTS API access.
This will check if ElevenLabs is accessible and list available voices.
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_elevenlabs_api():
    """Check if ElevenLabs API is accessible and list available voices."""
    # Get API key from environment
    api_key = os.environ.get('ELEVENLABS_API_KEY')
    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable not found.")
        return False
    
    # Sanitize API key for logging (show only first and last few characters)
    sanitized_key = f"{api_key[:3]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
    print(f"Using ElevenLabs API key (sanitized): {sanitized_key}, length: {len(api_key)}")
    
    # Set the API URL and headers
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Make the request
    try:
        print(f"Sending request to {url}")
        response = requests.get(url, headers=headers)
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            voices = data.get('voices', [])
            print(f"ElevenLabs API is available. {len(voices)} voices found.")
            
            # Print voice details
            print("\nAvailable Voices:")
            for i, voice in enumerate(voices, 1):
                print(f"{i}. {voice.get('name')} (ID: {voice.get('voice_id')})")
            
            return True
        else:
            print(f"API request failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error accessing ElevenLabs API: {str(e)}")
        return False

def test_tts_generation():
    """Test generating TTS audio with ElevenLabs."""
    # Get API key from environment
    api_key = os.environ.get('ELEVENLABS_API_KEY')
    if not api_key:
        print("Error: ELEVENLABS_API_KEY environment variable not found.")
        return False
    
    # Default voice ID for ElevenLabs
    voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice
    
    # Set the API URL and headers
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Test message
    text = "This is a test of the text to speech system. Mashaaer Feelings is working properly."
    
    # Request data
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        print(f"Sending TTS generation request for text: {text}")
        response = requests.post(url, json=data, headers=headers)
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            # Save the audio to a file
            output_file = "test_tts_output.mp3"
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"TTS generation successful. Audio saved to {output_file}")
            return True
        else:
            print(f"TTS generation failed: {response.text}")
            return False
    except Exception as e:
        print(f"Error generating TTS: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== ElevenLabs TTS API Test ===")
    if check_elevenlabs_api():
        print("\n✅ ElevenLabs API check successful! The API is accessible.")
        
        # Optionally test TTS generation
        print("\n=== Testing TTS Generation ===")
        if test_tts_generation():
            print("\n✅ TTS generation test successful!")
        else:
            print("\n❌ TTS generation test failed.")
    else:
        print("\n❌ ElevenLabs API check failed! Please check your API key and internet connection.")