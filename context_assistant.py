"""
Contextual Voice Assistant for Robin AI
Handles context-aware conversations with personality-driven responses
"""

import logging
import json
import random
import re
from datetime import datetime
from collections import deque
import os

logger = logging.getLogger(__name__)

class ContextAssistant:
    """Manages contextual conversations with personality-driven responses"""
    
    def __init__(self, db_manager, profile_manager, emotion_tracker=None, intent_classifier=None):
        """Initialize the context assistant with necessary dependencies"""
        self.db_manager = db_manager
        self.profile_manager = profile_manager
        self.emotion_tracker = emotion_tracker
        self.intent_classifier = intent_classifier
        
        # Context memory maintains recent conversations
        self.context_memory = deque(maxlen=10)  # Remember last 10 exchanges
        
        # Personality traits and their response styles
        self.personality_traits = {
            'playful': {
                'greeting_patterns': [
                    "Hey there, {name}! What's up?",
                    "Hi {name}! Great to chat with you!",
                    "Hello {name}! Ready for some fun conversation?"
                ],
                'response_patterns': [
                    "That's super interesting, {name}! Tell me more!",
                    "Oh wow, I love hearing about that!",
                    "Cool! I'm totally with you on that!",
                    "That's awesome! What else is on your mind?"
                ],
                'question_patterns': [
                    "What's the most exciting thing you've done lately?",
                    "If you could have any superpower, what would it be?",
                    "What's making you smile today?",
                    "What's something fun you're looking forward to?"
                ],
                'agreement_patterns': [
                    "Totally agree!",
                    "You got it!",
                    "Absolutely right!",
                    "You know it!"
                ],
                'empathy_patterns': [
                    "I get how you feel!",
                    "Sounds like you're having a blast!",
                    "I'm right there with you!",
                    "I can totally relate to that feeling!"
                ],
                'word_choices': {
                    'positive': ['awesome', 'amazing', 'fantastic', 'super', 'cool'],
                    'negative': ['bummer', 'not great', 'unfortunate', 'rough'],
                    'intensifiers': ['totally', 'absolutely', 'incredibly', 'really'],
                    'fillers': ['like', 'you know', 'so', 'basically']
                }
            },
            'formal': {
                'greeting_patterns': [
                    "Good day, {name}. How may I assist you?",
                    "Greetings, {name}. How are you today?",
                    "Welcome, {name}. What can I help you with?"
                ],
                'response_patterns': [
                    "I understand your point, {name}. Please continue.",
                    "That's a valid observation. Would you care to elaborate?",
                    "I appreciate your perspective on this matter.",
                    "Thank you for sharing that information."
                ],
                'question_patterns': [
                    "What matters would you like to discuss today?",
                    "How may I be of service to you at this time?",
                    "Is there a specific topic you would like to explore?",
                    "What information would be most valuable to you right now?"
                ],
                'agreement_patterns': [
                    "I concur with your assessment.",
                    "Your conclusion is accurate.",
                    "That is a correct analysis.",
                    "Your reasoning is sound."
                ],
                'empathy_patterns': [
                    "I understand that might be challenging.",
                    "Your situation is acknowledged.",
                    "I recognize the importance of this to you.",
                    "Your concerns are valid and noteworthy."
                ],
                'word_choices': {
                    'positive': ['excellent', 'beneficial', 'advantageous', 'optimal'],
                    'negative': ['unfortunate', 'suboptimal', 'challenging', 'concerning'],
                    'intensifiers': ['particularly', 'notably', 'significantly', 'considerably'],
                    'fillers': ['however', 'moreover', 'furthermore', 'indeed']
                }
            },
            'calm': {
                'greeting_patterns': [
                    "Hello {name}, it's nice to see you today.",
                    "Hi {name}, how are you feeling?",
                    "Greetings {name}, I hope you're having a peaceful day."
                ],
                'response_patterns': [
                    "I see what you mean, {name}. That's interesting.",
                    "Thank you for sharing that with me.",
                    "I appreciate your thoughts on this.",
                    "That's a thoughtful perspective."
                ],
                'question_patterns': [
                    "What's on your mind today?",
                    "How have you been feeling lately?",
                    "Is there something specific you'd like to talk about?",
                    "What would you like to explore in our conversation?"
                ],
                'agreement_patterns': [
                    "Yes, I agree with you.",
                    "That makes sense to me.",
                    "I can see why you feel that way.",
                    "You have a good point there."
                ],
                'empathy_patterns': [
                    "I understand how you feel.",
                    "That sounds like it was meaningful for you.",
                    "I can see why that would be important.",
                    "Your feelings about this are completely valid."
                ],
                'word_choices': {
                    'positive': ['good', 'nice', 'pleasant', 'helpful'],
                    'negative': ['difficult', 'challenging', 'uncomfortable', 'tough'],
                    'intensifiers': ['quite', 'rather', 'fairly', 'somewhat'],
                    'fillers': ['well', 'hmm', 'I see', 'you know']
                }
            },
            'assertive': {
                'greeting_patterns': [
                    "Hello {name}, I'm ready when you are.",
                    "Hi {name}, let's get started.",
                    "Greetings {name}, what can we accomplish today?"
                ],
                'response_patterns': [
                    "Here's what I think about that, {name}.",
                    "Let me be direct with you.",
                    "From my perspective, this is important.",
                    "I have a clear view on this matter."
                ],
                'question_patterns': [
                    "What specific results are you looking for?",
                    "What's your goal here?",
                    "How should we prioritize this?",
                    "What's the next step you want to take?"
                ],
                'agreement_patterns': [
                    "Yes, that's exactly right.",
                    "I completely agree.",
                    "That's the correct approach.",
                    "You've got the right idea."
                ],
                'empathy_patterns': [
                    "I understand your position.",
                    "Your concern is valid and needs addressing.",
                    "I recognize why this matters to you.",
                    "Your perspective makes perfect sense."
                ],
                'word_choices': {
                    'positive': ['effective', 'successful', 'productive', 'valuable'],
                    'negative': ['ineffective', 'problematic', 'counterproductive', 'wasteful'],
                    'intensifiers': ['definitely', 'certainly', 'absolutely', 'clearly'],
                    'fillers': ['listen', 'look', 'understand this', 'simply put']
                }
            }
        }
        
        # Additional language support
        self.arabic_personality_traits = {
            'playful': {
                'greeting_patterns': [
                    "مرحباً {name}! كيف حالك؟",
                    "أهلاً {name}! سعيد بالتحدث معك!",
                    "هاي {name}! جاهز لمحادثة ممتعة؟"
                ],
                'response_patterns': [
                    "هذا مثير للاهتمام، {name}! أخبرني المزيد!",
                    "واو، أحب سماع ذلك!",
                    "رائع! أنا متفق معك تماماً!",
                    "هذا مذهل! ما الذي يدور في ذهنك أيضاً؟"
                ],
                # Additional Arabic patterns would be defined similarly
            },
            'formal': {
                'greeting_patterns': [
                    "السلام عليكم {name}. كيف يمكنني مساعدتك؟",
                    "تحياتي، {name}. كيف حالك اليوم؟",
                    "مرحباً بك، {name}. بماذا يمكنني أن أخدمك؟"
                ],
                # Additional patterns would be defined
            },
            # Other personalities would be defined for Arabic
        }
        
        # Load conversation topics and contextual responses
        self.topics = {
            'weather': {
                'keywords': ['weather', 'rain', 'sunny', 'temperature', 'hot', 'cold', 'forecast'],
                'questions': [
                    "How's the weather where you are?",
                    "Do you prefer sunny or rainy days?",
                    "What's your favorite season?"
                ],
                'responses': {
                    'playful': [
                        "Weather can totally change the mood, right? I'm always up for a sunny day!",
                        "Rain or shine, we can still have a great conversation!",
                        "If I could control the weather, it would be perfect all the time for you!"
                    ],
                    'formal': [
                        "The weather does indeed have a significant impact on daily activities.",
                        "Weather patterns are fascinating from both scientific and experiential perspectives.",
                        "I appreciate your observation regarding the meteorological conditions."
                    ],
                    'calm': [
                        "Weather can be quite influential on our mood and energy.",
                        "I find it peaceful to observe the changing weather patterns.",
                        "It's nice to appreciate whatever weather we have today."
                    ],
                    'assertive': [
                        "Weather conditions are important to consider when planning activities.",
                        "Let's focus on how to make the best of today's weather.",
                        "Here's what I think about this weather situation."
                    ]
                }
            },
            'technology': {
                'keywords': ['technology', 'computer', 'phone', 'device', 'app', 'software', 'digital'],
                'questions': [
                    "What technology do you use most often?",
                    "How do you feel about AI and the future of technology?",
                    "What's your favorite app or digital tool?"
                ],
                'responses': {
                    # Responses for each personality type would be defined
                }
            },
            'health': {
                'keywords': ['health', 'exercise', 'fitness', 'diet', 'sleep', 'wellness', 'meditation'],
                'questions': [
                    "How do you take care of your health?",
                    "Do you have any favorite wellness practices?",
                    "What helps you feel your best?"
                ],
                'responses': {
                    # Responses for each personality type would be defined
                }
            }
            # Additional topics would be defined
        }
        
        # Context categories to track
        self.context_categories = [
            'time_of_day',  # morning, afternoon, evening, night
            'user_emotion',  # happy, sad, neutral, etc.
            'conversation_topic',  # weather, technology, personal, etc.
            'previous_exchanges',  # count of back-and-forth exchanges
            'user_engagement'  # high, medium, low based on response length/time
        ]
        
        # Time-based greetings
        self.time_greetings = {
            'morning': {
                'en': [
                    "Good morning, {name}! How's your day starting?",
                    "Morning, {name}! Hope you slept well.",
                    "Hello {name}, it's a fresh new morning!"
                ],
                'ar': [
                    "صباح الخير يا {name}! كيف بدأ يومك؟",
                    "صباحك سعيد يا {name}! أتمنى أنك نمت جيداً.",
                    "مرحباً {name}، إنه صباح جديد منعش!"
                ]
            },
            'afternoon': {
                'en': [
                    "Good afternoon, {name}! How's your day going?",
                    "Hello {name}, hope you're having a productive afternoon!",
                    "Hi {name}, how has your day been so far?"
                ],
                'ar': [
                    "مساء الخير يا {name}! كيف يسير يومك؟",
                    "مرحباً {name}، أتمنى أن تمضي فترة ما بعد الظهر بشكل منتج!",
                    "مرحباً {name}، كيف كان يومك حتى الآن؟"
                ]
            },
            'evening': {
                'en': [
                    "Good evening, {name}! How was your day?",
                    "Evening, {name}! Winding down for the day?",
                    "Hello {name}, hope you had a great day!"
                ],
                'ar': [
                    "مساء الخير يا {name}! كيف كان يومك؟",
                    "مساء الخير {name}! هل تستعد لنهاية اليوم؟",
                    "مرحباً {name}، أتمنى أن يكون يومك رائعاً!"
                ]
            },
            'night': {
                'en': [
                    "Hello {name}, you're up late! How can I help you tonight?",
                    "Good night, {name}. What's keeping you awake?",
                    "Hi {name}, hope you're having a peaceful night."
                ],
                'ar': [
                    "مرحباً {name}، أنت مستيقظ متأخراً! كيف يمكنني مساعدتك الليلة؟",
                    "ليلة سعيدة يا {name}. ما الذي يبقيك مستيقظاً؟",
                    "مرحباً {name}، أتمنى أن تقضي ليلة هادئة."
                ]
            }
        }
    
    def get_current_time_of_day(self):
        """Determine the current time of day (morning, afternoon, evening, night)"""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 12:
            return 'morning'
        elif 12 <= current_hour < 17:
            return 'afternoon'
        elif 17 <= current_hour < 22:
            return 'evening'
        else:
            return 'night'
    
    def add_to_context(self, user_input, response, emotion=None, intent=None):
        """Add an exchange to the context memory"""
        exchange = {
            'user_input': user_input,
            'response': response,
            'emotion': emotion,
            'intent': intent,
            'timestamp': datetime.now().isoformat()
        }
        
        self.context_memory.append(exchange)
        return exchange
    
    def get_context_summary(self):
        """Generate a summary of the current conversation context"""
        if not self.context_memory:
            return {
                'exchanges': 0,
                'primary_emotion': 'neutral',
                'topics': [],
                'duration_minutes': 0,
                'time_of_day': self.get_current_time_of_day()
            }
        
        # Count exchanges
        exchanges = len(self.context_memory)
        
        # Determine primary emotion
        emotions = [exchange.get('emotion', 'neutral') for exchange in self.context_memory 
                    if exchange.get('emotion')]
        primary_emotion = max(set(emotions), key=emotions.count) if emotions else 'neutral'
        
        # Identify potential topics (simplified approach)
        all_text = ' '.join([exchange.get('user_input', '') for exchange in self.context_memory])
        topics = []
        for topic, data in self.topics.items():
            for keyword in data['keywords']:
                if keyword.lower() in all_text.lower():
                    topics.append(topic)
                    break
        
        # Calculate conversation duration
        if exchanges > 1:
            try:
                start_time = datetime.fromisoformat(self.context_memory[0]['timestamp'])
                end_time = datetime.fromisoformat(self.context_memory[-1]['timestamp'])
                duration_minutes = (end_time - start_time).total_seconds() / 60
            except (KeyError, ValueError, IndexError):
                duration_minutes = 0
        else:
            duration_minutes = 0
        
        return {
            'exchanges': exchanges,
            'primary_emotion': primary_emotion,
            'topics': list(set(topics)),  # Remove duplicates
            'duration_minutes': duration_minutes,
            'time_of_day': self.get_current_time_of_day()
        }
    
    def get_time_appropriate_greeting(self, name=None, language='en'):
        """Get a greeting appropriate for the current time of day"""
        profile = self.profile_manager.get_current_profile()
        personality = profile.get('preferred_tone', 'calm')
        time_of_day = self.get_current_time_of_day()
        
        if not name:
            name = profile.get('nickname', 'User')
            
        # Get greetings for this time of day
        time_greetings = self.time_greetings.get(time_of_day, {}).get(language, [])
        if not time_greetings:
            # Fallback to personality-based greeting
            if language == 'ar':
                greetings = self.arabic_personality_traits.get(personality, {}).get('greeting_patterns', [])
            else:
                greetings = self.personality_traits.get(personality, {}).get('greeting_patterns', [])
        else:
            greetings = time_greetings
            
        # Select a random greeting and format with name
        if greetings:
            greeting = random.choice(greetings)
            return greeting.format(name=name)
        else:
            # Ultimate fallback
            return "Hello, {name}!".format(name=name) if language == 'en' else "مرحباً, {name}!".format(name=name)
    
    def detect_topic(self, text):
        """Detect the likely conversation topic from user input"""
        text = text.lower()
        matched_topics = []
        
        for topic, data in self.topics.items():
            for keyword in data['keywords']:
                if keyword.lower() in text:
                    matched_topics.append((topic, 1))  # Simple matching for now
                    
        # Sort by match strength and return the top topic
        if matched_topics:
            matched_topics.sort(key=lambda x: x[1], reverse=True)
            return matched_topics[0][0]
        
        return None
    
    def get_personality_response(self, user_input, emotion=None, intent=None):
        """Generate a personality-driven contextual response"""
        # Get the current user profile and preferences
        profile = self.profile_manager.get_current_profile()
        personality = profile.get('preferred_tone', 'calm')
        language = profile.get('language', 'en')
        name = profile.get('nickname', 'User')
        
        # Get context summary
        context = self.get_context_summary()
        
        # Detect emotion if not provided
        if not emotion and self.emotion_tracker:
            emotion = self.emotion_tracker.analyze_text(user_input)
        
        # Detect intent if not provided
        if not intent and self.intent_classifier:
            intent = self.intent_classifier.classify(user_input)
        
        # Detect topic
        topic = self.detect_topic(user_input) or (context['topics'][0] if context['topics'] else None)
        
        # Generate response based on topic, personality, context, and language
        response = self.generate_contextual_response(
            user_input=user_input,
            personality=personality,
            topic=topic,
            context=context,
            emotion=emotion,
            intent=intent,
            language=language,
            name=name
        )
        
        # Add this exchange to context
        self.add_to_context(user_input, response, emotion, intent)
        
        # Also log to database if available
        if self.db_manager:
            self.db_manager.log_conversation(user_input, response, emotion=emotion, intent=intent)
        
        return response
    
    def generate_contextual_response(self, user_input, personality, topic, context, emotion, intent, language, name):
        """Generate a response based on all contextual factors"""
        # First exchange in conversation
        if context['exchanges'] == 0:
            return self.get_time_appropriate_greeting(name, language)
        
        # If we have a detected topic and specific responses for it
        if topic and topic in self.topics:
            topic_data = self.topics[topic]
            personality_responses = topic_data['responses'].get(personality, [])
            
            if personality_responses:
                response = random.choice(personality_responses)
                return response.format(name=name)
        
        # Get generic responses based on personality if no topic match
        personality_data = self.personality_traits.get(personality, self.personality_traits['calm'])
        
        # Different response types based on context
        if context['exchanges'] <= 2:
            # Early in conversation, ask questions
            patterns = personality_data['question_patterns']
        elif 'question' in user_input.lower() or user_input.endswith('?'):
            # User asked a question, provide thoughtful response
            patterns = personality_data['response_patterns']
        elif len(user_input) < 20:
            # Short input, encourage more sharing
            patterns = personality_data['question_patterns'] 
        else:
            # Standard response
            patterns = personality_data['response_patterns']
        
        # Handle emotional content
        if emotion and emotion != 'neutral':
            # Add empathetic response for emotional content
            empathy_patterns = personality_data['empathy_patterns']
            if empathy_patterns:
                response = random.choice(empathy_patterns)
                return response.format(name=name)
        
        # Select and format response
        if patterns:
            response = random.choice(patterns)
            return response.format(name=name)
        
        # Absolute fallback
        return f"I understand, {name}. Please tell me more."
        
    def get_conversation_history(self, limit=5):
        """Get recent conversation history from context memory"""
        return list(self.context_memory)[-limit:] if self.context_memory else []

"""
Usage example:

context_assistant = ContextAssistant(db_manager, profile_manager, emotion_tracker, intent_classifier)
response = context_assistant.get_personality_response("How's the weather today?")
"""