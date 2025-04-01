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
        self.config = config
        
        # Initialize TTS providers
        self.elevenlabs = ElevenLabsTTS(api_key=config.ELEVENLABS_API_KEY)
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
            if not self.config.is_offline() and self.elevenlabs.is_available():
                self.use_elevenlabs = True
                self.logger.info("ElevenLabs TTS is available")
            else:
                self.logger.info("ElevenLabs TTS is not available")
            
            # Always check gTTS as fallback
            if self.gtts.is_available():
                self.use_gtts = True
                self.logger.info("Google TTS is available")
            else:
                self.logger.info("Google TTS is not available")
            
            if not self.use_elevenlabs and not self.use_gtts:
                self.logger.warning("No TTS providers available")
            
            return self.use_elevenlabs or self.use_gtts
        
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {str(e)}")
            return False
    
    def speak(self, text, voice="default", language=None, profile_manager=None):
        """
        Synthesize speech from text with the best available provider
        
        Args:
            text (str): The text to be spoken
            voice (str): Voice ID or category (default uses profile preferences)
            language (str): Language code (en, ar) - determines voice selection
            profile_manager: Optional profile manager to get voice preferences
        """
        if not text:
            self.logger.warning("Empty text provided to TTS")
            return None
            
        # If using profile_manager, adapt response style and get voice preference
        if profile_manager:
            # Adapt text based on preferred tone
            text = profile_manager.adapt_response(text, language)
            
            # Get preferred voice for language if not explicitly specified
            if voice == "default":
                voice = profile_manager.get_tts_voice_for_language(language)
        
        with self.tts_lock:
            try:
                # Try ElevenLabs first if available and preferred
                if self.use_elevenlabs and self.config.TTS_PROVIDER == "elevenlabs":
                    try:
                        self.logger.debug(f"Using ElevenLabs for: {text[:20]}... (voice: {voice})")
                        audio_path = self.elevenlabs.speak(text, voice)
                        self._play_audio(audio_path)
                        return audio_path
                    except Exception as e:
                        self.logger.warning(f"ElevenLabs TTS failed, falling back to gTTS: {str(e)}")
                
                # Fall back to gTTS
                if self.use_gtts:
                    self.logger.debug(f"Using gTTS for: {text[:20]}... (voice: {voice})")
                    audio_path = self.gtts.speak(text, voice)
                    self._play_audio(audio_path)
                    return audio_path
                
                self.logger.error("No TTS providers available")
                return None
            
            except Exception as e:
                self.logger.error(f"TTS error: {str(e)}")
                return None
    
    def _play_audio(self, audio_path):
        """Play the audio file (platform-independent)"""
        if not os.path.exists(audio_path):
            self.logger.error(f"Audio file not found: {audio_path}")
            return False
        
        try:
            # Use different players depending on platform
            if os.name == 'nt':  # Windows
                subprocess.Popen(['start', audio_path], shell=True)
            elif os.name == 'posix':  # Linux/Mac
                # Try different players
                players = ['mpg123', 'mpg321', 'play', 'ffplay']
                played = False
                
                for player in players:
                    try:
                        subprocess.Popen([player, audio_path], 
                                         stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE)
                        played = True
                        break
                    except:
                        pass
                
                if not played:
                    self.logger.warning("No audio player found. Install mpg123, mpg321, sox, or ffmpeg.")
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to play audio: {str(e)}")
            return False
    
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
