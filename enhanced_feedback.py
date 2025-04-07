"""
Enhanced Feedback Module for Mashaaer Feelings
This module provides comprehensive feedback functionalities with emotional micro-interactions.
"""

import os
import json
import logging
import datetime
from flask import Blueprint, render_template, request, jsonify, render_template_string, redirect, url_for
from emotion_tracker import EmotionTracker

# Initialize logger
logger = logging.getLogger(__name__)

try:
    # Import the EmotionTracker
    from main import emotion_tracker
except ImportError:
    # Create our own if importing from main fails
    try:
        # Try to get the db_manager from main
        from main import db_manager
        emotion_tracker = EmotionTracker(db_manager)
    except ImportError:
        # Fall back to no parameter if that's what the current implementation expects
        try:
            from database.db_manager import DatabaseManager
            db_manager = DatabaseManager(None)  # Pass None temporarily
            emotion_tracker = EmotionTracker(db_manager)
        except (ImportError, TypeError):
            # Last resort, create without any parameters
            emotion_tracker = EmotionTracker()

# Create Blueprint
enhanced_feedback_bp = Blueprint('enhanced_feedback', __name__)

@enhanced_feedback_bp.route('/enhanced-feedback', methods=['GET'])
def index():
    """Serve the enhanced feedback system homepage"""
    logger.debug("Enhanced feedback homepage accessed")
    return render_template('enhanced_feedback.html')

@enhanced_feedback_bp.route('/enhanced-feedback/health', methods=['GET'])
def health():
    """Health check endpoint for enhanced feedback system"""
    logger.debug("Enhanced feedback health check accessed")
    return jsonify({
        "status": "ok",
        "module": "enhanced_feedback",
        "timestamp": datetime.datetime.now().isoformat()
    })

@enhanced_feedback_bp.route('/api/enhanced-feedback/process', methods=['POST'])
@enhanced_feedback_bp.route('/api/enhanced-feedback', methods=['POST'])
def process_enhanced_feedback():
    """
    Process enhanced feedback with emotion-driven response
    
    Expected JSON request body:
    {
        "name": "User Name",          // Optional, defaults to "Anonymous"
        "feedback": "Feedback text",  // Required
        "rating": 4,                  // Optional rating (1-5)
        "emotion": "happy",           // Optional detected emotion
        "timestamp": "ISO timestamp"  // Optional, server will add if missing
    }
    
    Returns JSON response:
    {
        "success": true,
        "message": "Thank you for your feedback!",
        "timestamp": "ISO timestamp",
        "emotion_effect": "happy",     // For triggering UI effects
        "sound_effect": "/static/sounds/success.mp3"
    }
    """
    logger.debug("Processing enhanced feedback submission")
    
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        if not data or 'feedback' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: feedback',
                'emotion_effect': 'confused',
                'sound_effect': '/static/sounds/error.mp3'
            }), 400
        
        # Create complete feedback data
        feedback_data = {
            'name': data.get('name', 'Anonymous'),
            'feedback': data.get('feedback'),
            'rating': data.get('rating', 5),  # Default to 5 if not provided
            'emotion': data.get('emotion'),   # May be None
            'timestamp': data.get('timestamp', datetime.datetime.now().isoformat())
        }
        
        # If no emotion provided, analyze from text
        if not feedback_data['emotion']:
            analysis = emotion_tracker.analyze_text(feedback_data['feedback'], return_details=False)
            feedback_data['emotion'] = analysis.get('primary_emotion', 'neutral')
        
        # Save feedback
        save_feedback(feedback_data)
        
        # Determine emotion effect
        emotion_effect = determine_emotion_effect(feedback_data)
        
        # Get sound effect for the emotion
        sound_effect = get_sound_for_emotion(emotion_effect)
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback!',
            'timestamp': datetime.datetime.now().isoformat(),
            'emotion_effect': emotion_effect,
            'sound_effect': f'/static/sounds/{sound_effect}'
        })
        
    except Exception as e:
        logger.error(f"Error processing enhanced feedback: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process feedback',
            'message': str(e),
            'emotion_effect': 'confused',
            'sound_effect': '/static/sounds/error.mp3'
        }), 500

@enhanced_feedback_bp.route('/direct-feedback', methods=['GET'])
@enhanced_feedback_bp.route('/enhanced-feedback/direct', methods=['GET'])
def direct_feedback():
    """Serve an enhanced feedback page with visual confirmations and sound effects"""
    logger.debug("Direct feedback page accessed")
    return render_template_string(get_enhanced_feedback_html())

def get_enhanced_feedback_html():
    """Returns the HTML template for the enhanced feedback page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mashaaer Feelings - Feedback</title>
        <link rel="stylesheet" href="/static/css/main.css">
        <link rel="stylesheet" href="/static/css/cosmic-theme.css">
        <link rel="stylesheet" href="/static/css/emotion_feedback_transitions.css">
        <style>
            body {
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 0;
                min-height: 100vh;
                background-color: #0a0a2a;
                background-image: url('/static/images/cosmic-bg.svg');
                background-size: cover;
                background-attachment: fixed;
                color: #f0f0ff;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .feedback-container {
                width: 90%;
                max-width: 600px;
                background-color: rgba(20, 20, 40, 0.8);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                padding: 30px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .feedback-title {
                font-size: 28px;
                color: #fff;
                margin-bottom: 20px;
                text-align: center;
                font-weight: 600;
            }
            
            .feedback-subtitle {
                font-size: 16px;
                color: #ccc;
                margin-bottom: 30px;
                text-align: center;
            }
            
            .feedback-form label {
                display: block;
                margin-bottom: 8px;
                color: #ddd;
                font-weight: 500;
            }
            
            .feedback-form input[type="text"],
            .feedback-form textarea {
                width: 100%;
                padding: 12px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                background-color: rgba(30, 30, 60, 0.6);
                color: #fff;
                margin-bottom: 20px;
                font-size: 16px;
                box-sizing: border-box;
                transition: border-color 0.3s, box-shadow 0.3s;
            }
            
            .feedback-form input[type="text"]:focus,
            .feedback-form textarea:focus {
                border-color: #7878ff;
                box-shadow: 0 0 8px rgba(120, 120, 255, 0.5);
                outline: none;
            }
            
            .feedback-form textarea {
                min-height: 120px;
                resize: vertical;
            }
            
            .emotion-selection {
                display: flex;
                flex-wrap: wrap;
                justify-content: center;
                gap: 15px;
                margin-bottom: 30px;
            }
            
            .emotion-selector {
                display: flex;
                flex-direction: column;
                align-items: center;
                cursor: pointer;
                padding: 10px;
                border-radius: 12px;
                transition: transform 0.2s, background-color 0.3s;
                border: 2px solid transparent;
            }
            
            .emotion-selector:hover {
                transform: translateY(-5px);
                background-color: rgba(255, 255, 255, 0.1);
            }
            
            .emotion-selector.selected {
                border-color: #7878ff;
                background-color: rgba(120, 120, 255, 0.2);
            }
            
            .emotion-icon {
                font-size: 30px;
                margin-bottom: 8px;
            }
            
            .emotion-label {
                font-size: 14px;
                color: #ddd;
            }
            
            .submit-btn {
                display: block;
                width: 100%;
                padding: 14px;
                border: none;
                border-radius: 8px;
                background-color: #7878ff;
                color: white;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: background-color 0.3s, transform 0.2s;
                margin-top: 10px;
            }
            
            .submit-btn:hover {
                background-color: #5a5aff;
            }
            
            .submit-btn:active {
                transform: scale(0.98);
            }
            
            .spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,.3);
                border-radius: 50%;
                border-top-color: #fff;
                animation: spin 1s ease-in-out infinite;
                margin-right: 10px;
                vertical-align: middle;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            .feedback-confirmation {
                position: fixed;
                top: 20px;
                left: 50%;
                transform: translateX(-50%) translateY(-100px);
                background-color: #7878ff;
                color: white;
                padding: 20px 30px;
                border-radius: 12px;
                box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
                text-align: center;
                transition: transform 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                z-index: 1000;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .feedback-confirmation.visible {
                transform: translateX(-50%) translateY(0);
            }
            
            .confirmation-content {
                display: flex;
                align-items: center;
            }
            
            .confirmation-icon {
                font-size: 24px;
                margin-right: 15px;
            }
            
            .confirmation-message {
                font-size: 16px;
                font-weight: 500;
            }
            
            @media (max-width: 600px) {
                .feedback-container {
                    width: 95%;
                    padding: 20px;
                }
                
                .emotion-selection {
                    gap: 10px;
                }
                
                .emotion-icon {
                    font-size: 24px;
                }
                
                .feedback-title {
                    font-size: 24px;
                }
            }
        </style>
    </head>
    <body>
        <div class="feedback-container">
            <h1 class="feedback-title">Share Your Feelings</h1>
            <p class="feedback-subtitle">We value your emotional experience and feedback</p>
            
            <form id="feedback-form" class="feedback-form">
                <label for="name">Your Name (Optional)</label>
                <input type="text" id="name" name="name" placeholder="Enter your name">
                
                <label for="feedback">Your Feedback</label>
                <textarea id="feedback" name="feedback" placeholder="Tell us how you feel about Mashaaer..."></textarea>
                
                <label>How do you feel right now?</label>
                <div class="emotion-selection">
                    <div class="emotion-selector" data-emotion="happy">
                        <div class="emotion-icon">😊</div>
                        <div class="emotion-label">Happy</div>
                    </div>
                    <div class="emotion-selector" data-emotion="excited">
                        <div class="emotion-icon">🤩</div>
                        <div class="emotion-label">Excited</div>
                    </div>
                    <div class="emotion-selector" data-emotion="calm">
                        <div class="emotion-icon">😌</div>
                        <div class="emotion-label">Calm</div>
                    </div>
                    <div class="emotion-selector" data-emotion="neutral">
                        <div class="emotion-icon">😐</div>
                        <div class="emotion-label">Neutral</div>
                    </div>
                    <div class="emotion-selector" data-emotion="confused">
                        <div class="emotion-icon">🤔</div>
                        <div class="emotion-label">Confused</div>
                    </div>
                    <div class="emotion-selector" data-emotion="sad">
                        <div class="emotion-icon">😢</div>
                        <div class="emotion-label">Sad</div>
                    </div>
                </div>
                
                <!-- Hidden field for emotion -->
                <input type="hidden" name="emotion" value="neutral">
                
                <button type="submit" class="submit-btn">Send Feedback</button>
            </form>
        </div>
        
        <!-- Add particle effects container -->
        <div class="particles-container"></div>
        
        <!-- Add emotion transition overlay -->
        <div class="emotion-transition"></div>
        
        <!-- Scripts -->
        <script src="/static/js/feedback_interactions.js"></script>
        <script>
            // Form submission handling with enhanced visual and audio feedback
            document.addEventListener('DOMContentLoaded', function() {
                console.log('Enhanced feedback page loaded');
                
                // Get the form element
                const form = document.getElementById('feedback-form');
                
                // Override the form submission handler from feedback_interactions.js
                if (form) {
                    form.addEventListener('submit', function(event) {
                        event.preventDefault();
                        
                        // Show loading state
                        const submitBtn = this.querySelector('button[type="submit"]');
                        if (submitBtn) {
                            submitBtn.disabled = true;
                            submitBtn.innerHTML = '<span class="spinner"></span> Sending...';
                        }
                        
                        // Get form data
                        const formData = new FormData(this);
                        const jsonData = {};
                        formData.forEach((value, key) => {
                            jsonData[key] = value;
                        });
                        
                        console.log('Submitting feedback:', jsonData);
                        
                        // Send the feedback to the correct endpoint
                        fetch('/api/enhanced-feedback', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(jsonData)
                        })
                        .then(response => response.json())
                        .then(data => {
                            console.log('Feedback response:', data);
                            
                            // Reset form
                            form.reset();
                            
                            // Show success message
                            showFeedbackConfirmation(data);
                            
                            // Reset button
                            if (submitBtn) {
                                submitBtn.disabled = false;
                                submitBtn.innerHTML = 'Send Feedback';
                                submitBtn.classList.add('success-feedback');
                                setTimeout(() => {
                                    submitBtn.classList.remove('success-feedback');
                                }, 1000);
                            }
                            
                            // Play success sound and effect
                            if (window.feedbackInteractions) {
                                window.feedbackInteractions.playSound('success');
                                window.feedbackInteractions.triggerEffect(data.emotion_effect || 'happy');
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            
                            // Reset button
                            if (submitBtn) {
                                submitBtn.disabled = false;
                                submitBtn.innerHTML = 'Try Again';
                                submitBtn.classList.add('error-feedback');
                                setTimeout(() => {
                                    submitBtn.classList.remove('error-feedback');
                                }, 1000);
                            }
                            
                            // Play error sound
                            if (window.feedbackInteractions) {
                                window.feedbackInteractions.playSound('error');
                            }
                        });
                    });
                }
                
                // Function to display feedback confirmation
                function showFeedbackConfirmation(data) {
                    // Create or get confirmation element
                    let confirmationEl = document.getElementById('feedback-confirmation');
                    if (!confirmationEl) {
                        confirmationEl = document.createElement('div');
                        confirmationEl.id = 'feedback-confirmation';
                        confirmationEl.className = 'feedback-confirmation';
                        document.body.appendChild(confirmationEl);
                    }
                    
                    // Set content based on response
                    confirmationEl.innerHTML = `
                        <div class="confirmation-content">
                            <div class="confirmation-icon">✓</div>
                            <div class="confirmation-message">${data.message || 'Thank you for your feedback!'}</div>
                        </div>
                    `;
                    
                    // Make visible
                    confirmationEl.classList.add('visible');
                    
                    // Hide after delay
                    setTimeout(() => {
                        confirmationEl.classList.remove('visible');
                    }, 3000);
                }
            });
        </script>
    </body>
    </html>
    """

def determine_emotion_effect(feedback_data):
    """
    Determine the appropriate emotion effect based on feedback data
    
    Args:
        feedback_data: The feedback data including rating and emotion
        
    Returns:
        String ID of the determined emotion effect
    """
    # Use provided emotion if available
    if feedback_data.get('emotion'):
        return feedback_data['emotion']
    
    # Otherwise determine from rating
    rating = feedback_data.get('rating', 3)
    
    if rating >= 4:
        return 'happy'
    elif rating == 3:
        return 'neutral'
    else:
        return 'sad'

def get_sound_for_emotion(emotion):
    """
    Get the appropriate sound file for an emotion
    
    Args:
        emotion: The emotion to get sound for
        
    Returns:
        String filename for the sound
    """
    emotion_sounds = {
        'happy': 'success.mp3',
        'excited': 'success.mp3',
        'calm': 'notification.mp3',  # Using notification.mp3 as calm.mp3 may not exist
        'confused': 'notification.mp3',
        'sad': 'notification.mp3',   # Changed from subtle.mp3 which doesn't exist
        'angry': 'error.mp3',
        'neutral': 'notification.mp3'
    }
    
    return emotion_sounds.get(emotion, 'success.mp3')

def save_feedback(feedback_data):
    """
    Save feedback data to database or file
    
    Args:
        feedback_data: The feedback data to save
        
    Returns:
        True if successful, False otherwise
    """
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

def register_enhanced_feedback_routes(app):
    """Register enhanced feedback routes with the Flask application"""
    app.register_blueprint(enhanced_feedback_bp)
    logger.info("Enhanced feedback routes registered")
