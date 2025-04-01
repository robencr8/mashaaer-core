import time
import logging
import threading
from datetime import datetime

class CoreLauncher:
    """Manages the initialization and orchestration of Robin AI's core systems"""
    
    def __init__(self, config, db_manager, emotion_tracker, tts_manager, 
                 intent_classifier, voice_recognition, face_detector):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.db_manager = db_manager
        self.emotion_tracker = emotion_tracker
        self.tts_manager = tts_manager
        self.intent_classifier = intent_classifier
        self.voice_recognition = voice_recognition
        self.face_detector = face_detector
        
        self.start_time = datetime.now()
        self.system_status = "initializing"
        self.threads = []
    
    def start(self):
        """Launch all core systems in sequence"""
        self.logger.info("Starting Robin AI core systems...")
        
        try:
            # Initialize database first
            self.logger.info("Initializing database...")
            self.db_manager.initialize_db()
            
            # Start each system in a separate thread
            self._start_subsystem("Emotion tracker", self.emotion_tracker.initialize)
            self._start_subsystem("Intent classifier", self.intent_classifier.initialize)
            
            # Check if we have voice recognition models downloaded, if in offline mode
            if self.config.is_offline():
                self.logger.info("Checking for offline voice models...")
                self._start_subsystem("Voice model verification", self.voice_recognition.verify_offline_models)
            
            # TTS setup
            self._start_subsystem("Text-to-speech", self.tts_manager.initialize)
            
            # Face recognition initialization
            self._start_subsystem("Face recognition", self.face_detector.initialize)
            
            # Mark as running after all systems are initialized
            self.system_status = "running"
            
            # Announce system ready
            welcome_message = "Robin AI is now ready. All systems initialized successfully."
            self.logger.info(welcome_message)
            
            # Synthesize greeting if TTS is available
            if not self.config.is_offline():
                try:
                    self.tts_manager.speak(welcome_message)
                except Exception as e:
                    self.logger.error(f"Could not synthesize welcome message: {str(e)}")
            
            # Keep the thread alive
            while True:
                time.sleep(10)
                
        except Exception as e:
            self.system_status = "error"
            self.logger.error(f"Core launcher error: {str(e)}")
    
    def _start_subsystem(self, name, func):
        """Start a subsystem in a separate thread"""
        self.logger.info(f"Starting subsystem: {name}")
        try:
            thread = threading.Thread(target=func)
            thread.daemon = True
            thread.start()
            self.threads.append((name, thread))
            self.logger.info(f"{name} started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start {name}: {str(e)}")
    
    def get_uptime(self):
        """Get the system uptime as a formatted string"""
        uptime = datetime.now() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def get_system_status(self):
        """Get the current system status"""
        # Check if all threads are still alive
        for name, thread in self.threads:
            if not thread.is_alive():
                self.logger.warning(f"Subsystem {name} is not responding")
                return "degraded"
        
        return self.system_status
