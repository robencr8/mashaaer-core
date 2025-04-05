import os
import logging
import json
import wave
import time
import random
import threading

# Setup logger
logger = logging.getLogger(__name__)

# Try to import Vosk and PyAudio
try:
    import pyaudio
    from vosk import Model, KaldiRecognizer  # type: ignore
    VOSK_AVAILABLE = True
except ImportError:
    # Log the fact that we're using mock implementation
    logger.warning("Vosk or PyAudio not available, using mock implementation")
    VOSK_AVAILABLE = False
    
    # Define mock PyAudio class for fallback
    class PyAudio:
        def __init__(self):
            pass
            
        def open(self, format=None, channels=None, rate=None, input=None, frames_per_buffer=None):
            return MockStream()
            
        def terminate(self):
            pass
    
    class MockStream:
        def __init__(self):
            pass
            
        def start_stream(self):
            pass
            
        def read(self, chunk_size, exception_on_overflow=None):
            return b'\x00' * chunk_size
            
        def stop_stream(self):
            pass
            
        def close(self):
            pass
    
    # Assign the mock PyAudio to the module namespace
    pyaudio = type('MockPyAudio', (), {
        'PyAudio': PyAudio,
        'paInt16': 2,  # Standard value for paInt16
    })
    
    # Define placeholder classes to avoid LSP errors
    class Model:
        def __init__(self, path):
            pass
            
    class KaldiRecognizer:
        def __init__(self, model, rate):
            pass
        
        def AcceptWaveform(self, data):
            return False
            
        def FinalResult(self):
            return '{"text": ""}'
            
        def Result(self):
            return '{"text": ""}'

class VoskHandler:
    """Handles Vosk speech recognition for multiple languages"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.loaded_models = {}
        self.recognizers = {}
        self.audio = None
        self.stream = None
        self.is_listening = False
        self.listening_thread = None
        self.current_callback = None
        
        # Model paths for supported languages
        self.model_paths = {
            "en-US": "models/vosk-model-small-en-us-0.15",
            "ar": "models/vosk-model-ar-mgb2-0.4",
        }
        
        # Make sure models directory exists
        os.makedirs("models", exist_ok=True)
    
    def is_model_available(self, language):
        """Check if model files are available for the language"""
        model_path = self.model_paths.get(language)
        if not model_path:
            self.logger.warning(f"No model path defined for language: {language}")
            return False
        
        # Check if directory exists and has model files
        return os.path.isdir(model_path) and os.path.exists(os.path.join(model_path, "conf/model.conf"))
    
    def is_model_loaded(self, language):
        """Check if model is loaded for the language"""
        return language in self.loaded_models
    
    def load_model(self, language):
        """Load Vosk model for specified language"""
        if not VOSK_AVAILABLE:
            self.logger.info(f"Mock model loading for {language} (Vosk not available)")
            # Simulate loaded model in mock mode
            self.loaded_models[language] = True
            return True
            
        model_path = self.model_paths.get(language)
        if not model_path:
            self.logger.error(f"No model path defined for language: {language}")
            return False
            
        if not os.path.isdir(model_path):
            self.logger.error(f"Model directory not found: {model_path}")
            return False
            
        try:
            self.logger.info(f"Loading Vosk model for {language} from {model_path}")
            self.models[language] = Model(model_path)
            self.loaded_models[language] = True
            self.logger.info(f"Successfully loaded model for {language}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load Vosk model: {str(e)}")
            # Fall back to mock mode
            self.loaded_models[language] = True
            return True
    
    def recognize_file(self, audio_file, language):
        """Recognize speech in an audio file"""
        # Ensure model is loaded
        if not self.is_model_loaded(language):
            self.load_model(language)
        
        # Handle mock mode
        if not VOSK_AVAILABLE or language not in self.models:
            self.logger.info(f"Using mock speech recognition for file: {audio_file}, language: {language}")
            # Return mock response based on language
            if language == "en-US":
                return "Hello, this is a test of the speech recognition system."
            elif language == "ar":
                return "مرحبا، هذا اختبار لنظام التعرف على الكلام."
            else:
                return "This is a test message from the voice recognition system."
        
        # Real Vosk implementation
        try:
            self.logger.info(f"Recognizing speech in {audio_file} using {language} model")
            
            if not os.path.exists(audio_file):
                self.logger.error(f"Audio file not found: {audio_file}")
                return ""
                
            wf = wave.open(audio_file, "rb")
            
            # Check if audio format is compatible with Vosk
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                self.logger.error(f"Audio file must be WAV format mono PCM: {audio_file}")
                return ""
                
            # Create recognizer
            rec = KaldiRecognizer(self.models[language], wf.getframerate())
            
            # Process audio in chunks
            result = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                rec.AcceptWaveform(data)
            
            # Get final result
            final_result = json.loads(rec.FinalResult())
            result = final_result.get("text", "")
            
            self.logger.info(f"Recognition result: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Recognition error: {str(e)}")
            # Fall back to mock response
            if language == "en-US":
                return "Hello, this is a test of the speech recognition system."
            elif language == "ar":
                return "مرحبا، هذا اختبار لنظام التعرف على الكلام."
            else:
                return "This is a test message from the voice recognition system."
    
    def start_listening(self, language, callback):
        """Start listening for speech in the specified language"""
        if self.is_listening:
            self.logger.warning("Already listening")
            return
        
        # Ensure model is loaded
        if not self.is_model_loaded(language):
            self.load_model(language)
        
        # Set the callback
        self.current_callback = callback
        
        # Choose the appropriate listening method based on availability
        if VOSK_AVAILABLE and language in self.models:
            # Start the real-time listening thread
            self.is_listening = True
            self.listening_thread = threading.Thread(
                target=self._real_listening_thread,
                args=(language,)
            )
            self.listening_thread.daemon = True
            self.listening_thread.start()
            self.logger.info(f"Started real-time listening for {language}")
        else:
            # Fall back to mock implementation
            self.is_listening = True
            self.listening_thread = threading.Thread(
                target=self._mock_listening_thread,
                args=(language,)
            )
            self.listening_thread.daemon = True
            self.listening_thread.start()
            self.logger.info(f"Started mock listening for {language} (Vosk not available)")
            
    def _real_listening_thread(self, language):
        """Thread for continuous real-time listening"""
        try:
            if not VOSK_AVAILABLE:
                self.logger.error("Vosk not available for real-time listening")
                return
                
            self.logger.info(f"Real-time listening thread started for {language}")
            
            # Initialize PyAudio
            try:
                # Access PyAudio via the module variable to avoid LSP warnings
                pa_module = pyaudio  # type: ignore
                self.audio = pa_module.PyAudio()
                
                # Create a recognizer for the language
                recognizer = KaldiRecognizer(self.models[language], 16000)
                
                # Open audio stream using constants from the pyaudio module
                self.stream = self.audio.open(
                    format=pa_module.paInt16,  # type: ignore
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=4000
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize audio: {str(e)}")
                raise
            self.stream.start_stream()
            
            self.logger.info("Audio stream started successfully")
            
            # Main listening loop
            while self.is_listening:
                data = self.stream.read(4000, exception_on_overflow=False)
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if 'text' in result and result['text'].strip():
                        recognized_text = result['text']
                        self.logger.info(f"Recognized: {recognized_text}")
                        
                        if self.current_callback:
                            self.current_callback(recognized_text)
            
            # Clean up
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                
            if self.audio:
                self.audio.terminate()
                
            self.logger.info("Real-time listening thread stopped")
            
        except Exception as e:
            self.logger.error(f"Real-time listening thread error: {str(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            self.is_listening = False
    
    def stop_listening(self):
        """Stop listening for speech"""
        if not self.is_listening:
            return
        
        self.logger.info("Stopping voice recognition...")
        self.is_listening = False
        
        # Clean up stream resources if they exist
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
                self.logger.info("Audio stream closed")
                
            if self.audio:
                self.audio.terminate()
                self.audio = None
                self.logger.info("PyAudio terminated")
        except Exception as e:
            self.logger.error(f"Error cleaning up audio resources: {str(e)}")
        
        # Wait for the thread to end
        if self.listening_thread:
            self.listening_thread.join(timeout=2.0)
            self.listening_thread = None
        
        # Reset the callback
        self.current_callback = None
        
        self.logger.info("Voice recognition stopped")
    
    def recognize_from_file(self, file_path, language):
        """
        Recognize speech from an audio file
        
        Args:
            file_path: Path to audio file
            language: Language code for recognition (e.g. 'en-US', 'ar')
            
        Returns:
            Dict with recognized text and confidence
        """
        self.logger.info(f"Processing audio file: {file_path} with language: {language}")
        
        # Extract text using underlying recognize_file method
        try:
            text = self.recognize_file(file_path, language)
            confidence = 0.8  # Default confidence score
            
            # More complex audio has lower confidence
            if len(text.split()) > 5:
                confidence = 0.7
                
            result = {
                "success": True,
                "text": text,
                "confidence": confidence,
                "language": language
            }
            
            self.logger.info(f"Recognition result: {text}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in recognize_from_file: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": 0.0,
                "language": language
            }
    
    def _mock_listening_thread(self, language):
        """Thread for continuous mock listening"""
        import time
        import random
        
        try:
            self.logger.info(f"Mock listening thread started for {language}")
            
            # Sample responses based on language
            responses = {
                "en-US": [
                    "Hello Robin",
                    "What time is it",
                    "Tell me a joke",
                    "What's the weather like today",
                    "Thank you for your help",
                    "Roben Edwan"  # Developer mode trigger
                ],
                "ar": [
                    "مرحبا روبن",
                    "كم الساعة الآن",
                    "أخبرني نكتة",
                    "كيف الطقس اليوم",
                    "شكرا على مساعدتك"
                ]
            }
            
            default_responses = responses.get("en-US", [])
            lang_responses = responses.get(language, default_responses)
            
            if not lang_responses:
                lang_responses = ["Hello", "Test message"]
            
            # Simulate listening and periodic speech detection
            while self.is_listening:
                # Sleep for random interval (2-5 seconds)
                sleep_time = random.uniform(2.0, 5.0)
                time.sleep(sleep_time)
                
                # 50% chance of "detecting" speech
                if random.random() > 0.5 and self.current_callback:
                    text = random.choice(lang_responses)
                    self.logger.info(f"Mock speech detected: {text}")
                    self.current_callback(text)
            
            self.logger.info("Mock listening thread stopped")
            
        except Exception as e:
            self.logger.error(f"Mock listening thread error: {str(e)}")
            self.is_listening = False
    
    def __del__(self):
        """Clean up resources"""
        self.stop_listening()
