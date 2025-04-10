"""
Music Recommendation Service for Mashaaer Feelings Application

This service provides mood-based music recommendations to enhance the emotional 
learning experience by suggesting appropriate music based on emotional states.
"""

import json
import logging
import os
import random
from typing import Dict, List, Any, Optional

import requests

# Define emotion types directly to avoid circular imports
import enum

class EmotionType(enum.Enum):
    """Types of emotions that can be tracked"""
    HAPPINESS = "happiness"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise" 
    DISGUST = "disgust"
    MIXED = "mixed"  # For complex emotions


# Configure logger
logger = logging.getLogger(__name__)

# OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class MusicRecommendationService:
    """Service for providing mood-based music recommendations"""
    
    # Mapping of emotions to musical attributes
    EMOTION_MUSIC_MAPPING = {
        "happiness": {
            "genres": ["pop", "dance", "electronic", "funk", "reggae"],
            "tempo": "upbeat",
            "mode": "major",
            "energy": "high",
            "valence": "positive",
            "description": "Uplifting, energetic music with positive vibes"
        },
        "sadness": {
            "genres": ["blues", "classical", "ambient", "folk", "alternative"],
            "tempo": "slow",
            "mode": "minor",
            "energy": "low",
            "valence": "negative",
            "description": "Melancholic, slow-tempo music with emotional depth"
        },
        "anger": {
            "genres": ["rock", "metal", "punk", "industrial", "dubstep"],
            "tempo": "fast",
            "mode": "minor",
            "energy": "high",
            "valence": "negative",
            "description": "Intense, high-energy music with powerful expressions"
        },
        "fear": {
            "genres": ["dark ambient", "film scores", "experimental", "instrumental"],
            "tempo": "variable",
            "mode": "minor",
            "energy": "tense",
            "valence": "negative",
            "description": "Atmospheric, suspenseful music with tense elements"
        },
        "surprise": {
            "genres": ["jazz", "experimental", "world", "fusion", "electronic"],
            "tempo": "variable",
            "mode": "varied",
            "energy": "medium",
            "valence": "neutral",
            "description": "Unexpected, eclectic music with interesting variations"
        },
        "disgust": {
            "genres": ["noise", "experimental", "industrial", "avant-garde"],
            "tempo": "irregular",
            "mode": "atonal",
            "energy": "abrasive",
            "valence": "negative",
            "description": "Unconventional, challenging music with unusual textures"
        },
        "mixed": {
            "genres": ["eclectic", "fusion", "world", "soundtrack", "instrumental"],
            "tempo": "varied",
            "mode": "varied",
            "energy": "medium",
            "valence": "complex",
            "description": "Diverse, multifaceted music with emotional complexity"
        }
    }
    
    # Sample playlists for each emotion
    SAMPLE_PLAYLISTS = {
        "happiness": [
            {
                "name": "Happy Vibes",
                "description": "Upbeat tunes to boost your mood",
                "tracks": [
                    {"title": "Happy", "artist": "Pharrell Williams"},
                    {"title": "Good as Hell", "artist": "Lizzo"},
                    {"title": "Walking on Sunshine", "artist": "Katrina & The Waves"},
                    {"title": "Uptown Funk", "artist": "Mark Ronson ft. Bruno Mars"},
                    {"title": "Can't Stop the Feeling!", "artist": "Justin Timberlake"}
                ]
            },
            {
                "name": "Joyful Classics",
                "description": "Timeless songs that bring joy",
                "tracks": [
                    {"title": "Dancing Queen", "artist": "ABBA"},
                    {"title": "I Got You (I Feel Good)", "artist": "James Brown"},
                    {"title": "Lovely Day", "artist": "Bill Withers"},
                    {"title": "Three Little Birds", "artist": "Bob Marley"},
                    {"title": "Signed, Sealed, Delivered", "artist": "Stevie Wonder"}
                ]
            }
        ],
        "sadness": [
            {
                "name": "Melancholy Moments",
                "description": "Songs to accompany reflective moods",
                "tracks": [
                    {"title": "Someone Like You", "artist": "Adele"},
                    {"title": "Fix You", "artist": "Coldplay"},
                    {"title": "Skinny Love", "artist": "Bon Iver"},
                    {"title": "Hurt", "artist": "Johnny Cash"},
                    {"title": "Nothing Compares 2 U", "artist": "Sinéad O'Connor"}
                ]
            },
            {
                "name": "Rainy Day Blues",
                "description": "Perfect soundtrack for gray skies",
                "tracks": [
                    {"title": "Everybody Hurts", "artist": "R.E.M."},
                    {"title": "The Sound of Silence", "artist": "Simon & Garfunkel"},
                    {"title": "Mad World", "artist": "Gary Jules"},
                    {"title": "Hallelujah", "artist": "Jeff Buckley"},
                    {"title": "Tears in Heaven", "artist": "Eric Clapton"}
                ]
            }
        ],
        "anger": [
            {
                "name": "Release the Tension",
                "description": "Powerful tracks to channel frustration",
                "tracks": [
                    {"title": "Killing In The Name", "artist": "Rage Against The Machine"},
                    {"title": "Break Stuff", "artist": "Limp Bizkit"},
                    {"title": "Bulls On Parade", "artist": "Rage Against The Machine"},
                    {"title": "Bleed It Out", "artist": "Linkin Park"},
                    {"title": "Du Hast", "artist": "Rammstein"}
                ]
            },
            {
                "name": "Controlled Chaos",
                "description": "Intense music with emotional power",
                "tracks": [
                    {"title": "Master of Puppets", "artist": "Metallica"},
                    {"title": "Chop Suey!", "artist": "System of a Down"},
                    {"title": "Toxicity", "artist": "System of a Down"},
                    {"title": "Sabotage", "artist": "Beastie Boys"},
                    {"title": "Mama Said Knock You Out", "artist": "LL Cool J"}
                ]
            }
        ],
        "fear": [
            {
                "name": "Facing Fears",
                "description": "Atmospheric tracks for confronting anxiety",
                "tracks": [
                    {"title": "Teardrop", "artist": "Massive Attack"},
                    {"title": "Climbing Up The Walls", "artist": "Radiohead"},
                    {"title": "The Alien", "artist": "Ben Salisbury & Geoff Barrow"},
                    {"title": "Requiem for a Dream", "artist": "Clint Mansell"},
                    {"title": "Creep", "artist": "Radiohead"}
                ]
            },
            {
                "name": "Tension & Release",
                "description": "Tracks that build and resolve tension",
                "tracks": [
                    {"title": "Hysteria", "artist": "Muse"},
                    {"title": "Breathe", "artist": "The Prodigy"},
                    {"title": "Clubbed to Death", "artist": "Rob Dougan"},
                    {"title": "Where Is My Mind?", "artist": "Pixies"},
                    {"title": "Until It Sleeps", "artist": "Metallica"}
                ]
            }
        ],
        "surprise": [
            {
                "name": "Unexpected Delights",
                "description": "Eclectic mix of surprising musical gems",
                "tracks": [
                    {"title": "Take Five", "artist": "Dave Brubeck"},
                    {"title": "Bohemian Rhapsody", "artist": "Queen"},
                    {"title": "Knights of Cydonia", "artist": "Muse"},
                    {"title": "Roundabout", "artist": "Yes"},
                    {"title": "Pyramid Song", "artist": "Radiohead"}
                ]
            },
            {
                "name": "Musical Plot Twists",
                "description": "Songs with unexpected structures and sounds",
                "tracks": [
                    {"title": "Paranoid Android", "artist": "Radiohead"},
                    {"title": "Stairway to Heaven", "artist": "Led Zeppelin"},
                    {"title": "Thriller", "artist": "Michael Jackson"},
                    {"title": "Flight of the Bumblebee", "artist": "Nikolai Rimsky-Korsakov"},
                    {"title": "Lateralus", "artist": "Tool"}
                ]
            }
        ],
        "disgust": [
            {
                "name": "Challenging Sounds",
                "description": "Unconventional music for testing boundaries",
                "tracks": [
                    {"title": "Revolution 9", "artist": "The Beatles"},
                    {"title": "The Art of Dying", "artist": "Gojira"},
                    {"title": "Frankie Teardrop", "artist": "Suicide"},
                    {"title": "Hamburger Lady", "artist": "Throbbing Gristle"},
                    {"title": "Dictator", "artist": "Deli Girls"}
                ]
            },
            {
                "name": "Sonic Experiments",
                "description": "Boundary-pushing audio experiences",
                "tracks": [
                    {"title": "Ventolin", "artist": "Aphex Twin"},
                    {"title": "Threnody for the Victims of Hiroshima", "artist": "Krzysztof Penderecki"},
                    {"title": "Faaip De Oiad", "artist": "Tool"},
                    {"title": "Ionization", "artist": "Edgard Varèse"},
                    {"title": "Catacombs", "artist": "Godspeed You! Black Emperor"}
                ]
            }
        ],
        "mixed": [
            {
                "name": "Emotional Journey",
                "description": "Diverse tracks spanning multiple emotional states",
                "tracks": [
                    {"title": "Bohemian Rhapsody", "artist": "Queen"},
                    {"title": "All of the Lights", "artist": "Kanye West"},
                    {"title": "Comfortably Numb", "artist": "Pink Floyd"},
                    {"title": "Nights", "artist": "Frank Ocean"},
                    {"title": "The Chain", "artist": "Fleetwood Mac"}
                ]
            },
            {
                "name": "Complex Emotions",
                "description": "Music that evokes a spectrum of feelings",
                "tracks": [
                    {"title": "Runaway", "artist": "Kanye West"},
                    {"title": "Like a Rolling Stone", "artist": "Bob Dylan"},
                    {"title": "Motion Picture Soundtrack", "artist": "Radiohead"},
                    {"title": "Hurt", "artist": "Nine Inch Nails"},
                    {"title": "Good News", "artist": "Mac Miller"}
                ]
            }
        ]
    }
    
    @staticmethod
    def get_recommendations(
        emotion: str, 
        intensity: Optional[float] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        limit: int = 2
    ) -> Dict[str, Any]:
        """
        Get music recommendations based on emotion
        
        Args:
            emotion: The emotional state to base recommendations on
            intensity: Optional intensity of the emotion (0.0 to 1.0)
            user_preferences: Optional dictionary of user music preferences
            limit: Number of playlists to return
            
        Returns:
            Dictionary with recommended playlists and explanation
        """
        try:
            # Validate emotion type
            if emotion not in [e.value for e in EmotionType]:
                emotion = "mixed"  # Default to mixed if invalid
            
            # Get music characteristics based on emotion
            music_characteristics = MusicRecommendationService.EMOTION_MUSIC_MAPPING.get(
                emotion, MusicRecommendationService.EMOTION_MUSIC_MAPPING["mixed"]
            )
            
            # Adjust based on intensity if provided
            if intensity is not None:
                intensity = float(intensity)
                intensity = max(0.0, min(1.0, intensity))  # Clamp to 0.0-1.0
                
                # Modify characteristics based on intensity
                music_characteristics = MusicRecommendationService._adjust_for_intensity(
                    music_characteristics, intensity
                )
            
            # Apply user preferences if provided
            if user_preferences:
                music_characteristics = MusicRecommendationService._apply_user_preferences(
                    music_characteristics, user_preferences
                )
            
            # Get recommendations using AI if API key is available
            if OPENAI_API_KEY:
                playlists = MusicRecommendationService._get_ai_recommendations(
                    emotion, music_characteristics, limit
                )
            else:
                # Use sample playlists as fallback
                playlists = MusicRecommendationService._get_sample_playlists(emotion, limit)
            
            # Return recommendations with explanation
            return {
                "success": True,
                "emotion": emotion,
                "intensity": intensity,
                "music_characteristics": music_characteristics,
                "playlists": playlists,
                "explanation": MusicRecommendationService._generate_explanation(
                    emotion, music_characteristics
                )
            }
            
        except Exception as e:
            logger.error(f"Error in get_recommendations: {str(e)}")
            return {
                "success": False,
                "error": "Failed to generate recommendations",
                "details": str(e)
            }
    
    @staticmethod
    def _adjust_for_intensity(music_characteristics: Dict[str, Any], intensity: float) -> Dict[str, Any]:
        """
        Adjust music characteristics based on emotional intensity
        
        Args:
            music_characteristics: Base music characteristics
            intensity: Intensity of the emotion (0.0 to 1.0)
            
        Returns:
            Adjusted music characteristics
        """
        adjusted = music_characteristics.copy()
        
        # Adjust energy based on intensity
        if "energy" in adjusted:
            if adjusted["energy"] == "high":
                if intensity < 0.3:
                    adjusted["energy"] = "medium"
                elif intensity < 0.7:
                    adjusted["energy"] = "medium-high"
                else:
                    adjusted["energy"] = "very high"
            elif adjusted["energy"] == "low":
                if intensity < 0.3:
                    adjusted["energy"] = "very low"
                elif intensity < 0.7:
                    adjusted["energy"] = "low"
                else:
                    adjusted["energy"] = "medium-low"
            elif adjusted["energy"] == "medium":
                if intensity < 0.3:
                    adjusted["energy"] = "low-medium"
                elif intensity < 0.7:
                    adjusted["energy"] = "medium"
                else:
                    adjusted["energy"] = "medium-high"
        
        # Adjust tempo based on intensity
        if "tempo" in adjusted:
            if adjusted["tempo"] == "fast":
                if intensity < 0.3:
                    adjusted["tempo"] = "medium"
                elif intensity < 0.7:
                    adjusted["tempo"] = "moderately fast"
                else:
                    adjusted["tempo"] = "very fast"
            elif adjusted["tempo"] == "slow":
                if intensity < 0.3:
                    adjusted["tempo"] = "very slow"
                elif intensity < 0.7:
                    adjusted["tempo"] = "slow"
                else:
                    adjusted["tempo"] = "medium-slow"
        
        return adjusted
    
    @staticmethod
    def _apply_user_preferences(music_characteristics: Dict[str, Any], user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply user preferences to music characteristics
        
        Args:
            music_characteristics: Base music characteristics
            user_preferences: User's music preferences
            
        Returns:
            Adjusted music characteristics
        """
        adjusted = music_characteristics.copy()
        
        # Apply preferred genres if specified
        if "preferred_genres" in user_preferences and user_preferences["preferred_genres"]:
            # Prioritize user's preferred genres
            preferred_genres = user_preferences["preferred_genres"]
            original_genres = adjusted.get("genres", [])
            
            # Find intersection between emotion genres and user preferences
            common_genres = [g for g in preferred_genres if g in original_genres]
            
            if common_genres:
                # If there are common genres, prioritize them
                remaining_slots = max(3 - len(common_genres), 0)
                other_genres = [g for g in original_genres if g not in common_genres]
                
                adjusted["genres"] = common_genres + other_genres[:remaining_slots]
            else:
                # If no common genres, use a mix of both
                adjusted["genres"] = preferred_genres[:2] + original_genres[:3]
        
        # Apply tempo preference if specified
        if "preferred_tempo" in user_preferences:
            # Blend the emotion-based tempo with user preference
            preferred_tempo = user_preferences["preferred_tempo"]
            if preferred_tempo != adjusted.get("tempo"):
                # Create a compromise tempo
                adjusted["tempo"] = f"moderately {preferred_tempo}"
        
        return adjusted
    
    @staticmethod
    def _get_ai_recommendations(emotion: str, characteristics: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        Get AI-generated music recommendations using OpenAI API
        
        Args:
            emotion: Emotional state
            characteristics: Music characteristics
            limit: Number of playlists to generate
            
        Returns:
            List of playlist recommendations
        """
        try:
            # Formulate prompt for the AI
            prompt = f"""
            Create {limit} music playlist recommendations for someone feeling {emotion}.
            The music should have these characteristics: {json.dumps(characteristics)}
            
            For each playlist, provide:
            1. A catchy name related to the emotion
            2. A brief description of the playlist's mood and purpose
            3. A list of 5 specific songs with artists that fit the emotion and characteristics
            
            Format your response as a JSON array with this structure for each playlist:
            {{
                "name": "Playlist Name",
                "description": "Brief description",
                "tracks": [
                    {{"title": "Song Title", "artist": "Artist Name"}},
                    ...
                ]
            }}
            
            Only return the JSON array, nothing else.
            """
            
            # Make API request
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }
            
            payload = {
                "model": "gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                "messages": [
                    {"role": "system", "content": "You are a music recommendation expert who creates playlists based on emotional states."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                playlists_json = json.loads(result["choices"][0]["message"]["content"])
                
                # Extract playlists array if nested
                if "playlists" in playlists_json:
                    playlists = playlists_json["playlists"]
                else:
                    playlists = playlists_json
                
                return playlists[:limit]
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                # Fallback to sample playlists if API call fails
                return MusicRecommendationService._get_sample_playlists(emotion, limit)
        
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {str(e)}")
            # Fallback to sample playlists
            return MusicRecommendationService._get_sample_playlists(emotion, limit)
    
    @staticmethod
    def _get_sample_playlists(emotion: str, limit: int) -> List[Dict[str, Any]]:
        """
        Get sample playlists for an emotion
        
        Args:
            emotion: Emotional state
            limit: Number of playlists to return
            
        Returns:
            List of playlists
        """
        # Get playlists for the emotion or use mixed as fallback
        playlists = MusicRecommendationService.SAMPLE_PLAYLISTS.get(
            emotion, MusicRecommendationService.SAMPLE_PLAYLISTS["mixed"]
        )
        
        # Return a subset if we have more than needed
        if len(playlists) > limit:
            return random.sample(playlists, limit)
        
        return playlists
    
    @staticmethod
    def _generate_explanation(emotion: str, characteristics: Dict[str, Any]) -> str:
        """
        Generate an explanation for the music recommendations
        
        Args:
            emotion: Emotional state
            characteristics: Music characteristics
            
        Returns:
            Explanation string
        """
        base_explanation = f"When feeling {emotion}, music with {characteristics.get('description', 'these characteristics')} can be beneficial."
        
        # Add details about genres
        if "genres" in characteristics:
            genres_text = ", ".join(characteristics["genres"])
            base_explanation += f" Genres like {genres_text} can complement this emotional state."
        
        # Add details about musical qualities
        qualities = []
        if "tempo" in characteristics:
            qualities.append(f"{characteristics['tempo']} tempo")
        if "energy" in characteristics:
            qualities.append(f"{characteristics['energy']} energy")
        if "mode" in characteristics:
            qualities.append(f"{characteristics['mode']} mode")
        
        if qualities:
            qualities_text = ", ".join(qualities)
            base_explanation += f" The {qualities_text} of these selections can help process and enhance your emotional experience."
        
        return base_explanation
    
    @staticmethod
    def get_available_emotions() -> List[Dict[str, str]]:
        """
        Get list of available emotions for recommendations
        
        Returns:
            List of emotion dictionaries with id, name, and description
        """
        emotions = []
        
        for emotion_type in EmotionType:
            emotion_id = emotion_type.value
            emotion_name = emotion_type.name.capitalize()
            
            # Get music characteristics for description
            characteristics = MusicRecommendationService.EMOTION_MUSIC_MAPPING.get(
                emotion_id, {"description": "Various musical styles"}
            )
            
            emotions.append({
                "id": emotion_id,
                "name": emotion_name,
                "description": characteristics.get("description", "")
            })
        
        return emotions