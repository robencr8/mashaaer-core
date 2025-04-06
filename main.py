"""
Main Flask Application for Mashaaer Feelings
This is the entry point for the Replit Gunicorn server.
"""
from flask import Flask, jsonify, send_from_directory, render_template_string, render_template, request, send_file
from flask_cors import CORS
import os
import logging
import sys
import json
import datetime
import platform
import time
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from enhanced_cors import enhance_cors
from routes_feedback_tool import register_feedback_routes

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

# Initialize recommendation engine
recommendation_engine = None 
try:
    from recommendation_engine import RecommendationEngine
    recommendation_engine = RecommendationEngine(db_manager, emotion_tracker)
    recommendation_engine.create_tables()
    logger.info("Recommendation engine initialized successfully")
except ImportError:
    logger.warning("Recommendation engine module could not be imported")
except Exception as e:
    logger.warning(f"Error initializing recommendation engine: {str(e)}")

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
except ImportError as e:
    logger.warning(f"VoiceRecognition import error: {str(e)}")
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

# Initialize memory store and logs
try:
    from memory_store import init_db
    from log_manager import init_logs
    
    # Initialize SQLite database for memory store
    init_db()
    
    # Initialize logging system
    init_logs()
    
    logger.info("Memory store and logging system initialized successfully")
except ImportError as e:
    logger.error(f"Could not import memory store or logging modules: {str(e)}")
except Exception as e:
    logger.error(f"Error initializing memory store or logs: {str(e)}")

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

# Import and register recommendation routes
try:
    from recommendation_routes import init_recommendation_api
    
    # Initialize recommendation API routes
    init_recommendation_api(app, db_manager, emotion_tracker)
    
    logger.info(f"Recommendation API routes registered successfully")
except ImportError as e:
    logger.error(f"Could not import recommendation routes: {str(e)}")
except Exception as e:
    logger.error(f"Error registering recommendation routes: {str(e)}")

# Apply enhanced CORS support
try:
    enhance_cors(app)
    register_feedback_routes(app)  # Register the feedback routes
    logger.info("Successfully registered enhanced CORS and feedback routes")
except Exception as e:
    logger.error(f"Error enhancing CORS: {str(e)}")

# Register admin routes
try:
    from admin_routes import admin_bp
    
    # Register the admin blueprint
    app.register_blueprint(admin_bp)
    
    logger.info("Admin routes registered successfully")
except ImportError as e:
    logger.error(f"Could not import admin routes: {str(e)}")
except Exception as e:
    logger.error(f"Error registering admin routes: {str(e)}")

# Add root route for the homepage
@app.route("/", methods=["GET"])
def index():
    """Serve the main homepage"""
    logger.debug("Serving homepage")
    return render_template("index.html")

# Add recommendations page route
# This is now handled by recommendation_routes.py

# Add emotion analysis API endpoint
@app.route("/api/analyze-emotion", methods=["POST"])
def analyze_emotion():
    """Analyze text for emotional content and return the detected emotion"""
    logger.debug("Analyzing emotion via API endpoint")
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: text'
            }), 400
            
        text = data['text']
        return_details = data.get('return_details', True)
        
        # Analyze the text using the emotion tracker
        result = emotion_tracker.analyze_text(text, return_details=return_details)
        
        # Format the response
        response = {
            'success': True,
            'primary_emotion': result.get('primary_emotion', 'neutral'),
            'emotion_data': result if return_details else None
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error analyzing emotion: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to analyze emotion',
            'message': str(e)
        }), 500

# Add versioned_url function for cache busting
def versioned_url(path):
    """Add version string to URL for cache busting"""
    version = int(time.time())
    return f"/static/{path}?v={version}"

# Add versioned_url to template context
@app.context_processor
def inject_versioned_url():
    """Make versioned_url available in all templates"""
    return dict(versioned_url=versioned_url)
