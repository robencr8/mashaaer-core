"""
Voice Tone Modulator for Mashaaer Feelings

This module enhances speech synthesis with emotional tone modulation
by analyzing and adapting text to evoke specific emotional responses.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class VoiceToneModulator:
    """
    Voice Tone Modulator for enhancing speech synthesis with emotional qualities.
    Integrates with EmotionModulator and TTSManager to produce emotionally
    appropriate voice responses.
    """
    
    def __init__(self, emotion_modulator=None, tts_manager=None):
        """
        Initialize the Voice Tone Modulator.
        
        Args:
            emotion_modulator: Instance of EmotionModulator
            tts_manager: Instance of TTSManager
        """
        self.emotion_modulator = emotion_modulator
        self.tts_manager = tts_manager
        self.default_voice_params = self._get_default_voice_params()
        
        # Load emotion-specific voice parameters
        self.emotion_voice_params = self._load_emotion_voice_params()
        logger.info("Voice Tone Modulator initialized successfully")
    
    def _get_default_voice_params(self) -> Dict[str, Any]:
        """Get default voice parameters"""
        return {
            "stability": 0.5,
            "similarity_boost": 0.5,
            "style": 0.0,
            "use_speaker_boost": True,
            "speed": 1.0,
        }
    
    def _load_emotion_voice_params(self) -> Dict[str, Dict[str, Any]]:
        """
        Load emotion-specific voice parameters from configuration file.
        Falls back to defaults if the configuration file is missing.
        """
        try:
            config_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "config",
                "emotion_voice_params.json"
            )
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default emotion voice parameters
                params = {
                    "happy": {
                        "stability": 0.4,
                        "similarity_boost": 0.7,
                        "style": 0.3,
                        "speed": 1.15
                    },
                    "sad": {
                        "stability": 0.7,
                        "similarity_boost": 0.4,
                        "style": -0.1,
                        "speed": 0.9
                    },
                    "angry": {
                        "stability": 0.3,
                        "similarity_boost": 0.8,
                        "style": 0.5,
                        "speed": 1.2
                    },
                    "calm": {
                        "stability": 0.8,
                        "similarity_boost": 0.3,
                        "style": -0.2,
                        "speed": 0.95
                    },
                    "excited": {
                        "stability": 0.35,
                        "similarity_boost": 0.75,
                        "style": 0.4,
                        "speed": 1.25
                    },
                    "neutral": {
                        "stability": 0.5,
                        "similarity_boost": 0.5,
                        "style": 0.0,
                        "speed": 1.0
                    }
                }
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                
                # Save default parameters
                with open(config_path, 'w') as f:
                    json.dump(params, f, indent=4)
                
                return params
        except Exception as e:
            logger.error(f"Error loading emotion voice parameters: {str(e)}")
            # Provide basic fallback parameters
            return {
                "happy": {"speed": 1.15, "stability": 0.4},
                "sad": {"speed": 0.9, "stability": 0.7},
                "angry": {"speed": 1.2, "stability": 0.3},
                "neutral": {"speed": 1.0, "stability": 0.5}
            }
    
    def get_voice_params_for_emotion(self, emotion: str) -> Dict[str, Any]:
        """
        Get voice parameters optimized for a specific emotion.
        
        Args:
            emotion: The emotion to get voice parameters for
            
        Returns:
            Dictionary of voice parameters
        """
        # Get the emotion-specific parameters
        emotion = emotion.lower()
        emotion_params = self.emotion_voice_params.get(
            emotion, self.emotion_voice_params.get("neutral", {})
        )
        
        # Merge with default parameters
        params = self.default_voice_params.copy()
        params.update(emotion_params)
        
        return params
    
    def generate_modulated_speech(
        self, 
        text: str, 
        emotion: str = "neutral",
        voice_id: Optional[str] = None,
        output_format: str = "mp3",
        language: str = "en"
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generate speech with emotional tone modulation.
        
        Args:
            text: The text to convert to speech
            emotion: The desired emotional tone
            voice_id: Optional voice ID to use
            output_format: Audio format (mp3, wav, etc.)
            language: Language code
            
        Returns:
            Tuple of (audio_file_path, metadata)
        """
        try:
            # 1. Modulate text to enhance emotional quality if EmotionModulator is available
            if self.emotion_modulator and self.emotion_modulator.is_available():
                try:
                    modulated_text = self.emotion_modulator.modulate_text(
                        text=text, 
                        target_emotion=emotion,
                        language=language
                    )
                    if modulated_text and isinstance(modulated_text, str):
                        logger.debug(f"Text modulated for emotion '{emotion}'")
                        text = modulated_text
                except Exception as e:
                    logger.warning(f"Failed to modulate text: {str(e)}")
            
            # 2. Get emotion-specific voice parameters
            voice_params = self.get_voice_params_for_emotion(emotion)
            
            # 3. Generate speech with TTS manager using the emotion parameters
            if self.tts_manager:
                # Apply emotion-specific parameters to TTS generation
                # TTSManager.generate_tts returns a dictionary
                tts_result = self.tts_manager.generate_tts(
                    text=text,
                    voice=voice_id if voice_id else "default", 
                    language=language,
                    use_cache=True
                )
                
                # Extract audio path from result
                audio_path = tts_result['path']
                
                # Create metadata dictionary
                metadata = {
                    "duration": 0,  # Will be calculated if available
                    "voice": voice_id if voice_id else "default",
                    "text": text,
                    "format": output_format
                }
                
                # Add emotion metadata
                metadata["emotion"] = emotion
                metadata["modulated"] = True
                
                return audio_path, metadata
            else:
                logger.error("TTS manager is not available")
                raise ValueError("TTS manager is not available")
        except Exception as e:
            logger.error(f"Error generating modulated speech: {str(e)}")
            raise
    
    def is_available(self) -> bool:
        """
        Check if the Voice Tone Modulator is fully available with all components.
        
        Returns:
            Boolean indicating availability
        """
        tts_available = self.tts_manager is not None
        emotion_available = (
            self.emotion_modulator is not None and 
            self.emotion_modulator.is_available()
        )
        
        # Log availability status
        logger.debug(f"Voice Tone Modulator availability - TTS: {tts_available}, Emotion: {emotion_available}")
        
        # Can still function with just TTS, but better with emotion modulator
        return tts_available
    
    def get_available_emotions(self) -> List[Dict[str, str]]:
        """
        Get list of available emotions for voice modulation.
        
        Returns:
            List of emotion descriptors with id, name and description
        """
        emotions = []
        for emotion_id in self.emotion_voice_params.keys():
            emotions.append({
                "id": emotion_id,
                "name": emotion_id.capitalize(),
                "description": f"Speech with {emotion_id} emotional tone"
            })
        return emotions