"""
AI-Powered Engagement Recommendation Engine

This module provides personalized recommendations to users based on
their emotional patterns, interaction history, and preferences.
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

import openai
from openai import OpenAI

from database.db_manager import DatabaseManager
from emotion_tracker import EmotionTracker

# Configure logging
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    AI-powered recommendation engine that provides personalized suggestions
    to improve user engagement and emotional well-being.
    """

    def __init__(self, db_manager: DatabaseManager, emotion_tracker: EmotionTracker):
        """
        Initialize the recommendation engine with necessary dependencies.

        Args:
            db_manager: Database manager for accessing user data
            emotion_tracker: Emotion tracking system for analyzing emotional patterns
        """
        self.db_manager = db_manager
        self.emotion_tracker = emotion_tracker
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.cache_duration = 3600  # Cache recommendations for 1 hour
        self.recommendation_cache = {}
        logger.info("Recommendation engine initialized")

    def get_recommendations(
        self,
        user_id: str,
        emotion_data: Optional[Dict] = None,
        context: Optional[Dict] = None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate personalized recommendations for a user.

        Args:
            user_id: Unique identifier for the user
            emotion_data: Current emotional state (optional)
            context: Additional context for recommendations (optional)
            force_refresh: Force regeneration of recommendations

        Returns:
            Dictionary containing personalized recommendations
        """
        cache_key = f"recommendations:{user_id}"
        
        # Check cache if not forcing refresh
        if not force_refresh and cache_key in self.recommendation_cache:
            cached_data = self.recommendation_cache[cache_key]
            # Use cache if it's still valid
            if time.time() - cached_data.get("timestamp", 0) < self.cache_duration:
                logger.debug(f"Returning cached recommendations for user {user_id}")
                return cached_data.get("data", {})
        
        # Collect user data for generating recommendations
        user_data = self._collect_user_data(user_id)
        
        # Merge with provided emotion data if available
        if emotion_data:
            user_data["current_emotion"] = emotion_data
        
        # Add context if provided
        if context:
            user_data.update(context)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(user_data)
        
        # Cache the results
        self.recommendation_cache[cache_key] = {
            "data": recommendations,
            "timestamp": time.time()
        }
        
        return recommendations

    def _collect_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        Collect relevant user data for generating recommendations.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary containing user data
        """
        # Default empty data structure
        user_data = {
            "user_id": user_id,
            "emotion_history": [],
            "interactions": [],
            "preferences": {},
            "recent_activities": [],
            "wellbeing_score": None,
            "challenges": []
        }
        
        try:
            # Fetch emotional history (last 7 days)
            emotion_history = self._get_emotion_history(user_id)
            user_data["emotion_history"] = emotion_history
            
            # Calculate emotional patterns and wellbeing score
            emotion_patterns, wellbeing_score = self._analyze_emotion_patterns(emotion_history)
            user_data["emotion_patterns"] = emotion_patterns
            user_data["wellbeing_score"] = wellbeing_score
            
            # Fetch user preferences
            preferences = self._get_user_preferences(user_id)
            user_data["preferences"] = preferences
            
            # Fetch recent activities/interactions
            recent_activities = self._get_recent_activities(user_id)
            user_data["recent_activities"] = recent_activities
            
            # Identify potential challenges based on emotional patterns
            challenges = self._identify_challenges(emotion_patterns, wellbeing_score)
            user_data["challenges"] = challenges
            
        except Exception as e:
            logger.error(f"Error collecting user data: {str(e)}")
        
        return user_data

    def _get_emotion_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve emotional history for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            List of emotion records
        """
        # Query the database for emotion records
        try:
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            query = """
            SELECT * FROM emotion_records 
            WHERE user_id = ? AND timestamp > ? 
            ORDER BY timestamp DESC
            """
            
            params = (user_id, seven_days_ago.isoformat())
            result = self.db_manager.execute_query(query, params)
            
            # Format the records
            emotion_history = []
            for record in result:
                try:
                    # Parse the emotion data JSON
                    emotion_data = json.loads(record["emotion_data"]) if isinstance(record["emotion_data"], str) else record["emotion_data"]
                    
                    emotion_history.append({
                        "timestamp": record["timestamp"],
                        "primary_emotion": record["primary_emotion"],
                        "intensity": record["intensity"] if "intensity" in record else None,
                        "emotion_data": emotion_data,
                        "source": record["source"] if "source" in record else "text",
                        "text": record["text"] if "text" in record else None
                    })
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Error parsing emotion record: {str(e)}")
            
            return emotion_history
            
        except Exception as e:
            logger.error(f"Database error when fetching emotion history: {str(e)}")
            return []

    def _analyze_emotion_patterns(
        self, emotion_history: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], float]:
        """
        Analyze emotional patterns from history.

        Args:
            emotion_history: List of emotion records

        Returns:
            Tuple of (emotion patterns dict, wellbeing score)
        """
        if not emotion_history:
            return {}, 0.5  # Default neutral wellbeing score
        
        # Count emotion occurrences
        emotion_counts = {}
        for record in emotion_history:
            emotion = record.get("primary_emotion", "neutral")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Calculate percentages
        total = sum(emotion_counts.values())
        emotion_percentages = {
            emotion: count / total for emotion, count in emotion_counts.items()
        }
        
        # Identify dominant emotions (top 3)
        dominant_emotions = sorted(
            emotion_percentages.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:3]
        
        # Calculate emotion transitions
        transitions = {}
        for i in range(1, len(emotion_history)):
            prev_emotion = emotion_history[i]["primary_emotion"]
            curr_emotion = emotion_history[i-1]["primary_emotion"]
            
            if prev_emotion not in transitions:
                transitions[prev_emotion] = {}
            
            transitions[prev_emotion][curr_emotion] = transitions[prev_emotion].get(curr_emotion, 0) + 1
        
        # Calculate wellbeing score
        wellbeing_score = self._calculate_wellbeing_score(emotion_percentages)
        
        # Identify emotion trends (increasing/decreasing)
        trends = {}
        if len(emotion_history) >= 3:
            # Group by day
            daily_emotions = {}
            for record in emotion_history:
                timestamp = datetime.fromisoformat(record["timestamp"]) if isinstance(record["timestamp"], str) else record["timestamp"]
                day = timestamp.date().isoformat()
                
                if day not in daily_emotions:
                    daily_emotions[day] = {}
                
                emotion = record["primary_emotion"]
                daily_emotions[day][emotion] = daily_emotions[day].get(emotion, 0) + 1
            
            # Calculate trends for top emotions
            days = sorted(daily_emotions.keys())
            for emotion, _ in dominant_emotions:
                if len(days) >= 2:
                    first_day = days[-1]
                    last_day = days[0]
                    
                    first_count = daily_emotions[first_day].get(emotion, 0) / sum(daily_emotions[first_day].values()) if sum(daily_emotions[first_day].values()) > 0 else 0
                    last_count = daily_emotions[last_day].get(emotion, 0) / sum(daily_emotions[last_day].values()) if sum(daily_emotions[last_day].values()) > 0 else 0
                    
                    if abs(last_count - first_count) > 0.1:  # 10% change threshold
                        trends[emotion] = "increasing" if last_count > first_count else "decreasing"
        
        # Combine all analysis into patterns
        patterns = {
            "dominant_emotions": dominant_emotions,
            "percentages": emotion_percentages,
            "transitions": transitions,
            "trends": trends
        }
        
        return patterns, wellbeing_score

    def _calculate_wellbeing_score(self, emotion_percentages: Dict[str, float]) -> float:
        """
        Calculate emotional wellbeing score based on emotion percentages.

        Args:
            emotion_percentages: Dictionary of emotion percentages

        Returns:
            Wellbeing score (0.0 to 1.0)
        """
        # Define emotion valence (positive/negative contribution to wellbeing)
        # Scale: -1.0 (very negative) to 1.0 (very positive)
        emotion_valence = {
            "joy": 0.9,
            "happiness": 0.85,
            "contentment": 0.8,
            "satisfaction": 0.75,
            "love": 0.9,
            "gratitude": 0.8,
            "excitement": 0.7,
            "amusement": 0.6,
            "pride": 0.65,
            "optimism": 0.7,
            "hope": 0.6,
            "inspiration": 0.7,
            "awe": 0.5,
            "interest": 0.4,
            "neutral": 0.0,
            "surprise": 0.1,
            "confusion": -0.2,
            "boredom": -0.3,
            "indifference": -0.4,
            "sadness": -0.6,
            "grief": -0.8,
            "disappointment": -0.5,
            "anxiety": -0.7,
            "fear": -0.75,
            "worry": -0.6,
            "nervousness": -0.5,
            "anger": -0.8,
            "frustration": -0.6,
            "annoyance": -0.5,
            "disgust": -0.7,
            "guilt": -0.6,
            "shame": -0.65,
            "regret": -0.55,
            "loneliness": -0.7,
            "jealousy": -0.6,
            "envy": -0.55,
            "contempt": -0.7,
            "mixed": 0.0  # Neutral for mixed emotions
        }
        
        # Calculate weighted score
        total_score = 0
        total_weight = 0
        
        for emotion, percentage in emotion_percentages.items():
            # Default to 0 (neutral) for unknown emotions
            valence = emotion_valence.get(emotion.lower(), 0)
            total_score += valence * percentage
            total_weight += percentage
        
        # Normalize to 0-1 range (from -1 to 1)
        if total_weight > 0:
            normalized_score = (total_score / total_weight + 1) / 2
            return max(0, min(1, normalized_score))  # Clamp between 0 and 1
        else:
            return 0.5  # Default to neutral

    def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve user preferences.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Dictionary of user preferences
        """
        try:
            query = "SELECT * FROM user_preferences WHERE user_id = ?"
            params = (user_id,)
            result = self.db_manager.execute_query(query, params)
            
            if result and len(result) > 0:
                preferences = result[0]
                
                # Parse JSON fields if needed
                for key in preferences:
                    if key.endswith('_json') and preferences[key]:
                        try:
                            preferences[key] = json.loads(preferences[key])
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in user preferences: {key}")
                
                return preferences
            else:
                # If no preferences found, check for user profile
                profile_query = "SELECT * FROM user_profiles WHERE user_id = ?"
                profile_result = self.db_manager.execute_query(profile_query, params)
                
                if profile_result and len(profile_result) > 0:
                    # Extract relevant profile data as preferences
                    profile = profile_result[0]
                    return {
                        "language": profile.get("language", "en"),
                        "name": profile.get("name", ""),
                        "interests": profile.get("interests", ""),
                        "profile_data": profile
                    }
                
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching user preferences: {str(e)}")
            return {}

    def _get_recent_activities(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve recent user activities.

        Args:
            user_id: Unique identifier for the user

        Returns:
            List of recent activity records
        """
        try:
            three_days_ago = datetime.now() - timedelta(days=3)
            
            # Query interaction logs
            query = """
            SELECT * FROM interaction_logs 
            WHERE user_id = ? AND timestamp > ? 
            ORDER BY timestamp DESC
            LIMIT 50
            """
            
            params = (user_id, three_days_ago.isoformat())
            result = self.db_manager.execute_query(query, params)
            
            activities = []
            for record in result:
                try:
                    activities.append({
                        "timestamp": record["timestamp"],
                        "action": record["action"],
                        "details": json.loads(record["details"]) if isinstance(record["details"], str) and record["details"] else {},
                        "duration": record.get("duration", None)
                    })
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Error parsing activity record: {str(e)}")
            
            return activities
            
        except Exception as e:
            logger.error(f"Error fetching recent activities: {str(e)}")
            return []

    def _identify_challenges(
        self, emotion_patterns: Dict[str, Any], wellbeing_score: float
    ) -> List[Dict[str, Any]]:
        """
        Identify potential challenges based on emotional patterns.

        Args:
            emotion_patterns: Dictionary of emotion patterns
            wellbeing_score: Calculated wellbeing score

        Returns:
            List of potential challenges
        """
        challenges = []
        
        # Check dominant negative emotions
        if "dominant_emotions" in emotion_patterns:
            for emotion, percentage in emotion_patterns["dominant_emotions"]:
                if emotion in [
                    "sadness", "anxiety", "fear", "anger", "frustration",
                    "grief", "loneliness", "guilt", "shame", "regret"
                ] and percentage > 0.3:  # 30% threshold
                    challenges.append({
                        "type": "dominant_negative_emotion",
                        "emotion": emotion,
                        "percentage": percentage,
                        "severity": "high" if percentage > 0.5 else "medium"
                    })
        
        # Check for emotional volatility
        if "transitions" in emotion_patterns:
            transitions = emotion_patterns["transitions"]
            volatility_score = 0
            transition_count = 0
            
            for from_emotion, targets in transitions.items():
                for to_emotion, count in targets.items():
                    if from_emotion != to_emotion:
                        transition_count += count
                        
                        # Increase volatility score for transitions between opposites
                        if (from_emotion in ["joy", "happiness", "contentment"] and 
                            to_emotion in ["sadness", "anger", "frustration"]) or \
                           (to_emotion in ["joy", "happiness", "contentment"] and 
                            from_emotion in ["sadness", "anger", "frustration"]):
                            volatility_score += count * 2
                        else:
                            volatility_score += count
            
            if transition_count > 0:
                volatility_ratio = volatility_score / transition_count
                if volatility_ratio > 1.5:
                    challenges.append({
                        "type": "emotional_volatility",
                        "volatility_score": volatility_ratio,
                        "severity": "high" if volatility_ratio > 2.0 else "medium"
                    })
        
        # Check overall wellbeing
        if wellbeing_score < 0.4:
            challenges.append({
                "type": "low_wellbeing",
                "score": wellbeing_score,
                "severity": "high" if wellbeing_score < 0.3 else "medium"
            })
        
        # Check for persistent negative trends
        if "trends" in emotion_patterns:
            trends = emotion_patterns["trends"]
            for emotion, direction in trends.items():
                if emotion in [
                    "sadness", "anxiety", "fear", "anger", "frustration", 
                    "grief", "loneliness", "guilt", "shame", "regret"
                ] and direction == "increasing":
                    challenges.append({
                        "type": "increasing_negative_emotion",
                        "emotion": emotion,
                        "severity": "medium"
                    })
                elif emotion in [
                    "joy", "happiness", "contentment", "satisfaction", 
                    "love", "gratitude", "excitement"
                ] and direction == "decreasing":
                    challenges.append({
                        "type": "decreasing_positive_emotion",
                        "emotion": emotion,
                        "severity": "medium"
                    })
        
        return challenges

    def _generate_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized recommendations using AI.

        Args:
            user_data: Collected user data

        Returns:
            Dictionary containing recommendations
        """
        try:
            # Create input for OpenAI
            current_emotion = user_data.get("current_emotion", {})
            current_primary = current_emotion.get("primary_emotion", "neutral") if current_emotion else "neutral"
            
            emotion_history = user_data.get("emotion_history", [])
            recent_emotions = [e.get("primary_emotion", "neutral") for e in emotion_history[:5]]
            
            wellbeing_score = user_data.get("wellbeing_score", 0.5)
            challenges = user_data.get("challenges", [])
            challenge_types = [c.get("type") for c in challenges]
            
            # Format user data for prompt
            prompt_data = {
                "current_emotion": current_primary,
                "recent_emotions": recent_emotions,
                "wellbeing_score": wellbeing_score,
                "challenges": challenge_types,
                "language": user_data.get("preferences", {}).get("language", "en")
            }
            
            # Prepare system prompt
            system_prompt = """
            You are Mashaaer, an AI emotional wellbeing advisor designed to provide holistic, culturally-sensitive recommendations to improve emotional wellbeing.
            
            Based on the user's emotional data, provide thoughtful recommendations in these categories:
            1. Immediate actions - Quick activities to improve the current emotional state
            2. Well-being practices - Long-term practices to build emotional resilience
            3. Social connections - Ways to leverage social support for emotional health
            4. Creative expression - Art, music, or writing activities suited to their emotional state
            5. Reflective insights - Thoughtful observations about patterns in their emotional journey
            
            Keep these guidelines in mind:
            - Be supportive, not clinical or diagnostic
            - Respect cultural sensitivities of Middle Eastern contexts
            - Focus on practical, accessible suggestions
            - Be specific and actionable, not generic
            - Include a mix of short-term and long-term recommendations
            - Format all responses in JSON
            """
            
            # Create user prompt
            user_prompt = f"""
            Please provide personalized recommendations based on this emotional data:
            - Current emotion: {prompt_data['current_emotion']}
            - Recent emotions: {', '.join(prompt_data['recent_emotions'])}
            - Wellbeing score: {prompt_data['wellbeing_score']} (0.0-1.0 scale)
            - Challenges: {', '.join(prompt_data['challenges']) if prompt_data['challenges'] else 'None identified'}
            - Preferred language: {prompt_data['language']}
            
            Respond in JSON format with these sections:
            {{
                "immediate_actions": [list of 3-5 immediate actions],
                "wellbeing_practices": [list of 3-5 practices],
                "social_connections": [list of 2-3 suggestions],
                "creative_expression": [list of 2-3 activities],
                "reflective_insights": [list of 2-3 insights],
                "affirmation": "A supportive affirmation based on their emotional state"
            }}
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            response_content = response.choices[0].message.content
            recommendations = json.loads(response_content)
            
            # Add metadata
            recommendations["generated_at"] = datetime.now().isoformat()
            recommendations["current_emotion"] = current_primary
            recommendations["wellbeing_score"] = wellbeing_score
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            
            # Fallback to basic recommendations
            return self._generate_fallback_recommendations(user_data)

    def _generate_fallback_recommendations(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate fallback recommendations when AI generation fails.

        Args:
            user_data: Collected user data

        Returns:
            Dictionary containing basic recommendations
        """
        current_emotion = user_data.get("current_emotion", {})
        current_primary = current_emotion.get("primary_emotion", "neutral") if current_emotion else "neutral"
        
        # Basic recommendations based on emotion categories
        positive_emotions = ["joy", "happiness", "contentment", "excitement", "love", "gratitude", "pride"]
        negative_emotions = ["sadness", "anger", "fear", "anxiety", "frustration", "grief", "loneliness"]
        neutral_emotions = ["neutral", "surprise", "confusion", "anticipation"]
        
        if current_primary in positive_emotions:
            recommendations = {
                "immediate_actions": [
                    "Express gratitude by writing down three things you're thankful for",
                    "Share your positive feelings with someone you care about",
                    "Channel your energy into a creative project"
                ],
                "wellbeing_practices": [
                    "Start a daily gratitude journal",
                    "Practice mindfulness meditation to maintain emotional balance",
                    "Establish a regular sleep schedule"
                ],
                "social_connections": [
                    "Reach out to someone who might need emotional support",
                    "Plan a social gathering to share your positive energy"
                ],
                "creative_expression": [
                    "Create art that captures your current positive feelings",
                    "Listen to music that enhances your mood"
                ],
                "reflective_insights": [
                    "Notice what activities or people contribute to your positive emotions",
                    "Reflect on how you can sustain this emotional state"
                ],
                "affirmation": "You deserve to experience joy and positivity. Allow yourself to fully embrace these feelings."
            }
        elif current_primary in negative_emotions:
            recommendations = {
                "immediate_actions": [
                    "Take three deep, slow breaths to center yourself",
                    "Go for a short walk outside",
                    "Listen to calming music",
                    "Drink a glass of water and practice self-care"
                ],
                "wellbeing_practices": [
                    "Establish a regular physical exercise routine",
                    "Practice self-compassion daily",
                    "Set healthy boundaries in relationships",
                    "Consider journaling about your feelings"
                ],
                "social_connections": [
                    "Reach out to a trusted friend or family member",
                    "Consider joining a support group related to your challenges"
                ],
                "creative_expression": [
                    "Express your feelings through writing or art",
                    "Create a playlist that helps process your emotions"
                ],
                "reflective_insights": [
                    "Your emotions are valid and provide important information",
                    "Difficult emotions are temporary and will evolve with time"
                ],
                "affirmation": "It's okay to not be okay. You have the strength to navigate through challenging emotions."
            }
        else:  # Neutral emotions
            recommendations = {
                "immediate_actions": [
                    "Engage in mindful breathing for 5 minutes",
                    "Set an intention for how you want to feel today",
                    "Do a brief body scan meditation"
                ],
                "wellbeing_practices": [
                    "Develop a consistent mindfulness practice",
                    "Create a balanced daily routine",
                    "Explore new activities that interest you"
                ],
                "social_connections": [
                    "Schedule time with someone who energizes you",
                    "Join a class or group aligned with your interests"
                ],
                "creative_expression": [
                    "Experiment with a new creative medium",
                    "Listen to music that inspires you"
                ],
                "reflective_insights": [
                    "Neutral states are good times for reflection and planning",
                    "Consider what emotional states you'd like to cultivate"
                ],
                "affirmation": "You are present and aware, ready to shape your emotional journey."
            }
        
        # Add metadata
        recommendations["generated_at"] = datetime.now().isoformat()
        recommendations["current_emotion"] = current_primary
        recommendations["wellbeing_score"] = user_data.get("wellbeing_score", 0.5)
        recommendations["is_fallback"] = True
        
        return recommendations

    def log_recommendation_feedback(
        self,
        user_id: str,
        recommendation_id: str,
        feedback: Dict[str, Any]
    ) -> bool:
        """
        Log user feedback on recommendations for continuous improvement.

        Args:
            user_id: Unique identifier for the user
            recommendation_id: Identifier for the recommendation
            feedback: User feedback data

        Returns:
            Boolean indicating success
        """
        try:
            feedback_data = json.dumps(feedback)
            timestamp = datetime.now().isoformat()
            
            query = """
            INSERT INTO recommendation_feedback 
            (user_id, recommendation_id, feedback, timestamp) 
            VALUES (?, ?, ?, ?)
            """
            
            params = (user_id, recommendation_id, feedback_data, timestamp)
            self.db_manager.execute_query(query, params, fetch=False)
            
            logger.info(f"Logged recommendation feedback for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging recommendation feedback: {str(e)}")
            return False

    def create_tables(self) -> None:
        """Create necessary database tables if they don't exist."""
        try:
            # Create table for recommendation feedback
            recommendation_feedback_query = """
            CREATE TABLE IF NOT EXISTS recommendation_feedback (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                recommendation_id VARCHAR(64) NOT NULL,
                feedback TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL
            )
            """
            self.db_manager.execute_query(recommendation_feedback_query, fetch=False)
            
            # Create table for user-recommendation interactions
            recommendation_interactions_query = """
            CREATE TABLE IF NOT EXISTS recommendation_interactions (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(64) NOT NULL,
                recommendation_id VARCHAR(64) NOT NULL,
                interaction_type VARCHAR(32) NOT NULL,
                details TEXT,
                timestamp TIMESTAMP NOT NULL
            )
            """
            self.db_manager.execute_query(recommendation_interactions_query, fetch=False)
            
            logger.info("Recommendation engine tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating recommendation engine tables: {str(e)}")