import os
import logging
import hashlib
from gtts import gTTS
from datetime import datetime

class GTTSFallback:
    """Google Text-to-Speech fallback implementation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Language mapping
        self.languages = {
            "default": "en",
            "english": "en",
            "male": "en",
            "female": "en",
            "british": "en-uk",
            "arabic": "ar",
            "french": "fr",
            "spanish": "es",
            "german": "de"
        }
        
        # Create directory for audio cache
        self.cache_dir = "tts_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def is_available(self):
        """Check if gTTS is available (requires internet connection)"""
        try:
            # Try a simple test
            test = gTTS("test", lang="en")
            return True
        except Exception as e:
            self.logger.error(f"gTTS not available: {str(e)}")
            return False
    
    def speak(self, text, voice="default"):
        """Generate speech from text using gTTS and return path to audio file"""
        # Map voice to language
        lang = self.languages.get(voice.lower(), "en")
        
        # Create a cache filename based on text and language
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_filename = f"gtts_{lang}_{text_hash}.mp3"
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        # Check if we already have this audio cached
        if os.path.exists(cache_path):
            self.logger.debug(f"Using cached audio for: {text[:20]}...")
            return cache_path
        
        try:
            self.logger.info(f"Generating speech for: {text[:50]}...")
            
            # Generate speech with gTTS
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Save to file
            tts.save(cache_path)
            
            return cache_path
        
        except Exception as e:
            self.logger.error(f"gTTS speech generation failed: {str(e)}")
            raise
    
    def get_available_voices(self):
        """Get list of available voices/languages"""
        return [
            {"id": "en", "name": "English (US)"},
            {"id": "en-uk", "name": "English (UK)"},
            {"id": "ar", "name": "Arabic"},
            {"id": "fr", "name": "French"},
            {"id": "es", "name": "Spanish"},
            {"id": "de", "name": "German"}
        ]
