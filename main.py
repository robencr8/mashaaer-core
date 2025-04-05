"""
Production-ready Flask application for Mashaaer Feelings

This is the main entry point for the full Mashaaer Feelings application,
with all APIs and components enabled.
"""
import os
import logging
import sys
from datetime import datetime
from flask import Flask, jsonify, render_template, send_from_directory, send_file, request
from flask_cors import CORS

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Import enhanced CORS if available, fallback to standard CORS if not
try:
    from enhanced_cors import configure_cors
    logger.info("Enhanced CORS module loaded")
    ENHANCED_CORS_AVAILABLE = True
except ImportError:
    logger.warning("Enhanced CORS module not available, using standard CORS")
    ENHANCED_CORS_AVAILABLE = False

# Import local modules
import api_routes
from config import Config
from database.db_manager import DatabaseManager
from emotion_tracker import EmotionTracker
from intent_classifier import IntentClassifier
from context_assistant import ContextAssistant
from tts.tts_manager import TTSManager
from voice.recognition import VoiceRecognition

# Optional imports - will be None if not available
try:
    from face_recognition_module import FaceDetector
    logger.info("FaceDetector module loaded successfully")
except ImportError:
    logger.warning("FaceDetector module not available")
    FaceDetector = None

try:
    from ai_model_router import AIModelRouter
    logger.info("AIModelRouter module loaded successfully")
except ImportError:
    logger.warning("AIModelRouter module not available")
    AIModelRouter = None

try:
    from profile_manager import ProfileManager
    logger.info("ProfileManager module loaded successfully")
except ImportError:
    logger.warning("ProfileManager module not available")
    ProfileManager = None

# Create a Flask app instance named 'app' for Replit compatibility
app = Flask(__name__, static_folder='static')

# Set a secret key for session management
app.secret_key = os.environ.get('SESSION_SECRET', os.urandom(24).hex())

# Load configuration
config = Config()

# Enable CORS for all routes with enhanced configuration
if ENHANCED_CORS_AVAILABLE:
    logger.info("Using enhanced CORS configuration")
    cors = configure_cors(app, dev_mode=config.DEBUG)
else:
    logger.warning("Using fallback CORS configuration - may have limited compatibility")
    # We can't use "*" with credentials, so fallback to explicit origins
    origins = [
        'https://mashaaer.replit.app',
        'http://localhost:5000', 
        'http://127.0.0.1:5000',
        'https://*.replit.app'
    ]
    logger.info(f"CORS fallback origins: {origins}")
    CORS(app, origins=origins, supports_credentials=True)

# Initialize components
db_manager = DatabaseManager(config)
emotion_tracker = EmotionTracker(db_manager)
intent_classifier = IntentClassifier()
tts_manager = TTSManager(config)  # Fixed: passing config instead of db_manager
tts_manager.initialize()  # Initialize TTS system
voice_recognition = VoiceRecognition(config)

# Initialize optional components
face_detector = FaceDetector() if FaceDetector else None
model_router = AIModelRouter() if AIModelRouter else None
profile_manager = ProfileManager(db_manager) if ProfileManager else None

# Initialize context assistant last since it depends on other components
context_assistant = ContextAssistant(
    db_manager=db_manager,
    profile_manager=profile_manager,
    emotion_tracker=emotion_tracker,
    intent_classifier=intent_classifier
)

# Initialize API routes
api = api_routes.init_api(
    app, db_manager, emotion_tracker, face_detector, 
    tts_manager, voice_recognition, intent_classifier, config,
    context_assistant, model_router, profile_manager
)

# Developer/diagnostic API routes (if available)
try:
    import api_routes_dev
    api_dev = api_routes_dev.init_developer_api(app, emotion_tracker, db_manager)
    logger.info("Developer API routes loaded")
except ImportError:
    logger.info("Developer API routes not available")

@app.route('/')
def index():
    """Main entry point for Mashaaer Feelings web application"""
    logger.info(f"Index page request received from {request.remote_addr}")
    # Serve the official production UI with cosmic design elements
    return render_template('startup_standalone.html')

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    logger.info(f"Health check request received from {request.remote_addr}")
    response = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "app": True,
            "database": db_manager is not None,
            "emotion_tracker": emotion_tracker is not None
        }
    }
    logger.info(f"Health check response: {response}")
    return jsonify(response)

# Cosmic onboarding experience
@app.route('/cosmic-onboarding')
def cosmic_onboarding():
    """Cosmic onboarding experience entry point"""
    try:
        return render_template('startup_standalone.html')
    except Exception as e:
        logger.error(f"Error serving cosmic onboarding: {e}")
        return render_template('error.html', message="Cosmic onboarding experience not available")

# Provide alternative access to the cosmic theme UI
@app.route('/cosmic-theme')
def cosmic_theme():
    """Alternative cosmic theme interface"""
    return render_template('startup_standalone.html')

# Direct access to the homepage UI
@app.route('/homepage')
def homepage_direct():
    """Direct access to the production homepage UI"""
    return render_template('startup_standalone.html')

# Route for consent page
@app.route('/consent')
def consent():
    """User consent page"""
    return render_template('consent.html')

# Route for voice registration
@app.route('/voice-register')
def voice_register():
    """Voice registration page"""
    return render_template('voice_register.html')

# Route for goodbye page
@app.route('/goodbye')
def goodbye():
    """Goodbye page for users who do not consent"""
    return render_template('goodbye.html')

# Simple test route
@app.route('/simple-test')
def simple_test():
    """Simple test page to verify web server is working"""
    return render_template('simple_test.html')

# Route for the static test page
@app.route('/static-test')
def static_test():
    """Static test page to verify web server connectivity"""
    logger.info(f"Static test page request received from {request.remote_addr}")
    return send_from_directory('static_test', 'simple_test.html')

# Route for serving TTS cache files
@app.route('/tts_cache/<path:filename>')
def serve_tts_cache(filename):
    """Serve TTS cache files"""
    try:
        return send_from_directory('tts_cache', filename)
    except Exception as e:
        logger.error(f"Error serving TTS cache file {filename}: {e}")
        return jsonify({"error": "Audio file not found"}), 404

# Catch-all route for serving static files
@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        return send_from_directory('static', filename)
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {e}")
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# Route for the CORS test page
@app.route('/cors-test')
def cors_test():
    """CORS test page to verify cross-origin configuration"""
    logger.info(f"CORS test page request received from {request.remote_addr}")
    return send_from_directory('static_test', 'cors_test.html')
