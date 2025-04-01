import os
import logging
from flask import Flask, render_template, request, jsonify, Response, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import threading
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import core components
from config import Config
from core_launcher import CoreLauncher
from emotion_tracker import EmotionTracker
from intent_classifier import IntentClassifier
from database.db_manager import DatabaseManager
from tts.tts_manager import TTSManager
from voice.recognition import VoiceRecognition
from vision.face_detector import FaceDetector

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "robin_ai_default_secret")

# Initialize components
config = Config()
db_manager = DatabaseManager()
emotion_tracker = EmotionTracker(db_manager)
tts_manager = TTSManager(config)
intent_classifier = IntentClassifier()
voice_recognition = VoiceRecognition(config)
face_detector = FaceDetector(config, db_manager)

# Developer mode constants
DEVELOPER_NAME = os.environ.get("DEVELOPER_NAME", "Roben Edwan")
DEVELOPER_MODE_FLAG = "dev_mode_enabled"

# Helper function to get developer mode status
def is_developer_mode():
    # Check session first (for current request)
    from flask import session
    if session.get(DEVELOPER_MODE_FLAG, False):
        return True
    
    # Then check database (persistent across sessions)
    try:
        value = db_manager.get_setting(DEVELOPER_MODE_FLAG, "false")
        if isinstance(value, str):
            return value.lower() == "true"
        return bool(value)
    except:
        return False

# Helper function to set developer mode
def set_developer_mode(enabled=True):
    # Update session
    from flask import session
    session[DEVELOPER_MODE_FLAG] = enabled
    
    # Update database
    db_manager.set_setting(DEVELOPER_MODE_FLAG, "true" if enabled else "false")
    
    logger.info(f"Developer mode {'enabled' if enabled else 'disabled'}")
    return enabled

# Scheduler for auto-learning
scheduler = BackgroundScheduler()

# Initialize core launcher
core_launcher = CoreLauncher(
    config=config,
    db_manager=db_manager,
    emotion_tracker=emotion_tracker,
    tts_manager=tts_manager,
    intent_classifier=intent_classifier,
    voice_recognition=voice_recognition,
    face_detector=face_detector
)

# Routes
@app.route('/')
def index():
    dev_mode = is_developer_mode()
    return render_template('index.html', dev_mode=dev_mode)

@app.route('/demo')
def demo():
    dev_mode = is_developer_mode()
    return render_template('demo.html', dev_mode=dev_mode)

@app.route('/emotion-timeline')
def emotion_timeline():
    emotions = emotion_tracker.get_emotion_history()
    dev_mode = is_developer_mode()
    return render_template('emotion_timeline.html', emotions=emotions, dev_mode=dev_mode)

@app.route('/admin')
def admin():
    # Only accessible in developer mode
    if not is_developer_mode():
        return redirect(url_for('index'))
    
    system_stats = {
        'uptime': core_launcher.get_uptime(),
        'memory_size': db_manager.get_db_size(),
        'emotion_count': emotion_tracker.get_total_entries(),
        'face_profiles': face_detector.get_profile_count(),
        'system_status': core_launcher.get_system_status()
    }
    
    return render_template('admin.html', stats=system_stats, dev_mode=True)

@app.route('/api/speak', methods=['POST'])
def speak():
    text = request.json.get('text', '')
    voice = request.json.get('voice', 'default')
    language = request.json.get('language', 'en-US')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        # Select voice based on language if not specifically provided
        if voice == 'default' and language == 'ar':
            voice = 'arabic'
        
        audio_path = tts_manager.speak(text, voice)
        return jsonify({
            'success': True, 
            'audio_path': audio_path,
            'text': text,
            'voice': voice,
            'language': language
        })
    except Exception as e:
        logger.error(f"TTS error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/listen', methods=['POST'])
def listen():
    audio_data = request.files.get('audio')
    
    if not audio_data:
        return jsonify({'error': 'No audio data provided'}), 400
    
    try:
        # Save temporary audio file
        temp_path = os.path.join(os.getcwd(), 'temp_audio.wav')
        audio_data.save(temp_path)
        
        # Process with voice recognition
        text = voice_recognition.process_audio(temp_path)
        
        # Check for developer mode trigger
        dev_mode = is_developer_mode()
        if DEVELOPER_NAME in text:
            dev_mode = set_developer_mode(True)
            logger.info("Developer mode activated via voice")
        
        # Process emotion
        emotion = emotion_tracker.analyze_text(text)
        emotion_tracker.log_emotion(emotion, text)
        
        # Get intent
        intent = intent_classifier.classify(text)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            'success': True, 
            'text': text, 
            'emotion': emotion,
            'intent': intent,
            'dev_mode': dev_mode
        })
    
    except Exception as e:
        logger.error(f"Voice recognition error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/detect-face', methods=['POST'])
def detect_face():
    face_image = request.files.get('image')
    
    if not face_image:
        return jsonify({'error': 'No image provided'}), 400
    
    try:
        # Save temporary image file
        temp_path = os.path.join(os.getcwd(), 'temp_face.jpg')
        face_image.save(temp_path)
        
        # Process with face detector
        result = face_detector.detect_faces(temp_path)
        
        # Check for developer mode trigger
        dev_mode = is_developer_mode()
        if result.get('name') == DEVELOPER_NAME:
            dev_mode = set_developer_mode(True)
            logger.info("Developer mode activated via face recognition")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify({
            'success': True,
            'result': result,
            'dev_mode': dev_mode
        })
    
    except Exception as e:
        logger.error(f"Face detection error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/emotion-data')
def emotion_data():
    days = request.args.get('days', 7, type=int)
    emotions = emotion_tracker.get_emotion_history(days=days)
    return jsonify(emotions)

def auto_learn_emotions():
    """Schedule function to retrain emotion model"""
    logger.info("Starting scheduled emotion learning...")
    emotion_tracker.retrain_model()
    logger.info("Emotion model retraining complete")

# Start the scheduler for auto-learning
def init_scheduler():
    scheduler.add_job(
        auto_learn_emotions, 
        'interval', 
        hours=12, 
        next_run_time=datetime.now() + timedelta(minutes=10)
    )
    scheduler.start()
    logger.info("Auto-learning scheduler initialized")

# Make sure database is initialized at module import time
db_manager.initialize_db()

if __name__ == "__main__":
    # Start scheduler
    init_scheduler()
    
    # Launch core systems in a separate thread
    threading.Thread(target=core_launcher.start).start()
    
    # Wait for core systems to initialize
    time.sleep(2)
    
    # Start Flask app
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
