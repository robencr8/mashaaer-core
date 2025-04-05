import os
import logging
import threading
import time
import json
from datetime import datetime
from .vosk_handler import VoskHandler

class VoiceRecognition:
    """Handles voice recognition functionality using Vosk for English and Arabic"""
    
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.vosk_handler = VoskHandler()
        self.recognized_text = ""
        self.is_listening = False
        self.listening_thread = None
        
        # Create directory for voice logs
        self.voice_logs_dir = "voice_logs"
        os.makedirs(self.voice_logs_dir, exist_ok=True)
    
    def initialize(self):
        """Initialize voice recognition system"""
        self.logger.info("Initializing voice recognition...")
        
        try:
            # Load models for each language
            for lang in self.config.VOICE_LANGUAGES:
                self.vosk_handler.load_model(lang)
            
            self.logger.info("Voice recognition initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to initialize voice recognition: {str(e)}")
            return False
    
    def verify_offline_models(self):
        """Check if offline voice models are available"""
        self.logger.info("Verifying offline voice models...")
        
        missing_models = []
        for lang in self.config.VOICE_LANGUAGES:
            if not self.vosk_handler.is_model_available(lang):
                missing_models.append(lang)
        
        if missing_models:
            self.logger.warning(f"Missing voice models for: {', '.join(missing_models)}")
            return False
        
        self.logger.info("All required voice models are available")
        return True
    
    def process_audio(self, audio_path, language=None):
        """Process audio file and return recognized text"""
        try:
            # If language not specified, use default
            if language is None:
                language = self.config.DEFAULT_VOICE
            
            # Make sure the model for this language is loaded
            if not self.vosk_handler.is_model_loaded(language):
                self.vosk_handler.load_model(language)
            
            # Process audio file
            text = self.vosk_handler.recognize_file(audio_path, language)
            
            # Log the recognized text
            self._log_recognition(text, audio_path, language)
            
            return text
        
        except Exception as e:
            self.logger.error(f"Error processing audio: {str(e)}")
            return ""
    
    def start_listening(self, language=None, callback=None):
        """Start continuous listening for voice commands"""
        if self.is_listening:
            self.logger.warning("Already listening")
            return False
        
        # If language not specified, use default
        if language is None:
            language = self.config.DEFAULT_VOICE
        
        # Make sure model is loaded
        if not self.vosk_handler.is_model_loaded(language):
            try:
                self.vosk_handler.load_model(language)
            except Exception as e:
                self.logger.error(f"Failed to load model: {str(e)}")
                return False
        
        # Start listening thread
        self.is_listening = True
        self.listening_thread = threading.Thread(
            target=self._listening_thread,
            args=(language, callback)
        )
        self.listening_thread.daemon = True
        self.listening_thread.start()
        
        self.logger.info(f"Started listening for {language}")
        return True
    
    def stop_listening(self):
        """Stop continuous listening"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=2.0)
        
        self.logger.info("Stopped listening")
    
    def _listening_thread(self, language, callback):
        """Thread for continuous listening"""
        try:
            self.vosk_handler.start_listening(
                language=language,
                callback=self._on_speech_recognized if callback is None else callback
            )
            
            # Keep the thread alive as long as we should be listening
            while self.is_listening:
                time.sleep(0.1)
            
            # Stop Vosk listening when we're done
            self.vosk_handler.stop_listening()
        
        except Exception as e:
            self.logger.error(f"Listening thread error: {str(e)}")
            self.is_listening = False
    
    def _on_speech_recognized(self, text):
        """Internal callback for speech recognition"""
        if text:
            self.recognized_text = text
            self.logger.debug(f"Recognized: {text}")
            
            # Log the recognition
            self._log_recognition(text)
    
    def recognize_speech_from_file(self, file_path, language="en-US"):
        """
        Recognize speech from an audio file
        
        Args:
            file_path: Path to audio file
            language: Language code for recognition (e.g. 'en-US', 'ar-EG')
            
        Returns:
            Dict with recognized text and confidence
        """
        self.logger.info(f"Recognizing speech from file: {file_path}, language: {language}")
        
        try:
            # Map language to language code
            language_code = language
            if language == "en":
                language_code = "en-US"
            elif language == "ar":
                language_code = "ar-EG"
                
            # Process the file using Vosk handler
            result = self.vosk_handler.recognize_from_file(file_path, language_code)
            
            # Log the recognition result
            if result and 'text' in result:
                self.logger.info(f"Successfully recognized: {result['text']}")
            else:
                self.logger.warning("Recognition returned no text")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error recognizing speech from file: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    def _log_recognition(self, text, audio_path=None, language=None):
        """Log speech recognition to file"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "text": text,
                "language": language,
                "audio_source": audio_path
            }
            
            # Create daily log file
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(self.voice_logs_dir, f"voice_log_{date_str}.json")
            
            entries = []
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        entries = json.load(f)
                except json.JSONDecodeError:
                    entries = []
            
            entries.append(log_entry)
            
            with open(log_file, 'w') as f:
                json.dump(entries, f, indent=2)
        
        except Exception as e:
            self.logger.error(f"Failed to log recognition: {str(e)}")
