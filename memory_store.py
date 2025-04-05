"""
Memory Store for Mashaaer Feelings Application
Handles persistent storage of user-specific preferences and data
"""
import sqlite3
import os
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

def init_db():
    """
    Initialize the memory database
    Creates the table if it doesn't exist
    """
    try:
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        conn = sqlite3.connect('memory.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                user_id TEXT,
                key TEXT,
                value TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Memory database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing memory database: {str(e)}")
        return False

def save_memory(user_id: str, key: str, value: Any):
    """
    Save a memory entry for a user
    
    Args:
        user_id: The ID of the user
        key: The key for the memory
        value: The value to store (will be converted to string)
    """
    try:
        conn = sqlite3.connect('memory.db')
        c = conn.cursor()
        
        # Convert value to string if it's not already
        if not isinstance(value, str):
            value = str(value)
        
        c.execute(
            "INSERT INTO memory (user_id, key, value) VALUES (?, ?, ?)", 
            (user_id, key, value)
        )
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Saved memory for user {user_id}: {key}={value}")
        return True
    except Exception as e:
        logger.error(f"Error saving memory: {str(e)}")
        return False

def get_memory(user_id: str, key: str) -> Optional[str]:
    """
    Get a memory entry for a user
    
    Args:
        user_id: The ID of the user
        key: The key for the memory
        
    Returns:
        The stored value as a string, or None if not found
    """
    try:
        conn = sqlite3.connect('memory.db')
        c = conn.cursor()
        
        c.execute(
            "SELECT value FROM memory WHERE user_id = ? AND key = ? ORDER BY timestamp DESC LIMIT 1", 
            (user_id, key)
        )
        
        row = c.fetchone()
        conn.close()
        
        if row:
            logger.debug(f"Retrieved memory for user {user_id}: {key}={row[0]}")
            return row[0]
        else:
            logger.debug(f"No memory found for user {user_id} and key {key}")
            return None
    except Exception as e:
        logger.error(f"Error getting memory: {str(e)}")
        return None

def get_all_user_memories(user_id: str) -> dict:
    """
    Get all memories for a user
    
    Args:
        user_id: The ID of the user
        
    Returns:
        Dictionary of key-value pairs for the user
    """
    try:
        conn = sqlite3.connect('memory.db')
        c = conn.cursor()
        
        c.execute("""
            SELECT key, value FROM (
                SELECT key, value, MAX(timestamp) as max_time 
                FROM memory 
                WHERE user_id = ? 
                GROUP BY key
            ) ORDER BY key
        """, (user_id,))
        
        rows = c.fetchall()
        conn.close()
        
        memories = {row[0]: row[1] for row in rows}
        
        logger.debug(f"Retrieved {len(memories)} memories for user {user_id}")
        return memories
    except Exception as e:
        logger.error(f"Error getting all user memories: {str(e)}")
        return {}

def delete_memory(user_id: str, key: str) -> bool:
    """
    Delete a memory entry for a user
    
    Args:
        user_id: The ID of the user
        key: The key for the memory to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect('memory.db')
        c = conn.cursor()
        
        c.execute("DELETE FROM memory WHERE user_id = ? AND key = ?", (user_id, key))
        
        rows_affected = c.rowcount
        conn.commit()
        conn.close()
        
        logger.debug(f"Deleted memory for user {user_id}: {key} ({rows_affected} rows affected)")
        return rows_affected > 0
    except Exception as e:
        logger.error(f"Error deleting memory: {str(e)}")
        return False

def clear_user_memories(user_id: str) -> bool:
    """
    Clear all memories for a user
    
    Args:
        user_id: The ID of the user
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect('memory.db')
        c = conn.cursor()
        
        c.execute("DELETE FROM memory WHERE user_id = ?", (user_id,))
        
        rows_affected = c.rowcount
        conn.commit()
        conn.close()
        
        logger.debug(f"Cleared all memories for user {user_id} ({rows_affected} rows affected)")
        return True
    except Exception as e:
        logger.error(f"Error clearing user memories: {str(e)}")
        return False