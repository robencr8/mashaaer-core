"""
Enhanced Feedback Form Module for Mashaaer Feelings
This module provides a simplified feedback form with emotional interactions.
"""

import os
import json
import logging
import datetime
from flask import Blueprint, render_template, request, jsonify, render_template_string

# Initialize logger
logger = logging.getLogger(__name__)

# Create Blueprint
feedback_form_bp = Blueprint('feedback_form', __name__)

@feedback_form_bp.route('/simple-feedback', methods=['GET'])
def simple_feedback():
    """Serve the simplified feedback form page"""
    logger.debug("Simple feedback form accessed")
    return render_template_string(get_simple_feedback_html())

@feedback_form_bp.route('/cosmic-feedback-test', methods=['GET'])
def cosmic_feedback_test():
    """Serve the cosmic feedback test page"""
    logger.debug("Cosmic feedback test page accessed")
    return render_template_string(get_feedback_test_html())

@feedback_form_bp.route('/api/simple-feedback', methods=['POST'])
def process_simple_feedback():
    """
    Process feedback from the simplified form
    
    Expected JSON request body:
    {
        "name": "User Name",
        "email": "user@example.com",
        "rating": 5,
        "feedback": "Feedback text",
        "emotion": "happy"
    }
    
    Returns JSON response:
    {
        "success": true,
        "message": "Thank you for your feedback!",
        "timestamp": "ISO timestamp",
        "emotion_effect": "happy"
    }
    """
    logger.debug("Processing simple feedback submission")
    
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        if not data or 'feedback' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing required parameter: feedback'
            }), 400
        
        # Create complete feedback data
        feedback_data = {
            'name': data.get('name', 'Anonymous'),
            'email': data.get('email', ''),
            'feedback': data.get('feedback'),
            'rating': data.get('rating', 3),
            'emotion': data.get('emotion', 'neutral'),
            'timestamp': datetime.datetime.now().isoformat()
        }
        
        # Save feedback
        save_feedback(feedback_data)
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback!',
            'timestamp': datetime.datetime.now().isoformat(),
            'emotion_effect': feedback_data['emotion']
        })
        
    except Exception as e:
        logger.error(f"Error processing simple feedback: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to process feedback: {str(e)}'
        }), 500

def get_simple_feedback_html():
    """Returns the HTML template for the simplified feedback page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mashaaer Feelings - Feedback</title>
        <style>
            :root {
                --primary-color: #7878ff;
                --background-color: #0a0a2a;
                --text-color: #f0f0ff;
                --border-color: rgba(255, 255, 255, 0.2);
                --success-color: #4CAF50;
                --error-color: #F44336;
            }
            
            body {
                font-family: 'Arial', sans-serif;
                max-width: 600px;
                margin: 20px auto;
                padding: 20px;
                border: 1px solid var(--border-color);
                border-radius: 12px;
                background-color: rgba(20, 20, 40, 0.8);
                color: var(--text-color);
                background-image: url('/static/images/cosmic-bg.svg');
                background-size: cover;
                background-attachment: fixed;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            
            h1 {
                text-align: center;
                color: var(--primary-color);
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: #ddd;
            }
            
            input, textarea {
                width: 100%;
                padding: 12px;
                margin-bottom: 20px;
                border: 1px solid var(--border-color);
                border-radius: 8px;
                background-color: rgba(30, 30, 60, 0.6);
                color: white;
                font-size: 16px;
                box-sizing: border-box;
            }
            
            input:focus, textarea:focus {
                border-color: var(--primary-color);
                outline: none;
                box-shadow: 0 0 8px rgba(120, 120, 255, 0.5);
            }
            
            textarea {
                min-height: 120px;
                resize: vertical;
            }
            
            .rating-group {
                display: flex;
                justify-content: space-between;
                margin-bottom: 20px;
            }
            
            .rating-option {
                display: flex;
                align-items: center;
                cursor: pointer;
            }
            
            .rating-option input {
                margin-right: 5px;
                width: auto;
            }
            
            button {
                width: 100%;
                padding: 14px;
                background: linear-gradient(90deg, #7878ff, #5a5aff);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                margin-top: 10px;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(120, 120, 255, 0.4);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            #feedbackResult {
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
            
            .particle {
                position: fixed;
                background: #ffffff;
                border-radius: 50%;
                z-index: 1000;
                pointer-events: none;
                opacity: 0;
            }
            
            @keyframes float-up {
                0% { transform: translateY(0) scale(1); opacity: 1; }
                100% { transform: translateY(-100px) scale(0); opacity: 0; }
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
            
            .emotion-transition {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 999;
                opacity: 0;
                transition: opacity 0.5s;
            }
            
            .transition-active {
                opacity: 0.5;
            }
            
            .happy-transition { background: radial-gradient(circle, rgba(255,215,0,0) 0%, rgba(255,215,0,0.3) 100%); }
            .sad-transition { background: radial-gradient(circle, rgba(70,130,180,0) 0%, rgba(70,130,180,0.3) 100%); }
            .neutral-transition { background: radial-gradient(circle, rgba(150,150,150,0) 0%, rgba(150,150,150,0.3) 100%); }
            .angry-transition { background: radial-gradient(circle, rgba(220,20,60,0) 0%, rgba(220,20,60,0.3) 100%); }
        </style>
    </head>
    <body>
        <h1>Share Your Feedback</h1>
        <form id="feedbackForm">
            <!-- Name Field -->
            <label for="name">Your Name:</label>
            <input type="text" id="name" name="name" placeholder="Enter your name" required>

            <!-- Email Field -->
            <label for="email">Your Email:</label>
            <input type="email" id="email" name="email" placeholder="Enter your email" required>

            <!-- Rating Options -->
            <label>How would you rate your experience?</label>
            <div class="rating-group">
                <label class="rating-option">
                    <input type="radio" id="rating_bad" name="rating" value="1">
                    <span>Poor</span>
                </label>
                <label class="rating-option">
                    <input type="radio" id="rating_average" name="rating" value="3" checked>
                    <span>Average</span>
                </label>
                <label class="rating-option">
                    <input type="radio" id="rating_excellent" name="rating" value="5">
                    <span>Excellent</span>
                </label>
            </div>

            <!-- Comments Field -->
            <label for="feedback">Your Feedback:</label>
            <textarea id="feedback" name="feedback" rows="4" placeholder="Tell us about your experience..." required></textarea>

            <!-- Hidden field for detected emotion -->
            <input type="hidden" id="emotion" name="emotion" value="neutral">

            <!-- Submit Button -->
            <button type="submit" id="submitButton">Send Feedback</button>
        </form>
        
        <div id="feedbackResult"></div>
        
        <!-- Add emotion transition overlay -->
        <div class="emotion-transition"></div>
        
        <!-- Audio elements for sound effects -->
        <audio id="clickSound" preload="auto">
            <source src="/static/sounds/click.mp3" type="audio/mpeg">
        </audio>
        <audio id="successSound" preload="auto">
            <source src="/static/sounds/success.mp3" type="audio/mpeg">
        </audio>
        <audio id="errorSound" preload="auto">
            <source src="/static/sounds/error.mp3" type="audio/mpeg">
        </audio>
        <audio id="notificationSound" preload="auto">
            <source src="/static/sounds/notification.mp3" type="audio/mpeg">
        </audio>
        
        <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Get DOM elements
                const form = document.getElementById('feedbackForm');
                const submitButton = document.getElementById('submitButton');
                const resultDiv = document.getElementById('feedbackResult');
                const feedbackTextarea = document.getElementById('feedback');
                const emotionField = document.getElementById('emotion');
                const emotionTransition = document.querySelector('.emotion-transition');
                
                // Audio elements
                const clickSound = document.getElementById('clickSound');
                const successSound = document.getElementById('successSound');
                const errorSound = document.getElementById('errorSound');
                const notificationSound = document.getElementById('notificationSound');
                
                // Play sound function with fallback
                function playSound(audioElement) {
                    if (audioElement && audioElement.play) {
                        // Reset the audio to the beginning
                        audioElement.currentTime = 0;
                        
                        // Play the sound with error handling
                        const playPromise = audioElement.play();
                        if (playPromise !== undefined) {
                            playPromise.catch(error => {
                                console.warn('Audio playback was prevented:', error);
                            });
                        }
                    }
                }
                
                // Analyze emotion in text
                function analyzeEmotion(text) {
                    const lowerText = text.toLowerCase();
                    
                    // Simple emotion detection based on keywords
                    const happyWords = ['happy', 'great', 'excellent', 'amazing', 'love', 'awesome', 'joy'];
                    const sadWords = ['sad', 'disappointing', 'sorry', 'unfortunate', 'unhappy', 'miss'];
                    const angryWords = ['angry', 'frustrated', 'annoyed', 'terrible', 'hate', 'worst'];
                    
                    if (happyWords.some(word => lowerText.includes(word))) {
                        return 'happy';
                    } else if (sadWords.some(word => lowerText.includes(word))) {
                        return 'sad';
                    } else if (angryWords.some(word => lowerText.includes(word))) {
                        return 'angry';
                    } else {
                        return 'neutral';
                    }
                }
                
                // Create particle effect
                function createParticles(emotion) {
                    const particleCount = 30;
                    const particleColors = {
                        'happy': '#FFD700', // Gold
                        'sad': '#4682B4',   // Steel Blue
                        'angry': '#DC143C', // Crimson
                        'neutral': '#A9A9A9' // Dark Gray
                    };
                    
                    const color = particleColors[emotion] || particleColors.neutral;
                    
                    for (let i = 0; i < particleCount; i++) {
                        const particle = document.createElement('div');
                        particle.className = 'particle';
                        
                        // Random position near the submit button
                        const buttonRect = submitButton.getBoundingClientRect();
                        const x = buttonRect.left + buttonRect.width/2 + (Math.random() - 0.5) * 200;
                        const y = buttonRect.top + buttonRect.height/2 + (Math.random() - 0.5) * 100;
                        
                        // Random size
                        const size = 4 + Math.random() * 6;
                        
                        // Style the particle
                        particle.style.width = `${size}px`;
                        particle.style.height = `${size}px`;
                        particle.style.background = color;
                        particle.style.boxShadow = `0 0 ${size/2}px ${color}`;
                        particle.style.left = `${x}px`;
                        particle.style.top = `${y}px`;
                        
                        // Add to document
                        document.body.appendChild(particle);
                        
                        // Animate
                        particle.style.opacity = '1';
                        particle.style.animation = `float-up ${1 + Math.random()}s ease-out forwards`;
                        
                        // Remove after animation completes
                        setTimeout(() => {
                            if (particle && particle.parentNode) {
                                particle.parentNode.removeChild(particle);
                            }
                        }, 2000);
                    }
                }
                
                // Show emotion transition effect
                function showEmotionTransition(emotion) {
                    // Remove all previous classes
                    emotionTransition.className = 'emotion-transition';
                    
                    // Add appropriate class
                    emotionTransition.classList.add(`${emotion}-transition`);
                    
                    // Trigger transition effect
                    setTimeout(() => {
                        emotionTransition.classList.add('transition-active');
                        
                        // End transition
                        setTimeout(() => {
                            emotionTransition.classList.remove('transition-active');
                        }, 800);
                    }, 10);
                }
                
                // Live emotion analysis as user types
                feedbackTextarea.addEventListener('input', function() {
                    if (this.value.length > 5) {
                        const emotion = analyzeEmotion(this.value);
                        emotionField.value = emotion;
                    }
                });
                
                // Form submission handler
                form.addEventListener('submit', function(event) {
                    event.preventDefault();
                    
                    // Play click sound
                    playSound(clickSound);
                    
                    // Show loading state
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<span class="spinner"></span> Sending...';
                    
                    // Get form data
                    const name = document.getElementById('name').value;
                    const email = document.getElementById('email').value;
                    const rating = document.querySelector('input[name="rating"]:checked').value;
                    const feedback = feedbackTextarea.value;
                    const emotion = emotionField.value;
                    
                    // Prepare data for API
                    const data = {
                        name: name,
                        email: email,
                        rating: parseInt(rating),
                        feedback: feedback,
                        emotion: emotion
                    };
                    
                    // Send to API
                    fetch('/api/simple-feedback', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    })
                    .then(response => response.json())
                    .then(result => {
                        // Reset button
                        submitButton.disabled = false;
                        submitButton.innerHTML = 'Send Feedback';
                        
                        // Show result message
                        resultDiv.className = result.success ? 'success' : 'error';
                        resultDiv.textContent = result.message;
                        resultDiv.style.display = 'block';
                        
                        if (result.success) {
                            // Play success sound
                            playSound(successSound);
                            
                            // Show emotion effect
                            const effectEmotion = result.emotion_effect || emotion || 'neutral';
                            createParticles(effectEmotion);
                            showEmotionTransition(effectEmotion);
                            
                            // Reset form
                            form.reset();
                            emotionField.value = 'neutral';
                            
                            // Hide result after a delay
                            setTimeout(() => {
                                resultDiv.style.display = 'none';
                            }, 5000);
                        } else {
                            // Play error sound
                            playSound(errorSound);
                        }
                    })
                    .catch(error => {
                        // Reset button
                        submitButton.disabled = false;
                        submitButton.innerHTML = 'Send Feedback';
                        
                        // Show error
                        resultDiv.className = 'error';
                        resultDiv.textContent = 'There was a problem sending your feedback. Please try again.';
                        resultDiv.style.display = 'block';
                        
                        // Play error sound
                        playSound(errorSound);
                        
                        console.error('Error:', error);
                    });
                });
                
                // Initialize
                playSound(notificationSound);
            });
        </script>
    </body>
    </html>
    """

def save_feedback(feedback_data):
    """Save feedback data to file"""
    logger.debug(f"Saving feedback: {feedback_data}")
    try:
        # Create directory if it doesn't exist
        os.makedirs('data/feedback', exist_ok=True)
        
        # Generate a unique filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/feedback/feedback_{timestamp}.json"
        
        # Write to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(feedback_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Feedback saved to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        return False

def get_feedback_test_html():
    """Returns the HTML template for the feedback test page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Feedback Form Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 20px auto;
                padding: 20px;
                background-color: #0a0a2a;
                color: #f0f0ff;
            }
            h1 {
                text-align: center;
            }
            .feedback-link {
                display: block;
                margin: 20px 0;
                padding: 15px;
                background: linear-gradient(90deg, #7878ff, #5a5aff);
                color: white;
                text-align: center;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                transition: all 0.3s;
            }
            .feedback-link:hover {
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(120, 120, 255, 0.4);
            }
            .test-url {
                display: block;
                margin: 20px 0;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                word-break: break-all;
            }
        </style>
    </head>
    <body>
        <h1>Mashaaer Feedback Test</h1>
        
        <p>Click below to open the simple feedback form:</p>
        <a href="/simple-feedback" class="feedback-link">Open Simple Feedback Form</a>
        
        <p>Or use this URL in your browser:</p>
        <div class="test-url">https://[your-replit-domain]/simple-feedback</div>
        
        <p>Alternative options:</p>
        <a href="/direct-feedback" class="feedback-link">Open Enhanced Feedback Form</a>
        
        <h2>API Endpoints</h2>
        <p>The following API endpoints are available for testing:</p>
        <ul>
            <li><code>/api/simple-feedback</code> - For submitting feedback from the simple form</li>
            <li><code>/api/enhanced-feedback</code> - For submitting feedback from the enhanced form</li>
        </ul>
        
        <h2>Test Instructions</h2>
        <ol>
            <li>Open one of the feedback forms using the links above</li>
            <li>Enter your name and email</li>
            <li>Select a rating or emotion</li>
            <li>Enter feedback text containing emotional keywords (e.g., "happy", "sad", "angry")</li>
            <li>Submit the form</li>
            <li>Observe the visual effects and audio feedback</li>
        </ol>
    </body>
    </html>
    """

def register_feedback_form_routes(app):
    """Register feedback form routes with the Flask application"""
    app.register_blueprint(feedback_form_bp)
    logger.info("Feedback form routes registered")