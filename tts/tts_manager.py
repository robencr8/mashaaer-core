import os
import logging
import subprocess
import threading
import time
from .elevenlabs import ElevenLabsTTS
from .gtts_fallback import GTTSFallback
import json

class TTSManager:
    """Manages text-to-speech functionality with provider fallback"""
    
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.config = config
        
        # Get ElevenLabs API key from config or environment
        elevenlabs_api_key = None
        
        # Try multiple methods to get the API key to ensure it's found
        if hasattr(config, 'ELEVENLABS_API_KEY') and config.ELEVENLABS_API_KEY:
            elevenlabs_api_key = config.ELEVENLABS_API_KEY
            self.logger.debug(f"Using ElevenLabs API key from config object, length: {len(elevenlabs_api_key)}")
        else:
            # Try direct environment access
            elevenlabs_api_key = os.environ.get('ELEVENLABS_API_KEY')
            
            if elevenlabs_api_key:
                self.logger.debug(f"Using ElevenLabs API key from environment, length: {len(elevenlabs_api_key)}")
            else:
                # Last resort - try getenv explicitly in case environ.get is failing
                try:
                    from os import getenv
                    elevenlabs_api_key = getenv('ELEVENLABS_API_KEY')
                    if elevenlabs_api_key:
                        self.logger.debug(f"Using ElevenLabs API key from os.getenv(), length: {len(elevenlabs_api_key)}")
                except Exception as e:
                    self.logger.error(f"Error accessing environment variable with getenv: {str(e)}")
        
        if not elevenlabs_api_key:
            self.logger.error("No ElevenLabs API key found in config or environment after all attempts")
        else:
            # Validate key format
            if elevenlabs_api_key and len(elevenlabs_api_key) < 32:
                self.logger.warning(f"ElevenLabs API key looks too short: {len(elevenlabs_api_key)} chars. May not be valid.")
            
            # Check for typical patterns of incorrect API keys
            if elevenlabs_api_key and elevenlabs_api_key.startswith('hf_'):
                self.logger.error(f"Detected a Hugging Face API key (starts with 'hf_') instead of an ElevenLabs key")
            
        # Initialize TTS providers (pass key directly to ensure it's used)
        self.elevenlabs = ElevenLabsTTS(api_key=elevenlabs_api_key)
        self.gtts = GTTSFallback()
        
        # Track which provider to use
        self.use_elevenlabs = False
        self.use_gtts = False
        
        # Lock for thread safety
        self.tts_lock = threading.Lock()
    
    def initialize(self):
        """Initialize TTS system"""
        self.logger.info("Initializing text-to-speech...")
        
        try:
            # Check which TTS providers are available
            if not self.config.is_offline():
                self.logger.info("Checking ElevenLabs availability...")
                
                # Debug the API key being used
                api_key = self.elevenlabs.api_key
                if api_key:
                    start = api_key[:4] if len(api_key) >= 4 else api_key
                    end = api_key[-4:] if len(api_key) >= 8 else ""
                    self.logger.debug(f"Using ElevenLabs API key: {start}...{end}, length: {len(api_key)}")
                    
                    # Properly test if ElevenLabs is available
                    try:
                        elevenlabs_available = self.elevenlabs.is_available()
                        if elevenlabs_available:
                            self.use_elevenlabs = True
                            self.logger.info("ElevenLabs TTS is available and working")
                        else:
                            self.logger.warning("ElevenLabs API test failed - will use fallback")
                            self.use_elevenlabs = False
                    except Exception as check_e:
                        self.logger.error(f"ElevenLabs availability check error: {str(check_e)}")
                        self.logger.error("ElevenLabs will be disabled due to API check failure")
                        self.use_elevenlabs = False
                else:
                    self.logger.error("ElevenLabs API key is empty or not found")
                    self.use_elevenlabs = False
            else:
                self.logger.info("Offline mode - not checking ElevenLabs TTS")
                self.use_elevenlabs = False
            
            # Always check gTTS as fallback
            try:
                if self.gtts.is_available():
                    self.use_gtts = True
                    self.logger.info("Google TTS is available as fallback")
                else:
                    self.logger.warning("Google TTS is not available - check internet connection")
                    self.use_gtts = False
            except Exception as gtts_e:
                self.logger.error(f"Google TTS availability check error: {str(gtts_e)}")
                self.use_gtts = False
            
            if not self.use_elevenlabs and not self.use_gtts:
                self.logger.warning("No TTS providers available - all voices will use offline fallback")
                # Enable offline operation with a basic fallback
                self.gtts.is_available = lambda: True
                self.use_gtts = True
            
            # Report the final status
            self.logger.info(f"TTS initialization complete: ElevenLabs={self.use_elevenlabs}, Google TTS={self.use_gtts}")
            return self.use_elevenlabs or self.use_gtts
        
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            # Enable offline fallback mode
            self.gtts.is_available = lambda: True
            self.use_gtts = True
            return True
    
    def speak(self, text, voice="default", language=None, profile_manager=None):
        """
        Synthesize speech from text with the best available provider
        
        Args:
            text (str): The text to be spoken
            voice (str): Voice ID or category (default uses profile preferences)
            language (str): Language code (en, ar) - determines voice selection
            profile_manager: Optional profile manager to get voice preferences
        """
        # Create a guaranteed fallback file early
        fallback_path = os.path.join("tts_cache", "error.mp3")
        if not os.path.exists(os.path.dirname(fallback_path)):
            os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
            
        if not os.path.exists(fallback_path):
            with open(fallback_path, 'wb') as f:
                f.write(b'')
                
        if not text:
            self.logger.warning("Empty text provided to TTS")
            empty_audio = os.path.join("tts_cache", "empty.mp3")
            with open(empty_audio, 'wb') as f:
                f.write(b'')
            return empty_audio
            
        # If using profile_manager, adapt response style and get voice preference
        if profile_manager:
            # Adapt text based on preferred tone
            text = profile_manager.adapt_response(text, language)
            
            # Get preferred voice for language if not explicitly specified
            if voice == "default":
                voice = profile_manager.get_tts_voice_for_language(language)
        
        with self.tts_lock:
            try:
                self.logger.info(f"Generating speech for text: '{text[:30]}...' with voice: {voice}")
                
                # Try ElevenLabs first if available and preferred
                if self.use_elevenlabs and self.config.TTS_PROVIDER == "elevenlabs":
                    try:
                        self.logger.info(f"Using ElevenLabs for: {text[:30]}... (voice: {voice})")
                        audio_path = self.elevenlabs.speak(text, voice)
                        if audio_path and os.path.exists(audio_path):
                            self.logger.info(f"ElevenLabs successfully generated audio: {audio_path}")
                            self._play_audio(audio_path)
                            return audio_path
                        else:
                            self.logger.warning(f"ElevenLabs returned invalid path: {audio_path}")
                    except Exception as e:
                        self.logger.warning(f"ElevenLabs TTS failed, falling back to gTTS: {str(e)}")
                        import traceback
                        self.logger.warning(f"ElevenLabs error traceback: {traceback.format_exc()}")
                
                # Fall back to gTTS
                if self.use_gtts:
                    try:
                        self.logger.info(f"Using gTTS for: {text[:30]}... (voice: {voice})")
                        audio_path = self.gtts.speak(text, voice)
                        if audio_path and os.path.exists(audio_path):
                            self.logger.info(f"gTTS successfully generated audio: {audio_path}")
                            self._play_audio(audio_path)
                            return audio_path
                        else:
                            self.logger.warning(f"gTTS returned invalid path: {audio_path}")
                    except Exception as e:
                        self.logger.warning(f"gTTS failed: {str(e)}")
                        import traceback
                        self.logger.warning(f"gTTS error traceback: {traceback.format_exc()}")
                
                # If we reach here, we need to return a fallback
                self.logger.error("All TTS providers failed, using fallback")
                
                # Force gtts to be available in GTTSFallback mode
                self.gtts.is_available = lambda: True
                
                try:
                    # Try to get a simple cached response
                    fallback_audio = self.gtts.speak("I'm sorry, I encountered an error.", voice)
                    if fallback_audio and os.path.exists(fallback_audio):
                        return fallback_audio
                except Exception as fallback_e:
                    self.logger.error(f"Error generating fallback audio: {str(fallback_e)}")
                
                # Last resort fallback
                return fallback_path
            
            except Exception as e:
                self.logger.error(f"TTS error: {str(e)}")
                import traceback
                self.logger.error(f"TTS error traceback: {traceback.format_exc()}")
                # Return the fallback path as a last resort
                return fallback_path
    
    def _play_audio(self, audio_path):
        """Play the audio file (platform-independent)"""
        if not os.path.exists(audio_path):
            self.logger.error(f"Audio file not found: {audio_path}")
            return False
        
        # In web application context, we don't actually play audio through server speakers
        # The audio file is served to the client and played in the browser
        # This method is kept for compatibility and potential future use in desktop apps
        self.logger.debug(f"Audio ready at path: {audio_path}")
        return True
    
    def get_available_voices(self):
        """Get a list of all available voices across providers"""
        voices = []
        
        # Get ElevenLabs voices if available
        if self.use_elevenlabs:
            voices.extend([
                {"id": v, "name": v.capitalize(), "provider": "elevenlabs"}
                for v in self.elevenlabs.voices
            ])
        
        # Add gTTS voices
        if self.use_gtts:
            voices.extend([
                {"id": v["id"], "name": v["name"], "provider": "gtts"}
                for v in self.gtts.get_available_voices()
            ])
        
        return voices
        
    def generate_tts(self, text, language=None, voice="default", use_cache=True):
        """
        Generate TTS audio and return a dictionary with audio information
        This is a wrapper for the speak method with enhanced API compatibility
        
        Args:
            text (str): The text to convert to speech
            language (str): Language code (e.g., 'en', 'ar')
            voice (str): Voice ID or name 
            use_cache (bool): Whether to use cached audio if available
            
        Returns:
            dict: Dictionary containing:
                - audio_url: URL to the generated audio file
                - cache_hit: Whether the result was served from cache
        """
        # Track if we get a cache hit
        self.last_was_cache_hit = False
        
        # If language is specified but voice is default, use the appropriate voice
        if language and voice == "default":
            # Use the language code as the voice identifier if possible
            # This will map directly to our enriched voice dictionary
            if language in self.elevenlabs.voices:
                voice = language
            elif language.startswith("ar"):
                # Use Arabic voice
                voice = "arabic"
            elif language.startswith("en"):
                # Use English voice
                voice = "english"
            
            self.logger.info(f"Mapped language '{language}' to voice '{voice}'")
        
        # Handle cache control
        if not use_cache:
            self.logger.info(f"Cache disabled for TTS request: '{text[:30]}...'")
            if hasattr(self.elevenlabs, 'disable_cache'):
                self.elevenlabs.disable_cache()
            if hasattr(self.gtts, 'disable_cache'):
                self.gtts.disable_cache()
        
        # Call the speak method to handle the actual TTS generation
        audio_path = self.speak(text, voice, language)
        
        # Convert file path to URL
        base_url = self.config.APP_URL or ""
        audio_url = f"{base_url}/{audio_path}"
        
        # Re-enable cache for future requests if it was disabled
        if not use_cache:
            if hasattr(self.elevenlabs, 'enable_cache'):
                self.elevenlabs.enable_cache()
            if hasattr(self.gtts, 'enable_cache'):
                self.gtts.enable_cache()
        
        # Return dictionary with results
        return {
            'audio_url': audio_url,
            'cache_hit': getattr(self, 'last_was_cache_hit', False),
            'path': audio_path
        }
