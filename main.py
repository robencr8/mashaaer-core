from flask import Flask, send_from_directory, render_template, redirect, request, jsonify
import os
import json
import sqlite3
import time
from flask_cors import CORS
import datetime
import logging

# Configure logging with file output to reduce console overhead
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='app.log')
console = logging.StreamHandler()
console.setLevel(logging.WARNING)
logging.getLogger('').addHandler(console)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, static_folder='public', static_url_path='')
app.config['START_TIME'] = time.time()

# Configure CORS with more specific settings
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"],
        "supports_credentials": False
    }
})

# Load config from .env if available
app_config = {
    'defaultLanguage': os.environ.get('DEFAULT_LANG', 'ar'),
    'enableElevenlabs': os.environ.get('ENABLE_ELEVENLABS', 'false').lower() == 'true',
    'fallbackToGtts': os.environ.get('FALLBACK_TO_GTTS', 'true').lower() == 'true',
    'chatModel': os.environ.get('ROBIN_CHAT_MODEL', 'openchat'),
    'apiEndpoint': os.environ.get('API_ENDPOINT', 'https://mashaaer.replit.app')
}

# Add health check endpoint for workflow
# (removed to avoid duplicate definition with the one at line 529)

# Initialize database
db_path = os.path.join(os.getcwd(), 'memory.db')
if not os.path.exists(db_path):
    # Create the database and tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create user preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id TEXT PRIMARY KEY,
            language TEXT DEFAULT ?,
            plan TEXT DEFAULT 'basic',
            last_intent TEXT,
            voice_personality TEXT DEFAULT 'classic-arabic',
            voice_speed REAL DEFAULT 1.0,
            voice_pitch REAL DEFAULT 1.0
        )
    ''', (app_config['defaultLanguage'],))
    
    # Create emotion history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotion_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp INTEGER,
            emotion TEXT,
            context TEXT,
            FOREIGN KEY (user_id) REFERENCES user_preferences (user_id)
        )
    ''')
    
    # Create billing history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS billing_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            date TEXT,
            description TEXT,
            amount REAL,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES user_preferences (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Helper function to get DB connection
def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# API Routes
@app.route('/api/voice_logic', methods=['POST'])
def voice_logic():
    try:
        data = request.get_json()
        logger.debug(f"Received voice_logic request: {data}")
        
        if not data or 'user_id' not in data or 'speech' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
        
        user_id = data['user_id']
        speech = data['speech']
        language = data.get('language')
        
        # Process the speech
        response_data = process_speech(user_id, speech, language)
        logger.debug(f"Returning response: {response_data}")
        
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error in voice_logic: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/<user_id>/preferences', methods=['GET'])
def get_user_preferences(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
        preferences = cursor.fetchone()
        
        if not preferences:
            # Create default preferences if not found
            default_preferences = {
                'user_id': user_id,
                'language': app_config['defaultLanguage'],
                'plan': 'basic',
                'last_intent': '',
                'voice_personality': 'classic-arabic',
                'voice_speed': 1.0,
                'voice_pitch': 1.0
            }
            
            cursor.execute(
                '''INSERT INTO user_preferences 
                   (user_id, language, plan, last_intent, voice_personality, voice_speed, voice_pitch) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (user_id, default_preferences['language'], default_preferences['plan'], 
                 default_preferences['last_intent'], default_preferences['voice_personality'], 
                 default_preferences['voice_speed'], default_preferences['voice_pitch'])
            )
            conn.commit()
            conn.close()
            
            return jsonify(default_preferences)
        
        # Convert from sqlite3.Row to dict
        result = dict(preferences)
        conn.close()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in get_user_preferences: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/<user_id>/preferences', methods=['PUT'])
def update_user_preferences(user_id):
    try:
        data = request.get_json()
        language = data.get('language')
        plan = data.get('plan')
        last_intent = data.get('last_intent')
        voice_personality = data.get('voice_personality')
        voice_speed = data.get('voice_speed')
        voice_pitch = data.get('voice_pitch')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            '''UPDATE user_preferences 
               SET language = ?, plan = ?, last_intent = ?, voice_personality = ?, voice_speed = ?, voice_pitch = ? 
               WHERE user_id = ?''',
            (language, plan, last_intent, voice_personality, voice_speed, voice_pitch, user_id)
        )
        
        if cursor.rowcount == 0:
            # Insert if not exists
            cursor.execute(
                '''INSERT INTO user_preferences 
                   (user_id, language, plan, last_intent, voice_personality, voice_speed, voice_pitch) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (user_id, language, plan, last_intent, voice_personality, voice_speed, voice_pitch)
            )
            conn.commit()
            conn.close()
            
            return jsonify({"message": "Preferences created successfully"})
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Preferences updated successfully"})
    except Exception as e:
        logger.error(f"Error in update_user_preferences: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/<user_id>/emotions', methods=['GET'])
def get_user_emotions(user_id):
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM emotion_history WHERE user_id = ?'
        params = [user_id]
        
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(int(start_date))
        
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(int(end_date))
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        emotions = cursor.fetchall()
        
        # Convert from sqlite3.Row to dict
        result = [dict(emotion) for emotion in emotions]
        conn.close()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in get_user_emotions: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/<user_id>/emotions', methods=['POST'])
def add_user_emotion(user_id):
    try:
        data = request.get_json()
        
        if not data or 'emotion' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
        
        emotion = data['emotion']
        context = data.get('context', '')
        timestamp = int(time.time() * 1000)  # Current time in milliseconds
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO emotion_history (user_id, timestamp, emotion, context) VALUES (?, ?, ?, ?)',
            (user_id, timestamp, emotion, context)
        )
        
        last_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({"id": last_id, "message": "Emotion added to history"})
    except Exception as e:
        logger.error(f"Error in add_user_emotion: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/<user_id>/billing', methods=['GET'])
def get_user_billing(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM billing_history WHERE user_id = ? ORDER BY date DESC', (user_id,))
        billing = cursor.fetchall()
        
        # Convert from sqlite3.Row to dict
        result = [dict(bill) for bill in billing]
        conn.close()
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in get_user_billing: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Voice logic processing function
def process_speech(user_id, speech, language=None):
    try:
        # Get user preferences
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
        preferences = cursor.fetchone()
        
        if not preferences:
            # Create default preferences if not found
            default_preferences = {
                'user_id': user_id,
                'language': app_config['defaultLanguage'],
                'plan': 'basic',
                'last_intent': '',
                'voice_personality': 'classic-arabic',
                'voice_speed': 1.0,
                'voice_pitch': 1.0
            }
            
            cursor.execute(
                '''INSERT INTO user_preferences 
                   (user_id, language, plan, last_intent, voice_personality, voice_speed, voice_pitch) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (user_id, default_preferences['language'], default_preferences['plan'], 
                 default_preferences['last_intent'], default_preferences['voice_personality'], 
                 default_preferences['voice_speed'], default_preferences['voice_pitch'])
            )
            conn.commit()
            preferences = default_preferences
        else:
            preferences = dict(preferences)
            
        # Process dialect variations
        processed_speech = process_dialect(speech, language or preferences['language'])
        
        # Check for language switch commands
        if speech.lower().find('تحدث بالعربية') >= 0:
            # Update user language preference
            cursor.execute('UPDATE user_preferences SET language = ? WHERE user_id = ?', ('ar', user_id))
            conn.commit()
            conn.close()
            
            return {
                "response": 'تم تغيير اللغة إلى العربية.',
                "action": 'switch_language',
                "language": 'ar'
            }
        
        if speech.lower().find('switch to english') >= 0:
            # Update user language preference
            cursor.execute('UPDATE user_preferences SET language = ? WHERE user_id = ?', ('en', user_id))
            conn.commit()
            conn.close()
            
            return {
                "response": 'Language switched to English.',
                "action": 'switch_language',
                "language": 'en'
            }
        
        # Check for subscription command
        if speech.lower().find('اشتراكي') >= 0 or speech.lower().find('subscription') >= 0:
            # Update user last intent
            cursor.execute('UPDATE user_preferences SET last_intent = ? WHERE user_id = ?', ('subscription_view', user_id))
            conn.commit()
            
            # Generate response
            if preferences['language'] == 'ar':
                response = f"حسناً، هذه هي معلومات اشتراكك. أنت حالياً على الخطة {get_plan_name_in_arabic(preferences['plan'])}."
            else:
                response = f"Here is your subscription information. You are currently on the {preferences['plan'].capitalize()} plan."
            
            conn.close()
            
            return {
                "response": response,
                "action": 'show_subscription',
                "plan": preferences['plan']
            }
        
        # Detect emotion using rule-based approach
        emotion = detect_emotion(processed_speech, preferences['language'])
        
        # Save emotion to history
        cursor.execute(
            'INSERT INTO emotion_history (user_id, timestamp, emotion, context) VALUES (?, ?, ?, ?)',
            (user_id, int(time.time() * 1000), emotion, processed_speech)
        )
        conn.commit()
        
        # Generate rule-based response
        response = generate_response(processed_speech, preferences['language'], preferences['voice_personality'])
        
        conn.close()
        
        return {
            "response": response,
            "action": 'respond',
            "emotion": emotion,
            "processed_speech": processed_speech
        }
    except Exception as e:
        logger.error(f"Error processing speech: {str(e)}")
        return {
            "response": "Sorry, there was an error processing your request.",
            "action": "error",
            "error": str(e)
        }

# Helper functions
def process_dialect(speech, language):
    # Define dialect mappings
    dialect_mappings = {
        # Arabic dialects
        'شلونك': 'كيف حالك',  # Gulf
        'عامل إيه': 'كيف حالك',  # Egyptian
        'مرتاح': 'كيف حالك',  # Levantine
        'لاباس': 'كيف حالك',  # Maghrebi
        
        # English dialects
        'yo, what\'s good': 'how are you',  # AAVE/Urban
        'how ya going': 'how are you',  # Australian
        'how ye daein': 'how are you',  # Scottish
        'how do you do': 'how are you'  # British formal
    }
    
    # Check if the speech contains any dialect phrases
    standardized = speech
    for dialect_phrase, standard_phrase in dialect_mappings.items():
        if dialect_phrase.lower() in speech.lower():
            standardized = speech.lower().replace(dialect_phrase.lower(), standard_phrase)
            logger.debug(f"Dialect detected: '{dialect_phrase}' mapped to '{standard_phrase}'")
            break
    
    return standardized

def detect_emotion(speech, language):
    # Define emotion keywords
    emotion_keywords = {
        'happy': {
            'ar': ['سعيد', 'فرح', 'ممتاز', 'رائع', 'جميل'],
            'en': ['happy', 'joy', 'excellent', 'great', 'wonderful']
        },
        'sad': {
            'ar': ['حزين', 'مؤسف', 'سيء', 'مؤلم'],
            'en': ['sad', 'unfortunate', 'bad', 'painful']
        },
        'angry': {
            'ar': ['غاضب', 'محبط', 'مزعج', 'سخيف'],
            'en': ['angry', 'frustrated', 'annoying', 'stupid']
        },
        'surprised': {
            'ar': ['متفاجئ', 'مندهش', 'لا أصدق', 'مذهل'],
            'en': ['surprised', 'amazed', 'unbelievable', 'shocking']
        },
        'fearful': {
            'ar': ['خائف', 'قلق', 'مرعب', 'مخيف'],
            'en': ['afraid', 'worried', 'terrifying', 'scary']
        },
        'neutral': {
            'ar': ['عادي', 'طبيعي'],
            'en': ['normal', 'neutral', 'okay']
        }
    }
    
    # Check for emotion keywords
    speech_lower = speech.lower()
    for emotion, langs in emotion_keywords.items():
        keywords = langs.get(language, langs.get('en', []))
        for keyword in keywords:
            if keyword.lower() in speech_lower:
                return emotion
    
    # Default to neutral if no emotion detected
    return 'neutral'

def generate_response(speech, language, personality):
    # Generic responses in different languages
    generic_responses = {
        'ar': [
            'أفهم ما تقول.',
            'كيف يمكنني مساعدتك؟',
            'أنا هنا للمساعدة.',
            'هل تحتاج إلى شيء آخر؟'
        ],
        'en': [
            'I understand what you\'re saying.',
            'How can I help you?',
            'I\'m here to assist.',
            'Do you need anything else?'
        ]
    }
    
    # Adjust response based on personality
    response_pool = generic_responses.get(language, generic_responses['en'])
    
    # Modify responses based on personality
    if personality == 'snoop-style' and language == 'en':
        response_pool = [
            'Yo, I got what you\'re sayin\'.',
            'How can I help you out, fam?',
            'I\'m here to assist, ya dig?',
            'Anything else you need, homie?'
        ]
    elif personality == 'youth-pop' and language == 'en':
        response_pool = [
            'Totally get what you mean!',
            'How can I help you today?',
            'I\'m here for you!',
            'Need anything else? Just ask!'
        ]
    elif personality == 'formal-british' and language == 'en':
        response_pool = [
            'I comprehend your statement, sir/madam.',
            'How might I be of service?',
            'I am at your disposal.',
            'Is there anything further you require?'
        ]
    
    # Return random response from the pool
    import random
    return random.choice(response_pool)

def get_plan_name_in_arabic(plan):
    plan_names = {
        'basic': 'الأساسية',
        'pro': 'الاحترافية',
        'supreme': 'المتميزة'
    }
    return plan_names.get(plan, 'الأساسية')

# Health and status endpoints for testing
@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": int(time.time())})

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "operational",
        "version": "1.0",
        "uptime": int(time.time() - app.config.get('START_TIME', time.time())),
        "endpoints": {
            "voice_logic": "/api/voice_logic",
            "user_preferences": "/api/user/:id/preferences",
            "user_emotions": "/api/user/:id/emotions"
        }
    })

# CORS test specific route
@app.route('/cors-test')
def cors_test():
    return send_from_directory('static_test', 'cors_test.html')

# Static assets routes
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join('public', path)):
        return send_from_directory('public', path)
    else:
        return send_from_directory('public', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)