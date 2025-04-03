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
        self.logger.info(f"ElevenLabs TTS generating speech for: '{text[:30]}...' with voice: {voice}")
        
        if not self.api_key:
            self.logger.error("ElevenLabs API key not set - attempting direct environment lookup")
            # Last attempt to get the key directly from environment
            direct_key = os.environ.get('ELEVENLABS_API_KEY')
            if direct_key:
                self.logger.info("Retrieved API key directly from environment in speak method")
                self.api_key = direct_key
            else:
                self.logger.error("Failed to retrieve ElevenLabs API key from environment")
                raise ValueError("ElevenLabs API key not set and not found in environment")
        
        # Get voice ID
        voice_id = self.voices.get(voice.lower(), self.voices["default"])
        self.logger.info(f"Mapped voice '{voice}' to ElevenLabs voice ID: {voice_id}")
        
        # Create a cache filename based on text and voice
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_filename = f"{voice_id}_{text_hash}.mp3"
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        # Check if we already have this audio cached
        if os.path.exists(cache_path):
            file_size = os.path.getsize(cache_path)
            if file_size > 0:
                self.logger.info(f"Using cached audio for: {text[:30]}... (size: {file_size} bytes)")
                return cache_path
            else:
                self.logger.warning(f"Found zero-byte cached file, will regenerate: {cache_path}")
        
        try:
            # Verify directories exist
            os.makedirs(self.cache_dir, exist_ok=True)
            
            # Rate limiting: max 3 requests per second
            current_time = time.time()
            if self.last_request_time and (current_time - self.last_request_time) < 0.33:
                delay_time = 0.33 - (current_time - self.last_request_time)
                self.logger.debug(f"Rate limiting - waiting {delay_time:.2f} seconds")
                time.sleep(delay_time)
            
            self.last_request_time = time.time()
            self.request_count += 1
            
            # Prepare API request
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg"
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            self.logger.debug(f"Making ElevenLabs API request to: {self.base_url}/text-to-speech/{voice_id}")
            
            # Make API request for text-to-speech
            start_time = time.time()
            self.logger.debug(f"Starting API request at: {datetime.now().isoformat()}")
            
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice_id}",
                headers=headers,
                json=data,
                timeout=20  # Increased timeout to prevent issues
            )
            
            request_time = time.time() - start_time
            self.logger.info(f"ElevenLabs API response in {request_time:.2f}s - status: {response.status_code}")
            
            # Log detailed response info for debugging
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
                self.logger.error(f"Response preview: {response.content[:100].hex()}")
                raise Exception(f"Unexpected response content type: {content_type}")
            
            # Get content length for verification
            content_length = len(response.content)
            self.logger.debug(f"Received audio content, size: {content_length} bytes")
            
            if content_length < 100:  # Sanity check - audio should be larger than this
                self.logger.error(f"Audio response too small ({content_length} bytes), may be invalid")
                self.logger.error(f"Response content (hex): {response.content.hex()}")
                raise Exception(f"Audio response too small: {content_length} bytes")
                
            # Save the audio file
            try:
                with open(cache_path, "wb") as f:
                    f.write(response.content)
                
                # Verify the file was created
                if os.path.exists(cache_path):
                    file_size = os.path.getsize(cache_path)
                    self.logger.info(f"Successfully generated speech and saved to {cache_path}. File size: {file_size} bytes")
                    if file_size < 100:
                        self.logger.warning(f"Saved audio file is suspiciously small: {file_size} bytes")
                    return cache_path
                else:
                    self.logger.error(f"Failed to save audio to {cache_path}")
                    raise Exception(f"Failed to save audio file to {cache_path}")
            except Exception as save_e:
                self.logger.error(f"Error saving audio file: {str(save_e)}")
                import traceback
                self.logger.error(f"File save traceback: {traceback.format_exc()}")
                raise save_e
        
        except Exception as e:
            self.logger.error(f"ElevenLabs speech generation failed: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            # Create a more detailed error message
            raise Exception(f"ElevenLabs TTS failed: {str(e)} (voice: {voice}, voice_id: {voice_id})")
    
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
