"""
Enhanced Feedback Module for Mashaaer Feelings
This module provides comprehensive feedback functionalities with emotional micro-interactions.
"""
from flask import Blueprint, jsonify, request, render_template_string, current_app
from flask_cors import CORS
import os
import logging
import datetime
import json
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create blueprint
enhanced_feedback_bp = Blueprint('enhanced_feedback', __name__)

# Configure CORS for all routes in this blueprint
CORS(enhanced_feedback_bp, supports_credentials=True)

# Ensure feedback data directory exists
os.makedirs('data/feedback', exist_ok=True)

@enhanced_feedback_bp.route("/enhanced-feedback", methods=["GET"])
def index():
    """Serve the enhanced feedback system homepage"""
    logger.debug("Serving enhanced feedback homepage")
    return render_template_string(get_enhanced_feedback_html())

@enhanced_feedback_bp.route("/enhanced-feedback/health", methods=["GET", "OPTIONS"])
def health():
    """Health check endpoint for enhanced feedback system"""
    logger.debug("Enhanced feedback health check endpoint accessed")
    return jsonify({
        "status": "ok",
        "message": "Mashaaer Enhanced Feedback service is running",
        "environment": os.environ.get("REPL_SLUG", "local"),
        "timestamp": datetime.datetime.now().isoformat()
    })

@enhanced_feedback_bp.route('/api/enhanced-feedback', methods=['POST', 'OPTIONS'])
def process_enhanced_feedback():
    """
    Process enhanced feedback with emotion-driven response
    """
    if request.method == 'OPTIONS':
        return '', 200
        
    logger.info("Received enhanced feedback request")
    
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

@enhanced_feedback_bp.route('/enhanced-feedback/direct', methods=['GET', 'POST'])
def direct_feedback():
    """Serve an enhanced feedback page with visual confirmations and sound effects"""
    logger.debug("Serving enhanced direct feedback page")
    
    # Handle POST request for feedback submission
    if request.method == "POST":
        try:
            # Get the JSON data from the request
            data = request.get_json()
            
            # Forward to API endpoint using internal request
            response = current_app.test_client().post(
                '/api/enhanced-feedback',
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
    return render_template_string(get_enhanced_feedback_html())

def get_enhanced_feedback_html():
    """Returns the HTML template for the enhanced feedback page"""
    return """
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
                
                <button type="submit" class="submit-btn">Submit Feedback</button>
            </form>
            
            <div id="feedback-result"></div>
        </div>
        
        <div class="emotion-transition" id="emotion-transition"></div>
        
        <!-- Sound effect audio elements -->
        <audio id="sound-hover" preload="auto"></audio>
        <audio id="sound-click" preload="auto"></audio>
        <audio id="sound-success" preload="auto"></audio>
        <audio id="sound-error" preload="auto"></audio>
        <audio id="sound-transition" preload="auto"></audio>
        
        <script src="/static/js/micro_interactions.js"></script>
        <script src="/static/js/feedback_interactions.js"></script>
        <script>
            // Track the current state
            let currentRating = 0;
            let currentEmotion = '';
            let soundEnabled = true;
            
            // Get DOM elements
            const form = document.getElementById('feedback-form');
            const resultDiv = document.getElementById('feedback-result');
            const stars = document.querySelectorAll('.star');
            const emotionOptions = document.querySelectorAll('.emotion-option');
            const audioToggle = document.querySelector('.audio-toggle');
            const transitionElement = document.getElementById('emotion-transition');
            
            // Audio elements
            const soundHover = document.getElementById('sound-hover');
            const soundClick = document.getElementById('sound-click');
            const soundSuccess = document.getElementById('sound-success');
            const soundError = document.getElementById('sound-error');
            const soundTransition = document.getElementById('sound-transition');
            
            // Set audio sources
            soundHover.src = '/static/sounds/hover.mp3';
            soundClick.src = '/static/sounds/click.mp3';
            soundSuccess.src = '/static/sounds/success.mp3';
            soundError.src = '/static/sounds/error.mp3';
            soundTransition.src = '/static/sounds/transition.mp3';
            
            // Initialize the form
            function initialize() {
                // Star rating functionality
                stars.forEach(star => {
                    star.addEventListener('click', function() {
                        if (soundEnabled) soundClick.play();
                        
                        const value = parseInt(this.getAttribute('data-value'));
                        currentRating = value;
                        
                        // Update visual state
                        stars.forEach(s => {
                            if (parseInt(s.getAttribute('data-value')) <= value) {
                                s.classList.add('active');
                            } else {
                                s.classList.remove('active');
                            }
                        });
                    });
                    
                    star.addEventListener('mouseover', function() {
                        if (soundEnabled) soundHover.play();
                    });
                });
                
                // Emotion selection functionality
                emotionOptions.forEach(option => {
                    option.addEventListener('click', function() {
                        if (soundEnabled) soundClick.play();
                        
                        const emotion = this.getAttribute('data-emotion');
                        const previousEmotion = currentEmotion;
                        currentEmotion = emotion;
                        
                        // Update visual state
                        emotionOptions.forEach(o => o.classList.remove('active'));
                        this.classList.add('active');
                        
                        // If emotion changed, play transition sound and show effect
                        if (previousEmotion && previousEmotion !== emotion) {
                            if (soundEnabled) soundTransition.play();
                            showEmotionTransition(emotion);
                        }
                    });
                    
                    option.addEventListener('mouseover', function() {
                        if (soundEnabled) soundHover.play();
                    });
                });
                
                // Toggle sound effects
                audioToggle.addEventListener('click', function() {
                    soundEnabled = !soundEnabled;
                    this.textContent = soundEnabled ? '🔊' : '🔇';
                    
                    if (soundEnabled) {
                        soundClick.play();
                    }
                });
                
                // Form submission
                form.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    
                    if (soundEnabled) soundClick.play();
                    
                    const nameInput = document.getElementById('name');
                    const feedbackInput = document.getElementById('feedback');
                    
                    // Validate feedback is provided
                    if (!feedbackInput.value.trim()) {
                        resultDiv.textContent = 'Please provide your feedback.';
                        resultDiv.className = 'error';
                        resultDiv.style.display = 'block';
                        if (soundEnabled) soundError.play();
                        return;
                    }
                    
                    // Prepare form data
                    const formData = {
                        name: nameInput.value.trim() || 'Anonymous',
                        feedback: feedbackInput.value.trim(),
                        rating: currentRating,
                        emotion: currentEmotion || 'neutral',
                        timestamp: new Date().toISOString()
                    };
                    
                    try {
                        // Send data to API
                        const response = await fetch('/api/enhanced-feedback', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(formData)
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            // Show success message
                            resultDiv.textContent = data.message;
                            resultDiv.className = 'success';
                            resultDiv.style.display = 'block';
                            
                            // Play success sound and show emotion effect
                            if (soundEnabled) soundSuccess.play();
                            showEmotionTransition(data.emotion_effect || 'happy');
                            
                            // Reset form
                            form.reset();
                            stars.forEach(s => s.classList.remove('active'));
                            emotionOptions.forEach(o => o.classList.remove('active'));
                            currentRating = 0;
                            currentEmotion = '';
                        } else {
                            // Show error message
                            resultDiv.textContent = data.message || 'Error submitting feedback.';
                            resultDiv.className = 'error';
                            resultDiv.style.display = 'block';
                            
                            // Play error sound
                            if (soundEnabled) soundError.play();
                        }
                    } catch (error) {
                        // Show error message
                        resultDiv.textContent = 'Error submitting feedback: ' + error.message;
                        resultDiv.className = 'error';
                        resultDiv.style.display = 'block';
                        
                        // Play error sound
                        if (soundEnabled) soundError.play();
                    }
                });
            }
            
            // Show emotion transition effect
            function showEmotionTransition(emotion) {
                // Emotion color mappings
                const emotionColors = {
                    'happy': {primary: '#FFD700', secondary: '#FFA500'},
                    'sad': {primary: '#4169E1', secondary: '#1E90FF'},
                    'angry': {primary: '#FF4500', secondary: '#FF6347'},
                    'calm': {primary: '#48D1CC', secondary: '#20B2AA'},
                    'excited': {primary: '#FF1493', secondary: '#FF69B4'},
                    'confused': {primary: '#9932CC', secondary: '#8B008B'},
                    'neutral': {primary: '#9370DB', secondary: '#7B68EE'}
                };
                
                // Set colors for the emotion
                const colors = emotionColors[emotion] || emotionColors.neutral;
                
                // Apply animation
                transitionElement.style.background = `radial-gradient(circle, ${colors.primary}00 0%, ${colors.secondary}00 100%)`;
                transitionElement.style.animation = 'none';
                
                // Force reflow
                void transitionElement.offsetWidth;
                
                // Add animation
                transitionElement.style.background = `radial-gradient(circle, ${colors.primary}33 0%, ${colors.secondary}00 100%)`;
                transitionElement.style.animation = 'emotionTransition 1.5s ease-out forwards';
            }
            
            // Add emotion transition animation to the stylesheet
            const style = document.createElement('style');
            style.textContent = `
                @keyframes emotionTransition {
                    0% {
                        opacity: 0;
                        transform: scale(0.8);
                    }
                    50% {
                        opacity: 0.5;
                        transform: scale(1.1);
                    }
                    100% {
                        opacity: 0;
                        transform: scale(1.5);
                    }
                }
            `;
            document.head.appendChild(style);
            
            // Initialize the form
            initialize();
        </script>
    </body>
    </html>
    """

def register_enhanced_feedback_routes(app):
    """Register enhanced feedback routes with the Flask application"""
    app.register_blueprint(enhanced_feedback_bp)
    logger.info("Enhanced feedback routes registered successfully")