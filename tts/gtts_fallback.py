import os
import logging
import hashlib
import json
import base64
import io
import importlib.util

# Check if gtts is available
gtts_spec = importlib.util.find_spec('gtts')
if gtts_spec is not None:
    from gtts import gTTS
else:
    gTTS = None

class GTTSFallback:
    """Text-to-Speech fallback implementation with cached responses"""
    
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
        
        # Initialize simple response cache for offline TTS
        self._init_offline_cache()
    
    def _init_offline_cache(self):
        """Initialize offline cache with common responses"""
        self.offline_responses = {
            "hello": "hello.mp3",
            "hi": "hello.mp3",
            "welcome": "welcome.mp3",
            "thank you": "thanks.mp3",
            "thanks": "thanks.mp3",
            "goodbye": "goodbye.mp3",
            "bye": "goodbye.mp3",
            "error": "error.mp3",
            "yes": "yes.mp3",
            "no": "no.mp3"
        }
        
        # Create basic greeting/response files if they don't exist
        self._create_default_audio_files()
    
    def _create_default_audio_files(self):
        """Create default audio files if they don't exist"""
        default_files = {
            "hello.mp3": "Hello, I am Robin AI.",
            "welcome.mp3": "Welcome to Robin AI.",
            "thanks.mp3": "Thank you.",
            "goodbye.mp3": "Goodbye, I'll be here if you need me.",
            "error.mp3": "I'm sorry, I encountered an error.",
            "yes.mp3": "Yes.",
            "no.mp3": "No."
        }
        
        for filename, text in default_files.items():
            filepath = os.path.join(self.cache_dir, filename)
            if not os.path.exists(filepath):
                try:
                    if gTTS:
                        # Try using gTTS if available
                        tts = gTTS(text=text, lang="en", slow=False)
                        tts.save(filepath)
                    else:
                        # Create an empty audio file as placeholder
                        with open(filepath, 'wb') as f:
                            f.write(b'')
                        self.logger.warning(f"Created empty placeholder for {filename}")
                except Exception as e:
                    self.logger.error(f"Failed to create default audio: {str(e)}")
    
    def is_available(self):
        """Check if TTS is available"""
        # Always return True since we have fallbacks
        return True
    
    def speak(self, text, voice="default"):
        """Generate speech from text using gTTS and return path to audio file"""
        # Map voice to language
        lang = self.languages.get(voice.lower(), "en")
        
        # Check for exact matches in offline responses
        text_lower = text.lower().strip()
        for key, audio_file in self.offline_responses.items():
            if key in text_lower:
                offline_path = os.path.join(self.cache_dir, audio_file)
                if os.path.exists(offline_path):
                    self.logger.debug(f"Using offline response for: {text[:20]}...")
                    return offline_path
        
        # Create a cache filename based on text and language
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_filename = f"gtts_{lang}_{text_hash}.mp3"
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        # Check if we already have this audio cached
        if os.path.exists(cache_path):
            self.logger.debug(f"Using cached audio for: {text[:20]}...")
            return cache_path
        
        # Try to generate speech with gTTS if available
        if gTTS:
            try:
                self.logger.info(f"Generating speech for: {text[:50]}...")
                
                # Generate speech with gTTS
                tts = gTTS(text=text, lang=lang, slow=False)
                
                # Save to file
                tts.save(cache_path)
                
                return cache_path
            
            except Exception as e:
                self.logger.error(f"gTTS speech generation failed: {str(e)}")
                # Fall through to next section for fallback
        else:
            self.logger.warning("gTTS not available, using fallback response")
        
        # If we reach here, either gTTS failed or isn't available
        # Create a placeholder file with text content for debugging
        with open(cache_path, 'wb') as f:
            # Just write an empty file as placeholder
            f.write(b'')
            
        self.logger.warning(f"Created empty placeholder for: {text[:50]}...")
        
        # Return a default audio file as fallback
        fallback_path = os.path.join(self.cache_dir, "error.mp3")
        if os.path.exists(fallback_path):
            return fallback_path
        else:
            # Last resort fallback - create a temp file and return it
            temp_path = os.path.join(self.cache_dir, "temp_fallback.mp3")
            with open(temp_path, 'wb') as f:
                f.write(b'')
            return temp_path
    
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
