"""
Emotion Modulator for Mashaaer Feelings Application
=================================================
This module provides advanced text modulation based on emotion recognition
to create more empathetic responses for the voice agent.

Uses OpenAI's API to analyze and modulate text based on detected emotions.
"""

import os
import json
import logging
import time
import re
from datetime import datetime

# Import the OpenAI module
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI module not available, emotion modulation will be limited")

# Configure logger
logger = logging.getLogger(__name__)

class EmotionModulator:
    """
    Handles the emotion-based modulation of text responses
    to create more empathetic and emotionally appropriate outputs.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the EmotionModulator with an OpenAI API key
        
        Args:
            api_key (str): OpenAI API key. If None, will attempt to get from environment.
        """
        self.logger = logging.getLogger(__name__)
        
        # Get API key from parameter or environment
        if not api_key:
            api_key = os.environ.get('OPENAI_API_KEY')
            if api_key:
                self.logger.info("Using OpenAI API key from environment")
            else:
                self.logger.warning("No OpenAI API key provided or found in environment")
        
        self.api_key = api_key
        self.openai_client = None
        
        # Initialize OpenAI client if available
        if OPENAI_AVAILABLE and self.api_key:
            try:
                # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
                # do not change this unless explicitly requested by the user
                self.openai_client = OpenAI(api_key=self.api_key)
                self.logger.info("OpenAI client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        
        # Cache for modulated responses to avoid repeated API calls
        self.cache_dir = "emotion_data"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Define emotion tone mappings
        self.emotion_tones = {
            "happy": {
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.6,
                    "style": 0.25,  # More enthusiastic
                    "use_speaker_boost": True
                },
                "text_transformation": "enthusiastic, upbeat, with shorter sentences and frequent exclamations"
            },
            "sad": {
                "voice_settings": {
                    "stability": 0.8,  # More stable/consistent
                    "similarity_boost": 0.4,
                    "style": -0.2,  # More subdued
                    "use_speaker_boost": False
                },
                "text_transformation": "gentle, empathetic, with careful word choice and softer phrasing"
            },
            "angry": {
                "voice_settings": {
                    "stability": 0.65,
                    "similarity_boost": 0.3,
                    "style": -0.4,  # More controlled
                    "use_speaker_boost": False
                },
                "text_transformation": "calm, steady, with clear structure and reassuring language"
            },
            "fearful": {
                "voice_settings": {
                    "stability": 0.75,
                    "similarity_boost": 0.5,
                    "style": -0.1,  # Balanced
                    "use_speaker_boost": False
                },
                "text_transformation": "reassuring, structured, with clear guidance and supportive phrases"
            },
            "surprised": {
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.55,
                    "style": 0.15,  # Slightly energetic
                    "use_speaker_boost": True
                },
                "text_transformation": "engaged, curious, with acknowledgments and thoughtful responses"
            },
            "neutral": {
                "voice_settings": {
                    "stability": 0.6,
                    "similarity_boost": 0.5,
                    "style": 0.0,  # Balanced
                    "use_speaker_boost": True
                },
                "text_transformation": "balanced, natural, with standard conversational patterns"
            }
        }
    
    def is_available(self):
        """Check if the emotion modulation service is available"""
        return OPENAI_AVAILABLE and self.api_key and self.openai_client is not None
    
    def analyze_emotion(self, text, user_context=None):
        """
        Analyze the emotional content of text
        
        Args:
            text (str): The text to analyze
            user_context (dict): Optional context about the user's history and preferences
            
        Returns:
            dict: Analysis results with predominant emotion and confidence
        """
        if not self.is_available():
            return {"emotion": "neutral", "confidence": 0.5}
        
        try:
            # Create cache key
            import hashlib
            cache_key = hashlib.md5(f"{text}_{str(user_context)}".encode()).hexdigest()
            cache_path = os.path.join(self.cache_dir, f"emotion_{cache_key}.json")
            
            # Check cache
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    return json.load(f)
            
            # Prepare analysis prompt
            system_prompt = """
            You are an emotional analysis expert. Analyze the following text to identify the predominant emotion.
            Focus on identifying one of these emotions: happy, sad, angry, fearful, surprised, neutral.
            Consider context if provided. Respond with a JSON object containing:
            - emotion: The predominant emotion (string, one of: happy, sad, angry, fearful, surprised, neutral)
            - confidence: Confidence level between 0 and 1 (number)
            - explanation: Brief explanation of your analysis (string)
            """
            
            # Include user context if available
            user_prompt = text
            if user_context:
                user_prompt += f"\n\nUser Context: {json.dumps(user_context)}"
            
            # Make API call
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Using the latest model for best analysis
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2  # Lower temperature for more consistent results
            )
            
            # Extract and validate response
            result = json.loads(response.choices[0].message.content)
            
            # Ensure required fields are present
            if "emotion" not in result or "confidence" not in result:
                raise ValueError("Invalid response format from OpenAI API")
            
            # Normalize emotion to one of our supported types
            emotion = result["emotion"].lower()
            if emotion not in self.emotion_tones:
                self.logger.warning(f"Unknown emotion '{emotion}', defaulting to 'neutral'")
                emotion = "neutral"
                result["emotion"] = emotion
            
            # Cache result
            with open(cache_path, 'w') as f:
                json.dump(result, f)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing emotion: {str(e)}")
            return {"emotion": "neutral", "confidence": 0.5}
    
    def modulate_text(self, text, target_emotion, user_emotion=None, language=None):
        """
        Modulate text to be more empathetic based on target emotion
        
        Args:
            text (str): Original text to modulate
            target_emotion (str): Emotion to optimize response for (e.g., 'sad', 'happy')
            user_emotion (str): Optional detected user emotion for context
            language (str): Language code ('en', 'ar', etc.) - default is English
            
        Returns:
            str: Modulated text with appropriate emotional tone
        """
        if not text:
            return text
            
        if not language:
            language = "en"
            
        # For non-English languages or when OpenAI is unavailable, use simplified modulation
        if not self.is_available() or language != "en":
            return self._simple_modulation(text, target_emotion, language)
        
        try:
            # Create cache key
            import hashlib
            cache_key = hashlib.md5(f"{text}_{target_emotion}_{user_emotion}_{language}".encode()).hexdigest()
            cache_path = os.path.join(self.cache_dir, f"modulated_{cache_key}.json")
            
            # Check cache
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    return json.load(f)["modulated_text"]
            
            # Get transformation style for target emotion
            transformation = self.emotion_tones.get(target_emotion, self.emotion_tones["neutral"])["text_transformation"]
            
            # Create system prompt
            system_prompt = f"""
            You are an expert in empathetic communication. Rewrite the text to better address someone feeling {target_emotion}.
            Make the response {transformation}.
            
            Your task is to rewrite the text to be more emotionally appropriate while preserving all factual information.
            Keep the length similar to the original. Don't add new information that wasn't implied in the original.
            Maintain the same language and formality level as the original.
            
            Reply with only the rewritten text, without explanations, quotes, or additional formatting.
            """
            
            # Include user emotion context if available
            user_prompt = text
            if user_emotion and user_emotion != target_emotion:
                system_prompt += f"\n\nThe person you're responding to is feeling {user_emotion}, but you want to guide them toward {target_emotion}."
            
            # Make API call
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Using the latest model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4  # Moderate temperature for creativity with consistency
            )
            
            # Extract and clean response
            modulated_text = response.choices[0].message.content.strip()
            
            # Cache result
            with open(cache_path, 'w') as f:
                json.dump({"original_text": text, "modulated_text": modulated_text}, f)
            
            return modulated_text
            
        except Exception as e:
            self.logger.error(f"Error modulating text: {str(e)}")
            return text  # Return original text on error
    
    def _simple_modulation(self, text, emotion, language):
        """
        Simple rule-based text modulation when OpenAI is not available
        
        Args:
            text (str): Text to modulate
            emotion (str): Target emotion
            language (str): Language code
            
        Returns:
            str: Modulated text
        """
        # Check language
        if language == "ar":
            # Arabic modulation patterns
            if emotion == "happy":
                if not any(char in text for char in ['!', '؟']):
                    text += '!'
            elif emotion == "sad":
                # Add soft ending for sad tone
                if text.endswith('.'):
                    text = text[:-1] + '...'
            return text
        else:
            # English modulation patterns
            if emotion == "happy":
                if not text.endswith(('!', '?')):
                    text += '!'
            elif emotion == "sad":
                if text.endswith('.'):
                    text = text[:-1] + '...'
            elif emotion == "angry":
                # Make sure sentences are complete and clear for angry responses
                if not text.endswith(('.', '!', '?')):
                    text += '.'
            
            return text
    
    def get_voice_settings(self, emotion):
        """
        Get the voice settings for a specific emotion
        
        Args:
            emotion (str): Emotion to get settings for
            
        Returns:
            dict: Voice settings optimized for the emotion
        """
        # Default to neutral if emotion not found
        if emotion not in self.emotion_tones:
            emotion = "neutral"
            
        return self.emotion_tones[emotion]["voice_settings"]