import os
import logging
import json
import numpy as np
from datetime import datetime, timedelta
import sqlite3
from collections import Counter

class EmotionTracker:
    """Tracks, analyzes and visualizes emotional data over time"""
    
    def __init__(self, db_manager):
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager
        self.emotion_labels = [
            "neutral", "happy", "sad", "angry", "fearful", 
            "disgusted", "surprised", "confused", "interested"
        ]
        
        # Simple keyword-based emotion analysis as fallback
        self.emotion_keywords = {
            "happy": ["happy", "glad", "joy", "awesome", "great", "excellent", "wonderful"],
            "sad": ["sad", "unhappy", "depressed", "down", "blue", "gloomy", "miserable"],
            "angry": ["angry", "mad", "furious", "outraged", "irritated", "annoyed"],
            "fearful": ["afraid", "scared", "terrified", "anxious", "worried", "nervous"],
            "disgusted": ["disgusted", "gross", "revolting", "nasty", "yuck"],
            "surprised": ["surprised", "shocked", "amazed", "astonished", "wow"],
            "confused": ["confused", "puzzled", "perplexed", "unsure", "uncertain"],
            "interested": ["interested", "curious", "intrigued", "fascinated"]
        }
        
        # Ensure emotion data directory exists
        self.data_dir = "emotion_data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def initialize(self):
        """Initialize the emotion tracker and create required tables"""
        self.logger.info("Initializing emotion tracker...")
        try:
            # Create emotions table if it doesn't exist
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS emotions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    
    def analyze_text(self, text):
        """Analyze text to determine emotion (simple keyword matching as fallback)"""
        if not text:
            return "neutral"
        
        text = text.lower()
        matches = {}
        
        # Count keyword matches for each emotion
        for emotion, keywords in self.emotion_keywords.items():
            matches[emotion] = sum(1 for keyword in keywords if keyword in text)
        
        # Get the emotion with the most matches
        if any(matches.values()):
            max_emotion = max(matches.items(), key=lambda x: x[1])[0]
            return max_emotion
        
        return "neutral"
    
    def analyze_voice(self, audio_path):
        """Analyze voice recording to determine emotion"""
        # This would normally use a ML model to analyze audio features
        # For now, return a random emotion as a placeholder
        import random
        return random.choice(self.emotion_labels)
    
    def log_emotion(self, emotion, text="", source="text", intensity=0.5):
        """Log an emotion detection event to the database"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            timestamp = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO emotions (emotion, text, timestamp, source, intensity) VALUES (?, ?, ?, ?, ?)",
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
                "intensity": intensity
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
            
            cursor.execute(
                "SELECT emotion, timestamp, intensity FROM emotions WHERE timestamp >= ? ORDER BY timestamp",
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
    
    def get_primary_emotion_for_name(self, name):
        """Get the primary emotion associated with a person's name"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Look for emotions associated with this name in text
            cursor.execute(
                "SELECT emotion, COUNT(*) as count FROM emotions WHERE text LIKE ? GROUP BY emotion ORDER BY count DESC LIMIT 1",
                (f"%{name}%",)
            )
            
            result = cursor.fetchone()
            if result and result[0]:
                return result[0]
                
            # If no specific emotion is found, check recognition history
            cursor.execute(
                "SELECT emotion, COUNT(*) as count FROM recognition_history WHERE name = ? GROUP BY emotion ORDER BY count DESC LIMIT 1",
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
        """Retrain the emotion model with collected data"""
        self.logger.info("Retraining emotion model...")
        
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            # Get all emotion data
            cursor.execute("SELECT text, emotion FROM emotions WHERE text IS NOT NULL AND text != ''")
            data = cursor.fetchall()
            
            if len(data) < 10:
                self.logger.info("Not enough data to retrain model, skipping")
                return
            
            # Update emotion keywords based on collected data
            new_keywords = {emotion: [] for emotion in self.emotion_labels}
            
            for text, emotion in data:
                # Simple approach: just split the text and use individual words
                if text and emotion in self.emotion_labels:
                    words = text.lower().split()
                    # Add words that are not too common or too short
                    for word in words:
                        if len(word) > 3 and word not in new_keywords[emotion]:
                            new_keywords[emotion].append(word)
            
            # Merge with existing keywords
            for emotion in self.emotion_labels:
                if emotion in self.emotion_keywords:
                    # Keep existing keywords and add new ones
                    combined = list(set(self.emotion_keywords[emotion] + new_keywords[emotion]))
                    # Limit to top 20 keywords per emotion
                    self.emotion_keywords[emotion] = combined[:20]
            
            self.logger.info("Emotion model retraining complete")
            
            # Save updated model
            model_path = os.path.join(self.data_dir, "emotion_keywords.json")
            with open(model_path, 'w') as f:
                json.dump(self.emotion_keywords, f, indent=2)
            
        except Exception as e:
            self.logger.error(f"Failed to retrain emotion model: {str(e)}")
