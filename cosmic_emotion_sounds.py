"""
Cosmic Emotion Sounds Integration for Mashaaer Feelings

This module integrates the cosmic soundscape generator with the emotion
detection system to produce emotion-adaptive ambient backgrounds.
"""

import os
import logging
from typing import Dict, Optional, Tuple
from cosmic_soundscape import cosmic_soundscape_generator, CosmicSoundscapeGenerator

# Configure logging
logger = logging.getLogger(__name__)

class CosmicEmotionSounds:
    """
    Integrates cosmic soundscapes with emotion detection to create
    adaptive ambient sounds that match the user's emotional state.
    """
    
    def __init__(self, output_dir: str = "static/cosmic_sounds"):
        """
        Initialize the cosmic emotion sounds integration.
        
        Args:
            output_dir: Directory to save generated emotion soundscapes
        """
        self.output_dir = output_dir
        self._ensure_output_directory()
        
        # Initialize generator if not already done
        if cosmic_soundscape_generator is None:
            logger.info("Initializing Cosmic Soundscape Generator")
            self.generator = CosmicSoundscapeGenerator(output_dir=output_dir)
        else:
            self.generator = cosmic_soundscape_generator
        
        # Map emotions to soundscape parameters
        self.emotion_sound_map = {
            "happy": {
                "mood": "peaceful",
                "base_freq": 65.41,  # C2 note (brighter)
                "layers": 3,
                "shimmer_amplitude": 0.25,
                "pad_amplitude": 0.3
            },
            "sad": {
                "mood": "mysterious",
                "base_freq": 38.89,  # D#1 note (deeper)
                "layers": 3,
                "shimmer_amplitude": 0.15,
                "pad_amplitude": 0.4
            },
            "angry": {
                "mood": "energetic",
                "base_freq": 55.0,  # A1 note (tension)
                "layers": 3,
                "shimmer_amplitude": 0.2,
                "pad_amplitude": 0.35,
                "distortion": 0.2
            },
            "surprised": {
                "mood": "energetic",
                "base_freq": 73.42,  # D2 note (higher)
                "layers": 2,
                "shimmer_amplitude": 0.3,
                "pad_amplitude": 0.25
            },
            "fearful": {
                "mood": "mysterious",
                "base_freq": 36.71,  # D1 note (very low)
                "layers": 3,
                "shimmer_amplitude": 0.1,
                "pad_amplitude": 0.45,
                "noise_type": "brown"
            },
            "neutral": {
                "mood": "peaceful",
                "base_freq": 55.0,  # A1 note (balanced)
                "layers": 2,
                "shimmer_amplitude": 0.15,
                "pad_amplitude": 0.3
            }
        }
        
        # Cache of generated emotion soundscapes
        self.emotion_sound_cache: Dict[str, str] = {}
    
    def _ensure_output_directory(self) -> None:
        """Ensure the output directory exists"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def get_emotion_soundscape(self, emotion: str, duration: float = 15.0) -> Optional[str]:
        """
        Get or generate a cosmic soundscape for the specified emotion.
        Uses cached versions if available.
        
        Args:
            emotion: The detected emotion (happy, sad, angry, etc.)
            duration: Duration of the soundscape in seconds
            
        Returns:
            Path to the generated MP3 file or None if generation failed
        """
        # Normalize emotion to lowercase and handle unknown emotions
        emotion = emotion.lower()
        if emotion not in self.emotion_sound_map:
            emotion = "neutral"
        
        # Check if we already have a cached version for this emotion
        cache_key = f"{emotion}_{int(duration)}"
        if cache_key in self.emotion_sound_cache:
            file_path = self.emotion_sound_cache[cache_key]
            if os.path.exists(file_path):
                logger.info(f"Using cached cosmic soundscape for emotion: {emotion}")
                return file_path
        
        # Generate a new soundscape for this emotion
        logger.info(f"Generating cosmic soundscape for emotion: {emotion}")
        
        # Get parameters for this emotion
        params = self.emotion_sound_map[emotion]
        
        # Generate the soundscape
        output_filename = f"cosmic_{emotion}_{int(duration)}s.wav"
        try:
            _, output_path = self.generator.generate_cosmic_soundscape(
                duration=duration,
                mood=params["mood"],
                layers=params.get("layers", 3),
                output_filename=output_filename
            )
            
            if output_path and os.path.exists(output_path):
                # The generator should have created an MP3 version
                mp3_path = output_path.replace('.wav', '.mp3')
                
                if os.path.exists(mp3_path):
                    # Cache the result
                    self.emotion_sound_cache[cache_key] = mp3_path
                    logger.info(f"Generated cosmic soundscape for {emotion}: {mp3_path}")
                    return mp3_path
        except Exception as e:
            logger.error(f"Error generating cosmic soundscape for {emotion}: {str(e)}")
        
        return None
    
    def get_transition_sound(self, from_emotion: str, to_emotion: str) -> Optional[str]:
        """
        Generate a transition sound between two emotions.
        
        Args:
            from_emotion: The starting emotion
            to_emotion: The ending emotion
            
        Returns:
            Path to the generated transition MP3 file or None if generation failed
        """
        logger.info(f"Generating transition sound from {from_emotion} to {to_emotion}")
        
        # Generate a transition sound
        transition_type = "sweep"
        if from_emotion == "happy" and to_emotion in ["sad", "fearful"]:
            transition_type = "whoosh"  # Descending whoosh for happy to sad transitions
        elif from_emotion in ["sad", "fearful"] and to_emotion == "happy":
            transition_type = "sweep"  # Rising sweep for sad to happy transitions
        elif from_emotion == "angry" or to_emotion == "angry":
            transition_type = "glitch"  # Glitchy transition for angry emotions
        
        output_filename = f"transition_{from_emotion}_to_{to_emotion}.wav"
        
        try:
            # Generate the transition
            transition_duration = 2.0  # Short transition
            transition_audio = self.generator.generate_cosmic_transition(
                duration=transition_duration,
                transition_type=transition_type,
                amplitude=0.4
            )
            
            # Save the transition
            output_path = os.path.join(self.output_dir, output_filename)
            import numpy as np
            from scipy.io import wavfile
            
            # Convert to 16-bit PCM
            transition_int16 = (transition_audio * 32767).astype(np.int16)
            wavfile.write(output_path, self.generator.sample_rate, transition_int16)
            
            # Convert to MP3
            try:
                from pydub import AudioSegment
                mp3_path = output_path.replace('.wav', '.mp3')
                audio = AudioSegment.from_wav(output_path)
                audio.export(mp3_path, format="mp3", bitrate="192k")
                logger.info(f"Generated transition sound: {mp3_path}")
                return mp3_path
            except Exception as e:
                logger.warning(f"Could not convert transition to MP3: {str(e)}")
                return output_path
                
        except Exception as e:
            logger.error(f"Error generating transition sound: {str(e)}")
        
        return None


# Create singleton instance
try:
    cosmic_emotion_sounds = CosmicEmotionSounds()
    logger.info("Cosmic Emotion Sounds initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Cosmic Emotion Sounds: {str(e)}")
    cosmic_emotion_sounds = None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    if cosmic_emotion_sounds is None:
        cosmic_emotion_sounds = CosmicEmotionSounds()
    
    # Generate soundscapes for different emotions
    emotions = ["happy", "sad", "angry", "neutral"]
    for emotion in emotions:
        sound_path = cosmic_emotion_sounds.get_emotion_soundscape(emotion, duration=10.0)
        if sound_path:
            print(f"Generated {emotion} soundscape: {sound_path}")
    
    # Generate a transition from sad to happy
    transition_path = cosmic_emotion_sounds.get_transition_sound("sad", "happy")
    if transition_path:
        print(f"Generated transition sound: {transition_path}")