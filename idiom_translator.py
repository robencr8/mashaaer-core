"""
Multilingual Emotion Idiom Translator for Mashaaer Feelings

This module provides functionality to translate emotional idioms and phrases
between different languages, preserving the cultural context and emotional meaning.
"""
import json
import logging
import os
from typing import Dict, Any, List, Optional, Tuple

from ai_model_router import AIModelRouter

# Set up logging
logger = logging.getLogger(__name__)

# Import mock data for testing and fallback
try:
    from mock_idiom_data import ENGLISH_IDIOMS, ARABIC_IDIOMS, MOCK_TRANSLATIONS
    MOCK_DATA_AVAILABLE = True
except ImportError:
    logger.warning("Mock idiom data not available. Some fallback functionality may be limited.")
    MOCK_DATA_AVAILABLE = False

class IdiomTranslator:
    """
    Translates emotional idioms and expressions between languages
    while preserving emotional context and cultural nuances.
    """
    
    def __init__(self, model_router: Optional[AIModelRouter] = None):
        """
        Initialize the idiom translator with an AI model router
        
        Args:
            model_router: AIModelRouter instance for language model access
        """
        self.model_router = model_router or AIModelRouter()
        self.supported_languages = ['en', 'ar']  # English and Arabic supported
        self.idiom_cache = {}  # Cache for translated idioms to reduce API calls
        logger.info("Idiom Translator initialized with %d supported languages", len(self.supported_languages))
    
    def translate_idiom(
        self, 
        idiom: str,
        source_lang: str,
        target_lang: str,
        emotion: Optional[str] = None,
        provide_explanation: bool = False
    ) -> Dict[str, Any]:
        """
        Translate an emotional idiom from source language to target language
        
        Args:
            idiom: The idiom or emotional expression to translate
            source_lang: Source language code (e.g., 'en', 'ar')
            target_lang: Target language code (e.g., 'en', 'ar')
            emotion: Optional hint about the emotion expressed in the idiom
            provide_explanation: Whether to include cultural explanation
            
        Returns:
            Dictionary with translated idiom and related information
        """
        # Validate languages
        if source_lang not in self.supported_languages:
            return {
                "success": False,
                "error": f"Source language '{source_lang}' not supported. Supported languages: {', '.join(self.supported_languages)}"
            }
            
        if target_lang not in self.supported_languages:
            return {
                "success": False, 
                "error": f"Target language '{target_lang}' not supported. Supported languages: {', '.join(self.supported_languages)}"
            }
        
        # If source and target languages are the same, return the original
        if source_lang == target_lang:
            return {
                "success": True,
                "original_idiom": idiom,
                "translated_idiom": idiom,
                "source_language": source_lang,
                "target_language": target_lang,
                "explanation": "No translation needed, languages are the same."
            }
        
        # Check cache to avoid unnecessary API calls
        cache_key = f"{idiom}_{source_lang}_{target_lang}_{emotion}_{provide_explanation}"
        if cache_key in self.idiom_cache:
            logger.debug("Idiom translation found in cache: %s", idiom)
            return self.idiom_cache[cache_key]
        
        # Create appropriate system prompt for the AI
        system_prompt = self._create_system_prompt(source_lang, target_lang, provide_explanation, emotion)
        
        # Create user prompt with the idiom to translate
        user_prompt = f"Translate this emotional expression or idiom: \"{idiom}\""
        if emotion:
            user_prompt += f"\nThe emotion expressed is: {emotion}"
        
        # Request translation from AI model
        response = self.model_router.generate_response(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        # Check if AI response was successful
        if not response["success"]:
            logger.error("Failed to translate idiom: %s", response.get("error", "Unknown error"))
            
            # Try to use mock data if available
            if MOCK_DATA_AVAILABLE and idiom in MOCK_TRANSLATIONS and target_lang in MOCK_TRANSLATIONS[idiom]:
                logger.info("Using mock translation data for idiom: %s", idiom)
                mock_data = MOCK_TRANSLATIONS[idiom][target_lang]
                result = {
                    "success": True,
                    "original_idiom": idiom,
                    "translated_idiom": mock_data["translated_idiom"],
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "emotional_meaning": mock_data["emotional_meaning"],
                    "note": "This translation is from cached example data (API unavailable)"
                }
                
                if "literal_meaning" in mock_data:
                    result["literal_meaning"] = mock_data["literal_meaning"]
                
                if provide_explanation and "cultural_context" in mock_data:
                    result["cultural_context"] = mock_data["cultural_context"]
                
                # Add to cache
                self.idiom_cache[cache_key] = result
                return result
            
            return {
                "success": False,
                "error": f"Failed to translate idiom: {response.get('error', 'Unknown error')}",
                "original_idiom": idiom,
                "source_language": source_lang,
                "target_language": target_lang
            }
        
        # Parse AI response to extract translation and explanation
        translation_result = self._parse_translation_response(
            response["content"], 
            idiom, 
            source_lang, 
            target_lang,
            provide_explanation
        )
        
        # Add to cache
        self.idiom_cache[cache_key] = translation_result
        
        return translation_result
    
    def _create_system_prompt(
        self, 
        source_lang: str, 
        target_lang: str, 
        provide_explanation: bool,
        emotion: Optional[str]
    ) -> str:
        """
        Create a system prompt for the AI model based on translation requirements
        
        Args:
            source_lang: Source language code
            target_lang: Target language code
            provide_explanation: Whether cultural explanation is needed
            emotion: Optional emotion context
            
        Returns:
            System prompt string for the AI model
        """
        # Map language codes to full names for better AI understanding
        lang_names = {
            'en': 'English',
            'ar': 'Arabic'
        }
        source_name = lang_names.get(source_lang, source_lang)
        target_name = lang_names.get(target_lang, target_lang)
        
        system_prompt = f"""You are an expert multilingual translator specializing in emotional expressions and idioms.
Your task is to translate emotional idioms from {source_name} to {target_name} while preserving their cultural 
and emotional meaning. Focus on finding equivalent emotional expressions in the target language rather than 
literal translations. Respond in JSON format with the following structure:
{{
  "translated_idiom": "The translated idiom in {target_name}",
  "literal_meaning": "Literal word-for-word translation (optional)",
  "emotional_meaning": "The emotional meaning of the idiom"
}}"""

        if provide_explanation:
            system_prompt += """,
  "cultural_context": "Brief explanation of the cultural context or origin"
}"""
        else:
            system_prompt += "\n}"
        
        if emotion:
            system_prompt += f"\n\nThe primary emotion expressed is: {emotion}"
        
        return system_prompt
    
    def _parse_translation_response(
        self, 
        ai_response: str, 
        original_idiom: str, 
        source_lang: str, 
        target_lang: str,
        explanation_requested: bool
    ) -> Dict[str, Any]:
        """
        Parse the AI response to extract the translation and explanation
        
        Args:
            ai_response: Raw AI response text
            original_idiom: Original idiom that was translated
            source_lang: Source language code
            target_lang: Target language code
            explanation_requested: Whether explanation was requested
            
        Returns:
            Structured dictionary with translation results
        """
        try:
            # Try to parse JSON directly from the response
            # Look for JSON block in the response
            response_text = ai_response.strip()
            
            # Find JSON block if it's embedded in text
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                data = json.loads(json_str)
            else:
                # Try to parse the whole response as JSON
                data = json.loads(response_text)
            
            # Create result dictionary
            result = {
                "success": True,
                "original_idiom": original_idiom,
                "translated_idiom": data.get("translated_idiom", "Translation not provided"),
                "source_language": source_lang,
                "target_language": target_lang,
                "emotional_meaning": data.get("emotional_meaning", "")
            }
            
            # Add literal meaning if available
            if "literal_meaning" in data:
                result["literal_meaning"] = data["literal_meaning"]
            
            # Add cultural context if requested and available
            if explanation_requested and "cultural_context" in data:
                result["cultural_context"] = data["cultural_context"]
            
            return result
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse JSON from AI response: %s", str(e))
            
            # Fallback to simple extraction if JSON parsing fails
            lines = ai_response.split('\n')
            translated_idiom = original_idiom  # Default fallback
            
            # Look for translation in the response text
            for line in lines:
                if ":" in line and not line.strip().startswith("{") and not line.strip().startswith("}"):
                    parts = line.split(":", 1)
                    if "translat" in parts[0].lower() and len(parts) > 1:
                        translated_idiom = parts[1].strip().strip('"\'')
                        break
            
            return {
                "success": True,
                "original_idiom": original_idiom,
                "translated_idiom": translated_idiom,
                "source_language": source_lang,
                "target_language": target_lang,
                "note": "Translation format was not structured as expected."
            }
    
    def get_common_emotion_idioms(self, language: str, emotion: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get a list of common emotional idioms for a specific language
        
        Args:
            language: Language code (e.g., 'en', 'ar')
            emotion: Optional filter for specific emotion
            
        Returns:
            List of dictionaries with idioms and their meanings
        """
        # Validate language
        if language not in self.supported_languages:
            logger.warning("Requested idioms for unsupported language: %s", language)
            return []
        
        # Use AI to generate common idioms for the language and emotion
        system_prompt = f"""You are an expert in {language} emotional idioms and expressions.
Generate a list of 5 common emotional idioms or expressions in JSON format. Each entry should include the idiom and its meaning.
Respond with a JSON array using the following structure:
[
  {{"idiom": "The idiom text", "meaning": "The meaning and emotional context", "emotion": "The primary emotion"}}
]"""

        if emotion:
            system_prompt += f"\n\nFocus on idioms related to the emotion: {emotion}"
        
        # Generate idiom list from AI
        response = self.model_router.generate_response(
            prompt=f"Generate common emotional idioms in {language}" + 
                   (f" for the emotion: {emotion}" if emotion else ""),
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=800
        )
        
        # Handle API errors
        if not response["success"]:
            logger.error("Failed to get common idioms: %s", response.get("error", "Unknown error"))
            
            # Use mock data if available
            if MOCK_DATA_AVAILABLE:
                logger.info("Using mock idiom data for language: %s, emotion: %s", language, emotion)
                if language == 'en':
                    idiom_data = ENGLISH_IDIOMS
                elif language == 'ar':
                    idiom_data = ARABIC_IDIOMS
                else:
                    return []
                
                # If emotion is specified, filter by that emotion, otherwise use 'general'
                emotion_key = emotion.lower() if emotion else 'general'
                # If the specific emotion is not in our data, fall back to general
                if emotion_key not in idiom_data:
                    emotion_key = 'general'
                
                return idiom_data.get(emotion_key, [])
        
        # Parse response to extract idioms list
        try:
            # Find JSON in response
            response_text = response["content"].strip()
            
            # Find JSON block if it's embedded in text
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                idioms = json.loads(json_str)
            else:
                # Try to parse the whole response as JSON
                idioms = json.loads(response_text)
            
            # Ensure proper format
            if isinstance(idioms, list):
                return idioms
            return []
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse idioms JSON from AI response: %s", str(e))
            return []

# Singleton instance for application-wide use
idiom_translator = None

def get_idiom_translator(model_router: Optional[AIModelRouter] = None) -> IdiomTranslator:
    """
    Get or create the singleton IdiomTranslator instance
    
    Args:
        model_router: Optional AIModelRouter instance
        
    Returns:
        Shared IdiomTranslator instance
    """
    global idiom_translator
    if idiom_translator is None:
        idiom_translator = IdiomTranslator(model_router)
    return idiom_translator