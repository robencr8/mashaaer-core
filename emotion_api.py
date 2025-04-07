"""
Emotion API for Mashaaer Feelings
Provides advanced emotion analysis for text input with multi-language support
"""

import os
import logging
import json
from flask import Blueprint, request, jsonify, render_template_string
from datetime import datetime
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from textblob import TextBlob
import nltk
from nltk.corpus import wordnet
import re

# Configure logger
logger = logging.getLogger(__name__)

# Try to download NLTK resources if not already available
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

# Create Blueprint
emotion_bp = Blueprint('emotion_api', __name__, url_prefix='/api')

# Dictionary of emotion keywords
EMOTION_KEYWORDS = {
    # English emotions
    'happy': ['happy', 'joy', 'delight', 'ecstatic', 'content', 'cheerful', 'glad', 'pleased', 'thrilled', 'elated', 'excited', 'satisfied'],
    'sad': ['sad', 'unhappy', 'sorrowful', 'depressed', 'down', 'miserable', 'gloomy', 'heartbroken', 'grief', 'despair', 'melancholic'],
    'angry': ['angry', 'mad', 'furious', 'outraged', 'irritated', 'annoyed', 'frustrated', 'enraged', 'hostile', 'infuriated'],
    'fear': ['afraid', 'scared', 'fearful', 'terrified', 'worried', 'anxious', 'panicked', 'nervous', 'dread', 'uneasy', 'tense'],
    'surprise': ['surprised', 'amazed', 'astonished', 'shocked', 'stunned', 'startled', 'speechless', 'dumbfounded', 'unexpected'],
    'disgust': ['disgusted', 'revolted', 'nauseated', 'repulsed', 'sick', 'appalled', 'horrified', 'distaste', 'aversion'],
    'calm': ['calm', 'peaceful', 'relaxed', 'tranquil', 'serene', 'composed', 'collected', 'centered', 'balanced', 'composed'],
    'love': ['love', 'adore', 'cherish', 'affection', 'fondness', 'devoted', 'passionate', 'attracted', 'caring', 'tender'],
    'confused': ['confused', 'puzzled', 'perplexed', 'bewildered', 'disoriented', 'unsure', 'uncertain', 'ambivalent'],
    'embarrassed': ['embarrassed', 'ashamed', 'humiliated', 'mortified', 'self-conscious', 'uncomfortable'],
    'bored': ['bored', 'uninterested', 'apathetic', 'indifferent', 'monotonous', 'tedious', 'dull', 'weary'],
    'hopeful': ['hopeful', 'optimistic', 'encouraged', 'positive', 'expectant', 'anticipation', 'looking forward'],
    'proud': ['proud', 'accomplished', 'satisfied', 'successful', 'confident', 'self-assured', 'triumphant'],
    'grateful': ['grateful', 'thankful', 'appreciative', 'blessed', 'indebted', 'obliged', 'appreciative'],
    
    # Arabic emotions (transliterated and English keywords that map to Arabic words)
    'سعيد': ['سعادة', 'فرح', 'بهجة', 'مسرور', 'مبتهج', 'راضي', 'سرور', 'ابتهاج', 'نشوة', 'انشراح', 'saeed', 'farah'],
    'حزين': ['حزن', 'كآبة', 'أسى', 'حسرة', 'غم', 'مكتئب', 'مهموم', 'مغموم', 'أسف', 'hazeen', 'hozn'],
    'غاضب': ['غضب', 'سخط', 'استياء', 'انفعال', 'هياج', 'حنق', 'ghadeb', 'sakht', 'infial'],
    'خائف': ['خوف', 'فزع', 'رعب', 'هلع', 'قلق', 'توتر', 'وجل', 'خشية', 'kha\'ef', 'khawf', 'faza'],
    'متفاجئ': ['مفاجأة', 'دهشة', 'ذهول', 'استغراب', 'صدمة', 'mufaja\'a', 'dahsha'],
    'مقرف': ['اشمئزاز', 'قرف', 'تقزز', 'نفور', 'iqraf', 'ishmi\'zaz'],
    'هادئ': ['هدوء', 'سكينة', 'طمأنينة', 'راحة', 'استرخاء', 'سلام', 'hadi', 'sukoon', 'istirkha'],
    'حب': ['محبة', 'عشق', 'ود', 'هيام', 'غرام', 'شغف', 'hubb', 'ishq', 'shaghaf'],
    'مشوش': ['ارتباك', 'حيرة', 'تشويش', 'تردد', 'mushawash', 'irtibak', 'hayra'],
    'محرج': ['إحراج', 'خجل', 'عار', 'خزي', 'muhrij', 'khajal'],
    'ملل': ['ضجر', 'سأم', 'رتابة', 'malal', 'sa\'am'],
    'أمل': ['رجاء', 'تفاؤل', 'توقع', 'amal', 'raja', 'tafa\'ul'],
    'فخور': ['فخر', 'اعتزاز', 'مباهاة', 'fakhr', 'i\'tizaz'],
    'ممتن': ['امتنان', 'شكر', 'عرفان', 'imtinan', 'shukr']
}

# Custom emotional phrases with higher weight
EMOTION_PHRASES = {
    # English phrases
    'happy': [
        "I feel great", "having a good day", "feeling wonderful", "so pleased", 
        "really happy", "brings me joy", "over the moon", "on cloud nine"
    ],
    'sad': [
        "feeling down", "makes me sad", "heart is heavy", "feel like crying", 
        "in tears", "deeply saddened", "lost and alone", "feel empty"
    ],
    'angry': [
        "makes me mad", "so frustrated", "pisses me off", "sick and tired", 
        "fed up", "had enough", "makes my blood boil", "drives me crazy"
    ],
    
    # Arabic phrases (with transliteration)
    'سعيد': ["أشعر بسعادة كبيرة", "يومي رائع", "أشعر بالفرح", "سعيد جداً"],
    'حزين': ["أشعر بالحزن", "قلبي مثقل", "أريد أن أبكي", "مكتئب للغاية"],
    'غاضب': ["هذا يغضبني", "أشعر بالإحباط", "سئمت من هذا", "لا أطيق هذا"]
}

# Intensity modifiers with weights
INTENSITY_MODIFIERS = {
    'extremely': 1.5, 'incredibly': 1.5, 'really': 1.3, 'very': 1.3, 'so': 1.2, 'quite': 1.1,
    'somewhat': 0.7, 'slightly': 0.6, 'a bit': 0.5, 'a little': 0.5,
    'للغاية': 1.5, 'جداً': 1.3, 'كثيراً': 1.3, 'نوعاً ما': 0.7, 'قليلاً': 0.5
}

# Negation words that flip emotion polarity
NEGATION_WORDS = {
    # English negations
    'english': ['not', 'no', "don't", "doesn't", "didn't", "won't", "isn't", "aren't", "wasn't",
               "weren't", "haven't", "hasn't", "hadn't", "cannot", "can't", "couldn't", "wouldn't",
               "shouldn't", "never", "none", "nobody", "nothing", "neither", "nor", "hardly",
               "scarcely", "barely", "rarely"],
    
    # Arabic negations
    'arabic': ['لا', 'لم', 'لن', 'ليس', 'ليست', 'غير', 'ما', 'مش', 'بدون', 'لست', 'لسنا', 'ما']
}

def init_emotion_api(app):
    """Initialize the emotion API blueprint with necessary dependencies"""
    logger.info("Initializing emotion API")
    app.register_blueprint(emotion_bp)
    return emotion_bp

@emotion_bp.route('/emotion', methods=['POST'])
def analyze_emotion():
    """
    Analyze text for emotional content with language detection
    
    Request body:
    {
        "text": "The text to analyze",
        "language": "auto|en|ar",  (optional - auto-detect if not provided or set to "auto")
        "context": ["previous message 1", "previous message 2"]  (optional - previous conversation context)
    }
    
    Returns:
    {
        "success": true,
        "primary_emotion": "happy",
        "emotion_scores": {
            "happy": 0.8,
            "sad": 0.1,
            "angry": 0.0,
            ...
        },
        "detected_language": "en",
        "confidence": 0.85,
        "timestamp": "2025-04-07T12:34:56.789Z"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Missing required parameter: text"
            }), 400
        
        text = data.get('text')
        language = data.get('language', 'auto')
        context = data.get('context', [])
        
        # Analyze the emotional content
        result = analyze_text_emotion(text, language, context)
        
        # Add a timestamp
        result['timestamp'] = datetime.utcnow().isoformat()
        result['success'] = True
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Emotion analysis error: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

def analyze_text_emotion(text, language='auto', context=None):
    """
    Analyze the emotional content of text
    
    Args:
        text (str): The text to analyze
        language (str): Language code ('auto', 'en' or 'ar')
        context (list): Optional list of previous messages for context
        
    Returns:
        dict: Dictionary with primary emotion and scores
    """
    # Auto-detect language if needed
    detected_language = language
    if language == 'auto':
        try:
            detected_language = detect(text)
            # Map to supported languages
            if detected_language.startswith('ar'):
                detected_language = 'ar'
            else:
                detected_language = 'en'  # Default to English for non-Arabic
        except LangDetectException:
            logger.warning(f"Language detection failed for: {text}")
            detected_language = 'en'  # Default to English
    
    # Initialize emotion scores
    emotion_scores = {emotion: 0.0 for emotion in EMOTION_KEYWORDS.keys()}
    
    # Process text
    if detected_language == 'ar':
        # Process Arabic text
        words = re.findall(r'\w+', text.lower())
        # Check for Arabic negations
        has_negation = any(neg in text.lower() for neg in NEGATION_WORDS['arabic'])
    else:
        # Process English text
        words = re.findall(r'\w+', text.lower())
        # Check for English negations
        has_negation = any(neg in text.lower() for neg in NEGATION_WORDS['english'])
    
    # Check for emotional phrases (higher weight)
    for emotion, phrases in EMOTION_PHRASES.items():
        text_lower = text.lower()
        for phrase in phrases:
            if phrase.lower() in text_lower:
                # Phrases have higher weight (2.0)
                emotion_scores[emotion] += 2.0
    
    # Check for individual emotion words
    for emotion, keywords in EMOTION_KEYWORDS.items():
        for word in words:
            if word in keywords:
                # Apply basic emotional word scoring
                emotion_scores[emotion] += 1.0
                
                # Check for intensity modifiers before this word
                for modifier, weight in INTENSITY_MODIFIERS.items():
                    if modifier + ' ' + word in text.lower():
                        emotion_scores[emotion] += weight
    
    # Apply negation (reverses polarity of emotions)
    if has_negation:
        # Create opposite emotion mapping for negation handling
        opposite_emotions = {
            'happy': 'sad', 'sad': 'happy',
            'angry': 'calm', 'calm': 'angry',
            'fear': 'calm', 'disgust': 'happy',
            'love': 'disgust', 'hopeful': 'sad',
            'سعيد': 'حزين', 'حزين': 'سعيد',
            'غاضب': 'هادئ', 'هادئ': 'غاضب',
            'خائف': 'هادئ'
        }
        
        # For each emotion with a score, reduce it and increase its opposite
        for emotion, score in list(emotion_scores.items()):
            if score > 0 and emotion in opposite_emotions:
                opposite = opposite_emotions[emotion]
                # Transfer some of the emotion score to its opposite
                transfer = score * 0.7
                emotion_scores[emotion] -= transfer
                emotion_scores[opposite] += transfer
    
    # Apply sentiment analysis for additional context (for English text)
    if detected_language == 'en':
        try:
            blob = TextBlob(text)
            sentiment = blob.sentiment.polarity  # -1 to 1
            
            # Enhance positive/negative emotions based on sentiment
            if sentiment > 0.3:
                emotion_scores['happy'] += sentiment * 0.5
                emotion_scores['hopeful'] += sentiment * 0.3
            elif sentiment < -0.3:
                emotion_scores['sad'] += abs(sentiment) * 0.5
                emotion_scores['angry'] += abs(sentiment) * 0.3
        except:
            # TextBlob analysis failed, continue without it
            pass
    
    # Add context from previous messages if available (with lesser weight)
    if context:
        context_weight = 0.3
        for prev_message in context[-3:]:  # Use last 3 messages at most
            try:
                prev_result = analyze_text_emotion(prev_message, detected_language, None)
                for emotion, score in prev_result['emotion_scores'].items():
                    emotion_scores[emotion] += score * context_weight
                # Reduce weight for older messages
                context_weight *= 0.5
            except:
                # Skip failed context analysis
                pass
    
    # Normalize scores (0 to 1 range)
    max_score = max(emotion_scores.values()) if emotion_scores.values() else 1.0
    if max_score > 0:
        for emotion in emotion_scores:
            emotion_scores[emotion] /= max_score
    
    # Find primary emotion
    if emotion_scores:
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        confidence = emotion_scores[primary_emotion]
    else:
        primary_emotion = "neutral"
        confidence = 0.0
    
    return {
        "primary_emotion": primary_emotion,
        "emotion_scores": emotion_scores,
        "detected_language": detected_language,
        "confidence": confidence
    }

@emotion_bp.route('/emotion-test', methods=['GET'])
def emotion_test_page():
    """
    Return a simple HTML page to test the emotion API
    """
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Emotion API Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
                background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
            }
            textarea {
                width: 100%;
                padding: 10px;
                min-height: 100px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-bottom: 20px;
                font-size: 16px;
            }
            select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-bottom: 20px;
                font-size: 16px;
            }
            button {
                background: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
                font-size: 16px;
                border-radius: 4px;
                cursor: pointer;
                display: block;
                margin: 0 auto;
            }
            button:hover {
                background: #2980b9;
            }
            #result {
                margin-top: 20px;
                padding: 15px;
                background: #f7f7f7;
                border-radius: 4px;
                white-space: pre-wrap;
                overflow-x: auto;
                display: none;
            }
            .emotion-bar {
                height: 20px;
                background: #f1f1f1;
                margin-top: 5px;
                border-radius: 10px;
                overflow: hidden;
            }
            .emotion-fill {
                height: 100%;
                background: linear-gradient(90deg, #3498db, #2980b9);
                width: 0;
                transition: width 0.5s;
                border-radius: 10px;
            }
            .emotion-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 10px;
                margin-top: 20px;
            }
            .emotion-item {
                margin-bottom: 10px;
            }
            .emotion-label {
                display: flex;
                justify-content: space-between;
            }
            .loading {
                text-align: center;
                margin-top: 20px;
                display: none;
            }
            .spinner {
                border: 4px solid rgba(0, 0, 0, 0.1);
                border-left-color: #3498db;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .primary-emotion {
                text-align: center;
                font-size: 24px;
                margin: 20px 0;
                padding: 10px;
                border-radius: 5px;
                background: #f1f1f1;
                display: none;
            }
            .language-detected {
                text-align: center;
                margin-bottom: 10px;
                font-style: italic;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Emotion Analysis API Test</h1>
            
            <label for="text">Enter text to analyze:</label>
            <textarea id="text" placeholder="Type your text here..."></textarea>
            
            <label for="language">Language:</label>
            <select id="language">
                <option value="auto">Auto-detect</option>
                <option value="en">English</option>
                <option value="ar">Arabic</option>
            </select>
            
            <button id="analyze">Analyze Emotion</button>
            
            <div class="loading">
                <div class="spinner"></div>
                <p>Analyzing...</p>
            </div>
            
            <div class="primary-emotion" id="primaryEmotion"></div>
            <div class="language-detected" id="languageDetected"></div>
            
            <div class="emotion-grid" id="emotionGrid"></div>
            
            <pre id="result"></pre>
        </div>
        
        <script>
            document.getElementById('analyze').addEventListener('click', async () => {
                const text = document.getElementById('text').value;
                const language = document.getElementById('language').value;
                
                if (!text) {
                    alert('Please enter some text to analyze');
                    return;
                }
                
                // Show loading
                document.getElementById('result').style.display = 'none';
                document.getElementById('primaryEmotion').style.display = 'none';
                document.getElementById('emotionGrid').innerHTML = '';
                document.querySelector('.loading').style.display = 'block';
                
                try {
                    const response = await fetch('/api/emotion', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            text,
                            language
                        })
                    });
                    
                    const data = await response.json();
                    
                    // Hide loading
                    document.querySelector('.loading').style.display = 'none';
                    
                    if (data.success) {
                        // Show primary emotion
                        const primaryElement = document.getElementById('primaryEmotion');
                        primaryElement.textContent = `Primary Emotion: ${data.primary_emotion} (${Math.round(data.confidence * 100)}% confidence)`;
                        primaryElement.style.display = 'block';
                        
                        // Show detected language
                        document.getElementById('languageDetected').textContent = 
                            `Detected Language: ${data.detected_language}`;
                        
                        // Create emotion bars
                        const emotionGrid = document.getElementById('emotionGrid');
                        emotionGrid.innerHTML = '';
                        
                        Object.entries(data.emotion_scores)
                            .sort((a, b) => b[1] - a[1]) // Sort by score descending
                            .forEach(([emotion, score]) => {
                                const percent = Math.round(score * 100);
                                if (percent > 0) { // Only show emotions with some score
                                    const item = document.createElement('div');
                                    item.className = 'emotion-item';
                                    
                                    const label = document.createElement('div');
                                    label.className = 'emotion-label';
                                    label.innerHTML = `<span>${emotion}</span><span>${percent}%</span>`;
                                    
                                    const bar = document.createElement('div');
                                    bar.className = 'emotion-bar';
                                    
                                    const fill = document.createElement('div');
                                    fill.className = 'emotion-fill';
                                    bar.appendChild(fill);
                                    
                                    item.appendChild(label);
                                    item.appendChild(bar);
                                    emotionGrid.appendChild(item);
                                    
                                    // Animate the bar fill after a small delay
                                    setTimeout(() => {
                                        fill.style.width = `${percent}%`;
                                    }, 100);
                                }
                            });
                        
                        // Show raw result
                        document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                        document.getElementById('result').style.display = 'block';
                    } else {
                        alert(`Error: ${data.error || 'Unknown error'}`);
                    }
                } catch (error) {
                    document.querySelector('.loading').style.display = 'none';
                    alert(`Error: ${error.message}`);
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html)