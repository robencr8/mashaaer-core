"""
Profile Manager for Robin AI
Handles user profile management, personality inference, and tone adaptation
"""

import os
import json
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class ProfileManager:
    """Manages user profiles with personality and tone analysis"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_profile = None
        
        # Default profile settings
        self.default_profile = {
            'full_name': 'User',
            'nickname': 'User',
            'age': None,
            'voice_style': 'default',
            'preferred_tone': 'neutral',
            'mood_type': 'balanced',
            'language': 'en',
            'theme': 'dark',
            'tts_voice': 'default',
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        # Tone categories and their characteristics
        self.tone_categories = {
            'playful': {
                'keywords': ['fun', 'playful', 'casual', 'friendly', 'cool', 'informal', 'funny', 'light'],
                'arabic_keywords': ['مرح', 'ودود', 'مضحك', 'لطيف', 'ممتع'],
                'tts_voices': {
                    'en': 'cheerful_female',
                    'ar': 'arabic_friendly'
                }
            },
            'formal': {
                'keywords': ['formal', 'professional', 'official', 'serious', 'business', 'proper'],
                'arabic_keywords': ['رسمي', 'مهني', 'جاد', 'عمل', 'احترافي'],
                'tts_voices': {
                    'en': 'deep_male',
                    'ar': 'arabic_formal'
                }
            },
            'calm': {
                'keywords': ['calm', 'soft', 'gentle', 'soothing', 'relaxed', 'quiet', 'peaceful'],
                'arabic_keywords': ['هادئ', 'ناعم', 'لطيف', 'مريح', 'سلس'],
                'tts_voices': {
                    'en': 'soft_female',
                    'ar': 'arabic_calm'
                }
            },
            'assertive': {
                'keywords': ['strong', 'confident', 'assertive', 'bold', 'clear', 'direct', 'powerful'],
                'arabic_keywords': ['قوي', 'واثق', 'حازم', 'جريء', 'مباشر'],
                'tts_voices': {
                    'en': 'strong_male',
                    'ar': 'arabic_assertive'
                }
            },
            'neutral': {
                'keywords': ['neutral', 'balanced', 'normal', 'default', 'standard', 'regular'],
                'arabic_keywords': ['محايد', 'متوازن', 'عادي', 'قياسي'],
                'tts_voices': {
                    'en': 'default',
                    'ar': 'arabic'
                }
            }
        }
        
        # Mood types and their characteristics
        self.mood_types = {
            'optimistic': ['happy', 'positive', 'bright', 'optimistic', 'cheerful', 'متفائل', 'إيجابي', 'مشرق'],
            'analytical': ['analytical', 'smart', 'logical', 'intelligent', 'rational', 'تحليلي', 'ذكي', 'منطقي'],
            'empathetic': ['kind', 'caring', 'empathetic', 'understanding', 'supportive', 'متعاطف', 'مهتم', 'متفهم'],
            'balanced': ['balanced', 'versatile', 'adaptive', 'flexible', 'متوازن', 'متنوع', 'مرن']
        }
    
    def initialize_tables(self):
        """Initialize database tables for user profiles"""
        try:
            # Create user_profile table if it doesn't exist
            self.db_manager.execute_query("""
                CREATE TABLE IF NOT EXISTS user_profile (
                    id SERIAL PRIMARY KEY,
                    full_name TEXT,
                    nickname TEXT,
                    age INTEGER,
                    voice_style TEXT,
                    preferred_tone TEXT,
                    mood_type TEXT,
                    language TEXT,
                    theme TEXT,
                    tts_voice TEXT,
                    created_at TEXT,
                    last_updated TEXT
                )
            """)
            logger.info("User profile table initialized")
            return True
        except Exception as e:
            logger.error(f"Error initializing user profile table: {str(e)}")
            return False
    
    def get_current_profile(self):
        """Get the current user profile"""
        if self.current_profile:
            return self.current_profile
            
        # Try to get profile from database
        try:
            # Get the most recent profile
            profile_data = self.db_manager.execute_query("""
                SELECT * FROM user_profile ORDER BY id DESC LIMIT 1
            """)
            
            if profile_data and len(profile_data) > 0:
                # Convert tuple to dictionary
                columns = ['id', 'full_name', 'nickname', 'age', 'voice_style', 
                          'preferred_tone', 'mood_type', 'language', 'theme', 
                          'tts_voice', 'created_at', 'last_updated']
                profile = dict(zip(columns, profile_data[0]))
                self.current_profile = profile
                return profile
            
            # If no profile exists, use default
            return self.default_profile
            
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return self.default_profile
    
    def infer_personality(self, answers):
        """
        Infer personality traits from onboarding answers
        
        Args:
            answers (dict): Dictionary of onboarding answers with keys:
                            voice_style, full_name, age, nickname, theme, language
                            
        Returns:
            dict: Inferred personality traits
        """
        try:
            # Extract voice style preferences
            voice_style = answers.get('voice_style', '').lower()
            language = answers.get('language', 'en')
            
            lang = language or 'en'  # Make sure language is not None
            
            # Default results
            results = {
                'preferred_tone': 'neutral',
                'tts_voice': 'default' if lang == 'en' else 'arabic',
                'mood_type': 'balanced'
            }
            
            # Analyze voice style for tone preferences
            inferred_tone = self._infer_tone(voice_style, language)
            if inferred_tone:
                results['preferred_tone'] = inferred_tone
                results['tts_voice'] = self.tone_categories[inferred_tone]['tts_voices'].get(language, 'default')
            
            # Analyze for mood type
            inferred_mood = self._infer_mood_type(voice_style)
            if inferred_mood:
                results['mood_type'] = inferred_mood
            
            logger.info(f"Inferred personality: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Error inferring personality: {str(e)}")
            lang = language or 'en'  # Make sure language is not None
            return {
                'preferred_tone': 'neutral',
                'tts_voice': 'default' if lang == 'en' else 'arabic',
                'mood_type': 'balanced'
            }
    
    def _infer_tone(self, voice_style, language="en"):
        """Infer tone preference from voice style input"""
        voice_style = voice_style.lower()
        
        # Default tone
        inferred_tone = 'neutral'
        max_matches = 0
        
        # Check each tone category for keyword matches
        for tone, attributes in self.tone_categories.items():
            # Get the appropriate keyword list based on language
            keywords = attributes['arabic_keywords'] if language == 'ar' else attributes['keywords']
            
            # Count matches
            matches = sum(1 for keyword in keywords if keyword in voice_style)
            
            # Update if we have more matches
            if matches > max_matches:
                max_matches = matches
                inferred_tone = tone
        
        return inferred_tone
    
    def _infer_mood_type(self, voice_style):
        """Infer mood type from voice style input"""
        voice_style = voice_style.lower()
        
        # Default mood type
        inferred_mood = 'balanced'
        max_matches = 0
        
        # Check each mood type for keyword matches
        for mood, keywords in self.mood_types.items():
            # Count matches
            matches = sum(1 for keyword in keywords if keyword in voice_style)
            
            # Update if we have more matches
            if matches > max_matches:
                max_matches = matches
                inferred_mood = mood
        
        return inferred_mood
    
    def create_profile(self, profile_data):
        """Create a new user profile"""
        try:
            # Ensure required fields
            if 'full_name' not in profile_data:
                raise ValueError("Full name is required")
                
            if 'language' not in profile_data:
                profile_data['language'] = 'en'
                
            # Infer personality if voice_style is provided
            if 'voice_style' in profile_data:
                inferred = self.infer_personality(profile_data)
                profile_data.update(inferred)
            
            # Set default values for missing fields
            for key, value in self.default_profile.items():
                if key not in profile_data:
                    profile_data[key] = value
            
            # Set timestamps
            now = datetime.now().isoformat()
            profile_data['created_at'] = now
            profile_data['last_updated'] = now
            
            # Insert into database
            columns = ', '.join(profile_data.keys())
            placeholders = ', '.join([f'${i+1}' for i in range(len(profile_data.keys()))])
            values = tuple(profile_data.values())
            
            query = f"INSERT INTO user_profile ({columns}) VALUES ({placeholders})"
            self.db_manager.execute_query(query, values)
            
            # Update current profile
            self.current_profile = profile_data
            
            logger.info(f"Created user profile for {profile_data.get('full_name')}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating user profile: {str(e)}")
            return False
    
    def update_profile(self, profile_data):
        """Update an existing user profile"""
        try:
            # Get current profile
            current_profile = self.get_current_profile()
            profile_id = current_profile.get('id')
            
            if not profile_id:
                # No existing profile, create new one
                return self.create_profile(profile_data)
            
            # Update with new data
            current_profile.update(profile_data)
            
            # Update timestamp
            current_profile['last_updated'] = datetime.now().isoformat()
            
            # If voice_style is updated, re-infer personality
            if 'voice_style' in profile_data:
                inferred = self.infer_personality(current_profile)
                current_profile.update(inferred)
            
            # Build update query
            update_parts = []
            values = []
            param_count = 1
            
            for key, value in current_profile.items():
                if key != 'id':  # Skip ID field
                    update_parts.append(f"{key} = ${param_count}")
                    values.append(value)
                    param_count += 1
            
            # Add ID for WHERE clause
            values.append(profile_id)
            
            query = f"UPDATE user_profile SET {', '.join(update_parts)} WHERE id = ${param_count}"
            self.db_manager.execute_query(query, tuple(values))
            
            # Update current profile
            self.current_profile = current_profile
            
            logger.info(f"Updated user profile for {current_profile.get('full_name')}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return False
    
    def get_tone_response_style(self, tone=None):
        """Get response style modifiers based on tone"""
        if not tone:
            current_profile = self.get_current_profile()
            tone = current_profile.get('preferred_tone', 'neutral')
        
        response_styles = {
            'playful': {
                'greetings': ['Hey there!', 'Hi friend!', "What's up?"],
                'ar_greetings': ['مرحباً!', 'أهلاً صديقي!', 'كيف الحال؟'],
                'emojis': True,
                'sentence_length': 'short',
                'formality': 'informal'
            },
            'formal': {
                'greetings': ['Good day.', 'Greetings.', 'Welcome.'],
                'ar_greetings': ['يوم سعيد.', 'تحياتي.', 'أهلاً بك.'],
                'emojis': False,
                'sentence_length': 'medium',
                'formality': 'formal'
            },
            'calm': {
                'greetings': ['Hello.', 'Hi there.', 'Welcome.'],
                'ar_greetings': ['مرحباً.', 'أهلاً بك.', 'مرحباً بك.'],
                'emojis': False,
                'sentence_length': 'medium',
                'formality': 'semi-formal'
            },
            'assertive': {
                'greetings': ['Hello!', 'Welcome!', 'Good to see you!'],
                'ar_greetings': ['مرحباً!', 'أهلاً وسهلاً!', 'سعيد برؤيتك!'],
                'emojis': False,
                'sentence_length': 'medium',
                'formality': 'confident'
            },
            'neutral': {
                'greetings': ['Hello.', 'Hi.', 'Welcome.'],
                'ar_greetings': ['مرحباً.', 'أهلاً.', 'أهلاً بك.'],
                'emojis': False,
                'sentence_length': 'medium',
                'formality': 'neutral'
            }
        }
        
        return response_styles.get(tone, response_styles['neutral'])
    
    def get_tts_voice_for_language(self, language=None):
        """Get the appropriate TTS voice for a language based on user preferences."""
        profile = self.get_current_profile()
        tone = profile.get('voice_style', 'calm')  # default calm

        if tone == 'sad':
            return "EXAVITQu4vr4xnSDxMaL"  # Example: Sad voice ID
        elif tone == 'happy':
            return "pNInz6obpgDQGcFmaJgB"  # Example: Happy tone
        elif tone == 'excited':
            return "ErXwobaYiN019PkySvjV"  # Excited expressive
        else:  # calm or unknown
            return "21m00Tcm4TlvDq8ikWAM"  # Bella
    
    def get_greeting(self, name=None, language=None):
        """Get a personalized greeting based on profile preferences"""
        current_profile = self.get_current_profile()
        
        if not language:
            language = current_profile.get('language', 'en')
            
        if not name:
            name = current_profile.get('nickname', 'User')
            
        preferred_tone = current_profile.get('preferred_tone', 'neutral')
        tone_style = self.get_tone_response_style(preferred_tone)
        
        # Get greetings list based on language
        greetings = tone_style['ar_greetings'] if language == 'ar' else tone_style['greetings']
        
        # Get a greeting (simplified selection, could be randomized)
        greeting = greetings[0]
        
        # Format with name
        if language == 'ar':
            return f"{greeting} {name}"
        else:
            return f"{greeting} {name}"
    
    def adapt_response(self, text, language=None):
        """Adapt a response based on user's preferred tone and language"""
        current_profile = self.get_current_profile()
        
        if not language:
            language = current_profile.get('language', 'en')
            
        preferred_tone = current_profile.get('preferred_tone', 'neutral')
        tone_style = self.get_tone_response_style(preferred_tone)
        
        # For playful tone, maybe add emojis
        if preferred_tone == 'playful' and language == 'en':
            if not text.endswith(('!', '?', '.')):
                text += '!'
                
        # For formal tone, ensure proper punctuation
        elif preferred_tone == 'formal':
            if not text.endswith(('!', '?', '.')):
                text += '.'
        
        return text