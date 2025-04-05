import os
import logging
from dotenv import load_dotenv

class Config:
    """Configuration manager for Robin AI"""
    
    def __init__(self):
        # Try to load from .env file
        load_dotenv()
        
        # Set up logging
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Config")
        
        # Basic settings
        self.OFFLINE_MODE = self._get_bool_env("OFFLINE_MODE", False)
        self.DEBUG = self._get_bool_env("DEBUG", True)
        
        # API keys - Use environment variable directly to ensure it's available
        self.ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
        
        # Debug ElevenLabs API key status
        if self.ELEVENLABS_API_KEY:
            self.logger.debug(f"ElevenLabs API key found, length: {len(self.ELEVENLABS_API_KEY)}")
        else:
            self.logger.error(f"ElevenLabs API key not found or empty")
        
        # Database configurations - Use environment variables directly
        self.DB_PATH = os.environ.get("DB_PATH", "robin_memory.db")
        self.USE_POSTGRES = self._get_bool_env("USE_POSTGRES", True)
        self.DATABASE_URL = os.environ.get("DATABASE_URL", "")
        self.PGHOST = os.environ.get("PGHOST", "")
        self.PGPORT = os.environ.get("PGPORT", "")
        self.PGUSER = os.environ.get("PGUSER", "")
        self.PGPASSWORD = os.environ.get("PGPASSWORD", "")
        self.PGDATABASE = os.environ.get("PGDATABASE", "")
        
        # Create data directories if they don't exist
        self.data_dirs = [
            "emotion_data", 
            "voice_logs", 
            "face_profiles",
            "temp"
        ]
        
        for dir_name in self.data_dirs:
            os.makedirs(dir_name, exist_ok=True)
            
        # Windows-specific paths
        if os.name == 'nt':
            self.LOG_DIR = "D:/Robin_Data/"
            os.makedirs(self.LOG_DIR, exist_ok=True)
        else:
            self.LOG_DIR = "./logs/"
            os.makedirs(self.LOG_DIR, exist_ok=True)
        
        # Voice recognition settings
        self.VOICE_LANGUAGES = ["en-US", "ar"]
        self.DEFAULT_VOICE = os.environ.get("DEFAULT_VOICE", "en-US")
        self.VOICE_ENABLED = self._get_bool_env("VOICE_ENABLED", True)
        
        # Face detection settings
        self.FACE_DETECTION_ENABLED = self._get_bool_env("FACE_DETECTION_ENABLED", True)
        
        # TTS settings
        self.TTS_PROVIDER = "elevenlabs" if self.ELEVENLABS_API_KEY and not self.OFFLINE_MODE else "gtts"
        
        # Application URL for CORS and templates
        self.APP_URL = os.environ.get("APP_URL", "https://mashaaer.replit.app")
        
        # Report configuration
        self._report_config()
    
    def _get_bool_env(self, key, default):
        """Helper to parse boolean environment variables"""
        value = os.environ.get(key, str(default)).lower()
        return value in ("true", "1", "yes", "y", "t")
    
    def _report_config(self):
        """Log the current configuration (excluding sensitive keys)"""
        self.logger.info(f"Robin AI Configuration:")
        self.logger.info(f"- OFFLINE_MODE: {self.OFFLINE_MODE}")
        self.logger.info(f"- DEBUG: {self.DEBUG}")
        self.logger.info(f"- DB_PATH: {self.DB_PATH}")
        self.logger.info(f"- USE_POSTGRES: {self.USE_POSTGRES}")
        if self.USE_POSTGRES:
            self.logger.info(f"- PGHOST: {self.PGHOST}")
            self.logger.info(f"- PGDATABASE: {self.PGDATABASE}")
        self.logger.info(f"- TTS_PROVIDER: {self.TTS_PROVIDER}")
        self.logger.info(f"- Voice languages: {self.VOICE_LANGUAGES}")
        self.logger.info(f"- VOICE_ENABLED: {self.VOICE_ENABLED}")
        self.logger.info(f"- FACE_DETECTION_ENABLED: {self.FACE_DETECTION_ENABLED}")
        self.logger.info(f"- APP_URL: {self.APP_URL}")
    
    def is_offline(self):
        """Check if system is in offline mode"""
        return self.OFFLINE_MODE
