"""
Voice Tone Modulator for Mashaaer Feelings Application
=====================================================
This module extends the existing emotion modulation capabilities 
with voice-specific tone modifications to create more empathetic
and emotionally appropriate vocal responses.

Uses the EmotionModulator and TTSManager to apply emotion-specific
voice characteristics to synthesized speech.
"""

import os
import json
import logging
import time
from datetime import datetime
from emotion_modulator import EmotionModulator

# Configure logger
logger = logging.getLogger(__name__)

class VoiceToneModulator:
    """
    Handles the emotion-based modulation of voice parameters
    to create more empathetic and emotionally appropriate speech outputs.
    """
    
    def __init__(self, emotion_modulator=None, tts_manager=None):
        """
        Initialize the VoiceToneModulator with emotion modulator and TTS manager
        
        Args:
            emotion_modulator (EmotionModulator): Instance for text analysis and modulation
            tts_manager: The TTS manager for speech synthesis
        """
        self.logger = logging.getLogger(__name__)
        self.emotion_modulator = emotion_modulator or EmotionModulator()
        self.tts_manager = tts_manager
        
        # Extend voice parameters with additional emotional characteristics
        self.voice_emotion_params = {
            "happy": {
                "pitch": 1.2,         # Higher pitch for happy tone
                "speed": 1.15,        # Slightly faster for enthusiastic tone
                "volume": 1.1,        # Slightly louder
                "clarity": 0.9,       # Clear pronunciation
                "breathiness": 0.4,   # Less breathy
                "vocal_tract": 1.0,   # Default vocal tract length
                "voice_quality": "vibrant"
            },
            "sad": {
                "pitch": 0.85,        # Lower pitch for sad tone
                "speed": 0.9,         # Slower for somber tone
                "volume": 0.9,        # Slightly quieter
                "clarity": 1.0,       # Normal clarity
                "breathiness": 0.6,   # Slightly more breathy
                "vocal_tract": 1.05,  # Slightly longer vocal tract for deeper sound
                "voice_quality": "soft"
            },
            "angry": {
                "pitch": 0.95,        # Slightly lower pitch for controlled anger
                "speed": 1.05,        # Slightly faster for intensity
                "volume": 1.0,        # Normal volume (controlled anger)
                "clarity": 1.2,       # Very clear pronunciations
                "breathiness": 0.3,   # Less breathy, more direct
                "vocal_tract": 1.1,   # Longer vocal tract for firm sound
                "voice_quality": "firm"
            },
            "fearful": {
                "pitch": 1.1,         # Higher pitch for fear/stress
                "speed": 1.1,         # Slightly faster
                "volume": 0.95,       # Slightly quieter
                "clarity": 0.9,       # Slightly less clear due to anxiety
                "breathiness": 0.7,   # More breathy
                "vocal_tract": 0.95,  # Slightly shorter vocal tract
                "voice_quality": "trembling"
            },
            "surprised": {
                "pitch": 1.25,        # Higher pitch for surprise
                "speed": 1.0,         # Normal speed
                "volume": 1.05,       # Slightly louder
                "clarity": 1.0,       # Normal clarity
                "breathiness": 0.5,   # Moderate breathiness
                "vocal_tract": 0.9,   # Shorter vocal tract
                "voice_quality": "bright"
            },
            "neutral": {
                "pitch": 1.0,         # Default pitch
                "speed": 1.0,         # Default speed
                "volume": 1.0,        # Default volume
                "clarity": 1.0,       # Default clarity
                "breathiness": 0.5,   # Default breathiness
                "vocal_tract": 1.0,   # Default vocal tract length
                "voice_quality": "balanced"
            }
        }
        
        # Define tone transition rules for emotional adaptation
        # How to transition between different emotional states
        self.tone_transitions = {
            # From sad to other emotions
            "sad": {
                "happy": {
                    "style": "gradual",     # Gradually increase pitch and speed
                    "intro_phrase": {
                        "en": "I understand you're feeling down, but I'd like to share something positive.",
                        "ar": "أفهم أنك تشعر بالحزن، لكنني أرغب في مشاركتك شيئًا إيجابيًا."
                    }
                },
                "angry": {
                    "style": "empathetic",  # Validate feelings first
                    "intro_phrase": {
                        "en": "I can see you're upset, and that's completely valid.",
                        "ar": "أرى أنك منزعج، وهذا شعور مفهوم تمامًا."
                    }
                }
            },
            # From angry to other emotions
            "angry": {
                "neutral": {
                    "style": "calming",     # Steady, lowering intensity
                    "intro_phrase": {
                        "en": "Let's take a moment to consider this calmly.",
                        "ar": "دعنا نأخذ لحظة للتفكير بهدوء."
                    }
                },
                "happy": {
                    "style": "redirecting", # Acknowledge then redirect
                    "intro_phrase": {
                        "en": "I understand your frustration. Let's try to find a positive approach.",
                        "ar": "أتفهم إحباطك. دعنا نحاول إيجاد نهج إيجابي."
                    }
                }
            },
            # Default transitions for any emotion
            "default": {
                "default": {
                    "style": "neutral",
                    "intro_phrase": {
                        "en": "",  # No special phrase, direct transition
                        "ar": ""
                    }
                }
            }
        }
    
    def modulate_voice_tone(self, text, detected_emotion, target_emotion=None, language="en"):
        """
        Modulate text and voice parameters for empathetic response
        
        Args:
            text (str): Original text to modulate
            detected_emotion (str): Detected user emotion (e.g., 'sad', 'happy')
            target_emotion (str): Target emotion to convey (default: appropriate response to detected)
            language (str): Language code ('en', 'ar')
            
        Returns:
            dict: Dictionary containing modulated text and voice parameters
        """
        if not text:
            return {"text": text, "params": self.voice_emotion_params["neutral"]}
            
        # If target emotion not specified, determine appropriate response emotion
        if not target_emotion:
            target_emotion = self._determine_response_emotion(detected_emotion)
            
        # Get transition style if transitioning between emotions
        transition_info = self._get_transition_info(detected_emotion, target_emotion, language)
        
        # Modulate text based on emotions
        modulated_text = text
        if transition_info and transition_info.get("intro_phrase"):
            intro = transition_info["intro_phrase"].get(language, "")
            if intro:
                modulated_text = f"{intro} {modulated_text}"
                
        # Use emotion modulator for text if available
        if self.emotion_modulator:
            try:
                modulated_text = self.emotion_modulator.modulate_text(
                    modulated_text, target_emotion, detected_emotion, language
                )
                self.logger.debug(f"Text modulated for emotion: {target_emotion}")
            except Exception as e:
                self.logger.error(f"Error modulating text: {str(e)}")
        
        # Get voice parameters for the target emotion
        voice_params = self.voice_emotion_params.get(target_emotion, self.voice_emotion_params["neutral"])
        
        # Apply transition style modifications if needed
        if transition_info and transition_info.get("style"):
            voice_params = self._apply_transition_style(voice_params, transition_info["style"], detected_emotion, target_emotion)
            
        # Return modulated text and parameters
        return {
            "text": modulated_text,
            "params": voice_params
        }
        
    def _determine_response_emotion(self, detected_emotion):
        """
        Determine the most appropriate emotion to respond with
        based on the detected user emotion
        
        Args:
            detected_emotion (str): The detected user emotion
            
        Returns:
            str: The appropriate response emotion
        """
        # Response emotion mapping
        response_mapping = {
            "sad": "happy",       # Respond to sadness with uplifting tone
            "angry": "neutral",   # Respond to anger with calm, neutral tone
            "fearful": "neutral", # Respond to fear with reassuring neutral tone
            "happy": "happy",     # Match happiness with happiness
            "surprised": "surprised", # Match surprise
            "neutral": "neutral"  # Match neutral with neutral
        }
        
        return response_mapping.get(detected_emotion, "neutral")
        
    def _get_transition_info(self, from_emotion, to_emotion, language):
        """
        Get information about how to transition between emotional states
        
        Args:
            from_emotion (str): Starting emotion
            to_emotion (str): Target emotion
            language (str): Language code
            
        Returns:
            dict: Transition information
        """
        # Try to get specific transition
        transition = self.tone_transitions.get(from_emotion, {}).get(to_emotion)
        
        # Fall back to default if specific not found
        if not transition:
            transition = self.tone_transitions.get("default", {}).get("default")
            
        return transition
        
    def _apply_transition_style(self, params, style, from_emotion, to_emotion):
        """
        Apply transition style modifications to voice parameters
        
        Args:
            params (dict): Base voice parameters
            style (str): Transition style name
            from_emotion (str): Starting emotion
            to_emotion (str): Target emotion
            
        Returns:
            dict: Modified voice parameters
        """
        # Clone parameters to avoid modifying the original
        modified_params = params.copy()
        
        if style == "gradual":
            # For gradual transitions, blend parameters
            from_params = self.voice_emotion_params.get(from_emotion, self.voice_emotion_params["neutral"])
            blend_factor = 0.3
            
            # Blend parameters
            for key in ["pitch", "speed", "volume", "clarity", "breathiness", "vocal_tract"]:
                if key in modified_params and key in from_params:
                    modified_params[key] = (modified_params[key] * (1 - blend_factor)) + (from_params[key] * blend_factor)
        
        elif style == "empathetic":
            # For empathetic transitions, slightly modify parameters to be gentler
            modified_params["speed"] = min(modified_params["speed"], 1.0)  # Not too fast
            modified_params["volume"] = min(modified_params["volume"], 1.0)  # Not too loud
            modified_params["clarity"] = max(modified_params["clarity"], 1.0)  # Clear speech
        
        elif style == "calming":
            # For calming transitions, reduce intensity
            modified_params["pitch"] *= 0.95  # Slightly lower pitch
            modified_params["speed"] *= 0.9   # Slower speech
            modified_params["volume"] *= 0.9  # Quieter volume
            
        elif style == "redirecting":
            # For redirecting transitions, start like the original but end like the target
            modified_params["speed"] = 0.95  # Slightly slower
            
        return modified_params
        
    def apply_voice_modulation(self, text, detected_emotion, target_emotion=None, language="en", voice="default"):
        """
        Apply both text and voice modulation to get TTS speech
        
        Args:
            text (str): Text to synthesize
            detected_emotion (str): Detected user emotion
            target_emotion (str): Target emotion to convey (or None for automatic)
            language (str): Language code ('en', 'ar')
            voice (str): Voice ID to use
            
        Returns:
            dict: Result containing audio path and parameters used
        """
        if not self.tts_manager:
            self.logger.warning("TTS Manager not available, cannot apply voice modulation")
            return {"success": False, "error": "TTS Manager not available"}
            
        # Modulate text and get voice parameters
        modulation = self.modulate_voice_tone(text, detected_emotion, target_emotion, language)
        
        # Log the modulation
        self.logger.info(f"Voice modulation: {detected_emotion} → {target_emotion or self._determine_response_emotion(detected_emotion)}")
        self.logger.debug(f"Original text: {text}")
        self.logger.debug(f"Modulated text: {modulation['text']}")
        
        # Apply voice parameters if TTS provider supports it
        voice_params = {}
        
        # Map our parameters to ElevenLabs parameters
        if hasattr(self.tts_manager, 'elevenlabs') and self.tts_manager.use_elevenlabs:
            # Create ElevenLabs voice settings
            voice_params = {
                "stability": min(max(0.3, 1.0 - modulation["params"]["breathiness"]), 0.8),
                "similarity_boost": min(max(0.3, modulation["params"]["clarity"]), 0.8),
                "style": min(max(-0.5, (modulation["params"]["pitch"] - 1.0) * 2), 0.5),  # Map pitch difference to style
                "use_speaker_boost": modulation["params"]["volume"] > 1.0
            }
            
        # Apply speech generation with modulated text and parameters
        try:
            # Generate speech with parameters
            audio_result = self.tts_manager.speak(
                modulation["text"],
                voice=voice,
                language=language,
                voice_params=voice_params
            )
            
            # Return result
            return {
                "success": True,
                "audio_path": audio_result,
                "modulated_text": modulation["text"],
                "params_applied": voice_params,
                "emotion": target_emotion or self._determine_response_emotion(detected_emotion)
            }
            
        except Exception as e:
            self.logger.error(f"Error applying voice modulation: {str(e)}")
            return {"success": False, "error": str(e)}