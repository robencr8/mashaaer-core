"""
Feedback API for Mashaaer Feelings
Provides endpoints for user feedback with emotion-based responses
"""

import os
import logging
import json
import time
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template_string

# Configure logger
logger = logging.getLogger(__name__)

# Create Blueprint
feedback_bp = Blueprint('feedback_api', __name__, url_prefix='/api')

# Configure feedback storage
FEEDBACK_DIR = os.path.join(os.getcwd(), 'data', 'feedback')
os.makedirs(FEEDBACK_DIR, exist_ok=True)

# Emotion response templates
RESPONSE_TEMPLATES = {
    'en': {
        'happy': [
            "Thank you for your wonderful feedback! We're delighted to hear you had a positive experience.",
            "Your positive feedback brightens our day! Thank you for sharing your happiness with us.",
            "We're thrilled that you're happy with your experience! Your feedback means a lot to us."
        ],
        'sad': [
            "We're sorry to hear about your experience. Thank you for bringing this to our attention so we can improve.",
            "Thank you for your honest feedback. We take your concerns seriously and will work to address them.",
            "We appreciate you sharing your thoughts with us, even though your experience wasn't what we hoped. We'll do better."
        ],
        'angry': [
            "We sincerely apologize for any frustration you've experienced. Your feedback is important for our improvement.",
            "Thank you for bringing this issue to our attention. We understand your frustration and will address it promptly.",
            "We value your candid feedback and apologize for not meeting your expectations. We're committed to resolving this."
        ],
        'default': [
            "Thank you for your feedback! We appreciate you taking the time to share your thoughts with us.",
            "Your feedback has been received. We value your input and will use it to enhance our services.",
            "Thanks for reaching out! Your feedback helps us improve and better serve our community."
        ]
    },
    'ar': {
        'سعيد': [
            "شكراً لملاحظاتك الرائعة! يسعدنا سماع تجربتك الإيجابية.",
            "ملاحظاتك الإيجابية تنير يومنا! شكراً لمشاركتنا سعادتك.",
            "نحن سعداء بأنك راضٍ عن تجربتك! ملاحظاتك تعني الكثير بالنسبة لنا."
        ],
        'حزين': [
            "نأسف لسماع تجربتك. شكراً لك على لفت انتباهنا حتى نتمكن من التحسين.",
            "شكراً على ملاحظاتك الصادقة. نحن نأخذ مخاوفك على محمل الجد وسنعمل على معالجتها.",
            "نقدر مشاركتك أفكارك معنا، على الرغم من أن تجربتك لم تكن كما كنا نأمل. سنعمل على التحسين."
        ],
        'غاضب': [
            "نعتذر بصدق عن أي إحباط واجهته. ملاحظاتك مهمة لتحسيننا.",
            "شكراً لك على لفت انتباهنا إلى هذه المشكلة. نتفهم إحباطك وسنعالجها على الفور.",
            "نقدر ملاحظاتك الصريحة ونعتذر لعدم تلبية توقعاتك. نحن ملتزمون بحل هذه المشكلة."
        ],
        'default': [
            "شكراً على ملاحظاتك! نقدر لك وقتك لمشاركة أفكارك معنا.",
            "تم استلام ملاحظاتك. نحن نقدر مساهمتك وسنستخدمها لتحسين خدماتنا.",
            "شكراً للتواصل! ملاحظاتك تساعدنا على التحسين وخدمة مجتمعنا بشكل أفضل."
        ]
    }
}

# Sound effects mapping
SOUND_EFFECTS = {
    'happy': 'happy_chime.mp3',
    'sad': 'gentle_notification.mp3',
    'angry': 'important_notification.mp3',
    'default': 'feedback_received.mp3',
    
    'سعيد': 'happy_chime.mp3',
    'حزين': 'gentle_notification.mp3',
    'غاضب': 'important_notification.mp3'
}

def init_feedback_api(app):
    """Initialize the feedback API blueprint with necessary dependencies"""
    logger.info("Initializing feedback API")
    app.register_blueprint(feedback_bp)
    return feedback_bp

@feedback_bp.route('/user-feedback', methods=['POST'])
def process_feedback():
    """
    Process user feedback with emotion-based context
    
    Request body:
    {
        "name": "User name",               (optional - defaults to "Anonymous")
        "email": "user@example.com",       (optional)
        "feedback": "Feedback message",    (required)
        "rating": 5,                       (optional - 1 to 5 stars)
        "emotion": "happy",                (optional - detected emotion)
        "language": "en",                  (optional - defaults to "en")
        "app_version": "1.0.0",            (optional)
        "device_info": "Browser/Device"    (optional)
    }
    
    Returns:
    {
        "success": true,
        "message": "Thank you for your feedback!",
        "feedback_id": "unique-id",
        "timestamp": "2025-04-07T12:34:56.789Z",
        "emotion_effect": "happy",     // For triggering UI effects
        "sound_effect": "/static/sounds/success.mp3"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'feedback' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: feedback"
            }), 400
        
        # Get request data with defaults
        name = data.get('name', 'Anonymous')
        email = data.get('email', '')
        feedback_text = data.get('feedback', '')
        rating = data.get('rating')
        emotion = data.get('emotion', 'default')
        language = data.get('language', 'en')
        app_version = data.get('app_version', '1.0.0')
        device_info = data.get('device_info', 'Unknown')
        
        # Generate timestamp and ID
        timestamp = datetime.utcnow().isoformat()
        feedback_id = f"{int(time.time())}_{hash(feedback_text)%10000:04d}"
        
        # Complete feedback data
        feedback_data = {
            "id": feedback_id,
            "name": name,
            "email": email,
            "feedback": feedback_text,
            "rating": rating,
            "emotion": emotion,
            "language": language,
            "app_version": app_version,
            "device_info": device_info,
            "timestamp": timestamp
        }
        
        # Save the feedback
        success = save_feedback(feedback_data)
        
        if not success:
            return jsonify({
                "success": False,
                "error": "Failed to save feedback"
            }), 500
        
        # Determine appropriate response message based on emotion and language
        response_message = generate_feedback_response(emotion, language)
        
        # Determine emotion effect for UI
        emotion_effect = determine_emotion_effect(feedback_data)
        
        # Get appropriate sound effect
        sound_effect = get_sound_for_emotion(emotion_effect)
        
        return jsonify({
            "success": True,
            "message": response_message,
            "feedback_id": feedback_id,
            "timestamp": timestamp,
            "emotion_effect": emotion_effect,
            "sound_effect": sound_effect
        })
    
    except Exception as e:
        logger.error(f"Feedback processing error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@feedback_bp.route('/verify-feedback', methods=['GET'])
def verify_feedback():
    """
    Simple endpoint to verify the feedback API is working
    """
    return jsonify({
        "success": True,
        "status": "Feedback API is operational",
        "version": "1.0",
        "timestamp": datetime.utcnow().isoformat()
    })

def determine_emotion_effect(feedback_data):
    """
    Determine the appropriate emotion effect based on feedback data
    
    Args:
        feedback_data: The feedback data including rating and emotion
        
    Returns:
        String ID of the determined emotion effect
    """
    # If emotion is explicitly provided, use it
    if 'emotion' in feedback_data and feedback_data['emotion'] != 'default':
        return feedback_data['emotion']
    
    # Otherwise, try to determine from rating
    if 'rating' in feedback_data and feedback_data['rating'] is not None:
        rating = int(feedback_data['rating'])
        
        if rating >= 4:
            return 'happy'
        elif rating == 3:
            return 'neutral'
        elif rating <= 2:
            return 'sad'
    
    # Default fallback
    return 'default'

def get_sound_for_emotion(emotion):
    """
    Get the appropriate sound file for an emotion
    
    Args:
        emotion: The emotion to get sound for
        
    Returns:
        String URL path for the sound
    """
    sound_file = SOUND_EFFECTS.get(emotion, SOUND_EFFECTS['default'])
    return f"/static/sounds/{sound_file}"

def generate_feedback_response(emotion, language='en'):
    """
    Generate an appropriate response message based on emotion and language
    
    Args:
        emotion: The emotion to generate a response for
        language: The language to respond in ('en' or 'ar')
        
    Returns:
        String response message
    """
    # Select appropriate language template
    lang_templates = RESPONSE_TEMPLATES.get(language, RESPONSE_TEMPLATES['en'])
    
    # Select appropriate emotion template
    emotion_templates = lang_templates.get(emotion, lang_templates['default'])
    
    # Select a random template from the list
    import random
    return random.choice(emotion_templates)

def save_feedback(feedback_data):
    """
    Save feedback data to database or file
    
    Args:
        feedback_data: Dictionary containing feedback information
        
    Returns:
        Boolean indicating success
    """
    try:
        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"feedback_{timestamp}_{feedback_data['id']}.json"
        filepath = os.path.join(FEEDBACK_DIR, filename)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(feedback_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Feedback saved: {filepath}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        return False

@feedback_bp.route('/cosmic-feedback-test', methods=['GET'])
def cosmic_feedback_test():
    """
    Return an HTML page for testing the cosmic feedback form
    """
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cosmic Feedback Test</title>
        <style>
            :root {
                --primary-color: #6A1B9A;
                --secondary-color: #9C27B0;
                --accent-color: #E1BEE7;
                --background-dark: #121212;
                --background-light: #121212;
                --text-light: #FFFFFF;
                --text-dark: #121212;
                --success-color: #4CAF50;
                --error-color: #F44336;
                --border-radius: 12px;
                --box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            
            @keyframes gradientBackground {
                0% {
                    background-position: 0% 50%;
                }
                50% {
                    background-position: 100% 50%;
                }
                100% {
                    background-position: 0% 50%;
                }
            }
            
            @keyframes floatingStars {
                0% {
                    transform: translateY(0px) translateX(0px) rotate(0deg);
                }
                50% {
                    transform: translateY(-15px) translateX(10px) rotate(180deg);
                }
                100% {
                    transform: translateY(0px) translateX(0px) rotate(360deg);
                }
            }
            
            @keyframes pulse {
                0% {
                    transform: scale(1);
                    opacity: 1;
                }
                50% {
                    transform: scale(1.05);
                    opacity: 0.8;
                }
                100% {
                    transform: scale(1);
                    opacity: 1;
                }
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(45deg, #0f0c29, #302b63, #24243e);
                background-size: 400% 400%;
                animation: gradientBackground 15s ease infinite;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: var(--text-light);
            }
            
            .cosmic-container {
                position: relative;
                max-width: 600px;
                width: 90%;
                padding: 30px;
                background: rgba(18, 18, 18, 0.8);
                backdrop-filter: blur(10px);
                border-radius: var(--border-radius);
                box-shadow: var(--box-shadow);
                overflow: hidden;
                z-index: 1;
            }
            
            .stars {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: -1;
            }
            
            .star {
                position: absolute;
                background: white;
                border-radius: 50%;
                filter: blur(1px);
                opacity: 0.7;
                animation: floatingStars 8s infinite;
            }
            
            h1 {
                text-align: center;
                margin-bottom: 30px;
                color: #E1BEE7;
                font-weight: 600;
                position: relative;
                display: inline-block;
                left: 50%;
                transform: translateX(-50%);
            }
            
            h1::after {
                content: '';
                position: absolute;
                bottom: -10px;
                left: 0;
                width: 100%;
                height: 3px;
                background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
            }
            
            .form-group {
                margin-bottom: 20px;
                position: relative;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                font-size: 14px;
                color: #E1BEE7;
                transition: all 0.3s;
            }
            
            input, textarea, select {
                width: 100%;
                padding: 15px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: var(--border-radius);
                color: var(--text-light);
                font-size: 16px;
                transition: all 0.3s;
                box-sizing: border-box;
            }
            
            input:focus, textarea:focus, select:focus {
                outline: none;
                border-color: var(--accent-color);
                box-shadow: 0 0 0 2px rgba(225, 190, 231, 0.3);
                background: rgba(255, 255, 255, 0.1);
            }
            
            textarea {
                min-height: 120px;
                resize: vertical;
            }
            
            .rating-container {
                display: flex;
                justify-content: center;
                gap: 15px;
                margin: 15px 0;
            }
            
            .rating-option {
                display: flex;
                flex-direction: column;
                align-items: center;
                cursor: pointer;
                transition: all 0.3s;
                opacity: 0.5;
                filter: grayscale(1);
            }
            
            .rating-option.active {
                opacity: 1;
                filter: none;
                transform: scale(1.1);
            }
            
            .rating-option .emoji {
                font-size: 30px;
                margin-bottom: 5px;
            }
            
            .rating-option .label {
                font-size: 12px;
                text-align: center;
            }
            
            .emotion-options {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 10px;
            }
            
            .emotion-btn {
                padding: 10px 15px;
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 30px;
                color: var(--text-light);
                cursor: pointer;
                transition: all 0.3s;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .emotion-btn:hover {
                background: rgba(255, 255, 255, 0.1);
                transform: translateY(-2px);
            }
            
            .emotion-btn.active {
                background: var(--primary-color);
                border-color: var(--accent-color);
                color: white;
            }
            
            .emotion-btn .emoji {
                font-size: 18px;
            }
            
            .submit-btn {
                width: 100%;
                padding: 15px;
                background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                color: white;
                border: none;
                border-radius: var(--border-radius);
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                margin-top: 20px;
                transition: all 0.3s;
                position: relative;
                overflow: hidden;
            }
            
            .submit-btn::before {
                content: '';
                position: absolute;
                top: 0;
                left: -100%;
                width: 100%;
                height: 100%;
                background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
                transition: all 0.5s;
            }
            
            .submit-btn:hover::before {
                left: 100%;
            }
            
            .submit-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(156, 39, 176, 0.4);
            }
            
            .result-message {
                margin-top: 20px;
                padding: 15px;
                border-radius: var(--border-radius);
                text-align: center;
                opacity: 0;
                transition: all 0.5s;
                transform: translateY(20px);
            }
            
            .result-message.success {
                background: rgba(76, 175, 80, 0.2);
                border: 1px solid rgba(76, 175, 80, 0.5);
                opacity: 1;
                transform: translateY(0);
            }
            
            .result-message.error {
                background: rgba(244, 67, 54, 0.2);
                border: 1px solid rgba(244, 67, 54, 0.5);
                opacity: 1;
                transform: translateY(0);
            }
            
            .cosmic-animation {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 1000;
                opacity: 0;
                transition: opacity 0.5s;
            }
            
            .cosmic-animation.active {
                opacity: 1;
            }
            
            #audioControl {
                position: absolute;
                top: 15px;
                right: 15px;
                background: none;
                border: none;
                color: rgba(255, 255, 255, 0.7);
                font-size: 20px;
                cursor: pointer;
                transition: all 0.3s;
                z-index: 10;
            }
            
            #audioControl:hover {
                color: white;
                transform: scale(1.1);
            }
            
            @media (max-width: 768px) {
                .cosmic-container {
                    width: 95%;
                    padding: 20px;
                }
                
                .rating-container {
                    gap: 10px;
                }
                
                .rating-option .emoji {
                    font-size: 24px;
                }
                
                .emotion-options {
                    justify-content: center;
                }
            }
        </style>
    </head>
    <body>
        <div class="cosmic-container">
            <div class="stars"></div>
            <button id="audioControl">🔊</button>
            
            <h1>Cosmic Feedback</h1>
            
            <div class="form-group">
                <label for="name">Your Name (Optional)</label>
                <input type="text" id="name" placeholder="Enter your name">
            </div>
            
            <div class="form-group">
                <label for="email">Your Email (Optional)</label>
                <input type="email" id="email" placeholder="Enter your email">
            </div>
            
            <div class="form-group">
                <label>How would you rate your experience?</label>
                <div class="rating-container">
                    <div class="rating-option" data-rating="1">
                        <div class="emoji">😞</div>
                        <div class="label">Poor</div>
                    </div>
                    <div class="rating-option" data-rating="2">
                        <div class="emoji">😕</div>
                        <div class="label">Fair</div>
                    </div>
                    <div class="rating-option" data-rating="3">
                        <div class="emoji">😐</div>
                        <div class="label">Okay</div>
                    </div>
                    <div class="rating-option" data-rating="4">
                        <div class="emoji">😊</div>
                        <div class="label">Good</div>
                    </div>
                    <div class="rating-option" data-rating="5">
                        <div class="emoji">🤩</div>
                        <div class="label">Excellent</div>
                    </div>
                </div>
            </div>
            
            <div class="form-group">
                <label for="feedback">Your Feedback</label>
                <textarea id="feedback" placeholder="Share your thoughts with us..."></textarea>
            </div>
            
            <div class="form-group">
                <label>How are you feeling?</label>
                <div class="emotion-options">
                    <div class="emotion-btn" data-emotion="happy">
                        <span class="emoji">😊</span>Happy
                    </div>
                    <div class="emotion-btn" data-emotion="sad">
                        <span class="emoji">😢</span>Sad
                    </div>
                    <div class="emotion-btn" data-emotion="angry">
                        <span class="emoji">😠</span>Frustrated
                    </div>
                    <div class="emotion-btn" data-emotion="surprised">
                        <span class="emoji">😲</span>Surprised
                    </div>
                    <div class="emotion-btn" data-emotion="confused">
                        <span class="emoji">😕</span>Confused
                    </div>
                </div>
            </div>
            
            <button class="submit-btn" id="submitFeedback">Send Cosmic Feedback</button>
            
            <div class="result-message" id="resultMessage"></div>
        </div>
        
        <div class="cosmic-animation" id="cosmicAnimation"></div>
        
        <audio id="feedbackSound" preload="none"></audio>
        
        <script>
            // Generate random stars
            function generateStars() {
                const starsContainer = document.querySelector('.stars');
                const starCount = 50;
                
                for (let i = 0; i < starCount; i++) {
                    const star = document.createElement('div');
                    star.classList.add('star');
                    
                    // Random size
                    const size = Math.random() * 3 + 1;
                    star.style.width = `${size}px`;
                    star.style.height = `${size}px`;
                    
                    // Random position
                    star.style.top = `${Math.random() * 100}%`;
                    star.style.left = `${Math.random() * 100}%`;
                    
                    // Random animation delay
                    star.style.animationDelay = `${Math.random() * 8}s`;
                    
                    starsContainer.appendChild(star);
                }
            }
            
            // Handle rating selection
            function setupRatingOptions() {
                const ratingOptions = document.querySelectorAll('.rating-option');
                
                ratingOptions.forEach(option => {
                    option.addEventListener('click', () => {
                        // Remove active class from all options
                        ratingOptions.forEach(opt => opt.classList.remove('active'));
                        
                        // Add active class to selected option
                        option.classList.add('active');
                    });
                });
            }
            
            // Handle emotion selection
            function setupEmotionButtons() {
                const emotionButtons = document.querySelectorAll('.emotion-btn');
                
                emotionButtons.forEach(button => {
                    button.addEventListener('click', () => {
                        // Remove active class from all buttons
                        emotionButtons.forEach(btn => btn.classList.remove('active'));
                        
                        // Add active class to selected button
                        button.classList.add('active');
                    });
                });
            }
            
            // Handle form submission
            function setupFormSubmission() {
                const submitButton = document.getElementById('submitFeedback');
                const resultMessage = document.getElementById('resultMessage');
                const feedbackSound = document.getElementById('feedbackSound');
                const cosmicAnimation = document.getElementById('cosmicAnimation');
                
                submitButton.addEventListener('click', async () => {
                    // Get form values
                    const name = document.getElementById('name').value || 'Anonymous';
                    const email = document.getElementById('email').value || '';
                    const feedback = document.getElementById('feedback').value;
                    
                    // Get selected rating
                    const selectedRating = document.querySelector('.rating-option.active');
                    const rating = selectedRating ? parseInt(selectedRating.dataset.rating) : null;
                    
                    // Get selected emotion
                    const selectedEmotion = document.querySelector('.emotion-btn.active');
                    const emotion = selectedEmotion ? selectedEmotion.dataset.emotion : 'default';
                    
                    // Validate feedback
                    if (!feedback) {
                        resultMessage.textContent = 'Please provide your feedback before submitting.';
                        resultMessage.className = 'result-message error';
                        return;
                    }
                    
                    // Prepare data
                    const data = {
                        name,
                        email,
                        feedback,
                        rating,
                        emotion,
                        language: 'en',
                        app_version: '1.0',
                        device_info: navigator.userAgent
                    };
                    
                    try {
                        // Show loading state
                        submitButton.disabled = true;
                        submitButton.textContent = 'Sending...';
                        
                        // Submit feedback to API
                        const response = await fetch('/api/user-feedback', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(data)
                        });
                        
                        const result = await response.json();
                        
                        if (result.success) {
                            // Show success message
                            resultMessage.textContent = result.message;
                            resultMessage.className = 'result-message success';
                            
                            // Play sound effect if available
                            if (result.sound_effect) {
                                feedbackSound.src = result.sound_effect;
                                feedbackSound.play().catch(e => console.log('Audio play prevented:', e));
                            }
                            
                            // Show animation based on emotion effect
                            if (result.emotion_effect) {
                                showEmotionAnimation(result.emotion_effect);
                            }
                            
                            // Reset form
                            document.getElementById('name').value = '';
                            document.getElementById('email').value = '';
                            document.getElementById('feedback').value = '';
                            document.querySelectorAll('.rating-option').forEach(opt => opt.classList.remove('active'));
                            document.querySelectorAll('.emotion-btn').forEach(btn => btn.classList.remove('active'));
                        } else {
                            // Show error message
                            resultMessage.textContent = result.error || 'An error occurred. Please try again.';
                            resultMessage.className = 'result-message error';
                        }
                    } catch (error) {
                        console.error('Error submitting feedback:', error);
                        resultMessage.textContent = 'An error occurred. Please try again.';
                        resultMessage.className = 'result-message error';
                    } finally {
                        // Reset button state
                        submitButton.disabled = false;
                        submitButton.textContent = 'Send Cosmic Feedback';
                    }
                });
            }
            
            // Show emotion-based animation
            function showEmotionAnimation(emotion) {
                const cosmicAnimation = document.getElementById('cosmicAnimation');
                
                // Clear previous animation
                cosmicAnimation.innerHTML = '';
                
                // Add emotion-specific animation
                switch (emotion) {
                    case 'happy':
                        cosmicAnimation.style.background = 'radial-gradient(circle, rgba(255,215,0,0.2) 0%, rgba(255,215,0,0) 70%)';
                        
                        for (let i = 0; i < 30; i++) {
                            const star = document.createElement('div');
                            star.style.position = 'absolute';
                            star.style.width = `${Math.random() * 20 + 10}px`;
                            star.style.height = star.style.width;
                            star.style.borderRadius = '50%';
                            star.style.backgroundColor = 'rgba(255, 215, 0, 0.7)';
                            star.style.boxShadow = '0 0 20px gold';
                            star.style.top = `${Math.random() * 100}%`;
                            star.style.left = `${Math.random() * 100}%`;
                            star.style.animation = `pulse ${Math.random() * 2 + 1}s infinite alternate`;
                            
                            cosmicAnimation.appendChild(star);
                        }
                        break;
                        
                    case 'sad':
                        cosmicAnimation.style.background = 'radial-gradient(circle, rgba(0,0,255,0.1) 0%, rgba(0,0,255,0) 70%)';
                        
                        for (let i = 0; i < 20; i++) {
                            const drop = document.createElement('div');
                            drop.style.position = 'absolute';
                            drop.style.width = '2px';
                            drop.style.height = `${Math.random() * 50 + 20}px`;
                            drop.style.backgroundColor = 'rgba(100, 150, 255, 0.5)';
                            drop.style.borderRadius = '50%';
                            drop.style.top = `${Math.random() * 100}%`;
                            drop.style.left = `${Math.random() * 100}%`;
                            drop.style.opacity = Math.random();
                            drop.style.animation = `floatingStars ${Math.random() * 3 + 2}s infinite`;
                            
                            cosmicAnimation.appendChild(drop);
                        }
                        break;
                        
                    case 'angry':
                        cosmicAnimation.style.background = 'radial-gradient(circle, rgba(255,0,0,0.1) 0%, rgba(255,0,0,0) 70%)';
                        
                        for (let i = 0; i < 15; i++) {
                            const spark = document.createElement('div');
                            spark.style.position = 'absolute';
                            spark.style.width = `${Math.random() * 5 + 3}px`;
                            spark.style.height = `${Math.random() * 30 + 10}px`;
                            spark.style.backgroundColor = 'rgba(255, 60, 0, 0.7)';
                            spark.style.boxShadow = '0 0 10px red';
                            spark.style.borderRadius = '2px';
                            spark.style.top = `${Math.random() * 100}%`;
                            spark.style.left = `${Math.random() * 100}%`;
                            spark.style.transform = `rotate(${Math.random() * 360}deg)`;
                            spark.style.animation = `pulse ${Math.random() * 0.5 + 0.2}s infinite alternate`;
                            
                            cosmicAnimation.appendChild(spark);
                        }
                        break;
                        
                    default:
                        cosmicAnimation.style.background = 'radial-gradient(circle, rgba(147, 112, 219, 0.1) 0%, rgba(147, 112, 219, 0) 70%)';
                        
                        for (let i = 0; i < 20; i++) {
                            const particle = document.createElement('div');
                            particle.style.position = 'absolute';
                            particle.style.width = `${Math.random() * 10 + 5}px`;
                            particle.style.height = particle.style.width;
                            particle.style.backgroundColor = 'rgba(147, 112, 219, 0.5)';
                            particle.style.borderRadius = '50%';
                            particle.style.top = `${Math.random() * 100}%`;
                            particle.style.left = `${Math.random() * 100}%`;
                            particle.style.animation = `floatingStars ${Math.random() * 3 + 2}s infinite`;
                            
                            cosmicAnimation.appendChild(particle);
                        }
                }
                
                // Show animation
                cosmicAnimation.classList.add('active');
                
                // Hide animation after 3 seconds
                setTimeout(() => {
                    cosmicAnimation.classList.remove('active');
                }, 3000);
            }
            
            // Toggle audio
            function setupAudioControl() {
                const audioControl = document.getElementById('audioControl');
                let audioEnabled = true;
                
                audioControl.addEventListener('click', () => {
                    audioEnabled = !audioEnabled;
                    audioControl.textContent = audioEnabled ? '🔊' : '🔇';
                    
                    // Mute/unmute the audio element
                    document.getElementById('feedbackSound').muted = !audioEnabled;
                });
            }
            
            // Initialize when DOM is loaded
            document.addEventListener('DOMContentLoaded', () => {
                generateStars();
                setupRatingOptions();
                setupEmotionButtons();
                setupFormSubmission();
                setupAudioControl();
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@feedback_bp.route('/simple-feedback-test', methods=['GET'])
def simple_feedback_test():
    """
    Return a simple HTML page for testing the feedback API
    """
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Simple Feedback Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: #fff;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            label {
                display: block;
                margin: 10px 0 5px;
            }
            input, textarea {
                width: 100%;
                padding: 8px;
                margin-bottom: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            textarea {
                height: 100px;
            }
            button {
                background: #4CAF50;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background: #45a049;
            }
            #result {
                margin-top: 20px;
                padding: 10px;
                background: #f9f9f9;
                border-left: 4px solid #4CAF50;
                display: none;
            }
            .error {
                background: #f9f9f9;
                border-left: 4px solid #f44336;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Simple Feedback Test</h1>
            
            <div>
                <label for="name">Name:</label>
                <input type="text" id="name" placeholder="Your name (optional)">
            </div>
            
            <div>
                <label for="email">Email:</label>
                <input type="email" id="email" placeholder="Your email (optional)">
            </div>
            
            <div>
                <label for="feedback">Feedback:</label>
                <textarea id="feedback" placeholder="Enter your feedback here..."></textarea>
            </div>
            
            <div>
                <label for="rating">Rating (1-5):</label>
                <input type="number" id="rating" min="1" max="5" value="5">
            </div>
            
            <div>
                <label for="emotion">Emotion:</label>
                <select id="emotion">
                    <option value="happy">Happy</option>
                    <option value="sad">Sad</option>
                    <option value="angry">Angry</option>
                    <option value="default">Neutral</option>
                </select>
            </div>
            
            <button id="submitBtn">Submit Feedback</button>
            
            <div id="result"></div>
            
            <div style="margin-top: 20px; padding: 10px; background: #f5f5f5; border-radius: 4px;">
                <h3>API Verification:</h3>
                <button id="verifyBtn">Verify API Connection</button>
                <div id="verifyResult" style="margin-top: 10px; display: none;"></div>
            </div>
        </div>
        
        <script>
            document.getElementById('submitBtn').addEventListener('click', async () => {
                const name = document.getElementById('name').value || 'Anonymous';
                const email = document.getElementById('email').value || '';
                const feedback = document.getElementById('feedback').value;
                const rating = parseInt(document.getElementById('rating').value);
                const emotion = document.getElementById('emotion').value;
                
                if (!feedback) {
                    showResult('Please enter your feedback', true);
                    return;
                }
                
                const data = {
                    name,
                    email,
                    feedback,
                    rating,
                    emotion,
                    language: 'en',
                    app_version: '1.0',
                    device_info: navigator.userAgent
                };
                
                try {
                    const response = await fetch('/api/user-feedback', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        showResult(`Success: ${result.message}<br>ID: ${result.feedback_id}<br>Timestamp: ${result.timestamp}`);
                        
                        // Clear form
                        document.getElementById('name').value = '';
                        document.getElementById('email').value = '';
                        document.getElementById('feedback').value = '';
                        document.getElementById('rating').value = '5';
                    } else {
                        showResult(`Error: ${result.error || 'Unknown error'}`, true);
                    }
                } catch (error) {
                    showResult(`Error: ${error.message}`, true);
                }
            });
            
            document.getElementById('verifyBtn').addEventListener('click', async () => {
                try {
                    const response = await fetch('/api/verify-feedback');
                    const result = await response.json();
                    
                    const verifyResult = document.getElementById('verifyResult');
                    verifyResult.style.display = 'block';
                    
                    if (result.success) {
                        verifyResult.innerHTML = `
                            <div style="color: green;">
                                <strong>✓ API is operational</strong><br>
                                Status: ${result.status}<br>
                                Version: ${result.version}<br>
                                Timestamp: ${result.timestamp}
                            </div>
                        `;
                    } else {
                        verifyResult.innerHTML = `
                            <div style="color: red;">
                                <strong>✗ API is not responding correctly</strong><br>
                                Error: ${result.error || 'Unknown error'}
                            </div>
                        `;
                    }
                } catch (error) {
                    const verifyResult = document.getElementById('verifyResult');
                    verifyResult.style.display = 'block';
                    verifyResult.innerHTML = `
                        <div style="color: red;">
                            <strong>✗ API connection failed</strong><br>
                            Error: ${error.message}
                        </div>
                    `;
                }
            });
            
            function showResult(message, isError = false) {
                const resultElement = document.getElementById('result');
                resultElement.innerHTML = message;
                resultElement.style.display = 'block';
                
                if (isError) {
                    resultElement.classList.add('error');
                } else {
                    resultElement.classList.remove('error');
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)