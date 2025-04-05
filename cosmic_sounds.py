"""
Cosmic Sounds Generator for Mashaaer

This module handles the generation and management of cosmic ambient sounds
for enhancing the user experience in the Mashaaer application.
"""

import os
import logging
import random
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import time

# Configure logging
logger = logging.getLogger(__name__)

class CosmicSoundsGenerator:
    """
    Generates and manages cosmic ambient sounds for the Mashaaer application.
    Handles different types of cosmic sounds and effects to enhance the 
    user experience during various interactions.
    """
    
    # Sound categories and their corresponding files
    SOUND_CATEGORIES = {
        "ambient": [
            "cosmic_ambient_1.mp3",
            "cosmic_ambient_2.mp3",
            "cosmic_ambient_3.mp3",
            "stellar_waves.mp3",
            "deep_space.mp3"
        ],
        "transition": [
            "cosmic_transition_1.mp3",
            "dimensional_shift.mp3",
            "stellar_portal.mp3",
            "quantum_leap.mp3"
        ],
        "interaction": [
            "cosmic_touch.mp3",
            "stellar_ping.mp3",
            "nebula_response.mp3",
            "constellation_connection.mp3"
        ],
        "meditation": [
            "cosmic_harmony.mp3", 
            "stellar_breathing.mp3",
            "galactic_meditation.mp3",
            "universal_balance.mp3"
        ],
        "welcome": [
            "cosmic_greeting.mp3",
            "stellar_welcome.mp3",
            "universe_entry.mp3"
        ]
    }
    
    # Sound durations (approximate, in seconds)
    SOUND_DURATIONS = {
        "ambient": 60,       # Longer ambient background sounds
        "transition": 5,      # Medium-length transition sounds
        "interaction": 2,     # Short interaction sounds
        "meditation": 30,     # Medium-long meditation sequences
        "welcome": 10         # Welcome sounds
    }
    
    def __init__(self, sound_dir: str = "static/cosmic_sounds"):
        """
        Initialize the cosmic sounds generator.
        
        Args:
            sound_dir: Directory containing the cosmic sound files
        """
        self.sound_dir = sound_dir
        self.ensure_sound_directory()
        self.sound_cache = {}
        self.currently_playing = None
        logger.info(f"Cosmic Sounds Generator initialized with sound directory: {sound_dir}")
        
    def ensure_sound_directory(self) -> None:
        """Ensure the cosmic sounds directory exists"""
        if not os.path.exists(self.sound_dir):
            os.makedirs(self.sound_dir, exist_ok=True)
            logger.info(f"Created cosmic sounds directory: {self.sound_dir}")
            
    def get_sound_path(self, category: str, specific_sound: Optional[str] = None) -> str:
        """
        Get the path to a sound file based on category and optionally a specific sound.
        
        Args:
            category: The sound category (ambient, transition, interaction, etc.)
            specific_sound: Optional specific sound filename
            
        Returns:
            Path to the sound file
        """
        if category not in self.SOUND_CATEGORIES:
            logger.warning(f"Unknown sound category: {category}, defaulting to 'ambient'")
            category = "ambient"
            
        if specific_sound:
            if specific_sound in self.SOUND_CATEGORIES[category]:
                sound_file = specific_sound
            else:
                logger.warning(f"Sound file {specific_sound} not found in category {category}, selecting random")
                sound_file = random.choice(self.SOUND_CATEGORIES[category])
        else:
            sound_file = random.choice(self.SOUND_CATEGORIES[category])
            
        return os.path.join(self.sound_dir, sound_file)
    
    def get_sound_info(self, category: str, specific_sound: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a cosmic sound.
        
        Args:
            category: The sound category (ambient, transition, interaction, etc.)
            specific_sound: Optional specific sound filename
            
        Returns:
            Dictionary with sound information
        """
        sound_path = self.get_sound_path(category, specific_sound)
        sound_filename = os.path.basename(sound_path)
        
        # Check if the sound file exists
        if not os.path.exists(sound_path):
            logger.warning(f"Sound file does not exist: {sound_path}")
            # Return a placeholder URL with information about the missing file
            return {
                "sound_url": f"/api/cosmic-sound/{category}/{sound_filename}",
                "category": category,
                "filename": sound_filename,
                "duration": self.SOUND_DURATIONS.get(category, 5),
                "exists": False,
                "timestamp": datetime.now().isoformat()
            }
        
        # Get file size
        file_size = os.path.getsize(sound_path)
        
        return {
            "sound_url": f"/api/cosmic-sound/{category}/{sound_filename}",
            "category": category,
            "filename": sound_filename,
            "size_bytes": file_size,
            "duration": self.SOUND_DURATIONS.get(category, 5),
            "exists": True,
            "timestamp": datetime.now().isoformat()
        }
    
    def list_available_sounds(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all available cosmic sounds categorized.
        
        Returns:
            Dictionary with categories and their available sounds
        """
        result = {}
        
        for category, sound_files in self.SOUND_CATEGORIES.items():
            result[category] = []
            for sound_file in sound_files:
                sound_path = os.path.join(self.sound_dir, sound_file)
                exists = os.path.exists(sound_path)
                
                sound_info = {
                    "filename": sound_file,
                    "exists": exists,
                    "sound_url": f"/api/cosmic-sound/{category}/{sound_file}",
                    "duration": self.SOUND_DURATIONS.get(category, 5),
                }
                
                if exists:
                    sound_info["size_bytes"] = os.path.getsize(sound_path)
                    
                result[category].append(sound_info)
                
        return result
    
    def get_random_sound(self, category: str) -> Dict[str, Any]:
        """
        Get a random cosmic sound from a category.
        
        Args:
            category: The sound category (ambient, transition, interaction, etc.)
            
        Returns:
            Dictionary with sound information
        """
        return self.get_sound_info(category)
    
    def check_sound_files(self) -> Dict[str, Any]:
        """
        Check which sound files exist and which are missing.
        
        Returns:
            Dictionary with information about existing and missing sound files
        """
        existing_files = []
        missing_files = []
        
        for category, sound_files in self.SOUND_CATEGORIES.items():
            for sound_file in sound_files:
                sound_path = os.path.join(self.sound_dir, sound_file)
                
                if os.path.exists(sound_path):
                    existing_files.append({
                        "category": category,
                        "filename": sound_file,
                        "path": sound_path,
                        "size_bytes": os.path.getsize(sound_path)
                    })
                else:
                    missing_files.append({
                        "category": category,
                        "filename": sound_file,
                        "path": sound_path
                    })
        
        return {
            "existing_files": existing_files,
            "missing_files": missing_files,
            "total_existing": len(existing_files),
            "total_missing": len(missing_files),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_cosmic_soundscape(self, 
                                   duration: int = 30, 
                                   layers: int = 3, 
                                   mood: str = "peaceful") -> Dict[str, Any]:
        """
        Generate a layered cosmic soundscape.
        
        This is a placeholder for future implementation of dynamic cosmic soundscape generation.
        Currently returns sample soundscape information.
        
        Args:
            duration: Duration of the soundscape in seconds
            layers: Number of sound layers to combine
            mood: Mood of the soundscape (peaceful, mysterious, energetic)
            
        Returns:
            Dictionary with soundscape information
        """
        logger.info(f"Generating cosmic soundscape: duration={duration}s, layers={layers}, mood={mood}")
        
        # This would be replaced with actual soundscape generation in the future
        soundscape_info = {
            "name": f"cosmic_soundscape_{int(time.time())}",
            "duration": duration,
            "layers": layers,
            "mood": mood,
            "base_sounds": [
                self.get_random_sound("ambient"),
                self.get_random_sound("meditation")
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return soundscape_info


# Create singleton instance
cosmic_sounds_generator = CosmicSoundsGenerator()