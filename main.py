"""
Production-ready Flask application for Mashaaer Feelings

This is the main entry point for the full Mashaaer Feelings application,
with all APIs and components enabled.
"""
import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, send_from_directory, jsonify, request, redirect, url_for
from enhanced_cors import configure_cors
import api_routes
import api_routes_dev

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('main')

# إنشاء تطبيق Flask
app = Flask(__name__)

# تكوين CORS المحسن
logger.info("Enhanced CORS module loaded")
configure_cors(app)

# تهيئة الوحدات بترتيب صحيح لتجنب التبعيات الدائرية
logger.info("Initializing core modules...")

# استيراد المكونات الضرورية
# 1. أولاً: تهيئة قاعدة البيانات
try:
    from database.db_manager import DatabaseManager
    db_manager = DatabaseManager()
except ImportError as e:
    logger.warning(f"DatabaseManager import error: {e}")
    db_manager = None

# 2. ثانياً: تهيئة التكوين
try:
    from config import Config
    config = Config()
except ImportError as e:
    logger.warning(f"Config import error: {e}")
    config = None

# 3. باقي المكونات التي تعتمد على قاعدة البيانات والتكوين
components = {}

try:
    from emotion_tracker import EmotionTracker
    components['emotion_tracker'] = EmotionTracker(db_manager)
except ImportError as e:
    logger.warning(f"EmotionTracker import error: {e}")
    components['emotion_tracker'] = None
except TypeError as e:
    logger.warning(f"EmotionTracker initialization error: {e}")
    components['emotion_tracker'] = None

try:
    from intent_classifier import IntentClassifier
    components['intent_classifier'] = IntentClassifier()
except ImportError as e:
    logger.warning(f"IntentClassifier import error: {e}")
    components['intent_classifier'] = None

try:
    from vision.face_detector import FaceDetector
    components['face_detector'] = FaceDetector(config, db_manager)
except ImportError as e:
    logger.warning(f"FaceDetector module not available: {e}")
    components['face_detector'] = None
except TypeError as e:
    logger.warning(f"FaceDetector initialization error: {e}")
    components['face_detector'] = None

try:
    from tts.tts_manager import TTSManager
    components['tts_manager'] = TTSManager(config)
except ImportError as e:
    logger.warning(f"TTSManager import error: {e}")
    components['tts_manager'] = None

try:
    from voice.voice_recognition import VoiceRecognition
    components['voice_recognition'] = VoiceRecognition()
except ImportError as e:
    logger.warning(f"VoiceRecognition import error: {e}")
    components['voice_recognition'] = None

try:
    from context_assistant import ContextAssistant
    components['context_assistant'] = ContextAssistant()
except ImportError as e:
    logger.warning(f"ContextAssistant import error: {e}")
    components['context_assistant'] = None

try:
    from ai_model_router import AIModelRouter
    components['model_router'] = AIModelRouter()
    logger.info("AIModelRouter module loaded successfully")
except ImportError as e:
    logger.warning(f"AIModelRouter import error: {e}")
    components['model_router'] = None

try:
    from profile_manager import ProfileManager
    components['profile_manager'] = ProfileManager()
    logger.info("ProfileManager module loaded successfully")
except ImportError as e:
    logger.warning(f"ProfileManager import error: {e}")
    components['profile_manager'] = None

# تسجيل مسارات API
logger.info("Initializing API routes...")
# لتجنب الأخطاء، نتحقق من وجود جميع المكونات المطلوبة أولاً
api_routes.init_api(
    app, 
    db_manager, 
    components.get('emotion_tracker'), 
    components.get('face_detector'), 
    components.get('tts_manager'), 
    components.get('voice_recognition'), 
    components.get('intent_classifier'), 
    config,
    components.get('context_assistant'), 
    components.get('model_router'), 
    components.get('profile_manager')
)

# تسجيل مسارات API للمطورين
try:
    api_routes_dev.init_developer_api(app, components.get('emotion_tracker'), db_manager)
    logger.info("Developer API routes loaded")
except Exception as e:
    logger.error(f"Failed to load developer API routes: {e}")

@app.route('/')
def index():
    """Main entry point for Mashaaer Feelings web application"""
    logger.info(f"Index page request received from {request.remote_addr}")
    return render_template('interactive_cosmic_splash.html')

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "ok",
        "time": datetime.now().isoformat(),
        "components": {
            "db": db_manager is not None,
            "emotion_tracker": components.get('emotion_tracker') is not None,
            "voice_recognition": components.get('voice_recognition') is not None,
            "face_detector": components.get('face_detector') is not None,
            "tts": components.get('tts_manager') is not None
        }
    })

@app.route('/hello')
def hello():
    """Simplest possible route to check server is responding"""
    logger.info(f"Hello endpoint accessed from {request.remote_addr}")
    return jsonify({
        "message": "Hello from Mashaaer API!",
        "status": "ok",
        "time": datetime.now().isoformat()
    })

@app.route('/replit-health')
def replit_health():
    """Special health endpoint for Replit verification"""
    return "OK", 200

@app.route('/cosmic-onboarding')
def cosmic_onboarding():
    """Cosmic onboarding experience entry point"""
    return render_template('cosmic_onboarding.html')

@app.route('/cosmic-theme')
def cosmic_theme():
    """Alternative cosmic theme interface"""
    return render_template('cosmic_theme.html')

@app.route('/direct')
def homepage_direct():
    """Direct access to the production homepage UI"""
    return render_template('interactive_cosmic_splash.html')

@app.route('/consent')
def consent():
    """User consent page"""
    return render_template('consent.html')

@app.route('/voice-register')
def voice_register():
    """Voice registration page"""
    return render_template('voice_register.html')

@app.route('/goodbye')
def goodbye():
    """Goodbye page for users who do not consent"""
    return render_template('goodbye.html')

@app.route('/simple-test')
def simple_test():
    """Simple test page to verify web server is working"""
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Mashaaer Simple Test</title></head>
    <body>
        <h1>الخادم يعمل بنجاح!</h1>
        <p>هذه صفحة اختبار بسيطة للتأكد من أن خادم الويب يعمل بشكل صحيح.</p>
        <p>Server is working correctly! This is a simple test page.</p>
    </body>
    </html>
    '''

@app.route('/static-test')
def static_test():
    """Static test page to verify web server connectivity"""
    return send_from_directory('static_test', 'index.html')

@app.route('/tts_cache/<path:filename>')
def serve_tts_cache(filename):
    """Serve TTS cache files"""
    return send_from_directory('tts_cache', filename)

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/cors-test')
def cors_test():
    """CORS test page to verify cross-origin configuration"""
    return send_from_directory('static', 'cors_test.html')

@app.route('/offline')
def offline():
    """Offline page for PWA"""
    logger.info(f"Offline page request received from {request.remote_addr}")
    return send_from_directory('static', 'offline.html')

@app.route('/manifest.json')
def manifest():
    """Serve the PWA manifest file"""
    logger.info(f"Manifest request received from {request.remote_addr}")
    return send_from_directory('static', 'manifest.json')

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon file"""
    return send_from_directory('static', 'favicon.ico')

@app.route('/icon-test')
def icon_test():
    """Test page for PWA icons"""
    logger.info(f"Icon test page request received from {request.remote_addr}")
    return render_template('icon_test.html')

@app.route('/service-worker.js')
def service_worker():
    """Serve the service worker JavaScript file"""
    logger.info(f"Service worker request received from {request.remote_addr}")
    return send_from_directory('static', 'service-worker.js')

@app.route('/pwa-test')
def pwa_test_page():
    """Test page for PWA features"""
    logger.info(f"PWA test page request received from {request.remote_addr}")
    return send_from_directory('static', 'pwa_test.html')

@app.route("/test-pwa")
def test_pwa_page():
    """Alternative test page for PWA features"""
    logger.info(f"Alternative PWA test page request received from {request.remote_addr}")
    return send_from_directory('static', 'pwa_test.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
