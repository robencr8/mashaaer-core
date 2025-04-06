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
from direct_test_route import init_direct_test
from direct_report_route import init_direct_report

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

# Configure CORS with proper settings for all API routes
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

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
    
# Initialize API feedback routes
try:
    from api_feedback import register_api_feedback_routes
    register_api_feedback_routes(app)
    logger.info("API feedback routes registered successfully")
except ImportError as e:
    logger.error(f"Could not import API feedback module: {str(e)}")
except Exception as e:
    logger.error(f"Error initializing API feedback routes: {str(e)}")

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

# Apply enhanced CORS support with detailed debugging
try:
    # First apply the original CORS enhancement
    enhance_cors(app)
    register_feedback_routes(app)  # Register the feedback routes
    
    # Then apply our improved CORS debugging
    from cors_debug import configure_cors_for_replit, add_minimal_test_endpoint
    configure_cors_for_replit(app)
    add_minimal_test_endpoint(app)
    
    # Register our custom feedback route for testing
    from feedback_route import register_feedback_routes as register_dedicated_feedback_routes
    register_dedicated_feedback_routes(app)
    
    logger.info("Successfully registered enhanced CORS configuration with debugging")
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

# Register idiom translator routes
try:
    from idiom_routes import init_idiom_routes
    from ai_model_router import AIModelRouter
    
    # Initialize AI model router for idiom translation
    model_router = AIModelRouter()
    
    # Initialize idiom translator routes
    idiom_bp = init_idiom_routes(app, model_router)
    
    logger.info("Idiom translator routes registered successfully")
except ImportError as e:
    logger.error(f"Could not import idiom translator routes: {str(e)}")
except Exception as e:
    logger.error(f"Error registering idiom translator routes: {str(e)}")

# Add root route for the homepage
@app.route("/", methods=["GET"])
def index():
    """Serve the main homepage"""
    logger.debug("Serving homepage")
    return render_template("index.html")

# Add direct feedback tool route with HTML response and enhanced UX
@app.route("/direct-feedback", methods=["GET", "POST"])
def direct_feedback():
    """Serve an enhanced feedback page with visual confirmations and sound effects"""
    logger.debug("Serving enhanced direct feedback page")
    
    # Handle POST request for feedback submission
    if request.method == "POST":
        try:
            # Forward request to our API feedback handler
            from api_feedback import process_direct_feedback
            return process_direct_feedback()
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
                
                h1 {
                    color: #5e2ca5;
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
                }
            }
        </style>
    </head>
    <body>
        <div class="cosmic-bg"></div>
        
        <div class="container">
            <div class="audio-controls">
                <button class="audio-toggle" id="toggleAudio" title="Toggle sound effects">
                    <i class="fas fa-volume-up"></i>
                </button>
            </div>
            
            <h1>Mashaaer Enhanced Feedback</h1>
            
            <form id="feedbackForm">
                <div class="form-group">
                    <label for="name">Your Name (Optional)</label>
                    <input type="text" id="name" placeholder="Enter your name">
                </div>
                
                <div class="form-group">
                    <label>How would you rate your experience?</label>
                    <div class="rating-stars">
                        <span class="star" data-value="1">★</span>
                        <span class="star" data-value="2">★</span>
                        <span class="star" data-value="3">★</span>
                        <span class="star" data-value="4">★</span>
                        <span class="star" data-value="5">★</span>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>How did you feel using our application?</label>
                    <div class="emotion-selector">
                        <div class="emotion-option" data-emotion="happy">Happy 😊</div>
                        <div class="emotion-option" data-emotion="sad">Sad 😢</div>
                        <div class="emotion-option" data-emotion="calm">Calm 😌</div>
                        <div class="emotion-option" data-emotion="excited">Excited 🤩</div>
                        <div class="emotion-option" data-emotion="confused">Confused 😕</div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="feedback">Your Feedback</label>
                    <textarea id="feedback" placeholder="Please share your thoughts on our application..."></textarea>
                </div>
                
                <button type="submit" class="submit-btn">Submit Feedback</button>
            </form>
            
            <div id="feedback-result"></div>
        </div>
        
        <!-- Audio elements for sound effects -->
        <audio id="clickSound" preload="auto">
            <source src="/static/sounds/click.mp3" type="audio/mp3">
        </audio>
        <audio id="hoverSound" preload="auto">
            <source src="/static/sounds/hover.mp3" type="audio/mp3">
        </audio>
        <audio id="successSound" preload="auto">
            <source src="/static/sounds/success.mp3" type="audio/mp3">
        </audio>
        <audio id="errorSound" preload="auto">
            <source src="/static/sounds/error.mp3" type="audio/mp3">
        </audio>
        <audio id="transitionSound" preload="auto">
            <source src="/static/sounds/transition.mp3" type="audio/mp3">
        </audio>
        
        <!-- Font Awesome for icons -->
        <script src="https://kit.fontawesome.com/3a64e75304.js" crossorigin="anonymous"></script>
        
        <script src="/static/js/micro_interactions.js"></script>
        <script src="/static/js/feedback_interactions.js"></script>
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Sound settings
                let soundEnabled = true;
                
                // Configure audio elements
                const clickSound = document.getElementById('clickSound');
                const hoverSound = document.getElementById('hoverSound');
                const successSound = document.getElementById('successSound');
                const errorSound = document.getElementById('errorSound');
                const transitionSound = document.getElementById('transitionSound');
                
                // Initialize sound volume
                clickSound.volume = 0.4;
                hoverSound.volume = 0.2;
                successSound.volume = 0.5;
                errorSound.volume = 0.5;
                transitionSound.volume = 0.4;
                
                // Play a sound
                function playSound(audio) {
                    if (soundEnabled) {
                        audio.currentTime = 0;
                        audio.play().catch(err => console.log('Audio play error:', err));
                    }
                }
                
                // Toggle sound button
                const toggleAudioBtn = document.getElementById('toggleAudio');
                toggleAudioBtn.addEventListener('click', function() {
                    soundEnabled = !soundEnabled;
                    this.querySelector('i').className = soundEnabled ? 'fas fa-volume-up' : 'fas fa-volume-mute';
                    playSound(clickSound);
                });
                
                // Add interactive behavior to buttons and inputs
                document.querySelectorAll('.submit-btn, .emotion-option, .star').forEach(el => {
                    el.addEventListener('mouseenter', () => playSound(hoverSound));
                    el.addEventListener('click', () => playSound(clickSound));
                });
                
                // Star rating functionality
                let currentRating = 0;
                document.querySelectorAll('.star').forEach(star => {
                    star.addEventListener('click', function() {
                        const value = parseInt(this.dataset.value);
                        currentRating = value;
                        
                        // Update active stars
                        document.querySelectorAll('.star').forEach(s => {
                            s.classList.toggle('active', parseInt(s.dataset.value) <= value);
                        });
                        
                        // Add special effect based on rating
                        if (value >= 4) {
                            createEmotionTransitionEffect('neutral', 'happy');
                        } else if (value <= 2) {
                            createEmotionTransitionEffect('neutral', 'sad');
                        }
                    });
                });
                
                // Emotion selection functionality
                let selectedEmotion = '';
                document.querySelectorAll('.emotion-option').forEach(option => {
                    option.addEventListener('click', function() {
                        // Clear previous selection
                        document.querySelectorAll('.emotion-option').forEach(opt => {
                            opt.classList.remove('active');
                        });
                        
                        // Set new selection
                        this.classList.add('active');
                        selectedEmotion = this.dataset.emotion;
                        
                        // Create emotion transition effect
                        createEmotionTransitionEffect('neutral', selectedEmotion);
                    });
                });
                
                // Form submission
                const feedbackForm = document.getElementById('feedbackForm');
                const resultDiv = document.getElementById('feedback-result');
                
                feedbackForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    // Collect form data
                    const name = document.getElementById('name').value;
                    const feedbackText = document.getElementById('feedback').value;
                    
                    // Basic validation
                    if (!feedbackText) {
                        resultDiv.textContent = 'Please provide your feedback';
                        resultDiv.className = 'error';
                        resultDiv.style.display = 'block';
                        playSound(errorSound);
                        return;
                    }
                    
                    // Prepare data for submission
                    const data = {
                        name: name || 'Anonymous',
                        rating: currentRating,
                        emotion: selectedEmotion,
                        feedback: feedbackText,
                        timestamp: new Date().toISOString()
                    };
                    
                    // Show loading state
                    const originalBtnText = document.querySelector('.submit-btn').textContent;
                    document.querySelector('.submit-btn').textContent = 'Sending...';
                    document.querySelector('.submit-btn').disabled = true;
                    
                    // Send data to server
                    fetch('/direct-feedback', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            resultDiv.textContent = 'Thank you for your feedback!';
                            resultDiv.className = 'success';
                            feedbackForm.reset();
                            document.querySelectorAll('.star').forEach(s => s.classList.remove('active'));
                            document.querySelectorAll('.emotion-option').forEach(opt => opt.classList.remove('active'));
                            
                            // Show success animation
                            createEmotionTransitionEffect('neutral', 'happy');
                            playSound(successSound);
                            
                            // Create particle effect
                            createSuccessFeedbackEffect();
                        } else {
                            resultDiv.textContent = data.message || 'Error submitting feedback';
                            resultDiv.className = 'error';
                            playSound(errorSound);
                        }
                    })
                    .catch(error => {
                        resultDiv.textContent = 'Error submitting feedback: ' + error.message;
                        resultDiv.className = 'error';
                        playSound(errorSound);
                    })
                    .finally(() => {
                        // Reset button state
                        document.querySelector('.submit-btn').textContent = originalBtnText;
                        document.querySelector('.submit-btn').disabled = false;
                        
                        // Show result
                        resultDiv.style.display = 'block';
                        
                        // Add pulse animation to result
                        resultDiv.classList.add('pulse-animation');
                        setTimeout(() => {
                            resultDiv.classList.remove('pulse-animation');
                        }, 2000);
                    });
                });
                
                // Create a success feedback effect
                function createSuccessFeedbackEffect() {
                    const container = document.querySelector('.container');
                    
                    // Create particle container
                    const particleContainer = document.createElement('div');
                    particleContainer.style.position = 'absolute';
                    particleContainer.style.top = '0';
                    particleContainer.style.left = '0';
                    particleContainer.style.width = '100%';
                    particleContainer.style.height = '100%';
                    particleContainer.style.pointerEvents = 'none';
                    particleContainer.style.zIndex = '100';
                    container.appendChild(particleContainer);
                    
                    // Create confetti particles
                    const colors = ['#FFD700', '#4169E1', '#FF4500', '#8A2BE2', '#9370DB'];
                    const particleCount = 40;
                    
                    for (let i = 0; i < particleCount; i++) {
                        const particle = document.createElement('div');
                        
                        // Randomize shape
                        const isCircle = Math.random() > 0.5;
                        
                        // Set style
                        particle.style.position = 'absolute';
                        particle.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
                        
                        if (isCircle) {
                            const size = 5 + Math.random() * 8;
                            particle.style.width = particle.style.height = `${size}px`;
                            particle.style.borderRadius = '50%';
                        } else {
                            const width = 4 + Math.random() * 6;
                            const height = 10 + Math.random() * 12;
                            particle.style.width = `${width}px`;
                            particle.style.height = `${height}px`;
                        }
                        
                        // Set initial position
                        particle.style.left = `${50 + (Math.random() * 20 - 10)}%`;
                        particle.style.top = `0`;
                        
                        // Add to container
                        particleContainer.appendChild(particle);
                        
                        // Animate
                        const duration = 1.5 + Math.random() * 2;
                        const delay = Math.random() * 0.4;
                        
                        particle.style.transition = `all ${duration}s ease-out ${delay}s`;
                        
                        // Schedule animation
                        setTimeout(() => {
                            particle.style.transform = `translateY(${90 + Math.random() * 10}vh) 
                                                     translateX(${Math.random() * 100 - 50}px) 
                                                     rotate(${Math.random() * 360}deg)`;
                            particle.style.opacity = '0';
                        }, 10);
                    }
                    
                    // Clean up particles after animation
                    setTimeout(() => {
                        if (container.contains(particleContainer)) {
                            container.removeChild(particleContainer);
                        }
                    }, 4000);
                }
                
                // Create emotion transition effect
                function createEmotionTransitionEffect(fromEmotion, toEmotion) {
                    // Create a container for sparkle particles
                    const container = document.createElement('div');
                    container.className = 'emotion-transition';
                    document.body.appendChild(container);
                    
                    // Default origin in center of viewport
                    const originX = window.innerWidth / 2;
                    const originY = window.innerHeight / 2;
                    
                    // Play transition sound
                    playSound(transitionSound);
                    
                    // Create sparkle particles
                    const particleCount = 25;
                    
                    // Color mapping based on emotion
                    const emotionColors = {
                        'happy': {primary: '#FFD700', secondary: '#FFA500'},
                        'sad': {primary: '#4169E1', secondary: '#1E90FF'},
                        'calm': {primary: '#48D1CC', secondary: '#20B2AA'},
                        'excited': {primary: '#FF1493', secondary: '#FF69B4'},
                        'confused': {primary: '#9932CC', secondary: '#8B008B'},
                        'neutral': {primary: '#9370DB', secondary: '#7B68EE'}
                    };
                    
                    // Get emotion colors or use neutral as fallback
                    const colors = emotionColors[toEmotion] || emotionColors.neutral;
                    
                    for (let i = 0; i < particleCount; i++) {
                        const sparkle = document.createElement('div');
                        
                        // Random size
                        const size = 4 + Math.random() * 8;
                        
                        // Set style
                        sparkle.style.position = 'absolute';
                        sparkle.style.width = `${size}px`;
                        sparkle.style.height = `${size}px`;
                        sparkle.style.borderRadius = '50%';
                        sparkle.style.backgroundColor = i % 2 === 0 ? colors.primary : colors.secondary;
                        sparkle.style.boxShadow = `0 0 6px ${i % 2 === 0 ? colors.primary : colors.secondary}`;
                        sparkle.style.opacity = '0';
                        
                        // Position at origin
                        sparkle.style.left = `${originX}px`;
                        sparkle.style.top = `${originY}px`;
                        
                        // Add to container
                        container.appendChild(sparkle);
                        
                        // Configure animation
                        const angle = (i / particleCount) * 360;
                        const distance = 30 + Math.random() * 90;
                        const duration = 0.8 + Math.random() * 1.2;
                        const delay = Math.random() * 0.3;
                        
                        // Set transition
                        sparkle.style.transition = `all ${duration}s cubic-bezier(0.165, 0.84, 0.44, 1) ${delay}s`;
                        
                        // Schedule animation
                        setTimeout(() => {
                            // Calculate end position
                            const endX = originX + distance * Math.cos(angle * Math.PI / 180);
                            const endY = originY + distance * Math.sin(angle * Math.PI / 180);
                            
                            // Apply animation
                            sparkle.style.transform = `translate(${endX - originX}px, ${endY - originY}px) scale(${Math.random() * 0.5 + 0.5})`;
                            sparkle.style.opacity = '1';
                            
                            // Fade out
                            setTimeout(() => {
                                sparkle.style.opacity = '0';
                            }, duration * 500);
                        }, 10);
                    }
                    
                    // Remove container after animation finishes
                    setTimeout(() => {
                        if (document.body.contains(container)) {
                            document.body.removeChild(container);
                        }
                    }, 3000);
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

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

# Register additional diagnostic routes
try:
    # Initialize diagnostic test endpoints
    init_direct_test(app)
    init_direct_report(app)
    logger.info("Diagnostic routes registered successfully")
except Exception as e:
    logger.error(f"Error registering diagnostic routes: {str(e)}")
