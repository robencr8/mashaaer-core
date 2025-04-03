import os
import json
import time
import uuid
import logging
import traceback
import twilio_api
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, session

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

def init_api(app, _db_manager, _emotion_tracker, _face_detector, 
            _tts_manager, _voice_recognition, _intent_classifier, _config,
            _context_assistant=None, _model_router=None):
    """Initialize the API blueprint with necessary dependencies"""
    global db_manager, emotion_tracker, face_detector, tts_manager, voice_recognition
    global intent_classifier, config, context_assistant, model_router
    
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
    
    # Register the blueprint with the app
    app.register_blueprint(api, url_prefix='/api')
    
    # Set up before_request handler for all API routes
    @api.before_request
    def log_api_request():
        # Log all API requests
        path = request.path
        method = request.method
        query = request.query_string.decode('utf-8')
        client_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Get or create a session ID
        session_id = _get_or_create_session_id()
        
        # Log the request
        logger.info(f"API Request: {method} {path}?{query} | Session: {session_id} | IP: {client_ip} | UA: {user_agent}")
    
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
    # ... code omitted for brevity ...
    
    return jsonify(api_docs)


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
        # Get uptime if core_launcher is available
        if 'core_launcher' in globals() and core_launcher is not None:
            status['system']['uptime'] = core_launcher.get_uptime()
            
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

# ... remaining API endpoints ...