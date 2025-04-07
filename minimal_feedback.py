from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- Feedback Routes ---
@app.route('/feedback')
@app.route('/direct-feedback')
def show_feedback():
    logger.debug("Serving feedback page")
    return render_template("feedback.html")

@app.route('/verify-feedback')
def verify_feedback():
    return "Mashaaer-Feedback-Live ✅", 200

@app.route('/api/enhanced-feedback', methods=['POST'])
def process_feedback():
    """Process enhanced feedback with emotion-driven response"""
    try:
        feedback_data = request.json
        logger.debug(f"Received feedback: {feedback_data}")
        
        if not feedback_data.get('feedback'):
            return jsonify({
                'success': False,
                'message': 'Feedback text is required'
            }), 400
            
        # Add timestamp if missing
        if not feedback_data.get('timestamp'):
            feedback_data['timestamp'] = datetime.now().isoformat()
            
        # Get name or use Anonymous
        if not feedback_data.get('name'):
            feedback_data['name'] = 'Anonymous'
            
        # Determine appropriate emotion effect
        emotion_effect = feedback_data.get('emotion', 'neutral')
        
        # Get appropriate sound
        sound_effect = get_sound_for_emotion(emotion_effect)
        
        # Save feedback
        save_feedback(feedback_data)
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback!',
            'timestamp': feedback_data['timestamp'],
            'emotion_effect': emotion_effect,
            'sound_effect': f'/static/sounds/{sound_effect}'
        })
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'An error occurred: {str(e)}'
        }), 500

def get_sound_for_emotion(emotion):
    """Get the appropriate sound file for an emotion"""
    emotion_sounds = {
        'happy': 'success.mp3',
        'excited': 'success.mp3',
        'calm': 'notification.mp3',
        'confused': 'notification.mp3',
        'sad': 'notification.mp3',
        'angry': 'error.mp3',
        'neutral': 'notification.mp3'
    }
    
    return emotion_sounds.get(emotion, 'success.mp3')

def save_feedback(feedback_data):
    """Save feedback data to file"""
    try:
        # Ensure data directory exists
        data_dir = os.path.join(os.getcwd(), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        # Append to feedback file
        feedback_file = os.path.join(data_dir, 'enhanced_feedback.json')
        
        # Read existing data
        existing_data = []
        if os.path.exists(feedback_file):
            try:
                with open(feedback_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                # File exists but is not valid JSON, start fresh
                existing_data = []
        
        # Add new feedback
        existing_data.append(feedback_data)
        
        # Write back to file
        with open(feedback_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Saved enhanced feedback from {feedback_data.get('name')} with emotion {feedback_data.get('emotion')}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to save feedback: {str(e)}")
        return False

# --- Default Root ---
@app.route('/')
def index():
    return """
    <h2>Mashaaer Feedback System is Live.</h2>
    <p>Available Routes:</p>
    <ul>
        <li><a href="/feedback">Feedback Form</a></li>
        <li><a href="/direct-feedback">Direct Feedback</a></li>
        <li><a href="/verify-feedback">Verify Feedback</a></li>
    </ul>
    """

# --- Static Files ---
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/test-feedback-system')
def test_feedback_system():
    """Serve a test page for the feedback system"""
    logger.debug("Serving test feedback system page")
    return send_from_directory('static_test', 'feedback_test.html')

# --- CORS Headers for API endpoints ---
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)