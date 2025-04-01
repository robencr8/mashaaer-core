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
        
        # API keys
        self.ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
        
        # Database configurations
        self.DB_PATH = os.getenv("DB_PATH", "robin_memory.db")
        self.USE_POSTGRES = self._get_bool_env("USE_POSTGRES", True)
        self.DATABASE_URL = os.getenv("DATABASE_URL", "")
        self.PGHOST = os.getenv("PGHOST", "")
        self.PGPORT = os.getenv("PGPORT", "")
        self.PGUSER = os.getenv("PGUSER", "")
        self.PGPASSWORD = os.getenv("PGPASSWORD", "")
        self.PGDATABASE = os.getenv("PGDATABASE", "")
        
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
        self.DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "en-US")
        
        # TTS settings
        self.TTS_PROVIDER = "elevenlabs" if self.ELEVENLABS_API_KEY and not self.OFFLINE_MODE else "gtts"
        
        # Report configuration
        self._report_config()
    
    def _get_bool_env(self, key, default):
        """Helper to parse boolean environment variables"""
        value = os.getenv(key, str(default)).lower()
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
    
    def is_offline(self):
        """Check if system is in offline mode"""
        return self.OFFLINE_MODE
