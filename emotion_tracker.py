import os
import logging
import json
import numpy as np
from datetime import datetime, timedelta
import sqlite3
from collections import Counter, defaultdict
import re
import math
import threading
import time
import random
from typing import Dict, List, Tuple, Optional, Union, Any

import nltk
from nltk.corpus import wordnet

# Import for OpenAI integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

nltk.download('wordnet')  # Ensure WordNet is downloaded

def _get_synonyms(keyword):
    synonyms = set()
    for syn in wordnet.synsets(keyword):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms

class EmotionTracker:
    """Advanced emotion tracking system with enhanced analysis algorithms"""
    
    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        
        ...
        
    def _analyze_with_rules(self, text, context=None):
        text = text.lower().strip()
        emotions = {emotion: 0.0 for emotion in self.emotion_labels}
        
        for emotion, keywords in self.emotion_keywords.items():
            for keyword, weight in keywords.items():
                if re.search(r"\b" + re.escape(keyword) + r"\b", text):
                    emotions[emotion] += weight
                # Check synonyms
                for synonym in _get_synonyms(keyword):
                    if re.search(r"\b" + re.escape(synonym) + r"\b", text):
                        emotions[emotion] += weight * 0.8

        # Contextual influence
        if context:
            context_emotions = self._analyze_context(context)
            for emotion, score in context_emotions.items():
                emotions[emotion] += score * 0.3

        if not emotions:
            return "neutral"
        
        return max(emotions, key=emotions.get)
        
    ...

class EmotionTracker:
    """Advanced emotion tracking system with enhanced analysis algorithms"""
    
    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        
        # Extended emotion labels for more nuanced analysis
        self.emotion_labels = [
            "neutral", "happy", "sad", "angry", "fearful", 
            "disgusted", "surprised", "confused", "interested",
            "excited", "anxious", "calm", "tired", "bored",
            "grateful", "hopeful", "lonely", "proud", "embarrassed"
        ]
        
        # Primary emotions (for aggregation and simplification)
        self.primary_emotions = {
            "joy": ["happy", "excited", "grateful", "hopeful", "proud"],
            "sadness": ["sad", "lonely", "tired"],
            "anger": ["angry", "disgusted"],
            "fear": ["fearful", "anxious", "embarrassed"],
            "surprise": ["surprised"],
            "neutral": ["neutral", "calm"],
            "curiosity": ["interested", "confused"],
            "boredom": ["bored"]
        }
        
        # Emotion intensity modifiers
        self.intensity_modifiers = {
            "very": 1.5,
            "extremely": 2.0,
            "slightly": 0.5,
            "somewhat": 0.7,
            "really": 1.3,
            "incredibly": 1.8,
            "absolutely": 1.7,
            "barely": 0.3,
            "hardly": 0.4,
            "completely": 1.6,
            "totally": 1.6
        }
        
        # Emotion negators
        self.negation_words = [
            "not", "don't", "doesn't", "didn't", "isn't", "aren't", 
            "wasn't", "weren't", "won't", "wouldn't", "no", "never"
        ]
        
        # Enhanced keyword dictionary with weights
        self.emotion_keywords = {
            "happy": {
                "happy": 1.0, "glad": 0.9, "joy": 1.0, "awesome": 0.8, 
                "great": 0.7, "excellent": 0.8, "wonderful": 0.9, 
                "delighted": 1.0, "pleased": 0.8, "cheerful": 0.9, 
                "thrilled": 1.0, "content": 0.7, "satisfied": 0.8
            },
            "sad": {
                "sad": 1.0, "unhappy": 0.9, "depressed": 1.0, "down": 0.7, 
                "blue": 0.6, "gloomy": 0.8, "miserable": 1.0, 
                "heartbroken": 1.0, "grief": 1.0, "sorrow": 0.9, 
                "disappointed": 0.8, "upset": 0.8, "devastated": 1.0
            },
            "angry": {
                "angry": 1.0, "mad": 0.9, "furious": 1.0, "outraged": 1.0, 
                "irritated": 0.7, "annoyed": 0.6, "frustrated": 0.8, 
                "enraged": 1.0, "hostile": 0.9, "bitter": 0.8,
                "hate": 0.9, "resent": 0.8
            },
            "fearful": {
                "afraid": 1.0, "scared": 1.0, "terrified": 1.0, "anxious": 0.8, 
                "worried": 0.7, "nervous": 0.7, "frightened": 0.9, 
                "panic": 1.0, "dread": 0.9, "horror": 1.0,
                "uneasy": 0.6, "disturbed": 0.7
            },
            "disgusted": {
                "disgusted": 1.0, "gross": 0.8, "revolting": 0.9, "nasty": 0.8, 
                "yuck": 0.7, "repulsed": 1.0, "nauseated": 0.9, 
                "appalled": 0.9, "sickened": 0.9
            },
            "surprised": {
                "surprised": 1.0, "shocked": 0.9, "amazed": 0.9, "astonished": 1.0, 
                "wow": 0.7, "stunned": 0.9, "startled": 0.8, 
                "unexpected": 0.7, "remarkable": 0.6
            },
            "confused": {
                "confused": 1.0, "puzzled": 0.9, "perplexed": 0.9, "unsure": 0.7, 
                "uncertain": 0.7, "baffled": 0.9, "bewildered": 0.9, 
                "disoriented": 0.8, "unclear": 0.6, "dubious": 0.7
            },
            "interested": {
                "interested": 1.0, "curious": 0.9, "intrigued": 0.9, "fascinated": 1.0, 
                "engaged": 0.8, "attentive": 0.8, "captivated": 0.9, 
                "focused": 0.7, "absorbed": 0.8
            },
            "excited": {
                "excited": 1.0, "enthusiastic": 0.9, "eager": 0.8, "energetic": 0.8,
                "exhilarated": 1.0, "animated": 0.7, "thrilled": 0.9,
                "pumped": 0.8, "stoked": 0.8
            },
            "anxious": {
                "anxious": 1.0, "apprehensive": 0.9, "tense": 0.8, "stressed": 0.9,
                "jittery": 0.8, "restless": 0.7, "uneasy": 0.8,
                "edgy": 0.7, "concerned": 0.6
            },
            "calm": {
                "calm": 1.0, "relaxed": 0.9, "peaceful": 0.9, "serene": 1.0,
                "tranquil": 1.0, "composed": 0.8, "collected": 0.8,
                "steady": 0.7, "mellow": 0.7
            },
            "tired": {
                "tired": 1.0, "exhausted": 1.0, "sleepy": 0.8, "fatigued": 0.9,
                "weary": 0.9, "drained": 0.9, "spent": 0.8,
                "worn": 0.8, "drowsy": 0.7
            },
            "bored": {
                "bored": 1.0, "disinterested": 0.9, "uninterested": 0.9, "apathetic": 0.8,
                "indifferent": 0.7, "uninspired": 0.8, "dull": 0.7,
                "tedious": 0.7, "monotonous": 0.7
            },
            "grateful": {
                "grateful": 1.0, "thankful": 1.0, "appreciative": 0.9, "blessed": 0.8,
                "indebted": 0.7, "pleased": 0.6, "touched": 0.7
            },
            "hopeful": {
                "hopeful": 1.0, "optimistic": 0.9, "encouraged": 0.8, "confident": 0.7,
                "positive": 0.7, "reassured": 0.7, "expectant": 0.8
            },
            "lonely": {
                "lonely": 1.0, "isolated": 0.9, "abandoned": 0.9, "alone": 0.8,
                "forsaken": 0.9, "rejected": 0.8, "neglected": 0.8
            },
            "proud": {
                "proud": 1.0, "accomplished": 0.9, "satisfied": 0.8, "fulfilled": 0.8,
                "confident": 0.7, "successful": 0.8, "triumphant": 0.9
            },
            "embarrassed": {
                "embarrassed": 1.0, "ashamed": 0.9, "humiliated": 1.0, "mortified": 1.0,
                "self-conscious": 0.8, "awkward": 0.7, "uncomfortable": 0.7
            }
        }
        
        # Context-based emotional phrases (for more accurate analysis)
        self.emotional_phrases = {
            "happy": [
                "having a great time", "couldn't be happier", "on cloud nine",
                "over the moon", "in high spirits", "feeling good about",
                "makes me smile", "brightens my day"
            ],
            "sad": [
                "feeling down", "heart is heavy", "brings tears to my eyes",
                "lost interest in", "don't feel like", "can't stop crying",
                "hard to deal with", "miss them so much"
            ],
            "angry": [
                "makes my blood boil", "fed up with", "had it with",
                "drives me crazy", "lost my temper", "getting on my nerves",
                "sick and tired of", "crossed the line"
            ],
            "fearful": [
                "scared to death", "worried sick", "feared the worst",
                "sends chills down my spine", "afraid of what might happen",
                "keeps me up at night", "feel threatened by"
            ]
        }
        
        # Contextual sentiment indicators
        self.positive_indicators = [
            "love", "adore", "enjoy", "appreciate", "like", "fond", 
            "favorite", "best", "perfect", "amazing", "fantastic",
            "worth", "recommend", "blessing", "grateful", "fortunate"
        ]
        
        self.negative_indicators = [
            "hate", "dislike", "awful", "terrible", "worst", "useless",
            "waste", "regret", "disappointed", "sorry", "unfortunately",
            "problem", "issue", "trouble", "struggle", "difficult",
            "annoying", "irritating", "unbearable", "fail", "mess"
        ]
        
        # OpenAI client (initialized on demand)
        self.openai_client = None
        
        # Memory for contextual analysis 
        self.conversation_memory = []
        self.memory_limit = 10
        
        # Custom model training status
        self.custom_model_trained = False
        self.model_training_lock = threading.Lock()
        
        # Emotion trend data
        self.trend_data = {}
        
        # Pattern recognition data
        self.pattern_data = defaultdict(list)
        
        # Ensure emotion data directory exists
        self.data_dir = "emotion_data"
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Try to load saved model data
        self._load_extended_model_data()
    
    def _load_extended_model_data(self):
        """Load extended model data from saved files"""
        try:
            # Load custom emotion keywords if available
            keywords_path = os.path.join(self.data_dir, "emotion_keywords.json")
            if os.path.exists(keywords_path):
                with open(keywords_path, 'r') as f:
                    saved_keywords = json.load(f)
                    # Merge with existing keywords
                    for emotion, words in saved_keywords.items():
                        if emotion in self.emotion_keywords:
                            # If format is different (weights vs list), handle accordingly
                            if isinstance(words, list):
                                # Convert list to dict with default weights of 1.0
                                self.emotion_keywords[emotion].update({word: 1.0 for word in words})
                            else:
                                # Already in dict format with weights
                                self.emotion_keywords[emotion].update(words)
            
            # Load emotional phrases if available
            phrases_path = os.path.join(self.data_dir, "emotional_phrases.json")
            if os.path.exists(phrases_path):
                with open(phrases_path, 'r') as f:
                    saved_phrases = json.load(f)
                    # Merge with existing phrases
                    for emotion, phrases in saved_phrases.items():
                        if emotion in self.emotional_phrases:
                            self.emotional_phrases[emotion].extend(phrases)
                        else:
                            self.emotional_phrases[emotion] = phrases
            
            # Load trend data if available
            trend_path = os.path.join(self.data_dir, "emotion_trends.json")
            if os.path.exists(trend_path):
                with open(trend_path, 'r') as f:
                    self.trend_data = json.load(f)
            
            # Mark custom model as trained if we loaded data
            self.custom_model_trained = True
            self.logger.info("Loaded extended emotion model data")
        except Exception as e:
            self.logger.error(f"Error loading extended model data: {str(e)}")
    
    def analyze_text_advanced(self, text: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Advanced analysis of text to determine emotions with intensity scores and context awareness
        
        Args:
            text: The text to analyze
            context: Optional list of previous conversation messages for context
            
        Returns:
            Dict containing primary emotion, all detected emotions with scores, and metadata
        """
        if not text:
            return {"primary_emotion": "neutral", "emotions": {"neutral": 1.0}, "intensity": 0.5}
        
        # Normalize text
        text = text.lower().strip()
        
        # Add to conversation memory for context
        self.conversation_memory.append(text)
        if len(self.conversation_memory) > self.memory_limit:
            self.conversation_memory.pop(0)
        
        # First attempt with OpenAI if available
        openai_result = self._analyze_with_openai(text, context) if OPENAI_AVAILABLE else None
        if openai_result:
            return openai_result
        
        # Fall back to advanced rule-based analysis
        return self._analyze_with_rules(text, context)
    
    def _analyze_with_openai(self, text: str, context: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Use OpenAI for emotion analysis if available"""
        try:
            # Check if OPENAI_API_KEY environment variable is set
            if not os.environ.get("OPENAI_API_KEY"):
                self.logger.warning("OpenAI API key not found, skipping AI-based emotion analysis")
                return None
            
            # Initialize OpenAI client if needed
            if not self.openai_client:
                self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Prepare system message
            system_message = {
                "role": "system", 
                "content": f"""You are an expert emotion analyzer. Analyze the emotional content of the text.
                Return a JSON object with the following structure:
                {{
                    "primary_emotion": "The single most prominent emotion in the text",
                    "emotions": {{
                        "emotion1": score (0.0-1.0),
                        "emotion2": score (0.0-1.0),
                        ...
                    }},
                    "intensity": "Overall emotional intensity (0.0-1.0)",
                    "explanation": "Brief explanation of the analysis"
                }}
                
                Valid emotion categories: {', '.join(self.emotion_labels)}
                Only include emotions that are present in the text.
                """
            }
            
            # Prepare user message with context if available
            user_content = text
            if context and len(context) > 0:
                context_text = "\n".join([f"Previous message: {msg}" for msg in context[-3:]])
                user_content = f"Context:\n{context_text}\n\nCurrent message: {text}"
            
            user_message = {"role": "user", "content": user_content}
            
            # Query OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[system_message, user_message],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Parse the result
            result = json.loads(response.choices[0].message.content)
            
            # Validate and adjust the result if needed
            if "primary_emotion" not in result or "emotions" not in result:
                self.logger.warning(f"Invalid OpenAI response format: {result}")
                return None
            
            # Ensure primary emotion is in our supported list
            if result["primary_emotion"] not in self.emotion_labels:
                result["primary_emotion"] = "neutral"
            
            # Filter emotions to our supported list
            result["emotions"] = {k: v for k, v in result["emotions"].items() if k in self.emotion_labels}
            
            # Ensure intensity is present and in bounds
            if "intensity" not in result:
                result["intensity"] = 0.5
            result["intensity"] = max(0.0, min(1.0, float(result["intensity"])))
            
            # Add timestamp
            result["timestamp"] = datetime.now().isoformat()
            
            self.logger.debug(f"OpenAI emotion analysis: {result['primary_emotion']} ({result['intensity']})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in OpenAI emotion analysis: {str(e)}")
            return None
    
    def _analyze_with_rules(self, text: str, context: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Rule-based emotion analysis with advanced features
        
        Returns a dictionary with:
        - primary_emotion: The strongest emotion detected
        - emotions: Dict of all emotions with their scores
        - intensity: Overall emotional intensity
        - metadata: Additional analysis info
        """
        # Initialize emotions dictionary with zeros
        emotions = {emotion: 0.0 for emotion in self.emotion_labels}
        
        # 1. Check for emotional phrases first (highest priority)
        for emotion, phrases in self.emotional_phrases.items():
            for phrase in phrases:
                if phrase.lower() in text.lower():
                    emotions[emotion] += 1.5  # Give phrases higher weight
        
        # 2. Check for keywords with weights
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Track negation context
        negation_active = False
        intensifier_value = 1.0
        
        for i, word in enumerate(words):
            # Check for negation words
            if word in self.negation_words:
                negation_active = True
                continue
            
            # Check for intensity modifiers
            if word in self.intensity_modifiers:
                intensifier_value = self.intensity_modifiers[word]
                continue
            
            # Check if word matches any emotion keywords
            for emotion, keywords in self.emotion_keywords.items():
                if isinstance(keywords, dict):
                    # Dictionary format with weights
                    if word in keywords:
                        score = keywords[word] * intensifier_value
                        if negation_active:
                            # If negated, reduce this emotion and possibly increase opposites
                            emotions[emotion] -= score
                            # Add small boost to opposite emotions
                            if emotion == "happy":
                                emotions["sad"] += 0.3 * score
                            elif emotion == "sad":
                                emotions["happy"] += 0.3 * score
                        else:
                            emotions[emotion] += score
                else:
                    # Simple list format (legacy support)
                    if word in keywords:
                        if negation_active:
                            emotions[emotion] -= 1.0 * intensifier_value
                        else:
                            emotions[emotion] += 1.0 * intensifier_value
            
            # Reset negation and intensity after applying to a word
            negation_active = False
            intensifier_value = 1.0
        
        # 3. Add sentiment analysis for unlabeled text
        sentiment_score = self._calculate_sentiment(text)
        if sentiment_score > 0.3:
            emotions["happy"] += sentiment_score * 0.5
        elif sentiment_score < -0.3:
            emotions["sad"] += abs(sentiment_score) * 0.5
        
        # 4. Add contextual analysis if context provided
        if context and len(context) > 0:
            context_emotions = self._analyze_context(context)
            # Merge with lower weight (context has 30% influence)
            for emotion, score in context_emotions.items():
                emotions[emotion] += score * 0.3
        
        # 5. Factor in temporal patterns
        self._update_pattern_data(emotions)
        pattern_influence = self._calculate_pattern_influence()
        for emotion, factor in pattern_influence.items():
            if emotion in emotions:
                emotions[emotion] *= factor  # Adjust based on patterns
        
        # Normalize to ensure no negatives and reasonable values
        for emotion in emotions:
            emotions[emotion] = max(0.0, emotions[emotion])
        
        # Calculate total and get primary emotion
        total = sum(emotions.values()) or 1.0  # Avoid division by zero
        normalized_emotions = {e: (s / total) for e, s in emotions.items() if s > 0}
        
        # If no emotions detected, return neutral
        if not normalized_emotions:
            return {
                "primary_emotion": "neutral",
                "emotions": {"neutral": 1.0},
                "intensity": 0.1,
                "metadata": {"source": "rule-based", "confidence": 0.3}
            }
        
        # Find primary emotion (highest score)
        primary_emotion = max(normalized_emotions.items(), key=lambda x: x[1])[0]
        
        # Calculate overall intensity
        max_score = max(normalized_emotions.values())
        scaled_intensity = min(1.0, max_score * 1.5)  # Scale up for better display
        
        # Return complete analysis
        return {
            "primary_emotion": primary_emotion,
            "emotions": normalized_emotions,
            "intensity": scaled_intensity,
            "metadata": {
                "source": "rule-based",
                "confidence": max_score,
                "context_length": len(context) if context else 0,
                "pattern_strength": sum(pattern_influence.values()) / len(pattern_influence) if pattern_influence else 0
            }
        }
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate a simple sentiment score (-1.0 to 1.0) based on positive/negative indicators"""
        pos_count = sum(1 for word in self.positive_indicators if word in text.lower())
        neg_count = sum(1 for word in self.negative_indicators if word in text.lower())
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        return (pos_count - neg_count) / (pos_count + neg_count)
    
    def _analyze_context(self, context: List[str]) -> Dict[str, float]:
        """Analyze conversation context to extract emotional tendencies"""
        # Combine all context messages
        combined_text = " ".join(context)
        
        # Simple keyword matching on combined text
        emotions = {emotion: 0.0 for emotion in self.emotion_labels}
        
        for emotion, keywords in self.emotion_keywords.items():
            if isinstance(keywords, dict):
                for word, weight in keywords.items():
                    pattern = r'\b' + re.escape(word) + r'\b'
                    matches = re.findall(pattern, combined_text.lower())
                    emotions[emotion] += len(matches) * weight
            else:
                for keyword in keywords:
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    matches = re.findall(pattern, combined_text.lower())
                    emotions[emotion] += len(matches)
        
        # Normalize
        total = sum(emotions.values()) or 1.0
        return {e: (s / total) for e, s in emotions.items() if s > 0}
    
    def _update_pattern_data(self, emotions: Dict[str, float]):
        """Update emotional pattern data to track temporal changes"""
        timestamp = datetime.now()
        day_key = timestamp.strftime("%Y-%m-%d")
        
        # Store top emotions for this timestamp
        top_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)[:3]
        
        if day_key not in self.trend_data:
            self.trend_data[day_key] = []
        
        # Add to trend data
        self.trend_data[day_key].append({
            "time": timestamp.strftime("%H:%M:%S"),
            "emotions": {e: v for e, v in top_emotions}
        })
        
        # Limit data size (keep last 30 days)
        keys = sorted(self.trend_data.keys())
        if len(keys) > 30:
            for old_key in keys[:-30]:
                del self.trend_data[old_key]
                
        # Save updated trend data periodically (every 10 updates)
        if sum(len(entries) for entries in self.trend_data.values()) % 10 == 0:
            try:
                trend_path = os.path.join(self.data_dir, "emotion_trends.json")
                with open(trend_path, 'w') as f:
                    json.dump(self.trend_data, f, indent=2)
            except Exception as e:
                self.logger.error(f"Error saving trend data: {str(e)}")
    
    def _calculate_pattern_influence(self) -> Dict[str, float]:
        """Calculate pattern influence factors based on recent emotion history"""
        # Initialize with neutral values (no influence)
        influence = {emotion: 1.0 for emotion in self.emotion_labels}
        
        # Get today's key
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        if today not in self.trend_data and yesterday not in self.trend_data:
            return influence  # No data to calculate patterns
            
        # Analyze today's patterns
        if today in self.trend_data:
            today_entries = self.trend_data[today]
            
            # Calculate frequency of each emotion today
            emotion_counts = defaultdict(float)
            for entry in today_entries:
                for emotion, score in entry["emotions"].items():
                    emotion_counts[emotion] += score
            
            # Adjust influence based on frequency (more frequent → higher influence)
            total = sum(emotion_counts.values()) or 1.0
            for emotion, count in emotion_counts.items():
                # Emotions seen today get a boost (continuity bias)
                influence[emotion] = 1.0 + (count / total) * 0.5  # Max 50% boost
        
        # Incorporate yesterday's patterns with lower weight
        if yesterday in self.trend_data:
            yesterday_entries = self.trend_data[yesterday]
            
            # Calculate which emotions were dominant yesterday
            emotion_counts = defaultdict(float)
            for entry in yesterday_entries:
                for emotion, score in entry["emotions"].items():
                    emotion_counts[emotion] += score
            
            # Slightly boost yesterday's emotions (much smaller effect)
            total = sum(emotion_counts.values()) or 1.0
            for emotion, count in emotion_counts.items():
                # Add small boost for yesterday's common emotions
                current = influence.get(emotion, 1.0)
                influence[emotion] = current + (count / total) * 0.2  # Max 20% boost
        
        return influence
    
    def detect_emotion_changes(self, timeframe: str = "day") -> Dict[str, Any]:
        """
        Detect significant changes in emotional patterns
        
        Args:
            timeframe: "day", "week", or "month"
            
        Returns:
            Dict with detected changes and significance scores
        """
        # Get current datetime and keys for comparison
        now = datetime.now()
        
        if timeframe == "day":
            current_key = now.strftime("%Y-%m-%d")
            previous_key = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        elif timeframe == "week":
            current_start = now - timedelta(days=now.weekday())
            previous_start = current_start - timedelta(days=7)
            current_key = current_start.strftime("%Y-%m-%d")
            previous_key = previous_start.strftime("%Y-%m-%d")
        elif timeframe == "month":
            current_month = now.replace(day=1)
            previous_month = (current_month - timedelta(days=1)).replace(day=1)
            current_key = current_month.strftime("%Y-%m")
            previous_key = previous_month.strftime("%Y-%m")
        else:
            return {"error": "Invalid timeframe. Use 'day', 'week', or 'month'."}
        
        # Get emotion distributions for both periods
        current_distribution = self._get_emotion_distribution(current_key, timeframe)
        previous_distribution = self._get_emotion_distribution(previous_key, timeframe)
        
        # Calculate changes
        changes = {}
        for emotion in self.emotion_labels:
            current = current_distribution.get(emotion, 0)
            previous = previous_distribution.get(emotion, 0)
            
            if current == 0 and previous == 0:
                continue
                
            # Calculate relative change and absolute difference
            if previous == 0:
                rel_change = 1.0  # 100% increase from zero
            else:
                rel_change = (current - previous) / previous
                
            abs_diff = current - previous
            
            # Only include significant changes
            if abs(rel_change) > 0.2 or abs(abs_diff) > 0.1:
                changes[emotion] = {
                    "relative_change": rel_change,
                    "absolute_change": abs_diff,
                    "current": current,
                    "previous": previous,
                    "significance": abs(rel_change) * abs(abs_diff) * 10  # Combined metric
                }
        
        # Sort by significance
        sorted_changes = dict(sorted(
            changes.items(), 
            key=lambda x: x[1]["significance"], 
            reverse=True
        ))
        
        return {
            "timeframe": timeframe,
            "current_period": current_key,
            "previous_period": previous_key,
            "changes": sorted_changes
        }
    
    def _get_emotion_distribution(self, key_prefix: str, timeframe: str) -> Dict[str, float]:
        """Get normalized emotion distribution for a specific time period"""
        distribution = {emotion: 0.0 for emotion in self.emotion_labels}
        
        # Collect all relevant entries
        entries = []
        for day_key, day_entries in self.trend_data.items():
            if timeframe == "day" and day_key == key_prefix:
                entries.extend(day_entries)
            elif timeframe == "week" and day_key.startswith(key_prefix[:8]):
                # Match the week beginning with key_prefix
                entries.extend(day_entries)
            elif timeframe == "month" and day_key.startswith(key_prefix[:7]):
                # Match the month
                entries.extend(day_entries)
        
        # Count emotions
        for entry in entries:
            for emotion, score in entry["emotions"].items():
                distribution[emotion] += score
        
        # Normalize
        total = sum(distribution.values()) or 1.0
        return {e: (v / total) for e, v in distribution.items() if v > 0}
    
    def analyze_emotion_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze emotion trends over time to identify patterns
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with trend analysis results
        """
        # Get data for the specified number of days
        try:
            today = datetime.now()
            start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
            
            # Collect relevant trend data
            trend_days = {}
            for day_key, day_entries in self.trend_data.items():
                if day_key >= start_date:
                    trend_days[day_key] = day_entries
            
            if not trend_days:
                # Fallback to database if trend data is empty
                return self._analyze_trends_from_database(days)
            
            # Analyze emotion distribution by day
            daily_distributions = {}
            for day, entries in trend_days.items():
                emotions = defaultdict(float)
                for entry in entries:
                    for emotion, score in entry["emotions"].items():
                        emotions[emotion] += score
                
                # Normalize
                total = sum(emotions.values()) or 1.0
                daily_distributions[day] = {e: (s / total) for e, s in emotions.items()}
            
            # Calculate primary emotions for each day
            primary_emotions = {}
            for day, dist in daily_distributions.items():
                if dist:
                    primary_emotions[day] = max(dist.items(), key=lambda x: x[1])[0]
                else:
                    primary_emotions[day] = "neutral"
            
            # Calculate overall distribution
            overall = defaultdict(float)
            for dist in daily_distributions.values():
                for emotion, score in dist.items():
                    overall[emotion] += score
            
            total = sum(overall.values()) or 1.0
            overall_distribution = {e: (s / total) for e, s in overall.items()}
            
            # Find dominant emotions (top 3)
            dominant = sorted(overall_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Detect patterns
            patterns = self._detect_emotion_patterns(daily_distributions)
            
            return {
                "period": f"{start_date} to {today.strftime('%Y-%m-%d')}",
                "days_analyzed": len(daily_distributions),
                "dominant_emotions": [{"emotion": e, "score": s} for e, s in dominant],
                "daily_primary": primary_emotions,
                "patterns": patterns,
                "trend_strength": patterns["strength"],
                "distribution": overall_distribution
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing emotion trends: {str(e)}")
            return {"error": str(e)}
    
    def _analyze_trends_from_database(self, days: int) -> Dict[str, Any]:
        """Analyze trends using database data when trend cache is empty"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get start date
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Query for emotions in the timeframe
            cursor.execute(
                "SELECT emotion, timestamp, intensity FROM emotions WHERE timestamp >= %s ORDER BY timestamp",
                (start_date,)
            )
            
            results = cursor.fetchall()
            
            # Group by day
            daily_emotions = defaultdict(lambda: defaultdict(float))
            
            for emotion, timestamp_str, intensity in results:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except ValueError:
                    # Try alternate format
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                
                day_key = timestamp.strftime("%Y-%m-%d")
                daily_emotions[day_key][emotion] += float(intensity)
            
            # Normalize distributions
            daily_distributions = {}
            for day, emotions in daily_emotions.items():
                total = sum(emotions.values()) or 1.0
                daily_distributions[day] = {e: (s / total) for e, s in emotions.items()}
            
            # Find primary emotion per day
            primary_emotions = {}
            for day, dist in daily_distributions.items():
                if dist:
                    primary_emotions[day] = max(dist.items(), key=lambda x: x[1])[0]
                else:
                    primary_emotions[day] = "neutral"
            
            # Calculate overall distribution
            overall = defaultdict(float)
            for dist in daily_distributions.values():
                for emotion, score in dist.items():
                    overall[emotion] += score
            
            total = sum(overall.values()) or 1.0
            overall_distribution = {e: (s / total) for e, s in overall.items() if s > 0}
            
            # Find dominant emotions (top 3)
            dominant = sorted(overall_distribution.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Detect patterns
            patterns = self._detect_emotion_patterns(daily_distributions)
            
            return {
                "period": f"Last {days} days",
                "days_analyzed": len(daily_distributions),
                "dominant_emotions": [{"emotion": e, "score": s} for e, s in dominant],
                "daily_primary": primary_emotions,
                "patterns": patterns,
                "trend_strength": patterns["strength"],
                "distribution": overall_distribution
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing emotion trends from database: {str(e)}")
            return {
                "period": f"Last {days} days",
                "error": str(e),
                "dominant_emotions": [],
                "distribution": {}
            }
    
    def _detect_emotion_patterns(self, daily_distributions: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Detect patterns in emotional data"""
        if not daily_distributions:
            return {"type": "insufficient_data", "description": "Not enough data to detect patterns", "strength": 0}
        
        days = sorted(daily_distributions.keys())
        if len(days) < 3:
            return {"type": "insufficient_days", "description": "Need at least 3 days of data", "strength": 0}
        
        # Check for consistent primary emotion
        primaries = []
        for day in days:
            dist = daily_distributions[day]
            if dist:
                primary = max(dist.items(), key=lambda x: x[1])[0]
                primaries.append(primary)
            else:
                primaries.append("neutral")
        
        # Count occurrences
        emotion_counts = Counter(primaries)
        most_common, count = emotion_counts.most_common(1)[0]
        consistency = count / len(primaries)
        
        if consistency >= 0.7:
            return {
                "type": "consistent_emotion",
                "emotion": most_common,
                "description": f"Consistently {most_common} ({count}/{len(primaries)} days)",
                "strength": consistency
            }
        
        # Check for alternating pattern
        if len(set(primaries)) == 2 and len(primaries) >= 4:
            # Check if emotions alternate
            alternating = True
            for i in range(len(primaries) - 2):
                if primaries[i] == primaries[i+1]:
                    alternating = False
                    break
            
            if alternating:
                return {
                    "type": "alternating",
                    "emotions": list(set(primaries)),
                    "description": f"Alternating between {' and '.join(set(primaries))}",
                    "strength": 0.8
                }
        
        # Check for upward/downward trends in specific emotions
        trends = {}
        for emotion in self.emotion_labels:
            values = [daily_distributions[day].get(emotion, 0) for day in days]
            if not any(values):
                continue
                
            # Calculate trend using linear regression slope
            n = len(values)
            x = list(range(n))
            x_mean = sum(x) / n
            y_mean = sum(values) / n
            
            numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            slope = numerator / denominator if denominator else 0
            
            # Normalize to -1 to 1 range
            max_possible_slope = max(values) - min(values)
            if max_possible_slope > 0:
                normalized_slope = slope / max_possible_slope
                
                # Only include significant trends
                if abs(normalized_slope) > 0.2:
                    trends[emotion] = normalized_slope
        
        if trends:
            # Find strongest trend
            strongest_emotion, strongest_trend = max(trends.items(), key=lambda x: abs(x[1]))
            trend_type = "increasing" if strongest_trend > 0 else "decreasing"
            
            return {
                "type": f"{trend_type}_trend",
                "emotion": strongest_emotion,
                "description": f"{strongest_emotion.capitalize()} is {trend_type}",
                "value": strongest_trend,
                "strength": abs(strongest_trend)
            }
        
        # If no clear pattern
        return {"type": "variable", "description": "No clear emotional pattern detected", "strength": 0.1}
    
    def get_emotional_wellbeing_score(self, days: int = 7) -> Dict[str, Any]:
        """
        Calculate an overall emotional wellbeing score based on recent emotion data
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with wellbeing score and contributing factors
        """
        try:
            # Get emotion trend data
            trends = self.analyze_emotion_trends(days)
            
            if "error" in trends:
                return {"score": 5.0, "confidence": 0.1, "error": trends["error"]}
            
            # Define positive and negative emotions
            positive_emotions = {"happy", "excited", "calm", "grateful", "hopeful", "proud", "interested"}
            negative_emotions = {"sad", "angry", "fearful", "disgusted", "anxious", "tired", "lonely", "embarrassed"}
            
            # Calculate positive vs negative ratio from distribution
            distribution = trends.get("distribution", {})
            
            positive_score = sum(distribution.get(e, 0) for e in positive_emotions)
            negative_score = sum(distribution.get(e, 0) for e in negative_emotions)
            
            # Calculate variety score (emotional diversity)
            significant_emotions = [e for e, s in distribution.items() if s > 0.05]
            variety_factor = min(1.0, len(significant_emotions) / 5)  # Ideal is 3-5 emotions
            
            # Calculate change factor (based on patterns)
            pattern_type = trends.get("patterns", {}).get("type", "variable")
            pattern_strength = trends.get("patterns", {}).get("strength", 0)
            
            change_factor = 1.0
            if pattern_type == "increasing_trend" and trends.get("patterns", {}).get("emotion") in positive_emotions:
                change_factor = 1.2  # Positive trend is good
            elif pattern_type == "decreasing_trend" and trends.get("patterns", {}).get("emotion") in negative_emotions:
                change_factor = 1.2  # Decreasing negative emotions is good
            elif pattern_type == "consistent_emotion" and trends.get("patterns", {}).get("emotion") in positive_emotions:
                change_factor = 1.1  # Consistent positive emotion is good
            elif pattern_type == "consistent_emotion" and trends.get("patterns", {}).get("emotion") in negative_emotions:
                change_factor = 0.9  # Consistent negative emotion is bad
            
            # Calculate base score (1-10 scale)
            if positive_score + negative_score > 0:
                # Ratio of positive to total significant emotions
                ratio = positive_score / (positive_score + negative_score)
                base_score = ratio * 10
            else:
                base_score = 5.0  # Neutral default
            
            # Apply modifiers
            wellbeing_score = base_score * variety_factor * change_factor
            
            # Ensure in range 1-10
            wellbeing_score = max(1.0, min(10.0, wellbeing_score))
            
            # Calculate confidence based on data quality
            data_points = sum(len(daily_distributions) for daily_distributions in trends.get("daily_primary", {}).values())
            confidence = min(1.0, data_points / (10 * days))
            
            # Format response
            dominant = trends.get("dominant_emotions", [])
            contributing_factors = []
            
            if dominant:
                primary = dominant[0]["emotion"] if dominant else "neutral"
                contributing_factors.append(f"Dominant emotion: {primary}")
            
            if pattern_type != "variable":
                contributing_factors.append(f"Pattern: {trends['patterns']['description']}")
            
            if variety_factor < 0.8:
                contributing_factors.append("Limited emotional range")
            elif variety_factor > 0.9:
                contributing_factors.append("Healthy emotional diversity")
            
            # Return comprehensive result
            return {
                "score": round(wellbeing_score, 1),
                "interpretation": self._interpret_wellbeing_score(wellbeing_score),
                "confidence": round(confidence, 2),
                "contributing_factors": contributing_factors,
                "dominant_emotions": dominant,
                "positive_ratio": round(ratio, 2) if 'ratio' in locals() else 0.5,
                "days_analyzed": days,
                "data_points": data_points if 'data_points' in locals() else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating wellbeing score: {str(e)}")
            return {"score": 5.0, "confidence": 0.1, "error": str(e)}
    
    def _interpret_wellbeing_score(self, score: float) -> str:
        """Interpret a wellbeing score with a descriptive label"""
        if score >= 9.0:
            return "Excellent emotional wellbeing"
        elif score >= 8.0:
            return "Very good emotional balance"
        elif score >= 7.0:
            return "Good emotional state"
        elif score >= 6.0:
            return "Moderately positive emotional state"
        elif score >= 5.0:
            return "Neutral emotional balance"
        elif score >= 4.0:
            return "Slight emotional challenges"
        elif score >= 3.0:
            return "Moderate emotional difficulties"
        elif score >= 2.0:
            return "Significant emotional distress"
        else:
            return "Severe emotional distress"
    
    def initialize(self):
        """Initialize the emotion tracker and create required tables"""
        self.logger.info("Initializing emotion tracker...")
        try:
            # Create emotions table if it doesn't exist
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emotions (
                    id SERIAL PRIMARY KEY,
                    emotion TEXT NOT NULL,
                    text TEXT,
                    timestamp TEXT NOT NULL,
                    source TEXT DEFAULT 'text',
                    intensity REAL DEFAULT 0.5
                )
            ''')
            
            conn.commit()
            self.logger.info("Emotion tracker initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize emotion tracker: {str(e)}")
    
    def analyze_text(self, text, context=None):
        """
        Analyze text to determine emotion (enhanced with advanced algorithms)
        
        Args:
            text: Text to analyze
            context: Optional context messages for improved analysis
            
        Returns:
            Primary emotion as string or detailed analysis dict if return_details=True
        """
        if not text:
            return "neutral"
        
        # Use advanced analysis under the hood
        result = self.analyze_text_advanced(text, context)
        
        # For backward compatibility, return just the primary emotion
        return result["primary_emotion"]
    
    def analyze_voice(self, audio_path, context=None):
        """
        Analyze voice recording to determine emotion using advanced techniques
        
        Args:
            audio_path: Path to the audio file to analyze
            context: Optional previous conversation context
            
        Returns:
            Primary emotion as string or detailed analysis dict if return_details=True
        """
        try:
            # Check if OpenAI integration is available for audio analysis
            if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
                result = self._analyze_voice_with_openai(audio_path, context)
                if result:
                    return result["primary_emotion"]
            
            # Fallback: Attempt to transcribe the audio and analyze the text
            # This would typically use a specialized voice emotion model
            # For now we'll simulate using pitch/tone features
            
            # Simulated voice features (would be extracted from audio)
            voice_features = {
                "pitch_mean": random.uniform(80, 250),  # in Hz
                "pitch_range": random.uniform(10, 100),  # in Hz
                "energy": random.uniform(0.2, 0.9),     # normalized energy
                "speech_rate": random.uniform(2, 6),    # syllables per second
                "pauses": random.uniform(0.05, 0.3)     # pause ratio
            }
            
            # Simple rule-based model for voice emotions
            emotions = {emotion: 0.0 for emotion in self.emotion_labels}
            
            # High pitch + high energy + fast speech = excitement/happiness 
            if voice_features["pitch_mean"] > 180 and voice_features["energy"] > 0.7:
                emotions["excited"] += 0.7
                emotions["happy"] += 0.5
            
            # Low pitch + low energy + slow speech = sadness
            if voice_features["pitch_mean"] < 120 and voice_features["energy"] < 0.5:
                emotions["sad"] += 0.7
                emotions["tired"] += 0.4
            
            # High energy + wide pitch range = anger
            if voice_features["energy"] > 0.7 and voice_features["pitch_range"] > 70:
                emotions["angry"] += 0.8
            
            # Low energy + narrow pitch range = calm/neutral
            if voice_features["energy"] < 0.4 and voice_features["pitch_range"] < 30:
                emotions["calm"] += 0.6
                emotions["neutral"] += 0.4
            
            # Fast speech + low pauses = excitement
            if voice_features["speech_rate"] > 5 and voice_features["pauses"] < 0.1:
                emotions["excited"] += 0.5
            
            # Slow speech + many pauses = thoughtful/confused
            if voice_features["speech_rate"] < 3 and voice_features["pauses"] > 0.2:
                emotions["confused"] += 0.6
                emotions["interested"] += 0.3
            
            # Find the emotion with the highest score
            if any(emotions.values()):
                primary_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                return primary_emotion
            
            # Default fallback if no clear emotion
            return "neutral"
            
        except Exception as e:
            self.logger.error(f"Error analyzing voice emotion: {str(e)}")
            return "neutral"
    
    def _analyze_voice_with_openai(self, audio_path, context=None):
        """Analyze voice using OpenAI's audio capabilities"""
        try:
            # Initialize OpenAI client if needed
            if not self.openai_client:
                self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # First transcribe the audio
            with open(audio_path, "rb") as audio_file:
                transcription = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            transcribed_text = transcription.text
            
            if not transcribed_text or len(transcribed_text.strip()) < 3:
                self.logger.warning("Voice transcription failed or returned empty text")
                return None
            
            # Then analyze the transcribed text with our advanced analyzer
            result = self.analyze_text_advanced(transcribed_text, context)
            
            # Add voice-specific metadata
            result["source"] = "voice"
            result["transcription"] = transcribed_text
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing voice with OpenAI: {str(e)}")
            return None
    
    def log_emotion(self, emotion, text="", source="text", intensity=0.5, session_id=None):
        """Log an emotion detection event to the database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            
            # Log to emotion_data table (used for dashboard visualizations)
            self.db_manager.execute_query(
                """
                INSERT INTO emotion_data (timestamp, emotion, source, intensity, text, session_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (timestamp, emotion, source, intensity, text, session_id)
            )
            
            # Also log to emotions table (used for model training)
            cursor.execute(
                "INSERT INTO emotions (emotion, text, timestamp, source, intensity) VALUES (%s, %s, %s, %s, %s)",
                (emotion, text, timestamp, source, intensity)
            )
            
            conn.commit()
            self.logger.debug(f"Logged emotion: {emotion} from {source}")
            
            # Also save to JSON file as backup (daily file)
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = os.path.join(self.data_dir, f"emotions_{date_str}.json")
            
            entry = {
                "emotion": emotion,
                "text": text,
                "timestamp": timestamp,
                "source": source,
                "intensity": intensity,
                "session_id": session_id
            }
            
            entries = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        entries = json.load(f)
                except json.JSONDecodeError:
                    entries = []
            
            entries.append(entry)
            
            with open(filename, 'w') as f:
                json.dump(entries, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to log emotion: {str(e)}")
            return False
    
    def get_emotion_history(self, days=7):
        """Get emotion history for the specified number of days"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get data from the last N days
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # The $1 parameter style requires prepared statements in psycopg2
            cursor.execute(
                "SELECT emotion, timestamp, intensity FROM emotions WHERE timestamp >= %s ORDER BY timestamp",
                (start_date,)
            )
            
            results = cursor.fetchall()
            
            # Format data for the chart
            emotions_by_date = {}
            for emotion, timestamp, intensity in results:
                # Parse timestamp and get just the date portion
                dt = datetime.fromisoformat(timestamp)
                date_str = dt.strftime("%Y-%m-%d")
                
                if date_str not in emotions_by_date:
                    emotions_by_date[date_str] = {}
                
                if emotion not in emotions_by_date[date_str]:
                    emotions_by_date[date_str][emotion] = 0
                
                emotions_by_date[date_str][emotion] += 1
            
            # Transform to array format for chart.js
            labels = sorted(emotions_by_date.keys())
            datasets = []
            
            for emotion in self.emotion_labels:
                data = [emotions_by_date.get(date, {}).get(emotion, 0) for date in labels]
                datasets.append({
                    "label": emotion.capitalize(),
                    "data": data
                })
            
            return {
                "labels": labels,
                "datasets": datasets
            }
        
        except Exception as e:
            self.logger.error(f"Failed to get emotion history: {str(e)}")
            return {"labels": [], "datasets": []}
    
    def get_total_entries(self):
        """Get the total number of emotion entries in the database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM emotions")
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            self.logger.error(f"Failed to get total entries: {str(e)}")
            return 0
            
    def get_session_emotion_history(self, session_id):
        """Get emotion history for a specific session"""
        try:
            # Get emotion data from the session using db_manager.execute_query
            # This query is used for retrieving emotion data by session ID
            results = self.db_manager.execute_query(
                """
                SELECT emotion, timestamp, intensity FROM emotion_data 
                WHERE session_id = %s 
                ORDER BY timestamp
                """,
                (session_id,)
            )
            
            if not results:
                return {
                    "timeline": [],
                    "distribution": {}
                }
            
            # Group by timestamp (in 5-minute intervals)
            timeline = []
            current_time = None
            current_emotions = None
            
            for emotion, timestamp_str, intensity in results:
                # Parse the timestamp
                try:
                    timestamp = datetime.fromisoformat(timestamp_str)
                except ValueError:
                    # Try alternate format
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                
                # Round to nearest 5-minute
                rounded_time = timestamp.replace(
                    minute=5 * (timestamp.minute // 5),
                    second=0,
                    microsecond=0
                )
                
                if current_time != rounded_time:
                    # New time interval
                    if current_emotions:
                        timeline.append({
                            "timestamp": current_time.isoformat(),
                            "emotions": current_emotions
                        })
                    
                    current_time = rounded_time
                    current_emotions = {e: 0 for e in self.emotion_labels}
                
                # Add the emotion intensity
                current_emotions[emotion] = max(current_emotions.get(emotion, 0), float(intensity))
            
            # Add the last emotions
            if current_emotions:
                timeline.append({
                    "timestamp": current_time.isoformat() if current_time else datetime.now().isoformat(),
                    "emotions": current_emotions
                })
            
            # Calculate distribution
            distribution = {}
            for entry in timeline:
                for emotion, intensity in entry["emotions"].items():
                    if intensity > 0:
                        distribution[emotion] = distribution.get(emotion, 0) + 1
            
            # Normalize distribution
            total = sum(distribution.values()) or 1
            distribution = {k: v / total for k, v in distribution.items()}
            
            return {
                "timeline": timeline,
                "distribution": distribution
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get session emotion history: {str(e)}")
            return {
                "timeline": [],
                "distribution": {}
            }
    
    def get_primary_emotion_for_name(self, name):
        """Get the primary emotion associated with a person's name"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Look for emotions associated with this name in text
            cursor.execute(
                "SELECT emotion, COUNT(*) as count FROM emotions WHERE text LIKE %s GROUP BY emotion ORDER BY count DESC LIMIT 1",
                (f"%{name}%",)
            )
            
            result = cursor.fetchone()
            if result and result[0]:
                return result[0]
                
            # If no specific emotion is found, check recognition history
            cursor.execute(
                "SELECT emotion, COUNT(*) as count FROM recognition_history WHERE name = %s GROUP BY emotion ORDER BY count DESC LIMIT 1",
                (name,)
            )
            
            result = cursor.fetchone()
            if result and result[0]:
                return result[0]
            
            # If still no result, return neutral
            return "neutral"
            
        except Exception as e:
            self.logger.error(f"Failed to get primary emotion for {name}: {str(e)}")
            return "neutral"
    
    def retrain_model(self):
        """Retrain the emotion model with collected data using advanced techniques"""
        self.logger.info("Retraining emotion model...")
        
        # Use a lock to prevent concurrent retraining
        with self.model_training_lock:
            try:
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                # Get all emotion data
                cursor.execute("SELECT text, emotion, intensity FROM emotions WHERE text IS NOT NULL AND text != ''")
                data = cursor.fetchall()
                
                if len(data) < 10:
                    self.logger.info("Not enough data to retrain model, skipping")
                    return {"status": "skipped", "reason": "insufficient_data"}
                
                # Extract keyword weights based on statistical significance
                keyword_stats = defaultdict(lambda: defaultdict(list))
                phrases = defaultdict(list)
                
                # Process all text samples
                for text, emotion, intensity in data:
                    if not text or emotion not in self.emotion_labels:
                        continue
                        
                    # Convert intensity to float if it's not already
                    if intensity is not None:
                        try:
                            intensity = float(intensity)
                        except (ValueError, TypeError):
                            intensity = 0.5
                    else:
                        intensity = 0.5
                    
                    # Extract words and calculate weights based on intensity
                    words = re.findall(r'\b\w+\b', text.lower())
                    
                    # Ignore very common words
                    common_words = {"the", "and", "is", "in", "to", "a", "of", "for", "that", "you", 
                                   "with", "on", "this", "are", "it", "as", "at", "be", "was", "have"}
                    filtered_words = [w for w in words if w not in common_words and len(w) > 2]
                    
                    # Add words with intensity as weight
                    for word in filtered_words:
                        keyword_stats[emotion][word].append(intensity)
                    
                    # Look for phrases (2-3 words)
                    if len(filtered_words) >= 2:
                        for i in range(len(filtered_words) - 1):
                            phrase = f"{filtered_words[i]} {filtered_words[i+1]}"
                            # Only add meaningful phrases that appear multiple times
                            if text.lower().count(phrase) > 0 and len(phrase) > 5:
                                phrases[emotion].append(phrase)
                    
                    if len(filtered_words) >= 3:
                        for i in range(len(filtered_words) - 2):
                            phrase = f"{filtered_words[i]} {filtered_words[i+1]} {filtered_words[i+2]}"
                            # Only add meaningful phrases
                            if text.lower().count(phrase) > 0 and len(phrase) > 8:
                                phrases[emotion].append(phrase)
                
                # Calculate average weights for each word
                new_keywords = {}
                for emotion in self.emotion_labels:
                    emotion_words = {}
                    for word, intensities in keyword_stats[emotion].items():
                        if len(intensities) >= 2:  # Only include words that appear multiple times
                            # Calculate weighted average
                            avg_intensity = sum(intensities) / len(intensities)
                            # Apply TF-IDF like scoring: words unique to this emotion get higher weight
                            exclusivity = 1.0
                            for other_emotion in self.emotion_labels:
                                if other_emotion != emotion and word in keyword_stats[other_emotion]:
                                    exclusivity *= 0.7  # Reduce weight for words found in multiple emotions
                            
                            final_weight = avg_intensity * exclusivity
                            emotion_words[word] = round(final_weight, 2)
                    
                    # Sort by weight and keep top words
                    sorted_words = sorted(emotion_words.items(), key=lambda x: x[1], reverse=True)
                    new_keywords[emotion] = dict(sorted_words[:30])  # Keep top 30 keywords
                
                # Update emotion keywords structure with new weights
                # Convert old format if needed
                for emotion in self.emotion_labels:
                    if emotion in self.emotion_keywords:
                        if isinstance(self.emotion_keywords[emotion], list):
                            # Convert old list format to dict with default weights
                            old_words = {word: 1.0 for word in self.emotion_keywords[emotion]}
                        else:
                            # Already in dict format
                            old_words = self.emotion_keywords[emotion]
                        
                        # Merge with new keywords, favoring new weights
                        if emotion in new_keywords:
                            merged = {**old_words, **new_keywords[emotion]}
                            # Keep top keywords by weight
                            sorted_merged = sorted(merged.items(), key=lambda x: x[1], reverse=True)
                            self.emotion_keywords[emotion] = dict(sorted_merged[:40])  # Increased to 40 for better coverage
                    else:
                        # If emotion wasn't in keywords, add it
                        self.emotion_keywords[emotion] = new_keywords.get(emotion, {})
                
                # Update emotional phrases (keep top 5 phrases per emotion)
                for emotion, emotion_phrases in phrases.items():
                    if emotion not in self.emotional_phrases:
                        self.emotional_phrases[emotion] = []
                    
                    # Count occurrences of each phrase
                    phrase_counts = Counter(emotion_phrases)
                    
                    # Keep most frequent phrases
                    top_phrases = [phrase for phrase, count in phrase_counts.most_common(5) if count >= 2]
                    
                    # Merge with existing phrases, avoiding duplicates
                    combined = set(self.emotional_phrases[emotion])
                    combined.update(top_phrases)
                    self.emotional_phrases[emotion] = list(combined)
                
                # Save updated models
                model_path = os.path.join(self.data_dir, "emotion_keywords.json")
                with open(model_path, 'w') as f:
                    json.dump(self.emotion_keywords, f, indent=2)
                
                phrases_path = os.path.join(self.data_dir, "emotional_phrases.json")
                with open(phrases_path, 'w') as f:
                    json.dump(self.emotional_phrases, f, indent=2)
                
                # Mark model as trained
                self.custom_model_trained = True
                
                self.logger.info(f"Advanced emotion model retraining complete with {len(data)} examples")
                return {
                    "status": "success", 
                    "samples": len(data),
                    "keywords_updated": sum(len(kw) for kw in self.emotion_keywords.values()),
                    "phrases_updated": sum(len(ph) for ph in self.emotional_phrases.values())
                }
                
            except Exception as e:
                self.logger.error(f"Failed to retrain emotion model: {str(e)}")
                return {"status": "error", "error": str(e)}
