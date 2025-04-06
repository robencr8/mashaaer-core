"""
API Routes for Multilingual Emotion Idiom Translator
Provides endpoints for translating emotional idioms between languages
"""
from flask import Blueprint, request, jsonify, current_app
import logging
from typing import Dict, Any, List, Optional

from idiom_translator import get_idiom_translator
from ai_model_router import AIModelRouter

# Set up logging
logger = logging.getLogger(__name__)

# Create Blueprint
idiom_bp = Blueprint('idioms', __name__, url_prefix='/api/idioms')

def init_idiom_routes(app, model_router: Optional[AIModelRouter] = None):
    """Initialize the idiom translation routes with necessary dependencies"""
    # Initialize the idiom translator with the model router
    get_idiom_translator(model_router)
    
    # Register the blueprint
    app.register_blueprint(idiom_bp)
    logger.info("Idiom translation routes registered successfully")
    return idiom_bp

@idiom_bp.route('/translate', methods=['POST'])
def translate_idiom():
    """
    Translate an emotional idiom or expression from one language to another
    
    Request body:
    {
        "idiom": "Walking on sunshine",
        "source_lang": "en",
        "target_lang": "ar",
        "emotion": "happy" (optional),
        "provide_explanation": true (optional, default: false)
    }
    
    Returns:
    {
        "success": true,
        "original_idiom": "Walking on sunshine",
        "translated_idiom": "أسير على أشعة الشمس",
        "source_language": "en",
        "target_language": "ar",
        "emotional_meaning": "Feeling extremely happy and carefree",
        "literal_meaning": "Walking on the sun's rays" (optional),
        "cultural_context": "..." (optional, if provide_explanation is true)
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Extract required fields
        idiom = data.get('idiom')
        source_lang = data.get('source_lang')
        target_lang = data.get('target_lang')
        
        if not idiom or not source_lang or not target_lang:
            return jsonify({
                'success': False, 
                'error': 'Missing required fields: idiom, source_lang, target_lang'
            }), 400
        
        # Extract optional fields
        emotion = data.get('emotion')
        provide_explanation = data.get('provide_explanation', False)
        
        # Get translator and translate
        translator = get_idiom_translator()
        result = translator.translate_idiom(
            idiom=idiom,
            source_lang=source_lang,
            target_lang=target_lang,
            emotion=emotion,
            provide_explanation=provide_explanation
        )
        
        # Log the translation request
        logger.info(
            f"Idiom translation: '{idiom}' from {source_lang} to {target_lang}" +
            (f" (emotion: {emotion})" if emotion else "")
        )
        
        # Return translation result
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error translating idiom: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to translate idiom',
            'message': str(e)
        }), 500

@idiom_bp.route('/common', methods=['GET'])
def get_common_idioms():
    """
    Get a list of common emotional idioms for a specific language
    
    Query parameters:
    - language: Language code (en, ar)
    - emotion: Optional filter for specific emotion (happy, sad, angry, etc.)
    
    Returns:
    {
        "success": true,
        "language": "en",
        "emotion": "happy" (if provided),
        "idioms": [
            {
                "idiom": "Walking on sunshine",
                "meaning": "Feeling extremely happy and carefree",
                "emotion": "happy"
            },
            ...
        ]
    }
    """
    try:
        # Extract query parameters
        language = request.args.get('language', 'en')
        emotion = request.args.get('emotion')
        
        # Validate language
        supported_languages = ['en', 'ar']
        if language not in supported_languages:
            return jsonify({
                'success': False,
                'error': f"Unsupported language: {language}. Supported languages: {', '.join(supported_languages)}"
            }), 400
        
        # Get translator and fetch common idioms
        translator = get_idiom_translator()
        idioms = translator.get_common_emotion_idioms(language, emotion)
        
        # Return results
        return jsonify({
            'success': True,
            'language': language,
            'emotion': emotion,
            'idioms': idioms
        })
    
    except Exception as e:
        logger.error(f"Error getting common idioms: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get common idioms',
            'message': str(e)
        }), 500

@idiom_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """
    Get the list of languages supported by the idiom translator
    
    Returns:
    {
        "success": true,
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "ar", "name": "Arabic"}
        ]
    }
    """
    languages = [
        {"code": "en", "name": "English"},
        {"code": "ar", "name": "Arabic"}
    ]
    
    return jsonify({
        'success': True,
        'languages': languages
    })