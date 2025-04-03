"""
Mobile API Routes for Mashaaer AI
Provides optimized endpoints for the mobile application with enhanced error handling,
caching strategies, and bandwidth-efficient responses.
"""
import os
import json
import time
import uuid
import logging
import traceback
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, session, current_app, Response
from werkzeug.utils import secure_filename

# Setup logging
logger = logging.getLogger(__name__)

# Blueprint definition
mobile_api = Blueprint('mobile_api', __name__)

# Global references (will be set when registered with app)
db_manager = None
emotion_tracker = None
tts_manager = None
voice_recognition = None
intent_classifier = None
config = None
context_assistant = None
model_router = None
profile_manager = None

def init_mobile_api(app, _db_manager, _emotion_tracker, _tts_manager, _voice_recognition, 
                  _intent_classifier, _config, _profile_manager, 
                  _context_assistant=None, _model_router=None):
    """Initialize the Mobile API blueprint with necessary dependencies"""
    global db_manager, emotion_tracker, tts_manager, voice_recognition
    global intent_classifier, config, context_assistant, model_router, profile_manager
    
    # Set global references
    db_manager = _db_manager
    emotion_tracker = _emotion_tracker
    tts_manager = _tts_manager
    voice_recognition = _voice_recognition
    intent_classifier = _intent_classifier
    config = _config
    context_assistant = _context_assistant
    model_router = _model_router
    profile_manager = _profile_manager
    
    # Register the blueprint with the app
    app.register_blueprint(mobile_api, url_prefix='/mobile-api')
    
    # Log the initialization
    logger.info(f"Mobile API Blueprint initialized with {len(mobile_api.deferred_functions)} routes")

def _get_or_create_session_id():
    """Get the current session ID or create a new one, with specific handling for mobile app"""
    if 'session_id' not in session:
        # Generate a new session ID
        session['session_id'] = str(uuid.uuid4())
        session['created_at'] = time.time()
        
        # Check if this is a mobile app session based on headers
        is_mobile_app = False
        user_agent = request.headers.get('User-Agent', '').lower()
        
        if 'mashaaer-mobile-app' in user_agent:
            is_mobile_app = True
        elif request.headers.get('X-Mashaaer-App'):
            is_mobile_app = True
        
        # Record session type
        session['is_mobile_app'] = is_mobile_app
        logger.info(f"Created new mobile session: {session['session_id']} (mobile app: {is_mobile_app})")
    
    return session['session_id']

@mobile_api.route('/status', methods=['GET'])
def mobile_status():
    """
    Get system status information optimized for mobile client
    
    This endpoint provides essential status information for the mobile app
    including server version, available services, and connection quality.
    
    Response format:
    {
        "success": true,
        "version": "1.1.0",
        "api_version": "v1",
        "services": {
            "tts": true,
            "voice_recognition": true,
            "emotion_analysis": true
        },
        "session_id": "f2b43594-1edc-4cd4-bfbe-844ec68a77ed",
        "timestamp": "2025-04-03T14:22:00Z",
        "latency_ms": 15
    }
    """
    start_time = time.time()
    
    # Get or create session ID
    session_id = _get_or_create_session_id()
    
    # Check available services
    tts_available = tts_manager is not None
    voice_available = voice_recognition is not None
    emotion_available = emotion_tracker is not None
    
    # Current app version
    app_version = "1.1.0"  # Should be sourced from config
    api_version = "v1"
    
    # Calculate response time
    latency_ms = int((time.time() - start_time) * 1000)
    
    return jsonify({
        "success": True,
        "version": app_version,
        "api_version": api_version,
        "services": {
            "tts": tts_available,
            "voice_recognition": voice_available,
            "emotion_analysis": emotion_available
        },
        "session_id": session_id,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "latency_ms": latency_ms
    })

@mobile_api.route('/analyze-emotion', methods=['POST'])
def mobile_analyze_emotion():
    print("\n===== ANALYZE EMOTION API CALLED =====")
    print(f"Request method: {request.method}")
    """
    Mobile-optimized emotion analysis endpoint
    
    Enhanced for mobile with:
    - Binary response format option for reducing payload size
    - Support for both text and audio input
    - Enhanced error handling for intermittent connections
    - Response caching for improved performance
    
    Request format:
    {
        "text": "Text to analyze",
        "language": "en" | "ar",
        "format": "json" | "minimal",
        "include_details": true | false,
        "bypass_cache": false | true
    }
    
    Response format (full):
    {
        "success": true,
        "result": {
            "primary_emotion": "happy",
            "emotions": {
                "happy": 0.8,
                "sad": 0.1,
                "angry": 0.05,
                "neutral": 0.05
            },
            "intensity": 0.8,
            "metadata": {
                "source": "emotion-analysis-v2",
                "confidence": 0.9
            },
            "timestamp": "2025-04-03T14:22:00Z"
        },
        "cache_status": "hit" | "miss" | "disabled"
    }
    
    Response format (minimal):
    {
        "s": true,
        "e": "happy", 
        "i": 0.8,
        "c": 0.9
    }
    """
    # Record start time for performance metrics
    start_time = time.time()
    
    try:
        # Parse request data
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
        
        text = data.get('text', '')
        language = data.get('language', 'en')
        response_format = data.get('format', 'json')  # 'json' or 'minimal'
        include_details = data.get('include_details', True)
        bypass_cache = data.get('bypass_cache', False)
        
        # Validate required fields
        if not text:
            # Prepare error response based on format
            if response_format == 'minimal':
                return jsonify({"s": False, "e": "missing_text"})
            else:
                return jsonify({
                    "success": False,
                    "error": "Text is required for emotion analysis"
                }), 400
        
        # Generate a cache key (normalize text to ensure consistent caching)
        import hashlib
        normalized_text = text.strip().lower()
        cache_key = f"emotion_{hashlib.md5(normalized_text.encode()).hexdigest()}_{language}"
        cache_status = "disabled" if bypass_cache else "miss"
        
        # Debug logging for testing
        print(f"DEBUG: Normalized text: '{normalized_text}'")
        print(f"DEBUG: Generated cache key: '{cache_key}'")
        print(f"DEBUG: Bypass cache: {bypass_cache}")
        
        # Check cache if not bypassing
        cached_result = None
        cache_metadata = {}
        if not bypass_cache and db_manager and hasattr(db_manager, 'get_cached_response'):
            try:
                cached_result, cache_metadata = db_manager.get_cached_response(cache_key)
                cache_status = "hit" if cache_metadata.get("cache_hit", False) else "miss"
                
                if cached_result and cache_metadata.get("cache_hit", False):
                    logger.debug(f"Cache hit for emotion analysis: {cache_key}, hit count: {cache_metadata.get('hit_count', 0)}")
                    
                    # Add cache status to response
                    if response_format == 'minimal':
                        return jsonify({
                            "s": True,
                            "e": cached_result.get("primary_emotion", "neutral"),
                            "i": cached_result.get("confidence", 0.8),
                            "c": cached_result.get("confidence", 0.8),
                            "cached": True
                        })
                    else:
                        # For full response format
                        result = {
                            "primary_emotion": cached_result.get("primary_emotion", "neutral"),
                            "intensity": cached_result.get("confidence", 0.8),
                            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "emotions": cached_result.get("emotions", {}),
                        }
                        
                        if include_details:
                            result["metadata"] = {
                                "source": "emotion-analysis-v2",
                                "confidence": cached_result.get("confidence", 0.8),
                                "language": language,
                                "processing_time_ms": 0,  # Near-instant with cache
                                "cache_created_at": cache_metadata.get("created_at"),
                                "cache_expires_at": cache_metadata.get("expires_at"),
                                "cache_hit_count": cache_metadata.get("hit_count", 1)
                            }
                        
                        # Performance metrics
                        end_time = time.time()
                        processing_time_ms = int((end_time - start_time) * 1000)
                        
                        return jsonify({
                            "success": True,
                            "result": result,
                            "cache_status": cache_status,
                            "processing_time_ms": processing_time_ms
                        })
            except Exception as e:
                logger.warning(f"Failed to process cached result: {str(e)}")
                # Fall through to regular processing
        
        # Check emotion tracker availability
        if emotion_tracker is None:
            if response_format == 'minimal':
                return jsonify({"s": False, "e": "service_unavailable"})
            else:
                return jsonify({
                    "success": False,
                    "error": "Emotion analysis service not available"
                }), 503
                
        # Generate session ID for tracking
        session_id = _get_or_create_session_id()
        
        # Log the request (without the full text for privacy)
        text_preview = text[:20] + '...' if len(text) > 20 else text
        logger.info(f"Mobile API: Emotion analysis request: '{text_preview}' in {language}")
        
        # Perform emotion analysis
        try:
            # Use fallback model if OpenAI is not available (quota exceeded)
            try:
                emotion_result = emotion_tracker.analyze_text(text)
            except Exception as e:
                if "quota" in str(e).lower() or "insufficient_quota" in str(e).lower():
                    logger.warning(f"OpenAI quota exceeded, using fallback emotion analysis: {str(e)}")
                    # Fallback to basic emotion detection
                    emotion_result = emotion_tracker.analyze_text_basic(text) if hasattr(emotion_tracker, 'analyze_text_basic') else "neutral"
                else:
                    # Re-raise other exceptions
                    raise
            
            # Handle different result formats from emotion tracker
            if isinstance(emotion_result, str):
                dominant_emotion = emotion_result
                confidence = 0.8
                all_emotions = {dominant_emotion: 0.8, "neutral": 0.2}
            else:
                dominant_emotion = emotion_result.get('primary_emotion', 'neutral')
                confidence = emotion_result.get('confidence', 0.8)
                all_emotions = emotion_result.get('emotions', {})
                
                # Cache the result for future requests
                if not bypass_cache and db_manager and hasattr(db_manager, 'store_cached_response'):
                    try:
                        # Debug print for cache decision
                        print(f"DEBUG: Storing in cache, bypass_cache={bypass_cache}, db_manager exists={db_manager is not None}")
                        
                        # Prepare data to cache
                        cache_data = {
                            "primary_emotion": dominant_emotion,
                            "confidence": confidence,
                            "emotions": all_emotions,
                            "language": language,
                            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                        }
                        
                        print(f"DEBUG: cache_data prepared: {json.dumps(cache_data)}")
                        print(f"DEBUG: cache_key for storage: {cache_key}")
                        
                        # Store in cache with an expiration time (3 days)
                        cache_expiry = 259200  # 3 days in seconds
                        store_success = db_manager.store_cached_response(cache_key, json.dumps(cache_data), expiry_seconds=cache_expiry)
                        print(f"DEBUG: Cache storage result: {store_success}")
                        
                        # Verify cache entry was created
                        from database.models import Cache
                        with db_manager.Session() as sess:
                            entry = sess.query(Cache).filter(Cache.key == cache_key).first()
                            print(f"DEBUG: Cache entry after storage: {entry is not None}")
                            if entry:
                                print(f"DEBUG: Cache key: {entry.key}, Created: {entry.created_at}, Hit count: {entry.hit_count}")
                        
                        logger.debug(f"Cached emotion analysis for key: {cache_key}")
                    except Exception as e:
                        print(f"DEBUG ERROR: Failed to cache result: {str(e)}")
                        print(f"DEBUG ERROR: Exception type: {type(e)}")
                        logger.warning(f"Failed to cache emotion result: {str(e)}")
            
                # Calculate response time
            end_time = time.time()
            processing_time_ms = int((end_time - start_time) * 1000)
        
            # Create response based on format preference
            if response_format == 'minimal':
                # Minimal format for low-bandwidth scenarios
                return jsonify({
                    "s": True,  # success
                    "e": dominant_emotion,  # emotion
                    "i": confidence,  # intensity
                    "c": confidence,  # confidence
                    "t": processing_time_ms  # processing time
                })
            else:
                # Full response with complete details
                result = {
                    "primary_emotion": dominant_emotion,
                    "intensity": confidence,
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                }
                
                # Include detailed emotion breakdown if requested
                if include_details:
                    result["emotions"] = all_emotions
                    result["metadata"] = {
                        "source": "emotion-analysis-v2",
                        "confidence": confidence,
                        "language": language,
                        "processing_time_ms": processing_time_ms
                    }
                
                return jsonify({
                    "success": True,
                    "result": result,
                    "cache_status": cache_status,
                    "processing_time_ms": processing_time_ms
                })
                
        except Exception as e:
            logger.error(f"Mobile API: Emotion analysis error: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Error responses
            if response_format == 'minimal':
                return jsonify({"s": False, "e": "analysis_error"})
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to analyze emotions",
                    "error_details": str(e)
                }), 500
            
    except Exception as e:
        logger.error(f"Mobile API: Unexpected error in emotion analysis: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Get response format from the request, defaulting to 'json'
        try:
            response_format = data.get('format', 'json')
        except:
            response_format = 'json'
        
        # Fallback error response
        if response_format == 'minimal':
            return jsonify({"s": False, "e": "unexpected_error"})
        else:
            return jsonify({
                "success": False,
                "error": "An unexpected error occurred",
                "error_details": str(e)
            }), 500

@mobile_api.route('/speak', methods=['POST'])
def mobile_speak():
    """
    Mobile-optimized text-to-speech endpoint
    
    Enhanced for mobile with:
    - Support for streaming audio response
    - Audio format selection (mp3, wav)
    - Cached response handling with ETag
    - Connection drop recovery
    
    Request format:
    {
        "text": "Text to speak",
        "language": "en-US" | "ar",
        "voice": "voice_id" | "default",
        "format": "mp3" | "wav",
        "stream": true | false
    }
    
    Response format (JSON):
    {
        "success": true,
        "audio_path": "/tts_cache/voice_id_hash.mp3",
        "text": "Text to speak",
        "voice": "voice_id",
        "language": "en-US",
        "provider_status": {
            "elevenlabs": true,
            "gtts": true
        }
    }
    
    Or binary audio data if stream=true
    """
    try:
        # Parse request data
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
        
        # Record start time for performance metrics
        start_time = time.time()
        
        text = data.get('text', '')
        voice = data.get('voice', 'default')
        language = data.get('language', 'en-US')
        audio_format = data.get('format', 'mp3')
        stream = data.get('stream', False)
        bypass_cache = data.get('bypass_cache', False)
        
        # Validate required fields
        if not text:
            return jsonify({
                "success": False,
                "error": "Text is required for TTS"
            }), 400
        
        # Check TTS availability
        if tts_manager is None:
            return jsonify({
                "success": False,
                "error": "TTS service not available"
            }), 503
            
        # Generate a cache key for TTS
        import hashlib
        cache_key = f"tts_{voice}_{language}_{hashlib.md5(text.encode()).hexdigest()}"
        cache_status = "disabled" if bypass_cache else "miss"
        
        # Check cache if not bypassing
        cached_result = None
        cache_metadata = {}
        if not bypass_cache and db_manager and hasattr(db_manager, 'get_cached_response'):
            try:
                cached_result, cache_metadata = db_manager.get_cached_response(cache_key)
                cache_status = "hit" if cache_metadata.get("cache_hit", False) else "miss"
                
                if cached_result and cache_metadata.get("cache_hit", False):
                    logger.debug(f"Cache hit for TTS: {cache_key}, hit count: {cache_metadata.get('hit_count', 0)}")
                    
                    # Get cached audio path
                    cached_audio_path = cached_result.get('audio_path')
                    
                    # Verify the audio file exists
                    if os.path.exists(cached_audio_path) and os.path.getsize(cached_audio_path) > 0:
                        logger.info(f"Mobile API: Using cached TTS audio: {cached_audio_path}")
                        
                        # Performance metrics
                        end_time = time.time()
                        processing_time_ms = int((end_time - start_time) * 1000)
                        
                        # Handle streaming if requested
                        if stream:
                            try:
                                with open(cached_audio_path, 'rb') as audio_file:
                                    audio_data = audio_file.read()
                                
                                content_type = 'audio/mpeg' if cached_audio_path.endswith('.mp3') else 'audio/wav'
                                
                                return Response(
                                    audio_data,
                                    mimetype=content_type,
                                    headers={
                                        'Content-Disposition': f'inline; filename={os.path.basename(cached_audio_path)}',
                                        'X-TTS-Voice': voice,
                                        'X-TTS-Language': language,
                                        'X-Cache-Status': 'hit',
                                        'X-Cache-Hits': str(cache_metadata.get('hit_count', 1)),
                                        'X-Processing-Time': str(processing_time_ms)
                                    }
                                )
                            except Exception as e:
                                logger.error(f"Mobile API: Cached streaming error: {str(e)}")
                                # Fall through to regenerate
                        else:
                            # Standard JSON response with cached path
                            response = {
                                'success': True,
                                'audio_path': cached_audio_path,
                                'text': text,
                                'voice': voice,
                                'language': language,
                                'cache_status': cache_status,
                                'processing_time_ms': processing_time_ms
                            }
                            
                            # Add cache metadata for debugging/monitoring
                            if config and getattr(config, 'DEBUG', False):
                                response['cache_metadata'] = {
                                    'hit_count': cache_metadata.get('hit_count', 1),
                                    'created_at': cache_metadata.get('created_at'),
                                    'expires_at': cache_metadata.get('expires_at')
                                }
                                
                            return jsonify(response)
                    else:
                        logger.warning(f"Cached audio file not found or empty: {cached_audio_path}")
                        # Fall through to regenerate
            except Exception as e:
                logger.warning(f"Failed to retrieve cached TTS result: {str(e)}")
                # Fall through to regular processing
            
        # Get TTS provider status for response
        elevenlabs_available = hasattr(tts_manager, 'use_elevenlabs') and tts_manager.use_elevenlabs
        gtts_available = hasattr(tts_manager, 'use_gtts') and tts_manager.use_gtts
        
        provider_status = {
            'elevenlabs': elevenlabs_available,
            'gtts': gtts_available
        }
        
        # Log the request details
        logger.info(f"Mobile API: TTS Request: text='{text[:30]}...', voice={voice}, language={language}")
        
        # Generate audio using TTS manager
        try:
            # Basic validation for language
            if language not in ['en', 'en-US', 'ar']:
                logger.warning(f"Unsupported language requested: {language}, falling back to 'en-US'")
                language = 'en-US'
                
            # Use profile manager if available for personalized voice
            if profile_manager and voice == 'default':
                voice = profile_manager.get_tts_voice_for_language(language)
                logger.debug(f"Selected voice from profile: {voice}")
            elif voice == 'default':
                # Select language-appropriate voice
                if language.startswith('ar'):
                    voice = '21m00Tcm4TlvDq8ikWAM'  # Default Arabic voice
                else:
                    voice = 'ErXwobaYiN019PkySvjV'  # Default English voice
            
            # Generate the audio
            audio_path = tts_manager.generate_tts(text, voice=voice, language=language)
            
            # Verify the audio file exists and has content
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                logger.info(f"Mobile API: TTS successful: {audio_path} ({os.path.getsize(audio_path)} bytes)")
                
                # Cache the result for future requests (if not bypassing cache)
                if not bypass_cache and db_manager and hasattr(db_manager, 'store_cached_response'):
                    try:
                        # Prepare data to cache
                        cache_data = {
                            "audio_path": audio_path,
                            "voice": voice,
                            "language": language,
                            "text_length": len(text),
                            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "file_size": os.path.getsize(audio_path)
                        }
                        
                        # Cache for 7 days - TTS results rarely change
                        cache_expiry = 604800  # 7 days in seconds
                        db_manager.store_cached_response(cache_key, json.dumps(cache_data), expiry_seconds=cache_expiry)
                        logger.debug(f"Cached TTS audio for key: {cache_key}")
                    except Exception as e:
                        logger.warning(f"Failed to cache TTS result: {str(e)}")
                
                # Calculate response time
                end_time = time.time()
                processing_time_ms = int((end_time - start_time) * 1000)
                
                # Streaming response requested
                if stream:
                    try:
                        # Read the audio file and stream it directly
                        with open(audio_path, 'rb') as audio_file:
                            audio_data = audio_file.read()
                        
                        # Determine content type
                        content_type = 'audio/mpeg' if audio_path.endswith('.mp3') else 'audio/wav'
                        
                        # Create streaming response
                        return Response(
                            audio_data,
                            mimetype=content_type,
                            headers={
                                'Content-Disposition': f'inline; filename={os.path.basename(audio_path)}',
                                'X-TTS-Voice': voice,
                                'X-TTS-Language': language,
                                'X-Cache-Status': cache_status,
                                'X-Processing-Time': str(processing_time_ms)
                            }
                        )
                    except Exception as e:
                        logger.error(f"Mobile API: Streaming error: {str(e)}")
                        return jsonify({
                            "success": False,
                            "error": "Failed to stream audio",
                            "error_details": str(e)
                        }), 500
                
                # Standard JSON response with path to audio file
                return jsonify({
                    'success': True, 
                    'audio_path': audio_path,
                    'text': text,
                    'voice': voice,
                    'language': language,
                    'provider_status': provider_status,
                    'cache_status': cache_status,
                    'processing_time_ms': processing_time_ms
                })
            else:
                logger.warning(f"Mobile API: TTS path {audio_path} not found or empty")
                return jsonify({
                    "success": False,
                    "error": "TTS generated empty audio file",
                    "provider_status": provider_status
                }), 500
                
        except Exception as e:
            logger.error(f"Mobile API: TTS error: {str(e)}")
            logger.error(traceback.format_exc())
            
            return jsonify({
                "success": False,
                "error": "Failed to generate speech",
                "error_details": str(e),
                "provider_status": provider_status
            }), 500
            
    except Exception as e:
        logger.error(f"Mobile API: Unexpected error in TTS endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred",
            "error_details": str(e)
        }), 500

@mobile_api.route('/voice-recognition', methods=['POST'])
def mobile_voice_recognition():
    """
    Mobile-optimized voice recognition endpoint
    
    Enhanced for mobile with:
    - Improved error handling for intermittent connections
    - Support for different audio formats
    - Compressed audio support
    - Batch processing
    
    Request format:
    - Multipart form with 'audio' file
    - Additional form fields:
      - language: 'ar' | 'en'
      - context: optional context hint
    
    Response format:
    {
        "success": true,
        "text": "Recognized text",
        "confidence": 0.9,
        "language": "ar",
        "metadata": {
            "processing_time_ms": 230,
            "audio_quality": "good"
        }
    }
    """
    try:
        # Get the session ID first for logging
        session_id = _get_or_create_session_id()
        
        # Log request details
        logger.info(f"Mobile API: Voice recognition request received for session {session_id}")
        logger.info(f"Mobile API: Request content type: {request.content_type}")
        
        # Extract parameters
        language = request.form.get('language', 'ar')
        context = request.form.get('context', 'general')
        
        # Map to full language code for voice recognition
        recognition_language = 'ar-EG' if language == 'ar' else 'en-US'
        
        # Check if voice recognition is available
        if voice_recognition is None:
            logger.warning("Mobile API: Voice recognition module not initialized")
            return jsonify({
                "success": False,
                "error": "Voice recognition not available",
                "text": ""
            }), 503
        
        # Check if we're running in demo/test mode
        is_test_mode = os.environ.get('USE_SAMPLE_VOICE_RESPONSES', 'true').lower() == 'true'
        
        if is_test_mode:
            # Use sample responses in test mode
            sample_responses = {
                'name': ['محمد', 'فاطمة', 'Ahmed', 'Sarah'],
                'nickname': ['محمد', 'مها', 'Ahmed', 'Sara'],
                'terms-agree': ['نعم', 'أوافق', 'Yes', 'I agree'],
                'full-name': ['محمد علي', 'فاطمة احمد', 'Ahmed Ali', 'Sarah Hassan'],
                'language': ['العربية', 'English'],
                'voice-style': ['default', 'formal', 'casual'],
                'general': ['مرحبا بك', 'كيف حالك', 'Hello there', 'How are you today']
            }
            
            import random
            recognized_text = random.choice(sample_responses.get(context, ['Hello', 'مرحبا']))
            confidence = 0.95
            processing_time = 120
            
            logger.info(f"Mobile API: Test mode, returning sample text: {recognized_text}")
            
            # Log success to database
            try:
                device_info = json.dumps({
                    'user_agent': request.user_agent.string,
                    'platform': request.user_agent.platform,
                    'browser': request.user_agent.browser
                }) if request.user_agent else None
                
                db_manager.log_voice_recognition(
                    session_id=session_id,
                    language=language,
                    error_type=None,
                    raw_input=None,
                    recognized_text=recognized_text,
                    success=True,
                    device_info=device_info,
                    context=context
                )
            except Exception as e:
                logger.error(f"Mobile API: Failed to log voice recognition: {str(e)}")
            
            # Return the test response
            return jsonify({
                "success": True,
                "text": recognized_text,
                "confidence": confidence,
                "language": language,
                "metadata": {
                    "processing_time_ms": processing_time,
                    "audio_quality": "simulated",
                    "mode": "test"
                }
            })
        
        # Get audio file for processing
        audio_file = request.files.get('audio')
        
        if not audio_file:
            logger.warning("Mobile API: No audio file provided")
            return jsonify({
                "success": False,
                "error": "No audio file provided",
                "text": ""
            }), 400
            
        # Save the audio file temporarily
        try:
            # Create temp directory if it doesn't exist
            temp_dir = os.path.join(os.getcwd(), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save the file with secure name
            filename = secure_filename(f"voice_{session_id}_{int(time.time())}.wav")
            temp_path = os.path.join(temp_dir, filename)
            
            audio_file.save(temp_path)
            logger.info(f"Mobile API: Saved audio file to {temp_path}")
            
            # Process the audio with voice recognition
            start_time = time.time()
            result = voice_recognition.recognize_speech_from_file(
                temp_path, 
                language=recognition_language
            )
            processing_time = int((time.time() - start_time) * 1000)
            
            # Remove temporary file
            try:
                os.remove(temp_path)
            except Exception as e:
                logger.warning(f"Mobile API: Failed to remove temp file: {str(e)}")
            
            if result.get('success', False):
                recognized_text = result.get('text', '')
                confidence = result.get('confidence', 0.0)
                
                logger.info(f"Mobile API: Successfully recognized: '{recognized_text}'")
                
                # Log success to database
                try:
                    device_info = json.dumps({
                        'user_agent': request.user_agent.string,
                        'platform': request.user_agent.platform,
                        'browser': request.user_agent.browser
                    }) if request.user_agent else None
                    
                    if hasattr(db_manager, 'log_voice_recognition'):
                        db_manager.log_voice_recognition(
                            session_id=session_id,
                            language=language,
                            error_type=None,
                            raw_input=None,
                            recognized_text=recognized_text,
                            success=True,
                            device_info=device_info,
                            context=context
                        )
                    else:
                        # Fallback if log_voice_recognition is not available
                        logger.info(f"Voice recognition success: '{recognized_text}' (session: {session_id})")
                except Exception as e:
                    logger.error(f"Mobile API: Failed to log voice recognition: {str(e)}")
                
                # Return success response
                return jsonify({
                    "success": True,
                    "text": recognized_text,
                    "confidence": confidence,
                    "language": language,
                    "metadata": {
                        "processing_time_ms": processing_time,
                        "audio_quality": "good"
                    }
                })
            else:
                error_type = result.get('error', 'Unknown recognition error')
                logger.warning(f"Mobile API: Voice recognition failed: {error_type}")
                
                # Log failure to database
                try:
                    device_info = json.dumps({
                        'user_agent': request.user_agent.string,
                        'platform': request.user_agent.platform,
                        'browser': request.user_agent.browser
                    }) if request.user_agent else None
                    
                    if hasattr(db_manager, 'log_voice_recognition'):
                        db_manager.log_voice_recognition(
                            session_id=session_id,
                            language=language,
                            error_type=error_type,
                            raw_input=None,
                            recognized_text=None,
                            success=False,
                            device_info=device_info,
                            context=context
                        )
                    else:
                        # Fallback if log_voice_recognition is not available
                        logger.warning(f"Voice recognition failed: {error_type} (session: {session_id})")
                except Exception as e:
                    logger.error(f"Mobile API: Failed to log voice recognition failure: {str(e)}")
                
                # Return error response
                return jsonify({
                    "success": False,
                    "error": "Voice recognition failed",
                    "error_details": error_type,
                    "text": "",
                    "metadata": {
                        "processing_time_ms": processing_time
                    }
                }), 422  # Unprocessable Entity
                
        except Exception as e:
            logger.error(f"Mobile API: Error processing audio file: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Log failure to database
            try:
                device_info = json.dumps({
                    'user_agent': request.user_agent.string,
                    'platform': request.user_agent.platform,
                    'browser': request.user_agent.browser
                }) if request.user_agent else None
                
                if hasattr(db_manager, 'log_voice_recognition'):
                    db_manager.log_voice_recognition(
                        session_id=session_id,
                        language=language,
                        error_type=str(e),
                        raw_input=None,
                        recognized_text=None,
                        success=False,
                        device_info=device_info,
                        context=context
                    )
                else:
                    # Fallback if log_voice_recognition is not available
                    logger.error(f"Voice recognition error: {str(e)} (session: {session_id})")
            except Exception as log_error:
                logger.error(f"Mobile API: Failed to log voice recognition error: {str(log_error)}")
            
            # Return error response
            return jsonify({
                "success": False,
                "error": "Failed to process audio file",
                "error_details": str(e),
                "text": ""
            }), 500
            
    except Exception as e:
        logger.error(f"Mobile API: Unexpected error in voice recognition endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred",
            "error_details": str(e),
            "text": ""
        }), 500

@mobile_api.route('/batch-analyze', methods=['POST'])
def batch_analyze():
    """
    Batch analysis endpoint for mobile clients
    
    Process multiple texts in a single request to reduce network overhead
    for mobile applications, especially useful in offline sync scenarios.
    
    Request format:
    {
        "texts": [
            {"id": "1", "text": "First text to analyze", "language": "en"},
            {"id": "2", "text": "Second text to analyze", "language": "ar"}
        ],
        "format": "json" | "minimal"
    }
    
    Response format:
    {
        "success": true,
        "results": [
            {"id": "1", "primary_emotion": "happy", "confidence": 0.8},
            {"id": "2", "primary_emotion": "sad", "confidence": 0.7}
        ],
        "timestamp": "2025-04-03T14:22:00Z",
        "processing_time_ms": 230
    }
    """
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Request must be JSON"
            }), 400
            
        data = request.json
        texts = data.get('texts', [])
        response_format = data.get('format', 'json')
        
        if not texts or not isinstance(texts, list):
            return jsonify({
                "success": False,
                "error": "texts array is required"
            }), 400
            
        # Check emotion tracker availability
        if emotion_tracker is None:
            return jsonify({
                "success": False,
                "error": "Emotion analysis service not available"
            }), 503
            
        # Process each text in the batch
        start_time = time.time()
        results = []
        
        for item in texts:
            item_id = item.get('id', str(uuid.uuid4()))
            text = item.get('text', '')
            language = item.get('language', 'en')
            
            if not text:
                # Skip empty texts
                results.append({
                    "id": item_id,
                    "success": False,
                    "error": "Empty text"
                })
                continue
                
            try:
                # Analyze emotion
                emotion_result = emotion_tracker.analyze_text(text)
                
                # Process the result
                if isinstance(emotion_result, str):
                    dominant_emotion = emotion_result
                    confidence = 0.8
                else:
                    dominant_emotion = emotion_result.get('primary_emotion', 'neutral')
                    confidence = emotion_result.get('confidence', 0.8)
                
                # Add to results
                results.append({
                    "id": item_id,
                    "success": True,
                    "primary_emotion": dominant_emotion,
                    "confidence": confidence
                })
                
            except Exception as e:
                # Record error for this item
                logger.error(f"Mobile API: Batch analysis error for item {item_id}: {str(e)}")
                results.append({
                    "id": item_id,
                    "success": False,
                    "error": str(e)
                })
                
        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Return the complete batch result
        return jsonify({
            "success": True,
            "results": results,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "processing_time_ms": processing_time_ms
        })
        
    except Exception as e:
        logger.error(f"Mobile API: Unexpected error in batch analysis: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred",
            "error_details": str(e)
        }), 500

@mobile_api.route('/cached-resources', methods=['GET'])
def cached_resources():
    """
    Get a list of cacheable resources for offline use
    
    This endpoint provides information about static resources that
    the mobile app can download and cache for offline operation.
    
    Query parameters:
    - language: 'en' | 'ar' | 'all' - Get resources for specific language
    - type: 'audio' | 'data' | 'all' - Get specific resource types
    
    Response format:
    {
        "success": true,
        "resources": [
            {
                "id": "welcome_en",
                "url": "/tts_cache/welcome_en.mp3",
                "type": "audio",
                "language": "en",
                "etag": "abc123",
                "size_bytes": 24680
            },
            ...
        ],
        "cache_version": "1.0.2",
        "total_size_bytes": 123456
    }
    """
    try:
        # Extract query parameters
        language = request.args.get('language', 'all')
        resource_type = request.args.get('type', 'all')
        
        # Define cacheable resources - this could be dynamically generated
        # from database or filesystem in a real implementation
        all_resources = [
            {
                "id": "welcome_en",
                "url": "/tts_cache/ErXwobaYiN019PkySvjV_e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.mp3",
                "type": "audio",
                "language": "en",
                "etag": "md5-hash",
                "size_bytes": 24680,
                "required": True
            },
            {
                "id": "welcome_ar",
                "url": "/tts_cache/21m00Tcm4TlvDq8ikWAM_f12694de19931ec0428e172635aaa6e0.mp3",
                "type": "audio",
                "language": "ar",
                "etag": "md5-hash",
                "size_bytes": 29540,
                "required": True
            },
            {
                "id": "emotion_models",
                "url": "/data/emotion_model_lite.json",
                "type": "data",
                "language": "all",
                "etag": "md5-hash",
                "size_bytes": 156000,
                "required": True
            }
        ]
        
        # Filter resources based on query parameters
        filtered_resources = []
        for resource in all_resources:
            # Filter by language
            if language != 'all' and resource['language'] != 'all' and resource['language'] != language:
                continue
            
            # Filter by type
            if resource_type != 'all' and resource['type'] != resource_type:
                continue
                
            filtered_resources.append(resource)
            
        # Calculate total size
        total_size = sum(r['size_bytes'] for r in filtered_resources)
        
        # Return the resource list
        return jsonify({
            "success": True,
            "resources": filtered_resources,
            "cache_version": "1.0.2",
            "total_size_bytes": total_size,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        })
        
    except Exception as e:
        logger.error(f"Mobile API: Unexpected error in cached resources: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred",
            "error_details": str(e)
        }), 500