"""
Production-ready Flask application for Mashaaer Feelings

This is the main entry point for the full Mashaaer Feelings application,
with all APIs and components enabled.
"""
import os
import logging
import sys
from datetime import datetime
from flask import Flask, jsonify, render_template, send_from_directory, send_file
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

# Enable CORS
CORS(app, resources={
    r"/api/*": {"origins": "*", "supports_credentials": True}
})

# Load configuration
config = Config()

# Initialize components
db_manager = DatabaseManager(config)
emotion_tracker = EmotionTracker(db_manager)
intent_classifier = IntentClassifier()
tts_manager = TTSManager(db_manager)
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
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mashaaer Feelings</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                text-align: center;
                background-color: #f8f9fa;
            }
            h1 {
                color: #2c3e50;
                margin-top: 40px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .button {
                display: inline-block;
                padding: 10px 20px;
                margin: 10px;
                background-color: #9c27b0;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Mashaaer Feelings</h1>
            <p>Your emotional intelligence companion</p>
            <p>The application is running correctly and ready to assist you.</p>
            <div>
                <a href="/health" class="button">Health Check</a>
                <a href="/api/status" class="button">API Status</a>
                <a href="/api/docs" class="button">API Documentation</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "app": True,
            "database": db_manager is not None,
            "emotion_tracker": emotion_tracker is not None
        }
    })

# Serve static files for cosmic onboarding experience
@app.route('/cosmic-onboarding')
def cosmic_onboarding():
    """Cosmic onboarding experience entry point"""
    try:
        return send_from_directory('static', 'cosmic_onboarding.html')
    except Exception as e:
        logger.error(f"Error serving cosmic onboarding: {e}")
        return render_template('error.html', message="Cosmic onboarding experience not available")

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