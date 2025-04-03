import requests
import json
import os

def test_play_cosmic_sound():
    """Test the play-cosmic-sound API endpoint"""
    print("Testing /api/play-cosmic-sound...")
    
    # Test welcome sound in English
    response = requests.post(
        "http://localhost:5000/api/play-cosmic-sound", 
        json={
            "sound_type": "welcome", 
            "language": "en"
        }
    )
    
    print(f"Response status: {response.status_code}")
    
    try:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            sound_path = result.get('sound_path')
            print(f"Sound path: {sound_path}")
            
            # Check if the file exists
            if sound_path.startswith('/'):
                # Remove leading slash for checking local file
                sound_path = sound_path[1:]
            
            if os.path.exists(sound_path):
                print(f"Sound file exists: {sound_path}")
            else:
                print(f"Sound file does not exist: {sound_path}")
        
    except Exception as e:
        print(f"Error parsing response: {str(e)}")

def test_direct_tts_manager():
    """Test the TTS manager directly using a Python API call"""
    print("\nTesting direct TTS manager call...")
    
    # Import the tts module
    import sys
    sys.path.append('.')
    
    try:
        # Import the config
        from config import Config
        config = Config()
        
        # Import and initialize the TTS manager
        from tts.tts_manager import TTSManager
        tts_manager = TTSManager(config)
        
        # Initialize the manager
        print("Initializing TTS manager...")
        success = tts_manager.initialize()
        print(f"TTS initialization success: {success}")
        
        if success:
            # Test generating speech
            text = "This is a test of the TTS system."
            print(f"Generating speech for: '{text}'")
            
            audio_path = tts_manager.speak(text)
            print(f"Generated audio path: {audio_path}")
            
            if os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"Audio file exists with size: {file_size} bytes")
            else:
                print(f"Audio file does not exist: {audio_path}")
            
            # Check which provider was used
            if tts_manager.use_elevenlabs:
                print("ElevenLabs TTS is available")
            else:
                print("ElevenLabs TTS is NOT available")
                
            if tts_manager.use_gtts:
                print("Google TTS is available")
            else:
                print("Google TTS is NOT available")
        
    except Exception as e:
        print(f"Error testing TTS manager: {str(e)}")
        import traceback
        traceback.print_exc()

def test_elevenlabs_directly():
    """Test the ElevenLabs TTS provider directly"""
    print("\nTesting ElevenLabs provider directly...")
    
    try:
        # Import required modules
        import os
        from tts.elevenlabs import ElevenLabsTTS
        
        # Get API key from environment
        api_key = os.environ.get('ELEVENLABS_API_KEY')
        print(f"API key length: {len(api_key) if api_key else 'No API key found'}")
        
        # Create the ElevenLabs instance
        elevenlabs = ElevenLabsTTS(api_key=api_key)
        
        # Check if API is available
        is_available = elevenlabs.is_available()
        print(f"ElevenLabs API available: {is_available}")
        
        if is_available:
            # Test generating speech
            text = "This is a direct test of the ElevenLabs API."
            print(f"Generating speech directly for: '{text}'")
            
            audio_path = elevenlabs.speak(text)
            print(f"Generated audio path: {audio_path}")
            
            if os.path.exists(audio_path):
                file_size = os.path.getsize(audio_path)
                print(f"Audio file exists with size: {file_size} bytes")
            else:
                print(f"Audio file does not exist: {audio_path}")
        
    except Exception as e:
        print(f"Error testing ElevenLabs directly: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Running TTS tests...\n")
    test_play_cosmic_sound()
    test_direct_tts_manager()
    test_elevenlabs_directly()
    print("\nTests completed.")