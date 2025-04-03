import os
import logging
import requests
import json
import time
from datetime import datetime

class ElevenLabsTTS:
    """Text-to-Speech implementation using ElevenLabs API"""
    
    def __init__(self, api_key=None):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # Directly attempt to get the API key from environment if not provided
        if not api_key:
            api_key = os.environ.get('ELEVENLABS_API_KEY')
            if api_key:
                self.logger.info("Retrieved ElevenLabs API key directly from environment")
            else:
                self.logger.error("Failed to retrieve ElevenLabs API key from environment")
        
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Voice presets (ID mappings)
        self.voices = {
            "default": "21m00Tcm4TlvDq8ikWAM",  # Rachel (friendly female voice)
            "male": "TxGEqnHWrfWFTfGW9XjX",     # Josh (male voice)
            "female": "21m00Tcm4TlvDq8ikWAM",   # Rachel (female voice)
            "british": "pNInz6obpgDQGcFmaJgB",  # Adam (British male)
            "arabic": "XrExE9yKIg1WjnnlVkGX"    # Arabic male voice
        }
        
        # Create directory for audio cache
        self.cache_dir = "tts_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Track API usage
        self.request_count = 0
        self.last_request_time = None
        
        # Log API key status
        if self.api_key:
            self.logger.debug(f"ElevenLabs API key provided, length: {len(self.api_key)}, starts with: {self.api_key[:4]}, ends with: {self.api_key[-4:]}")
        else:
            self.logger.error("No ElevenLabs API key available")
    
    def is_available(self):
        """Check if the ElevenLabs API is available with a valid key"""
        if not self.api_key:
            self.logger.error("ElevenLabs API key not set or is empty")
            return False
        
        try:
            # Make a simple request to the API to check if the key is valid
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            self.logger.debug(f"Checking ElevenLabs API availability with key length: {len(self.api_key)}")
            self.logger.debug(f"Request URL: {self.base_url}/voices")
            self.logger.debug(f"Headers (sanitized): {{'xi-api-key': '[REDACTED]', 'Content-Type': 'application/json'}}")
            
            response = requests.get(
                f"{self.base_url}/voices",
                headers=headers
            )
            
            self.logger.debug(f"API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                voices_data = response.json()
                voice_count = len(voices_data.get('voices', []))
                self.logger.info(f"ElevenLabs API is available and key is valid. {voice_count} voices available.")
                return True
            else:
                self.logger.error(f"ElevenLabs API returned status code {response.status_code}")
                self.logger.error(f"Response body: {response.text}")
                
                # Try to parse the error for more details
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        self.logger.error(f"Error details: {json.dumps(error_data['detail'])}")
                except:
                    self.logger.error("Could not parse error response as JSON")
                
                return False
        
        except Exception as e:
            self.logger.error(f"ElevenLabs API check failed: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def speak(self, text, voice="default"):
        """Generate speech from text and return path to audio file"""
        if not self.api_key:
            self.logger.error("ElevenLabs API key not set - attempting direct environment lookup")
            # Last attempt to get the key directly from environment
            direct_key = os.environ.get('ELEVENLABS_API_KEY')
            if direct_key:
                self.logger.info("Retrieved API key directly from environment in speak method")
                self.api_key = direct_key
            else:
                raise ValueError("ElevenLabs API key not set and not found in environment")
        
        # Rate limiting: max 3 requests per second
        current_time = time.time()
        if self.last_request_time and (current_time - self.last_request_time) < 0.33:
            time.sleep(0.33 - (current_time - self.last_request_time))
        
        self.last_request_time = time.time()
        self.request_count += 1
        
        # Get voice ID
        voice_id = self.voices.get(voice.lower(), self.voices["default"])
        self.logger.debug(f"Using voice ID: {voice_id} for voice name: {voice}")
        
        # Create a cache filename based on text and voice
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_filename = f"{voice_id}_{text_hash}.mp3"
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        # Check if we already have this audio cached
        if os.path.exists(cache_path):
            self.logger.debug(f"Using cached audio for: {text[:20]}...")
            return cache_path
        
        try:
            # Prepare API request
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg"
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            self.logger.debug(f"Making ElevenLabs API request to: {self.base_url}/text-to-speech/{voice_id}")
            self.logger.debug(f"Request data: {json.dumps(data)}")
            
            # Make API request for text-to-speech
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                headers=headers,
                json=data
            )
            
            self.logger.debug(f"ElevenLabs API response status: {response.status_code}")
            self.logger.debug(f"ElevenLabs API response headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                error_msg = f"ElevenLabs API error: {response.status_code}"
                
                # Try to parse error details
                try:
                    error_data = response.json()
                    error_msg += f" - {json.dumps(error_data)}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                self.logger.error(error_msg)
                raise Exception(error_msg)
            
            # Check if response is audio
            content_type = response.headers.get('Content-Type', '')
            if not content_type.startswith('audio/'):
                self.logger.error(f"Expected audio response but got {content_type}")
                self.logger.error(f"Response preview: {response.content[:100]}")
                raise Exception(f"Unexpected response content type: {content_type}")
                
            # Save the audio file
            with open(cache_path, "wb") as f:
                f.write(response.content)
            
            file_size = os.path.getsize(cache_path)
            self.logger.info(f"Generated speech for: {text[:50]}... File size: {file_size} bytes")
            
            return cache_path
        
        except Exception as e:
            self.logger.error(f"ElevenLabs speech generation failed: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def get_available_voices(self):
        """Get list of available voices from the API"""
        if not self.api_key:
            return []
        
        try:
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/voices",
                headers=headers
            )
            
            if response.status_code != 200:
                self.logger.error(f"Failed to get voices: {response.status_code} - {response.text}")
                return []
            
            voices_data = response.json()
            
            # Format the response
            voices = []
            for voice in voices_data.get("voices", []):
                voices.append({
                    "id": voice.get("voice_id"),
                    "name": voice.get("name"),
                    "preview_url": voice.get("preview_url")
                })
            
            return voices
        
        except Exception as e:
            self.logger.error(f"Error getting voices: {str(e)}")
            return []
