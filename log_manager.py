"""
Log Manager for Mashaaer Feelings Application
Handles logging of user interactions for analysis and improvement
"""
import csv
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Constants
LOG_DIR = 'logs'
INTERACTION_LOG_FILE = os.path.join(LOG_DIR, 'interaction_log.csv')

def init_logs():
    """
    Initialize the logging system
    Creates the logs directory and files if they don't exist
    """
    try:
        # Ensure logs directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Create interaction log file with headers if it doesn't exist
        if not os.path.exists(INTERACTION_LOG_FILE):
            with open(INTERACTION_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 
                    'user_input', 
                    'emotion', 
                    'action', 
                    'params',
                    'language'
                ])
        
        logger.info("Logging system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing logging system: {str(e)}")
        return False

def log_interaction(user_input: str, emotion: str, action: str, params: Dict[str, Any], language: str = 'en'):
    """
    Log a user interaction
    
    Args:
        user_input: The text input from the user
        emotion: The detected emotion
        action: The action taken by the system
        params: Additional parameters for the action
        language: The language of the interaction ('en' or 'ar')
    """
    try:
        # Ensure logs directory exists
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Convert params to JSON string
        params_str = json.dumps(params) if isinstance(params, dict) else str(params)
        
        # Write to CSV log
        with open(INTERACTION_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.utcnow().isoformat(),
                user_input,
                emotion,
                action,
                params_str,
                language
            ])
        
        logger.debug(f"Logged interaction: emotion={emotion}, action={action}, lang={language}")
        return True
    except Exception as e:
        logger.error(f"Error logging interaction: {str(e)}")
        return False

def get_recent_interactions(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get recent interactions from the log
    
    Args:
        limit: Maximum number of interactions to retrieve
        
    Returns:
        List of interaction records as dictionaries
    """
    try:
        if not os.path.exists(INTERACTION_LOG_FILE):
            return []
        
        interactions = []
        with open(INTERACTION_LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Skip header row
            
            # Read rows and convert to dictionaries
            for row in reader:
                if len(row) >= 5:  # Ensure row has minimum expected columns
                    interaction = {
                        'timestamp': row[0],
                        'user_input': row[1],
                        'emotion': row[2],
                        'action': row[3],
                        'params': row[4],
                        'language': row[5] if len(row) >= 6 else 'en'  # Default to 'en' if language not present
                    }
                    interactions.append(interaction)
        
        # Return the most recent interactions first, up to the limit
        return interactions[-limit:][::-1] if interactions else []
    except Exception as e:
        logger.error(f"Error getting recent interactions: {str(e)}")
        return []

def get_emotion_statistics() -> Dict[str, int]:
    """
    Get statistics on emotions from the interaction log
    
    Returns:
        Dictionary with emotion counts
    """
    try:
        if not os.path.exists(INTERACTION_LOG_FILE):
            return {}
        
        emotion_counts = {}
        with open(INTERACTION_LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            
            for row in reader:
                if len(row) >= 3:  # Ensure row has emotion column
                    emotion = row[2]
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        return emotion_counts
    except Exception as e:
        logger.error(f"Error getting emotion statistics: {str(e)}")
        return {}

def get_action_statistics() -> Dict[str, int]:
    """
    Get statistics on actions from the interaction log
    
    Returns:
        Dictionary with action counts
    """
    try:
        if not os.path.exists(INTERACTION_LOG_FILE):
            return {}
        
        action_counts = {}
        with open(INTERACTION_LOG_FILE, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            
            for row in reader:
                if len(row) >= 4:  # Ensure row has action column
                    action = row[3]
                    action_counts[action] = action_counts.get(action, 0) + 1
        
        return action_counts
    except Exception as e:
        logger.error(f"Error getting action statistics: {str(e)}")
        return {}

def clear_logs() -> bool:
    """
    Clear all logs
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if os.path.exists(INTERACTION_LOG_FILE):
            # Recreate the file with just the headers
            with open(INTERACTION_LOG_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 
                    'user_input', 
                    'emotion', 
                    'action', 
                    'params',
                    'language'
                ])
            
            logger.info("Logs cleared successfully")
            return True
        
        return False
    except Exception as e:
        logger.error(f"Error clearing logs: {str(e)}")
        return False