"""
Main Flask Application for Mashaaer Feelings
This is the entry point for the Replit Gunicorn server.
"""
from flask import Flask, jsonify, send_from_directory, render_template_string, render_template, request
from flask_cors import CORS
import os
import logging
import sys
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add project root to path to enable imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import Config
from database.db_manager import DatabaseManager
from emotion_tracker import EmotionTracker

# Initialize core components
config = Config()
db_manager = DatabaseManager(config)
db_manager.initialize_db()
emotion_tracker = EmotionTracker(db_manager)

# Initialize face detection if enabled
face_detector = None
try:
    if config.get('FACE_DETECTION_ENABLED', True):
        from vision.face_detector import FaceDetector
        face_detector = FaceDetector(config)
except ImportError:
    logger.warning("Face detection module could not be imported")
except Exception as e:
    logger.warning(f"Error initializing face detection: {str(e)}")

# Initialize TTS manager
tts_manager = None
try:
    from tts.tts_manager import TTSManager
    tts_manager = TTSManager(config)
    tts_manager.initialize()
except ImportError:
    logger.warning("TTS module could not be imported")
except Exception as e:
    logger.warning(f"Error initializing TTS: {str(e)}")

# Initialize voice recognition
voice_recognition = None
try:
    from voice.recognition import VoiceRecognition
    voice_recognition = VoiceRecognition(config)
    voice_recognition.initialize()
except ImportError:
    logger.warning("Voice recognition module could not be imported")
except Exception as e:
    logger.warning(f"Error initializing voice recognition: {str(e)}")

# Initialize intent classifier
intent_classifier = None
try:
    from intent_classifier import IntentClassifier
    intent_classifier = IntentClassifier(config)
except ImportError:
    logger.warning("Intent classifier module could not be imported")
except Exception as e:
    logger.warning(f"Error initializing intent classifier: {str(e)}")

# Create the Flask application instance
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Configure CORS with all origins allowed
CORS(app, origins="*", supports_credentials=False)

# Set a secret key for session management
app.secret_key = os.environ.get("SESSION_SECRET", "mashaaer_development_key")

# Import and register API routes
try:
    from api_routes import init_api
    from app_routes import register_routes  # Import function to register additional routes
    
    # Initialize API routes
    api_blueprint = init_api(app, db_manager, emotion_tracker, face_detector, 
                          tts_manager, voice_recognition, intent_classifier, config)
    
    # Register additional routes from app_routes.py
    register_routes(app)
    
    logger.info(f"API routes registered successfully")
except ImportError as e:
    logger.error(f"Could not import API routes: {str(e)}")
except Exception as e:
    logger.error(f"Error registering API routes: {str(e)}")

@app.route('/')
def index():
    logger.debug("Serving index page")
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Mashaaer Feelings</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
                color: #333;
                background-color: #f8f8f8;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            .card {
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .status {
                display: inline-block;
                background: #2ecc71;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            a {
                color: #3498db;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Mashaaer Feelings Application</h1>
            <p>Status: <span class="status">Running</span></p>
            <p>The server is up and responding to requests.</p>
            <p>Check the <a href="/health">/health</a> endpoint for detailed status information.</p>
            <p>Server time: <script>document.write(new Date().toLocaleString());</script></p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    logger.debug("Health check requested")
    return jsonify({
        "status": "ok",
        "message": "Server is healthy",
        "version": "1.0.0",
        "timestamp": str(os.popen('date -u').read().strip())
    })

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                              'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/replit-test')
def replit_test():
    logger.debug("Serving replit test page")
    return send_from_directory('static', 'replit_test.html')

@app.route('/simple-test')
def simple_test():
    logger.debug("Serving simple test page (inline HTML)")
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Test</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: Arial, sans-serif;
                margin: 40px;
                line-height: 1.6;
            }
            h1 { color: #0066cc; }
            .box {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 20px;
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <div class="box">
            <h1>Simple Test Page</h1>
            <p>This is a simple test page with inline HTML.</p>
            <p>Current time: <span id="time"></span></p>
        </div>
        <script>
            document.getElementById('time').textContent = new Date().toLocaleString();
        </script>
    </body>
    </html>
    """
    return html

@app.route('/cosmic')
def cosmic_splash():
    logger.debug("Serving interactive cosmic splash page")
    return render_template('interactive_cosmic_splash.html')

@app.route('/ultra-simple')
def ultra_simple():
    logger.debug("Serving ultra simple test page (static file)")
    return send_from_directory('static', 'ultra_simple.html')

@app.route('/emotion-test')
def emotion_test():
    logger.debug("Serving emotion test page")
    return send_from_directory('static', 'emotion_test.html')

@app.route('/api/analyze-emotion', methods=['POST'])
def analyze_emotion():
    """
    Analyze text for emotional content and return the detected emotion
    
    Request body:
    {
        "text": "Text to analyze for emotions",
        "context": ["Optional previous messages for context"],
        "return_details": true/false (optional, default: true),
        "source": "text" or "voice" (optional, indicates the source of the text)
    }
    
    Returns:
    {
        "success": true/false,
        "primary_emotion": "emotion_name",
        "emotion_data": {
            "emotions": {
                "happy": 0.7,
                "surprised": 0.2,
                ...
            },
            "intensity": 0.8
        }
    }
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: text"
            }), 400
            
        text = data.get('text', '')
        context = data.get('context', [])
        return_details = data.get('return_details', True)
        source = data.get('source', 'text')  # 'text' or 'voice'
        
        logger.debug(f"Analyzing emotion for: '{text[:50]}...' (length: {len(text)}, source: {source})")
        
        # Get emotion analysis from the emotion tracker
        result = emotion_tracker.analyze_text(text, context, return_details=True)
        
        # Prepare the response
        response = {
            "success": True,
            "primary_emotion": result.get("primary_emotion", "neutral"),
            "source": source
        }
        
        # Include detailed emotion data if requested
        if return_details:
            response["emotion_data"] = {
                "emotions": result.get("emotions", {}),
                "intensity": result.get("intensity", 0.5)
            }
        
        # Log the emotion with source information
        try:
            from flask import session
            import uuid
            
            session_id = session.get('session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                session['session_id'] = session_id
                
            # Log the emotion with the source type
            if hasattr(emotion_tracker, 'log_emotion'):
                emotion_tracker.log_emotion(
                    result.get("primary_emotion", "neutral"),
                    text,
                    source_type=source,
                    intensity=result.get("intensity", 0.5),
                    session_id=session_id
                )
        except Exception as log_error:
            logger.warning(f"Could not log emotion: {str(log_error)}")
            
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error analyzing emotion: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Failed to analyze emotion: {str(e)}"
        }), 500

# Add new imports for voice analysis
import traceback
from werkzeug.utils import secure_filename
from voice.recognition import VoiceRecognition

# Initialize voice recognition
voice_recognition = None
try:
    voice_recognition = VoiceRecognition(config)
    voice_recognition.initialize()
except Exception as e:
    logger.warning(f"Failed to initialize voice recognition: {str(e)}")

@app.route('/api/analyze-voice-emotion', methods=['POST'])
def analyze_voice_emotion():
    """
    Record voice, convert to text, and analyze emotional content
    
    This endpoint combines voice recognition with emotion analysis in one step.
    The audio file is processed by the voice recognition system, then the
    recognized text is analyzed for emotional content.
    
    Request parameters:
    - audio: The audio file to process (required)
    - language: The language of the audio (optional, default: 'ar')
    - return_details: Whether to return emotion details (optional, default: True)
    
    Returns:
    {
        "success": true/false,
        "text": "Recognized text from audio",
        "primary_emotion": "emotion_name",
        "emotion_data": {
            "emotions": { ... },
            "intensity": 0.8
        }
    }
    """
    try:
        logger.debug("Voice emotion analysis API called")
        
        # Check if necessary modules are available
        if not voice_recognition:
            return jsonify({
                "success": False,
                "error": "Voice recognition module not available"
            }), 503
        
        if not emotion_tracker:
            return jsonify({
                "success": False,
                "error": "Emotion tracking module not available"
            }), 503
        
        # Check if we have an audio file
        if 'audio' not in request.files:
            return jsonify({
                "success": False,
                "error": "No audio file provided"
            }), 400
        
        audio_file = request.files['audio']
        if not audio_file:
            return jsonify({
                "success": False,
                "error": "Empty audio file provided"
            }), 400
        
        # Get other parameters
        language = request.form.get('language') or request.args.get('language')
        if not language:
            from flask import session
            language = session.get('language', 'ar')
        
        return_details = request.form.get('return_details', 'true').lower() == 'true'
        
        # Create temp directory if necessary
        temp_dir = 'temp'
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save the audio file temporarily
        import time
        filename = f"voice_emotion_{int(time.time())}.wav"
        temp_path = os.path.join(temp_dir, filename)
        audio_file.save(temp_path)
        
        # Process with voice recognition
        recognition_language = 'ar-EG' if language == 'ar' else 'en-US'
        recognition_result = voice_recognition.recognize_speech_from_file(
            temp_path, 
            language=recognition_language
        )
        
        # Remove the temporary file
        try:
            os.remove(temp_path)
        except Exception as e:
            logger.warning(f"Could not remove temporary audio file: {str(e)}")
        
        # Check voice recognition result
        if not recognition_result.get('success', False):
            return jsonify({
                "success": False,
                "error": recognition_result.get('error', 'Voice recognition failed')
            }), 422
        
        # Get the recognized text
        recognized_text = recognition_result.get('text', '')
        if not recognized_text:
            return jsonify({
                "success": False,
                "error": "No text could be recognized from the audio"
            }), 422
        
        # Analyze emotion in the recognized text
        emotion_result = emotion_tracker.analyze_text(recognized_text, return_details=True)
        
        # Prepare the response
        response = {
            "success": True,
            "text": recognized_text,
            "primary_emotion": emotion_result.get("primary_emotion", "neutral"),
            "source": "voice",
            "language": language
        }
        
        # Include detailed emotion data if requested
        if return_details:
            response["emotion_data"] = {
                "emotions": emotion_result.get("emotions", {}),
                "intensity": emotion_result.get("intensity", 0.5)
            }
        
        # Log the emotion with source information
        try:
            from flask import session
            import uuid
            
            session_id = session.get('session_id')
            if not session_id:
                session_id = str(uuid.uuid4())
                session['session_id'] = session_id
                
            # Log the emotion with the source type
            if hasattr(emotion_tracker, 'log_emotion'):
                emotion_tracker.log_emotion(
                    emotion_result.get("primary_emotion", "neutral"),
                    recognized_text,
                    source_type="voice",
                    intensity=emotion_result.get("intensity", 0.5),
                    session_id=session_id
                )
        except Exception as log_error:
            logger.warning(f"Could not log voice emotion: {str(log_error)}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in voice emotion analysis: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": f"Failed to analyze voice emotion: {str(e)}"
        }), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404 error: {e}")
    return jsonify({"error": "Resource not found", "status": "error"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"500 error: {e}")
    return jsonify({"error": "Internal server error", "status": "error"}), 500

# This allows running the app directly with python main.py
if __name__ == "__main__":
    logger.info("Starting Mashaaer Feelings application")
    app.run(host="0.0.0.0", port=5000, debug=True)