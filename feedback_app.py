"""
Simplified Feedback Application
A lightweight Flask application focusing only on the feedback functionality.
"""
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import os
import logging
import datetime
import json
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create the Flask application instance
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# Configure CORS with proper settings for all routes
CORS(app, supports_credentials=True)

# Set a secret key for session management
app.secret_key = os.environ.get("SESSION_SECRET", "mashaaer_development_key")

# Ensure feedback directory exists
os.makedirs('data/feedback', exist_ok=True)

# Add root route for a simple homepage
@app.route("/", methods=["GET"])
def index():
    """Serve a simple homepage"""
    logger.debug("Serving homepage")
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mashaaer Feedback System</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
                background: #1a1a2e;
                color: #fff;
            }
            h1 {
                color: #9370DB;
            }
            a {
                color: #7B68EE;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>Mashaaer Feedback System</h1>
        <p>This is a simplified version of the feedback system.</p>
        <p><a href="/direct-feedback">Try our enhanced feedback form</a></p>
        <p>Check the <a href="/health">/health</a> endpoint for status information.</p>
    </body>
    </html>
    """

# Health check endpoint
@app.route("/health", methods=["GET", "OPTIONS"])
def health():
    """Health check endpoint"""
    logger.debug("Health check endpoint accessed")
    return jsonify({
        "status": "ok",
        "message": "Mashaaer Feedback service is running",
        "environment": os.environ.get("REPL_SLUG", "unknown"),
        "timestamp": datetime.datetime.now().isoformat()
    })

# API endpoint for direct feedback
@app.route('/api/direct-feedback', methods=['POST', 'OPTIONS'])
def process_direct_feedback():
    """
    Process direct feedback with emotion-driven response
    """
    if request.method == 'OPTIONS':
        return '', 200
        
    logger.info("Received feedback request")
    
    try:
        # Get the JSON data from the request
        feedback_data = request.get_json()
        
        # Add timestamp if not provided
        if 'timestamp' not in feedback_data:
            feedback_data['timestamp'] = datetime.datetime.now().isoformat()
            
        # Add user agent and IP info for tracking
        feedback_data['user_agent'] = request.headers.get('User-Agent', 'Unknown')
        feedback_data['ip_address'] = request.remote_addr
        
        # Log the feedback data
        logger.info(f"Received feedback: {json.dumps(feedback_data)}")
        
        # Save feedback to file
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"data/feedback/feedback_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(feedback_data, f, indent=2)
            
        logger.info(f"Feedback saved to {filename}")
        
        # Determine emotion effect based on feedback
        emotion = feedback_data.get('emotion', 'neutral')
        
        # Return success response with emotion effect
        return jsonify({
            "success": True,
            "message": "Thank you for your feedback!",
            "timestamp": datetime.datetime.now().isoformat(),
            "emotion_effect": emotion,
            "sound_effect": "/static/sounds/success.mp3"
        })
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Error processing feedback",
            "error": str(e),
            "emotion_effect": "confused",
            "sound_effect": "/static/sounds/error.mp3"
        }), 500

# Direct feedback page with enhanced UX
@app.route('/direct-feedback', methods=['GET', 'POST'])
def direct_feedback():
    """Serve an enhanced feedback page with visual confirmations and sound effects"""
    logger.debug("Serving enhanced direct feedback page")
    
    # Handle POST request for feedback submission
    if request.method == "POST":
        try:
            # Get the JSON data from the request
            data = request.get_json()
            
            # Forward to API endpoint using internal request
            response = app.test_client().post(
                '/api/direct-feedback',
                json=data,
                headers={'Content-Type': 'application/json'}
            )
            
            # Return the API response
            return response.get_data(), response.status_code, response.headers.items()
        except Exception as e:
            logger.error(f"Error processing feedback: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Error processing feedback",
                "error": str(e),
                "emotion_effect": "confused",
                "sound_effect": "/static/sounds/error.mp3"
            }), 500
    
    # For GET requests, serve the feedback form
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mashaaer Enhanced Feedback</title>
        <link rel="stylesheet" href="/static/css/micro_interactions.css">
        <link rel="stylesheet" href="/static/css/emotion_micro_interactions.css">
        <style>
            :root {
                --emotion-primary: #9370DB;
                --emotion-secondary: #7B68EE;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                color: #fff;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
            }
            
            .container {
                max-width: 600px;
                width: 90%;
                background: rgba(30, 30, 60, 0.7);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                overflow: hidden;
                position: relative;
            }
            
            .cosmic-bg {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: url('/static/images/cosmic-bg.svg');
                opacity: 0.15;
                z-index: -1;
            }
            
            h1 {
                color: var(--emotion-primary);
                text-align: center;
                margin-bottom: 20px;
                font-weight: 600;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                font-size: 14px;
                color: #c8c8f0;
            }
            
            input, textarea, select {
                width: 100%;
                padding: 12px;
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                color: white;
                font-size: 16px;
                transition: all 0.3s;
            }
            
            input:focus, textarea:focus, select:focus {
                outline: none;
                border-color: var(--emotion-primary);
                box-shadow: 0 0 0 2px rgba(147, 112, 219, 0.3);
            }
            
            textarea {
                min-height: 120px;
                resize: vertical;
            }
            
            .rating-stars {
                display: flex;
                gap: 8px;
                margin-top: 10px;
            }
            
            .star {
                font-size: 30px;
                cursor: pointer;
                color: rgba(255, 255, 255, 0.3);
                transition: all 0.2s;
            }
            
            .star:hover, .star.active {
                color: gold;
                transform: scale(1.1);
            }
            
            .emotion-selector {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 10px;
            }
            
            .emotion-option {
                padding: 8px 15px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 30px;
                cursor: pointer;
                transition: all 0.3s;
                font-size: 14px;
            }
            
            .emotion-option:hover, .emotion-option.active {
                background-color: var(--emotion-primary);
                border-color: var(--emotion-primary);
            }
            
            .submit-btn {
                width: 100%;
                padding: 14px;
                background: linear-gradient(90deg, var(--emotion-primary), var(--emotion-secondary));
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                margin-top: 20px;
                transition: all 0.3s;
            }
            
            .submit-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(147, 112, 219, 0.4);
            }
            
            .submit-btn:active {
                transform: translateY(0);
            }
            
            #feedback-result {
                margin-top: 20px;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                display: none;
            }
            
            .success {
                background-color: rgba(76, 175, 80, 0.2);
                border: 1px solid rgba(76, 175, 80, 0.5);
            }
            
            .error {
                background-color: rgba(244, 67, 54, 0.2);
                border: 1px solid rgba(244, 67, 54, 0.5);
            }
            
            .emotion-transition {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 1000;
            }
            
            .audio-controls {
                display: flex;
                align-items: center;
                justify-content: flex-end;
                margin-bottom: 20px;
            }
            
            .audio-toggle {
                background: none;
                border: none;
                color: rgba(255, 255, 255, 0.7);
                font-size: 20px;
                cursor: pointer;
                padding: 5px;
                transition: all 0.3s;
            }
            
            .audio-toggle:hover {
                color: white;
                transform: scale(1.1);
            }
            
            .audio-toggle i {
                pointer-events: none;
            }
            
            .pulse-animation {
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% {
                    transform: scale(1);
                }
                50% {
                    transform: scale(1.05);
                }
                100% {
                    transform: scale(1);
                }
            }
            
            /* Dark/Light mode compatibility */
            @media (prefers-color-scheme: light) {
                body {
                    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
                    color: #333;
                }
                
                .container {
                    background: rgba(255, 255, 255, 0.8);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                }
                
                label {
                    color: #555;
                }
                
                input, textarea, select {
                    background: rgba(0, 0, 0, 0.05);
                    border: 1px solid rgba(0, 0, 0, 0.1);
                    color: #333;
                }
                
                .star {
                    color: rgba(0, 0, 0, 0.2);
                }
                
                .emotion-option {
                    border: 1px solid rgba(0, 0, 0, 0.1);
                    color: #333;
                }
            }
        </style>
    </head>
    <body>
        <div class="cosmic-bg"></div>
        
        <div class="container">
            <div class="audio-controls">
                <button class="audio-toggle" title="Toggle sound effects">
                    🔊
                </button>
            </div>
            
            <h1 class="pulse-animation">Share Your Feelings</h1>
            
            <form id="feedback-form">
                <div class="form-group">
                    <label for="name">Your Name (Optional)</label>
                    <input type="text" id="name" name="name" placeholder="Anonymous">
                </div>
                
                <div class="form-group">
                    <label for="feedback">Your Feedback</label>
                    <textarea id="feedback" name="feedback" placeholder="Tell us how you feel about Mashaaer..." required></textarea>
                </div>
                
                <div class="form-group">
                    <label>Rate Your Experience</label>
                    <div class="rating-stars">
                        <span class="star" data-value="1">★</span>
                        <span class="star" data-value="2">★</span>
                        <span class="star" data-value="3">★</span>
                        <span class="star" data-value="4">★</span>
                        <span class="star" data-value="5">★</span>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>How are you feeling?</label>
                    <div class="emotion-selector">
                        <div class="emotion-option" data-emotion="happy">Happy 😊</div>
                        <div class="emotion-option" data-emotion="sad">Sad 😢</div>
                        <div class="emotion-option" data-emotion="angry">Angry 😠</div>
                        <div class="emotion-option" data-emotion="calm">Calm 😌</div>
                        <div class="emotion-option" data-emotion="excited">Excited 🤩</div>
                        <div class="emotion-option" data-emotion="confused">Confused 🤔</div>
                    </div>
                </div>
                
                <button type="submit" class="submit-btn">Send Feedback</button>
            </form>
            
            <div id="feedback-result"></div>
        </div>
        
        <div class="emotion-transition" id="emotion-transition"></div>
        
        <!-- Audio elements for sound effects -->
        <audio id="hover-sound" preload="auto">
            <source src="/static/sounds/hover.mp3" type="audio/mpeg">
        </audio>
        <audio id="click-sound" preload="auto">
            <source src="/static/sounds/click.mp3" type="audio/mpeg">
        </audio>
        <audio id="success-sound" preload="auto">
            <source src="/static/sounds/success.mp3" type="audio/mpeg">
        </audio>
        <audio id="error-sound" preload="auto">
            <source src="/static/sounds/error.mp3" type="audio/mpeg">
        </audio>
        <audio id="transition-sound" preload="auto">
            <source src="/static/sounds/transition.mp3" type="audio/mpeg">
        </audio>
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Elements
                const form = document.getElementById('feedback-form');
                const resultDiv = document.getElementById('feedback-result');
                const stars = document.querySelectorAll('.star');
                const emotionOptions = document.querySelectorAll('.emotion-option');
                const audioToggle = document.querySelector('.audio-toggle');
                const transitionContainer = document.getElementById('emotion-transition');
                
                // Audio elements
                const hoverSound = document.getElementById('hover-sound');
                const clickSound = document.getElementById('click-sound');
                const successSound = document.getElementById('success-sound');
                const errorSound = document.getElementById('error-sound');
                const transitionSound = document.getElementById('transition-sound');
                
                // State
                let selectedRating = 0;
                let selectedEmotion = '';
                let soundEnabled = true;
                
                // Initialize
                function initialize() {
                    // Set up audio toggle
                    audioToggle.addEventListener('click', function() {
                        soundEnabled = !soundEnabled;
                        audioToggle.textContent = soundEnabled ? '🔊' : '🔇';
                        
                        if (soundEnabled) {
                            playSound(clickSound);
                        }
                    });
                    
                    // Set up star rating
                    stars.forEach(star => {
                        // Hover effects
                        star.addEventListener('mouseenter', function() {
                            const value = parseInt(this.dataset.value);
                            highlightStars(value);
                            if (soundEnabled) playSound(hoverSound);
                        });
                        
                        star.addEventListener('mouseleave', function() {
                            highlightStars(selectedRating);
                        });
                        
                        // Click to select
                        star.addEventListener('click', function() {
                            selectedRating = parseInt(this.dataset.value);
                            highlightStars(selectedRating);
                            if (soundEnabled) playSound(clickSound);
                        });
                    });
                    
                    // Set up emotion options
                    emotionOptions.forEach(option => {
                        // Hover effects
                        option.addEventListener('mouseenter', function() {
                            if (soundEnabled) playSound(hoverSound);
                        });
                        
                        // Click to select
                        option.addEventListener('click', function() {
                            const emotion = this.dataset.emotion;
                            
                            // Deselect previous emotion
                            emotionOptions.forEach(opt => opt.classList.remove('active'));
                            
                            // Select new emotion
                            this.classList.add('active');
                            selectedEmotion = emotion;
                            
                            if (soundEnabled) playSound(clickSound);
                        });
                    });
                    
                    // Set up form submission
                    form.addEventListener('submit', submitFeedback);
                }
                
                // Highlight stars up to a certain value
                function highlightStars(value) {
                    stars.forEach(star => {
                        const starValue = parseInt(star.dataset.value);
                        if (starValue <= value) {
                            star.classList.add('active');
                        } else {
                            star.classList.remove('active');
                        }
                    });
                }
                
                // Play sound with error handling
                function playSound(audioElement) {
                    if (!soundEnabled) return;
                    
                    // Reset sound to beginning
                    audioElement.currentTime = 0;
                    
                    // Play with error handling
                    const playPromise = audioElement.play();
                    
                    if (playPromise !== undefined) {
                        playPromise.catch(error => {
                            console.warn('Audio playback error:', error);
                        });
                    }
                }
                
                // Create sparkle effect for emotions
                function createSparkleEffect(emotion) {
                    // Clear previous effects
                    transitionContainer.innerHTML = '';
                    
                    // Play transition sound
                    playSound(transitionSound);
                    
                    // Define colors based on emotion
                    let colors = ['#FFD700', '#FFC107', '#FFEB3B']; // Default (happy) colors
                    
                    if (emotion === 'sad') {
                        colors = ['#42A5F5', '#2196F3', '#1976D2'];
                    } else if (emotion === 'angry') {
                        colors = ['#EF5350', '#F44336', '#D32F2F'];
                    } else if (emotion === 'calm') {
                        colors = ['#66BB6A', '#4CAF50', '#388E3C'];
                    } else if (emotion === 'excited') {
                        colors = ['#FF9800', '#FF5722', '#FFEB3B'];
                    } else if (emotion === 'confused') {
                        colors = ['#AB47BC', '#9C27B0', '#7B1FA2'];
                    }
                    
                    // Create sparkles
                    for (let i = 0; i < 50; i++) {
                        createSparkle(colors);
                    }
                }
                
                // Create individual sparkle
                function createSparkle(colors) {
                    const sparkle = document.createElement('div');
                    sparkle.style.position = 'absolute';
                    sparkle.style.width = Math.random() * 15 + 5 + 'px';
                    sparkle.style.height = sparkle.style.width;
                    sparkle.style.borderRadius = '50%';
                    sparkle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                    sparkle.style.boxShadow = `0 0 ${Math.random() * 10 + 5}px ${sparkle.style.backgroundColor}`;
                    sparkle.style.opacity = Math.random() + 0.5;
                    
                    // Random position
                    sparkle.style.left = Math.random() * 100 + 'vw';
                    sparkle.style.top = Math.random() * 100 + 'vh';
                    
                    // Add to container
                    transitionContainer.appendChild(sparkle);
                    
                    // Animate with random duration
                    const duration = Math.random() * 2 + 1;
                    sparkle.style.animation = `sparkle-fade ${duration}s ease-out forwards`;
                    
                    // Remove after animation
                    setTimeout(() => {
                        if (transitionContainer.contains(sparkle)) {
                            transitionContainer.removeChild(sparkle);
                        }
                    }, duration * 1000);
                }
                
                // Submit feedback
                function submitFeedback(event) {
                    event.preventDefault();
                    
                    // Get form data
                    const formData = {
                        name: document.getElementById('name').value || 'Anonymous',
                        feedback: document.getElementById('feedback').value,
                        rating: selectedRating,
                        emotion: selectedEmotion
                    };
                    
                    // Submit via fetch
                    fetch('/api/direct-feedback', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Display result
                        resultDiv.innerHTML = data.message;
                        resultDiv.className = data.success ? 'success' : 'error';
                        resultDiv.style.display = 'block';
                        
                        // Play appropriate sound
                        if (data.success) {
                            playSound(successSound);
                        } else {
                            playSound(errorSound);
                        }
                        
                        // Create sparkle effect based on emotion
                        if (data.emotion_effect) {
                            createSparkleEffect(data.emotion_effect);
                        }
                        
                        // Reset form after success
                        if (data.success) {
                            setTimeout(() => {
                                form.reset();
                                selectedRating = 0;
                                highlightStars(0);
                                emotionOptions.forEach(opt => opt.classList.remove('active'));
                                selectedEmotion = '';
                            }, 2000);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        resultDiv.innerHTML = 'An error occurred while submitting feedback. Please try again.';
                        resultDiv.className = 'error';
                        resultDiv.style.display = 'block';
                        playSound(errorSound);
                    });
                }
                
                // Add sparkle animation to CSS
                const styleSheet = document.createElement('style');
                styleSheet.innerHTML = `
                    @keyframes sparkle-fade {
                        0% {
                            transform: scale(0) rotate(0deg);
                            opacity: 0;
                        }
                        50% {
                            opacity: 1;
                        }
                        100% {
                            transform: scale(1) rotate(180deg);
                            opacity: 0;
                        }
                    }
                `;
                document.head.appendChild(styleSheet);
                
                // Initialize the form
                initialize();
            });
        </script>
    </body>
    </html>
    """
    
    return html_content

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)