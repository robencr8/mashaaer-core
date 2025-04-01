import os
import logging
import json
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
db_manager = DatabaseManager(config=config, db_path=config.DB_PATH)
emotion_tracker = EmotionTracker(db_manager)
tts_manager = TTSManager(config)
intent_classifier = IntentClassifier()
voice_recognition = VoiceRecognition(config)
face_detector = FaceDetector(config, db_manager)

# Initialize API routes
from api_routes import init_api
init_api(app, db_manager, emotion_tracker, face_detector, 
         tts_manager, voice_recognition, intent_classifier, config)

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

@app.route('/profile')
def profile():
    profiles = face_detector.get_all_profiles()
    dev_mode = is_developer_mode()
    return render_template('profile.html', profiles=profiles, dev_mode=dev_mode)
    
@app.route('/live-view')
def live_view():
    dev_mode = is_developer_mode()
    return render_template('live_view.html', dev_mode=dev_mode)

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

@app.route('/session-report')
def session_report():
    """Show the session report dashboard with real-time data visualization"""
    dev_mode = is_developer_mode()
    
    # Get sample emotion labels and data for initial chart display
    emotion_labels = ['Happy', 'Sad', 'Angry', 'Surprised', 'Fearful', 'Disgusted', 'Neutral']
    emotion_data = [12, 5, 3, 7, 2, 1, 8]
    
    return render_template('session_report.html', 
                          dev_mode=dev_mode, 
                          labels=emotion_labels, 
                          data=emotion_data)

@app.route('/download/session.csv')
def download_session_csv():
    """Download session data as CSV"""
    from flask import session as flask_session
    import csv
    from io import StringIO
    
    # Get session ID from query parameters or use current session
    session_id = request.args.get('session_id', None)
    if session_id == 'current' or not session_id:
        session_id = flask_session.get('session_id')
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            flask_session['session_id'] = session_id
    
    # Get emotion data for this session
    emotions_query = """
        SELECT emotion, timestamp, intensity, text, source
        FROM emotion_data
        WHERE session_id = ?
        ORDER BY timestamp ASC
    """
    emotion_data = db_manager.execute_query(emotions_query, (session_id,))
    
    # Create CSV in memory
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Emotion', 'Timestamp', 'Intensity', 'Text', 'Source'])
    
    for row in emotion_data:
        writer.writerow(row)
    
    output = si.getvalue()
    si.close()
    
    # Return the CSV as a file download
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=session_report.csv"}
    )

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
        
        # Get session ID for logging
        from flask import session
        session_id = session.get('session_id', None)
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            
        # Log emotion with session ID
        emotion_tracker.log_emotion(emotion, text, session_id=session_id)
        
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
        
        # Update last seen for recognized faces
        if result and result.get('count', 0) > 0:
            for face in result.get('faces', []):
                if face.get('recognized', False):
                    # Update the last seen timestamp for this face
                    face_detector._update_last_seen(face.get('name'))
                    
                    # Attach an emotion if available based on metadata
                    face['emotion'] = emotion_tracker.get_primary_emotion_for_name(face.get('name', ''))
        
        # Check for developer mode trigger
        dev_mode = is_developer_mode()
        if result.get('faces') and any(face.get('name') == DEVELOPER_NAME for face in result.get('faces', [])):
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

@app.route('/api/add-face-profile', methods=['POST'])
def add_face_profile():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image provided'}), 400
        
    name = request.form.get('name')
    if not name:
        return jsonify({'success': False, 'error': 'No name provided'}), 400
        
    # Get metadata if available
    metadata = {}
    metadata_json = request.form.get('metadata')
    if metadata_json:
        try:
            metadata = json.loads(metadata_json)
        except:
            pass
    
    # Save image to temporary file
    image = request.files['image']
    temp_path = os.path.join(os.getcwd(), 'temp_profile.jpg')
    image.save(temp_path)
    
    try:
        # Add face to profiles
        result = face_detector.add_face(name, temp_path, metadata)
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        if result:
            logger.info(f"Added new face profile for {name}")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to add face profile'}), 500
    
    except Exception as e:
        logger.error(f"Error adding face profile: {str(e)}")
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete-face-profile/<profile_id>', methods=['DELETE'])
def delete_face_profile(profile_id):
    try:
        # This would be implemented in the face_detector
        # For now, we'll return a mock response
        logger.info(f"Deleting face profile {profile_id}")
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error deleting face profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
@app.route("/api/profile/<name>")
def get_profile(name):
    try:
        # Get profile by name
        profiles = face_detector.get_all_profiles()
        profile = next((p for p in profiles if p['name'] == name), None)
        
        if not profile:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404
        
        # Add emotion data if available
        try:
            # Get the primary emotion from the emotion tracker
            profile['primary_emotion'] = emotion_tracker.get_primary_emotion_for_name(name)
        except:
            profile['primary_emotion'] = 'neutral'
        
        return jsonify({'success': True, 'profile': profile})
    except Exception as e:
        logger.error(f"Error getting profile: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
        
@app.route('/api/log-recognition', methods=['POST'])
def log_recognition():
    try:
        data = request.json
        name = data.get('name')
        emotion = data.get('emotion', 'neutral')
        confidence = data.get('confidence', 0.0)
        
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        # Update last seen timestamp
        face_detector._update_last_seen(name)
        
        # Get session ID for logging
        from flask import session
        session_id = session.get('session_id', None)
        if not session_id:
            import uuid
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            
        # Log the emotion with session ID
        emotion_tracker.log_emotion(emotion, f"Face recognition: {name}", source="face", session_id=session_id)
        
        # Update profile interactions count
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Get the metadata
        cursor.execute("SELECT metadata FROM faces WHERE name = ?", (name,))
        result = cursor.fetchone()
        
        if result and result[0]:
            try:
                metadata = json.loads(result[0])
                
                # Update interactions count
                interactions = metadata.get('interactions', 0)
                metadata['interactions'] = interactions + 1
                
                # Update recognition rate (simulate improvement over time)
                current_rate = metadata.get('recognition_rate', 70)
                confidence_value = int(confidence * 100)
                new_rate = min(98, int((current_rate * 3 + confidence_value) / 4))
                metadata['recognition_rate'] = new_rate
                
                # Save updated metadata
                cursor.execute(
                    "UPDATE faces SET metadata = ? WHERE name = ?",
                    (json.dumps(metadata), name)
                )
                conn.commit()
            except Exception as e:
                logger.error(f"Error updating profile metadata: {str(e)}")
        
        # Log to recognition history table
        try:
            # Create table if it doesn't exist (not needed as we already created it in the DB schema)
            # We'll just use the existing recognition_history table
            
            # Add record with session_id
            timestamp = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO recognition_history (name, timestamp, confidence, emotion, session_id) VALUES (?, ?, ?, ?, ?)",
                (name, timestamp, confidence, emotion, session_id)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error logging recognition to history: {str(e)}")
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error logging recognition: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

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
