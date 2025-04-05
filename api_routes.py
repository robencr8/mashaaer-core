import os
import json
import time
import uuid
import logging
import traceback
import twilio_api
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, session, current_app

# Setup logging
logger = logging.getLogger(__name__)

# Blueprint definition
api = Blueprint('api', __name__)

# Global references (will be set when registered with app)
db_manager = None
emotion_tracker = None
face_detector = None
tts_manager = None
voice_recognition = None
intent_classifier = None
config = None
context_assistant = None
model_router = None
profile_manager = None

def init_api(app, _db_manager, _emotion_tracker, _face_detector, 
            _tts_manager, _voice_recognition, _intent_classifier, _config,
            _context_assistant=None, _model_router=None, _profile_manager=None):
    """Initialize the API blueprint with necessary dependencies"""
    global db_manager, emotion_tracker, face_detector, tts_manager, voice_recognition
    global intent_classifier, config, context_assistant, model_router, profile_manager
    
    # Set global references
    db_manager = _db_manager
    emotion_tracker = _emotion_tracker
    face_detector = _face_detector
    tts_manager = _tts_manager
    voice_recognition = _voice_recognition
    intent_classifier = _intent_classifier
    config = _config
    context_assistant = _context_assistant
    model_router = _model_router
    profile_manager = _profile_manager
    
    # Register the blueprint with the app
    app.register_blueprint(api, url_prefix='/api')
    
    # Log the initialization
    logger.info(f"API Blueprint initialized with {len(api.deferred_functions)} routes")
    
    # Return the blueprint for reference
    return api

def _get_or_create_session_id():
    """Get the current session ID or create a new one"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['created_at'] = time.time()
        logger.info(f"Created new session: {session['session_id']}")
    return session['session_id']


@api.route('/docs', methods=['GET'])
def api_docs():
    """API documentation listing all available endpoints"""
    docs = {
        'api_version': '1.2.0',
        'title': 'Mashaaer Feelings API',
        'description': 'REST API for the Mashaaer Feelings application',
        'endpoints': {
            '/api/status': {
                'methods': ['GET'],
                'description': 'Get system status information'
            },
            '/api/analyze-emotion': {
                'methods': ['POST'],
                'description': 'Analyze text for emotional content',
                'request_body': {'text': 'string', 'context': 'array (optional)'}
            },
            '/api/cosmic-onboarding/profile': {
                'methods': ['POST'],
                'description': 'Update user profile during cosmic onboarding'
            },
            '/api/cosmic-sound': {
                'methods': ['GET'],
                'description': 'Generate sound for cosmic interface'
            },
            '/api/send-sms': {
                'methods': ['POST'],
                'description': 'Send SMS notification via Twilio'
            },
            '/api/voice/listen': {
                'methods': ['POST'],
                'description': 'Listen for voice input'
            },
            '/api/log-voice-error': {
                'methods': ['POST'],
                'description': 'Log voice input errors'
            }
        }
    }
    
    return jsonify(docs)


@api.route('/status', methods=['GET'])
def get_status():
    """Get system status information"""
    # ... code omitted for brevity ...
    
    # Prepare status response
    status = {
        'system': {
            'status': 'online',
            'timestamp': datetime.now().isoformat(),
            'session_id': _get_or_create_session_id(),
            'version': '1.2.0',
            'uptime': 'Unknown'  # Will be filled if core_launcher exists
        },
        'subsystems': {
            'database': db_manager is not None,
            'emotion_tracker': emotion_tracker is not None,
            'face_recognition': face_detector is not None,
            'tts': tts_manager is not None,
            'voice_recognition': voice_recognition is not None,
            'intent_classifier': intent_classifier is not None,
            'context_assistant': context_assistant is not None,
            'model_router': model_router is not None,
        },
        'services': {
            'twilio': {
                'enabled': True,
                'configured': twilio_api.is_twilio_configured(),
                'status': 'available' if twilio_api.is_twilio_configured() else 'unconfigured'
            },
            'openai': {
                'enabled': 'OPENAI_API_KEY' in os.environ,
                'status': 'available' if 'OPENAI_API_KEY' in os.environ else 'unconfigured'
            }
        }
    }
    
    # Add more details if available
    try:
        # Add database details if available
        if db_manager is not None:
            db_status = db_manager.get_status() if hasattr(db_manager, 'get_status') else {'status': 'unknown'}
            status['subsystems']['database_details'] = db_status
            
        # Add emotion tracker details if available
        if emotion_tracker is not None:
            emotion_status = emotion_tracker.get_status() if hasattr(emotion_tracker, 'get_status') else {'status': 'unknown'}
            status['subsystems']['emotion_tracker_details'] = emotion_status
    except Exception as e:
        # Log but don't fail if we can't get detailed status
        logger.warning(f"Error getting detailed status: {str(e)}")
    
    return jsonify(status)

# ... other API endpoints omitted for brevity ...

@api.route('/sms', methods=['POST'])
def send_sms():
    """Send SMS notification via Twilio with enhanced UAE number support"""
    try:
        # Parse request data (support both JSON and form data)
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
        
        # Extract parameters
        to_number = data.get('to_number') or data.get('to') or data.get('number')
        message = data.get('message') or data.get('text') or data.get('content') or ''
        
        if not to_number:
            return jsonify({
                'success': False,
                'error': 'Recipient phone number is required',
                'required_fields': ['to_number', 'message']
            }), 400
            
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message content is required',
                'required_fields': ['to_number', 'message']
            }), 400
        
        # Check if Twilio is available
        if not twilio_api.is_twilio_configured():
            import os
            missing_env_vars = []
            if not os.environ.get("TWILIO_ACCOUNT_SID"):
                missing_env_vars.append("TWILIO_ACCOUNT_SID")
            if not os.environ.get("TWILIO_AUTH_TOKEN"):
                missing_env_vars.append("TWILIO_AUTH_TOKEN")
            if not os.environ.get("TWILIO_PHONE_NUMBER"):
                missing_env_vars.append("TWILIO_PHONE_NUMBER")
                
            return jsonify({
                'success': False,
                'error': 'Twilio service is not available.',
                'missing_credentials': missing_env_vars,
                'solution': 'Please set the required Twilio environment variables and restart the server.'
            }), 503
            
        # Save original number for reference and logging
        original_number = to_number
        
        # Special handling for UAE numbers to help with formatting
        if to_number:
            if to_number.startswith('05') and len(to_number) == 10:  # UAE mobile format 05xxxxxxxx
                to_number = '+971' + to_number[1:]
            elif to_number.startswith('5') and len(to_number) == 9:  # UAE mobile without leading 0
                to_number = '+971' + to_number
            elif to_number.startswith('971') and not to_number.startswith('+'):
                to_number = '+' + to_number
            elif to_number.startswith('00971'):
                to_number = '+971' + to_number[5:]
            elif to_number.startswith('0'):
                # Generic handling for numbers starting with 0, assume UAE
                to_number = '+971' + to_number
            elif to_number.startswith('00'):
                # Handle double-zero prefixed international format (instead of +)
                to_number = '+' + to_number[2:]
            else:
                # Generic fallback - add + prefix
                to_number = '+' + to_number
                
            logger.info(f"API: Reformatted number from '{original_number}' to '{to_number}'")
        
        # Log the attempt with sanitized number for privacy
        sanitized_number = to_number[:6] + "XXXX" if len(to_number) > 6 else "XXXXXX"
        logger.info(f"API: Attempting to send SMS to {sanitized_number}")
            
        # Send the message
        result = twilio_api.send_sms(to_number, message)
        
        # Handle None result (in case of API failure)
        if result is None:
            result = {'success': False, 'error': 'Twilio API call failed'}
            
        if result.get('success', False):
            # Log success but with sanitized number for privacy
            logger.info(f"API: Successfully sent SMS to {sanitized_number}")
            
            # Create a response with detailed information
            from datetime import datetime
            return jsonify({
                'success': True,
                'message': f'SMS sent successfully',
                'details': {
                    'sid': result.get('sid', ''),
                    'to': sanitized_number,
                    'from': result.get('from', ''),
                    'segments': result.get('segments', 1),
                    'length': result.get('length', len(message)),
                    'timestamp': datetime.now().isoformat(),
                    'message_preview': message[:20] + '...' if len(message) > 20 else message
                }
            })
        else:
            # Extract error details from the result
            error_message = result.get('error', 'Failed to send SMS')
            solution = result.get('solution', '')
            details = result.get('details', '')
            error_type = result.get('error_type', 'unknown_error')
            
            # Log the error
            logger.error(f"API: SMS sending failed: {error_message}")
            if details:
                logger.error(f"API: SMS error details: {details}")
            
            # Create error response
            response = {
                'success': False,
                'error': error_message,
                'error_type': error_type
            }
            
            # Add optional fields if available
            if solution:
                response['solution'] = solution
                logger.info(f"API: SMS error solution: {solution}")
            if details:
                response['details'] = details
            
            # Add UAE-specific help if available
            if 'uae_number_info' in result:
                response['uae_number_info'] = result['uae_number_info']
            elif '+971' in to_number or '971' in to_number or '05' in original_number:
                # Add UAE format helpers even if not provided by the handler
                response['uae_number_info'] = {
                    'examples': ['+971522233989', '+971501234567'],
                    'format_info': 'UAE mobile numbers start with "5" after the country code',
                    'local_format': 'Local format: 05XXXXXXXX',
                    'international_format': 'International format: +971XXXXXXXX' 
                }
                
            # Get appropriate status code
            status_code = 400 if error_type in ['invalid_number_format', 'trial_account_restriction'] else 500
                
            return jsonify(response), status_code
                
    except Exception as e:
        error_message = str(e)
        logger.error(f"API: Exception in send_sms endpoint: {error_message}")
        import traceback
        
        return jsonify({
            'success': False,
            'error': 'Internal server error processing SMS request',
            'error_details': error_message
        }), 500


@api.route('/log-voice-error', methods=['POST', 'GET'])
def log_voice_error():
    """Log voice input errors from the client side with enhanced error categorization
    
    Request body:
    {
        "step": "name",  // The step or context where the error occurred
        "error_type": "network",  // Error classification (network, permission, timeout, etc.)
        "error_message": "Failed to connect",  // The raw error message
        "language": "ar"  // The language being used during the error
    }
    """
    try:
        # Parse request data
        if request.method == 'GET':
            data = request.args.to_dict()
        else:  # POST
            if request.is_json:
                data = request.json
            else:
                data = request.form.to_dict()
        
        # Extract parameters
        step = data.get('step', 'unknown')
        error_type = data.get('error_type', 'unknown')
        error_message = data.get('error_message', 'No error message provided')
        language = data.get('language', 'en')
        
        # Get session and device info
        session_id = _get_or_create_session_id()
        device_info = json.dumps({
            'user_agent': request.user_agent.string,
            'platform': request.user_agent.platform,
            'browser': request.user_agent.browser
        }) if request.user_agent else None
        
        logger.warning(f"API: Client-side voice error in step '{step}': {error_type} - {error_message}")
        
        # Check if database manager is available
        if db_manager is None:
            logger.error("API: Cannot log voice error - database manager not available")
            return jsonify({
                'success': False,
                'error': 'Database service not available'
            }), 503
        
        # Log the error to the database
        db_manager.log_voice_recognition(
            session_id=session_id,
            language=language,
            error_type=f"{error_type}: {error_message}",
            raw_input=None,
            recognized_text=None,
            success=False,
            device_info=device_info,
            context=step
        )
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Voice error logged successfully'
        })
        
    except Exception as e:
        logger.error(f"API: Exception in log_voice_error endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': 'Internal server error while logging voice error',
            'error_details': str(e)
        }), 500

@api.route('/cosmic-onboarding-profile', methods=['POST'])
def cosmic_onboarding_profile():
    """Update user profile during cosmic onboarding experience
    
    This endpoint should be accessed via POST since it creates/updates profile data.
    """
    try:
        # Parse request data from POST
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()

        # Get basic profile data
        full_name = data.get('full_name')
        nickname = data.get('nickname')
        language = data.get('language_preference', 'ar')
        onboarding_complete = data.get('onboarding_complete', False)

        logger.info(f"Cosmic onboarding profile update: name={full_name}, nickname={nickname}, language={language}, onboarding_complete={onboarding_complete}")

        # Store in session
        from flask import session
        session['language'] = language
        session['nickname'] = nickname
        session['full_name'] = full_name

        # Update the profile in database
        profile_data = {
            'full_name': full_name,
            'nickname': nickname,
            'language': language
        }

        # Update the user profile
        if profile_manager is None:
            logger.error("Cannot update profile - profile_manager not initialized")
            return jsonify({
                'success': False,
                'error': 'Profile manager not available'
            }), 503
        profile_manager.update_profile(profile_data)

        # Save onboarding_complete flag in database
        if onboarding_complete:
            logger.info("Setting onboarding_complete flag to true in database")
            db_manager.set_setting('onboarding_complete', 'true')

        # Get appropriate voice for selected language
        tts_voice = profile_manager.get_tts_voice_for_language(language)

        # Use nickname or first name if nickname is empty
        user_name = nickname
        if not user_name and full_name:
            user_name = full_name.split(' ')[0]

        # Create welcome message based on user's language
        if language == 'ar':
            welcome_msg = f"مرحبًا بك يا {user_name} في مشاعر. أنا سعيد بوجودك معنا."
        else:
            welcome_msg = f"Welcome {user_name} to Mashaaer Feelings. I'm glad to have you with us."

        # Speak welcome message
        try:
            audio_path = tts_manager.speak(welcome_msg, tts_voice, language, profile_manager)
            logger.info(f"Welcome message TTS generated at: {audio_path}")
        except Exception as e:
            logger.error(f"Error speaking welcome message: {str(e)}")
            import traceback
            logger.error(f"TTS error traceback: {traceback.format_exc()}")
            audio_path = None

        # Check TTS provider status
        elevenlabs_available = hasattr(tts_manager, 'use_elevenlabs') and tts_manager.use_elevenlabs
        gtts_available = hasattr(tts_manager, 'use_gtts') and tts_manager.use_gtts

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'welcome_message': welcome_msg,
            'audio_path': audio_path,
            'tts_status': {
                'elevenlabs': elevenlabs_available,
                'gtts': gtts_available,
                'provider': config.TTS_PROVIDER
            }
        })

    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        import traceback
        logger.error(f"Profile update error traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api.route('/play-cosmic-sound', methods=['GET'])
def play_cosmic_sound():
    """Generate and return a sound for the cosmic interface based on the type and language
    
    This endpoint should be accessed via GET since it retrieves sound data without 
    making server-side changes.
    """
    # Import os here to ensure it's available in the function scope
    import os
    
    try:
        # Parse request data from GET parameters
        sound_type = request.args.get('sound_type', 'welcome')
        language = request.args.get('language', 'en')
        
        # Log the request
        logger.info(f"API: Cosmic sound request: {sound_type} in {language}")
        
        # Validate sound type
        valid_sound_types = ['welcome', 'greeting', 'click', 'hover', 'listen_start', 'listen_stop']
        if sound_type not in valid_sound_types:
            return jsonify({
                'success': False,
                'error': f'Invalid sound type. Valid options are: {", ".join(valid_sound_types)}'
            }), 400
        
        # Check if TTS manager is available for voice sounds
        if sound_type in ['welcome', 'greeting'] and tts_manager is None:
            return jsonify({
                'success': False,
                'error': 'Text-to-speech service not available'
            }), 503
        
        # Handle welcome message based on language
        if sound_type == 'welcome':
            welcome_text = "Welcome to Mashaaer, Create the future, I hear you" if language == 'en' else "اصنع المستقبل، أنا أسمعك"
            
            # Use TTS to generate the audio
            try:
                # Generate TTS audio
                voice = "arabic" if language == "ar" else "default"
                logger.debug(f"Generating welcome TTS in {language} with voice '{voice}', text: '{welcome_text}'")
                
                if tts_manager is not None:
                    # Check if TTS is properly initialized
                    if hasattr(tts_manager, 'use_elevenlabs'):
                        logger.debug(f"TTS Manager status - ElevenLabs available: {tts_manager.use_elevenlabs}, Google TTS available: {tts_manager.use_gtts}")
                    
                    # Check if ElevenLabs is initialized properly with the correct API key
                    if hasattr(tts_manager, 'elevenlabs') and tts_manager.elevenlabs:
                        logger.debug(f"ElevenLabs API key status - Length: {len(tts_manager.elevenlabs.api_key) if tts_manager.elevenlabs.api_key else 'No key'}")
                        
                    # Re-initialize TTS if needed
                    if not tts_manager.use_elevenlabs and not tts_manager.use_gtts:
                        logger.info("Re-initializing TTS manager to ensure providers are available")
                        tts_manager.initialize()
                    
                    # Generate the TTS audio
                    audio_path = tts_manager.generate_tts(welcome_text, voice=voice, language=language)
                    logger.debug(f"TTS generated audio path: {audio_path}")
                else:
                    logger.error("TTS Manager is not available")
                    return jsonify({'success': False, 'error': 'TTS service not available'}), 503
                
                if audio_path:
                    # Check if the generated audio exists 
                    if os.path.exists(audio_path):
                        logger.debug(f"Audio file exists: {audio_path} - Size: {os.path.getsize(audio_path)} bytes")
                    else:
                        logger.warning(f"Audio file does not exist at path: {audio_path}")
                    
                    # Return the audio file path
                    return jsonify({
                        'success': True,
                        'sound_path': audio_path
                    })
                else:
                    logger.error("TTS returned None for audio path")
                    return jsonify({
                        'success': False,
                        'error': 'Failed to generate welcome audio'
                    }), 500
            except Exception as e:
                logger.error(f"Error generating welcome TTS: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Return a fallback path if available
                fallback_path = os.path.join("tts_cache", "error.mp3")
                if os.path.exists(fallback_path):
                    return jsonify({
                        'success': True,
                        'sound_path': fallback_path,
                        'warning': 'Using fallback audio due to TTS error'
                    })
                
                return jsonify({
                    'success': False,
                    'error': f'TTS generation error: {str(e)}'
                }), 500
        
        # Handle greeting message
        elif sound_type == 'greeting':
            greeting_text = "I'm listening to you" if language == 'en' else "أنا أستمع إليك"
            
            # Generate greeting audio
            try:
                voice = "arabic" if language == "ar" else "default"
                if tts_manager is not None:
                    audio_path = tts_manager.generate_tts(greeting_text, voice=voice, language=language)
                else:
                    logger.error("TTS Manager is not available")
                    return jsonify({'success': False, 'error': 'TTS service not available'}), 503
                
                if audio_path:
                    return jsonify({
                        'success': True,
                        'sound_path': audio_path
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to generate greeting audio'
                    }), 500
            except Exception as e:
                logger.error(f"Error generating greeting TTS: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'TTS generation error: {str(e)}'
                }), 500
        
        # For non-voice sounds, just return the path to the static sound file
        else:
            sound_file = f"{sound_type}.mp3"
            sound_path = f"/static/audio/{sound_file}"
            
            # Check if the file exists
            import os
            full_path = os.path.join('static', 'audio', sound_file)
            if not os.path.exists(full_path):
                logger.warning(f"API: Cosmic sound file not found: {full_path}")
                
                # Return fallback sound if available
                return jsonify({
                    'success': True,
                    'sound_path': '/static/audio/click.mp3',
                    'warning': f'Requested sound {sound_file} not found, using fallback'
                })
            
            return jsonify({
                'success': True,
                'sound_path': sound_path
            })
    
    except Exception as e:
        logger.error(f"API: Error in play_cosmic_sound: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@api.route('/analyze-emotion', methods=['POST'])
def analyze_emotion():
    """Analyze text for emotional content and return the detected emotion
    
    This endpoint should be accessed via POST since it performs analysis on 
    the provided text data and may store results in the cache.
    """
    try:
        # Parse request data from POST
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
        
        text = data.get('text', '')
        language = data.get('language', 'en')
        return_details = data.get('return_details', False)
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text is required for emotion analysis'
            }), 400
        
        # Check if emotion tracker is available
        if emotion_tracker is None:
            return jsonify({
                'success': False,
                'error': 'Emotion analysis service not available'
            }), 503
        
        # Log the request (without the full text for privacy)
        text_preview = text[:20] + '...' if len(text) > 20 else text
        logger.info(f"API: Emotion analysis request: '{text_preview}' in {language}")
        
        # Analyze emotion with proper return_details parameter
        try:
            emotion_result = emotion_tracker.analyze_text(text, context=None, return_details=return_details)
            
            # Handle string or dict result types
            if isinstance(emotion_result, str):
                dominant_emotion = emotion_result
                confidence = 0.8
                all_emotions = {dominant_emotion: 1.0, "neutral": 0.2}
            else:
                dominant_emotion = emotion_result.get('primary_emotion', 'neutral')
                confidence = emotion_result.get('confidence', 0.8)
                all_emotions = emotion_result.get('emotions', {})
            
            # Map complex emotions to simpler ones for the cosmic UI
            simple_emotion_map = {
                # Happy group
                'happy': 'happy',
                'joy': 'happy',
                'happiness': 'happy',
                'excitement': 'happy',
                'optimism': 'happy',
                'grateful': 'happy',
                'hopeful': 'happy',
                'proud': 'happy',
                'amused': 'happy',
                'satisfied': 'happy',
                
                # Sad group
                'sad': 'sad',
                'sadness': 'sad',
                'grief': 'sad',
                'disappointment': 'sad',
                'lonely': 'sad',
                'tired': 'sad',
                
                # Angry group
                'angry': 'angry',
                'anger': 'angry',
                'annoyance': 'angry',
                'frustration': 'angry',
                'disgusted': 'angry',
                
                # Neutral group
                'neutral': 'neutral',
                'calm': 'neutral',
                'contemplative': 'neutral',
                
                # Surprised group (maps to neutral in cosmic UI)
                'surprised': 'neutral',
                
                # Interested/confused group (maps to neutral in cosmic UI)
                'interested': 'neutral',
                'confused': 'neutral',
                'inspired': 'neutral',
                
                # Fear group (maps to sad in cosmic UI)
                'fearful': 'sad',
                'anxious': 'sad',
                'embarrassed': 'sad',
                
                # Boredom (maps to neutral in cosmic UI)
                'bored': 'neutral'
            }
            
            # Convert to simple emotion for UI
            if isinstance(dominant_emotion, str):
                logger.debug(f"API: Looking up simple emotion for {dominant_emotion.lower()}")
                simple_emotion = simple_emotion_map.get(dominant_emotion.lower(), 'neutral')
                logger.debug(f"API: Mapped '{dominant_emotion.lower()}' to '{simple_emotion}'")
            else:
                simple_emotion = 'neutral'
                logger.debug(f"API: Dominant emotion is not a string: {type(dominant_emotion)}")
            
            return jsonify({
                'success': True,
                'emotion': simple_emotion,
                'detailed_emotion': dominant_emotion,
                'confidence': confidence,
                'all_emotions': all_emotions
            })
            
        except Exception as e:
            logger.error(f"Error analyzing emotion: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Emotion analysis error: {str(e)}'
            }), 500
    
    except Exception as e:
        logger.error(f"API: Error in analyze_emotion: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@api.route('/sms-alert', methods=['POST'])
def send_sms_alert():
    """Send SMS notification with pre-formatted alert message with enhanced error handling"""
    try:
        # Support both JSON and form data for flexibility
        if request.is_json:
            data = request.json
        else:
            data = request.form.to_dict()
        
        # Support multiple parameter names for better API compatibility
        to_number = data.get('to_number') or data.get('phone_number') or data.get('to') or data.get('number')
        alert_type = data.get('alert_type') or data.get('type') or data.get('notification_type') or 'default'
        
        # Support either direct alert_data object or individual parameters
        alert_data = data.get('alert_data', {})
        
        # If no alert_data provided but individual parameters are, build alert_data dynamically
        if not alert_data and isinstance(data, dict):
            # Filter out known non-data parameters
            excluded_keys = ['to_number', 'phone_number', 'to', 'number', 'alert_type', 'type', 'notification_type', 'alert_data']
            # Add all remaining parameters to alert_data
            alert_data = {k: v for k, v in data.items() if k not in excluded_keys}
        
        # Special handling for owner shortcuts
        if to_number and to_number.lower() in ["roben", "owner", "admin", "me", "creator"]:
            import os
            owner_number = os.environ.get("OWNER_PHONE_NUMBER")
            if owner_number:
                logger.info(f"API: Using owner shortcut: Converting '{to_number}' to owner's number")
                to_number = owner_number
            else:
                logger.warning("API: Owner shortcut used but OWNER_PHONE_NUMBER not set")
                
        # Special handling for Roben's number in any format
        roben_patterns = ["522233989", "0522233989", "971522233989", "00971522233989", "+971522233989"]
        if to_number and any(pattern in to_number for pattern in roben_patterns):
            logger.info("API: Detected Roben's number, using standardized format")
            to_number = "+971522233989"
        
        if not to_number:
            return jsonify({
                'success': False,
                'error': 'Recipient phone number is required',
                'required_fields': {
                    'to_number': 'Recipient phone number in E.164 format (+971XXXXXXXXX)'
                },
                'help': {
                    'uae_format': 'For UAE numbers, use +971XXXXXXXXX or 05XXXXXXXX format',
                    'shortcuts': 'You can use "owner", "roben", "admin", or "me" to send to the owner'
                }
            }), 400
            
        # Check if Twilio is available
        if not twilio_api.is_twilio_configured():
            import os
            missing_env_vars = []
            if not os.environ.get("TWILIO_ACCOUNT_SID"):
                missing_env_vars.append("TWILIO_ACCOUNT_SID")
            if not os.environ.get("TWILIO_AUTH_TOKEN"):
                missing_env_vars.append("TWILIO_AUTH_TOKEN")
            if not os.environ.get("TWILIO_PHONE_NUMBER"):
                missing_env_vars.append("TWILIO_PHONE_NUMBER")
                
            return jsonify({
                'success': False,
                'error': 'Twilio service is not available.',
                'missing_credentials': missing_env_vars,
                'solution': 'Please set the required Twilio environment variables and restart the server.'
            }), 503
            
        # Save original number for reference and logging
        original_number = to_number
        
        # Special handling for UAE numbers
        if to_number:
            if to_number.startswith('05') and len(to_number) == 10:  # UAE mobile format 05xxxxxxxx
                to_number = '+971' + to_number[1:]
            elif to_number.startswith('5') and len(to_number) == 9:  # UAE mobile without leading 0
                to_number = '+971' + to_number
            elif to_number.startswith('971') and not to_number.startswith('+'):
                to_number = '+' + to_number
            elif to_number.startswith('00971'):
                to_number = '+971' + to_number[5:]
                
        # Validate required alert parameters
        if alert_type == 'default' and not alert_data.get('message'):
            # Need at least a message for default alerts
            return jsonify({
                'success': False,
                'error': 'Message content is required for default alerts',
                'required_fields': {
                    'message': 'The message content to send'
                }
            }), 400
            
        # Prepare title and message based on alert type
        title = ''
        message = ''
        
        if alert_type == 'default':
            title = alert_data.get('title', 'Notification')
            message = alert_data.get('message', '')
        elif alert_type == 'emotion':
            # Emotion alert format
            emotion = alert_data.get('emotion', 'unknown')
            confidence = alert_data.get('confidence', 0)
            text = alert_data.get('text', '')
            user = alert_data.get('user', 'User')
            
            title = f"Emotion Alert: {emotion.capitalize()}"
            message = f"{user} is expressing {emotion} emotion with {confidence:.0%} confidence.\n\nMessage: \"{text}\""
        elif alert_type == 'face':
            # Face recognition alert format
            name = alert_data.get('name', 'Unknown person')
            confidence = alert_data.get('confidence', 0)
            location = alert_data.get('location', 'Unknown location')
            timestamp = alert_data.get('timestamp', datetime.now().strftime("%H:%M:%S"))
            
            title = f"Face Recognition: {name}"
            message = f"Detected {name} at {location} at {timestamp} with {confidence:.0%} confidence."
        elif alert_type == 'system':
            # System alert format
            component = alert_data.get('component', 'System')
            status = alert_data.get('status', 'unknown')
            details = alert_data.get('details', '')
            
            title = f"System Alert: {component}"
            message = f"Component {component} status changed to {status}.\n\nDetails: {details}"
        else:
            # Generic alert - use raw data
            title = alert_data.get('title', 'Alert')
            message = alert_data.get('message', str(alert_data)) if alert_data else 'No message content'
            
        # Log the alert (with privacy measures)
        sanitized_number = to_number[:6] + "XXXX" if len(to_number) > 6 else "XXXXXX"
        logger.info(f"API: Sending {alert_type} alert to {sanitized_number}: {title}")
        
        # Send the notification
        result = twilio_api.send_notification(to_number, title, message, alert_type)
        
        # Handle None result (in case of API failure)
        if result is None:
            result = {'success': False, 'error': 'Twilio notification API call failed'}
            
        if result.get('success', False):
            # Log success
            logger.info(f"API: Successfully sent {alert_type} alert to {sanitized_number}")
            
            return jsonify({
                'success': True,
                'message': f'{alert_type.capitalize()} alert sent successfully',
                'details': {
                    'to': sanitized_number,
                    'title': title,
                    'type': alert_type,
                    'timestamp': datetime.now().isoformat()
                }
            })
        else:
            # Handle error similar to the send_sms endpoint
            error_message = result.get('error', f'Failed to send {alert_type} alert')
            logger.error(f"API: Alert sending failed: {error_message}")
            
            return jsonify({
                'success': False,
                'error': error_message,
                'alert_type': alert_type,
                'title': title
            }), 500
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"API: Exception in send_sms_alert endpoint: {error_message}")
        
        return jsonify({
            'success': False,
            'error': 'Internal server error processing alert request',
            'error_details': error_message
        }), 500

@api.route('/listen-for-voice', methods=['POST'])
def listen_for_voice():
    """
    Listen for voice input and convert to text
    
    This endpoint supports voice recognition for the onboarding wizard
    and other interactive components of the Mashaaer interface.
    
    Uses POST method as it processes audio data and stores voice recognition results.
    """
    try:
        logger.info("API: Voice recognition request received")
        logger.info(f"API: Request method: {request.method}")
        logger.info(f"API: Request content type: {request.content_type}")
        logger.info(f"API: Request headers: {dict(request.headers)}")
        
        # Add CORS headers for this specific endpoint
        response_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, X-Requested-With, Accept, Origin, Authorization',
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Expose-Headers': 'Content-Length, Content-Type, Date',
            'Cross-Origin-Resource-Policy': 'cross-origin'
        }
        
        # Check if voice recognition module is available
        if not voice_recognition:
            logger.warning("API: Voice recognition module not initialized")
            return jsonify({
                'success': False,
                'error': 'Voice recognition not available',
                'text': '',
                'debug': 'Voice recognition module not initialized'
            }), 400, response_headers
        
        # Get the current onboarding step from query params or form data
        step = request.args.get('step') or request.form.get('step') or 'name'
        logger.info(f"API: Voice recognition step: {step}")
        
        # Check if we're running in test/demo mode where we use sample responses
        import os
        is_test_mode = os.environ.get('USE_SAMPLE_VOICE_RESPONSES', 'true').lower() == 'true'
        logger.info(f"API: Voice recognition running in test mode: {is_test_mode}")
        
        if is_test_mode:
            # Sample responses based on step context
            sample_responses = {
                'name': ['محمد', 'فاطمة', 'Ahmed', 'Sarah'],
                'nickname': ['محمد', 'مها', 'Ahmed', 'Sara'],
                'terms-agree': ['نعم', 'أوافق', 'Yes', 'I agree'],
                'full-name': ['محمد علي', 'فاطمة احمد', 'Ahmed Ali', 'Sarah Hassan'],
                'language': ['العربية', 'English'],
                'voice-style': ['default', 'formal', 'casual']
            }
            
            import random
            recognized_text = random.choice(sample_responses.get(step, ['نعم']))
            confidence = 0.95
            logger.info(f"API: Voice recognition test mode, returning sample text: {recognized_text}")
        else:
            try:
                # Get the preferred language for voice recognition
                language = request.args.get('language') or request.form.get('language')
                
                # Default to Arabic if not specified
                if not language:
                    # Try to get from session or default to Arabic
                    language = session.get('language') or os.environ.get('DEFAULT_LANGUAGE', 'ar')
                
                # Map language code to recognition language
                recognition_language = 'ar-EG' if language == 'ar' else 'en-US'
                logger.info(f"API: Voice recognition language: {recognition_language}")
                
                # Perform actual voice recognition
                result = voice_recognition.recognize_speech(language=recognition_language)
                
                if not result['success']:
                    logger.warning(f"API: Voice recognition failed: {result.get('error', 'Unknown error')}")
                    
                    # Log the voice recognition failure
                    session_id = _get_or_create_session_id()
                    language = request.args.get('language') or request.form.get('language') or session.get('language', 'ar')
                    device_info = json.dumps({
                        'user_agent': request.user_agent.string,
                        'platform': request.user_agent.platform,
                        'browser': request.user_agent.browser
                    }) if request.user_agent else None
                    
                    # Log failure to database with error details
                    db_manager.log_voice_recognition(
                        session_id=session_id,
                        language=language,
                        error_type=result.get('error', 'Unknown recognition error'),
                        raw_input=result.get('raw_data', None),
                        recognized_text=None,
                        success=False,
                        device_info=device_info,
                        context=step
                    )
                    
                    return jsonify({
                        'success': False,
                        'error': 'Voice recognition failed',
                        'error_details': result.get('error', 'Unknown recognition error'),
                        'text': '',
                        'step': step,
                        'debug': f"Failed to recognize speech with error: {result.get('error')}"
                    }), 400, response_headers
                
                recognized_text = result['text']
                confidence = result.get('confidence', 0.5)
                logger.info(f"API: Voice recognition successful, returning text: {recognized_text} with confidence {confidence}")
            except Exception as rec_error:
                logger.error(f"API: Error during speech recognition: {str(rec_error)}")
                logger.error(traceback.format_exc())
                
                # Log the exception to the database
                session_id = _get_or_create_session_id()
                language = request.args.get('language') or request.form.get('language') or session.get('language', 'ar')
                device_info = json.dumps({
                    'user_agent': request.user_agent.string,
                    'platform': request.user_agent.platform,
                    'browser': request.user_agent.browser
                }) if request.user_agent else None
                
                # Log exception to database
                db_manager.log_voice_recognition(
                    session_id=session_id,
                    language=language,
                    error_type=f"exception:{type(rec_error).__name__}",
                    raw_input=None,
                    recognized_text=None,
                    success=False,
                    device_info=device_info,
                    context=f"{step}:exception"
                )
                
                return jsonify({
                    'success': False,
                    'error': 'Speech recognition error',
                    'error_details': str(rec_error),
                    'text': '',
                    'step': step,
                    'debug': f"Exception during recognition: {str(rec_error)}"
                }), 500, response_headers
        
        # Log the voice recognition with detailed error tracking
        session_id = _get_or_create_session_id()
        language = request.args.get('language') or request.form.get('language') or session.get('language', 'ar')
        device_info = json.dumps({
            'user_agent': request.user_agent.string,
            'platform': request.user_agent.platform,
            'browser': request.user_agent.browser
        }) if request.user_agent else None
        
        # Log voice recognition attempt to database
        db_manager.log_voice_recognition(
            session_id=session_id,
            language=language,
            error_type=None,  # No error if we reached this point
            raw_input=None,   # We don't store the raw audio
            recognized_text=recognized_text,
            success=True,
            device_info=device_info,
            context=step      # The onboarding step as context
        )
        
        return jsonify({
            'success': True,
            'text': recognized_text,
            'confidence': confidence,
            'step': step
        }), 200, response_headers
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"API: Exception in voice recognition endpoint: {error_message}")
        logger.error(traceback.format_exc())
        
        # Log the global exception to the database
        try:
            session_id = _get_or_create_session_id()
            step = request.args.get('step') or request.form.get('step') or 'unknown'
            language = request.args.get('language') or request.form.get('language') or session.get('language', 'ar')
            device_info = json.dumps({
                'user_agent': request.user_agent.string if request.user_agent else 'unknown',
                'platform': request.user_agent.platform if request.user_agent else 'unknown',
                'browser': request.user_agent.browser if request.user_agent else 'unknown'
            })
            
            # Log global exception to database
            db_manager.log_voice_recognition(
                session_id=session_id,
                language=language,
                error_type=f"global_exception:{type(e).__name__}",
                raw_input=None,
                recognized_text=None,
                success=False,
                device_info=device_info,
                context=f"{step}:global_exception"
            )
        except Exception as log_error:
            # If even logging fails, just log to console - don't let it disrupt the error response
            logger.error(f"Failed to log voice recognition error: {str(log_error)}")
        
        return jsonify({
            'success': False,
            'error': 'Voice recognition error',
            'error_details': error_message,
            'text': '',
            'step': request.args.get('step') or request.form.get('step') or 'unknown',
            'debug': f"General exception: {error_message}"
        }), 500, response_headers

# ... remaining API endpoints ...