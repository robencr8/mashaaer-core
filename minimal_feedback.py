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

@app.route('/connection-test')
def connection_test():
    """Serve connection test page for feedback system"""
    logger.debug("Serving connection test page")
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mashaaer Feedback Connection Tester</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .result {
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
            }
            .success {
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
            }
            .error {
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                color: #721c24;
            }
            .info {
                background-color: #d1ecf1;
                border: 1px solid #bee5eb;
                color: #0c5460;
            }
            pre {
                background-color: #f8f9fa;
                padding: 10px;
                border-radius: 5px;
                overflow-x: auto;
                border: 1px solid #ddd;
            }
            button {
                padding: 10px 16px;
                background-color: #7878ff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 10px;
                margin-bottom: 10px;
                font-weight: bold;
            }
            button:hover {
                background-color: #5a5aff;
            }
            h1, h2 {
                color: #333;
            }
        </style>
    </head>
    <body>
        <h1>Mashaaer Feedback Connection Tester</h1>
        
        <div>
            <button id="testServerStatus">Test Server Status</button>
            <button id="testFeedbackPage">Test Feedback Page</button>
            <button id="testApiEndpoint">Test API Endpoint</button>
            <button id="clearResults">Clear Results</button>
        </div>
        
        <h2>Test Results:</h2>
        <div id="results"></div>
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                const resultsDiv = document.getElementById('results');
                
                function addResult(message, type = 'info', data = null) {
                    const resultDiv = document.createElement('div');
                    resultDiv.className = `result ${type}`;
                    
                    const timestamp = new Date().toISOString();
                    resultDiv.innerHTML = `<strong>${timestamp}</strong>: ${message}`;
                    
                    if (data) {
                        const preElem = document.createElement('pre');
                        preElem.textContent = typeof data === 'object' ? JSON.stringify(data, null, 2) : data;
                        resultDiv.appendChild(preElem);
                    }
                    
                    resultsDiv.prepend(resultDiv);
                }
                
                // Test server status
                document.getElementById('testServerStatus').addEventListener('click', function() {
                    addResult('Testing server status...', 'info');
                    
                    fetch('/verify-feedback')
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            return response.text();
                        })
                        .then(data => {
                            addResult('Server is active and responding', 'success', data);
                        })
                        .catch(error => {
                            addResult(`Server test failed: ${error.message}`, 'error');
                        });
                });
                
                // Test feedback page
                document.getElementById('testFeedbackPage').addEventListener('click', function() {
                    addResult('Testing direct-feedback page...', 'info');
                    
                    fetch('/direct-feedback')
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            return response.text();
                        })
                        .then(data => {
                            addResult('Feedback page loaded successfully', 'success', 
                                `Page size: ${data.length} bytes`);
                        })
                        .catch(error => {
                            addResult(`Feedback page test failed: ${error.message}`, 'error');
                        });
                });
                
                // Test API endpoint
                document.getElementById('testApiEndpoint').addEventListener('click', function() {
                    addResult('Testing API endpoint...', 'info');
                    
                    const testData = {
                        name: 'Connection Tester',
                        feedback: 'This is an automated test of the feedback API',
                        emotion: 'neutral',
                        timestamp: new Date().toISOString()
                    };
                    
                    fetch('/api/enhanced-feedback', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(testData)
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        addResult('API endpoint is working correctly', 'success', data);
                    })
                    .catch(error => {
                        addResult(`API endpoint test failed: ${error.message}`, 'error');
                    });
                });
                
                // Clear results
                document.getElementById('clearResults').addEventListener('click', function() {
                    resultsDiv.innerHTML = '';
                });
                
                // Initial message
                addResult('Connection tester initialized', 'info', {
                    url: window.location.href,
                    timestamp: new Date().toISOString()
                });
            });
        </script>
    </body>
    </html>
    '''

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