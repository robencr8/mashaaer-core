"""
Memory Store for Mashaaer Feelings Application
Handles persistent storage of user-specific preferences and data

Extended for Phase 2 with additional features:
- Memory expiration management
- Enhanced memory retrieval with filters
- Memory categories and tagging
- Memory usage analytics 
"""
import sqlite3
import os
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List, Tuple, Union

logger = logging.getLogger(__name__)

def init_db():
    """
    Initialize the memory database
    Creates the tables if they don't exist
    Adds new schema elements for Phase 2
    """
    try:
        # Ensure logs directory exists
        os.makedirs('logs', exist_ok=True)
        
        conn = sqlite3.connect('memory.db')
        c = conn.cursor()
        
        # Create core memory table (v1)
        c.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                user_id TEXT,
                key TEXT,
                value TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if category column exists, add if not (Phase 2)
        cursor = conn.execute('PRAGMA table_info(memory)')
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'category' not in columns:
            c.execute('ALTER TABLE memory ADD COLUMN category TEXT DEFAULT "general"')
            logger.info("Added category column to memory table")
            
        if 'expires_at' not in columns:
            c.execute('ALTER TABLE memory ADD COLUMN expires_at DATETIME DEFAULT NULL')
            logger.info("Added expires_at column to memory table")
            
        if 'importance' not in columns:
            c.execute('ALTER TABLE memory ADD COLUMN importance INTEGER DEFAULT 1')
            logger.info("Added importance column to memory table")
            
        # Create memory tags table (Phase 2)
        c.execute('''
            CREATE TABLE IF NOT EXISTS memory_tags (
                memory_id INTEGER,
                tag TEXT,
                PRIMARY KEY (memory_id, tag)
            )
        ''')
        
        # Create memory access log table (Phase 2)
        c.execute('''
            CREATE TABLE IF NOT EXISTS memory_access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                key TEXT,
                access_type TEXT,  -- 'read', 'write', 'delete'
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Memory database initialized successfully with Phase 2 enhancements")
        return True
    except Exception as e:
        logger.error(f"Error initializing memory database: {str(e)}")
        return False

def save_memory(user_id: str, key: str, value: Any, category: str = "general", 
                importance: int = 1, expires_in_days: Optional[int] = None,
                tags: Optional[List[str]] = None):
    """
    Save a memory entry for a user with enhanced metadata (Phase 2)
    
    Args:
        user_id: The ID of the user
        key: The key for the memory
        value: The value to store (will be converted to string)
        category: Category for organizing memories (e.g., "preferences", "interactions")
        importance: Importance level (1-5, with 5 being most important)
        expires_in_days: Optional number of days after which this memory expires
        tags: Optional list of tags to associate with this memory
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect('memory.db')
        c = conn.cursor()
        
        # Convert value to string if it's not already
        if not isinstance(value, str):
            value = str(value)
        
        # Calculate expiration date if provided
        expires_at = None
        if expires_in_days is not None:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        # Insert the memory
        c.execute("""
            INSERT INTO memory 
            (user_id, key, value, category, importance, expires_at) 
            VALUES (?, ?, ?, ?, ?, ?)
            """, 
            (user_id, key, value, category, importance, expires_at)
        )
        
        # Get the ID of the inserted memory for tags
        memory_id = c.lastrowid
        
        # Add tags if provided
        if tags and memory_id:
            for tag in tags:
                c.execute("INSERT OR IGNORE INTO memory_tags (memory_id, tag) VALUES (?, ?)",
                         (memory_id, tag))
        
        # Log the access
        c.execute("""
            INSERT INTO memory_access_log (user_id, key, access_type)
            VALUES (?, ?, ?)
            """,
            (user_id, key, "write")
        )
        
        conn.commit()
        
        # Log details
        log_msg = f"Saved memory for user {user_id}: {key}={value[:30]}... " if len(str(value)) > 30 else f"Saved memory for user {user_id}: {key}={value}"
        log_msg += f"[category={category}, importance={importance}]"
        if expires_at:
            log_msg += f" [expires: {expires_at}]"
        if tags:
            log_msg += f" [tags: {', '.join(tags)}]"
            
        logger.debug(log_msg)
        
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving memory: {str(e)}")
        return False

def get_memory(user_id: str, key: str, include_metadata: bool = False) -> Optional[Union[str, Dict[str, Any]]]:
    """
    Get a memory entry for a user with optional metadata (Phase 2)
    
    Args:
        user_id: The ID of the user
        key: The key for the memory
        include_metadata: Whether to include metadata in the response
        
    Returns:
        If include_metadata is False: The stored value as a string, or None if not found
        If include_metadata is True: Dict with value and metadata, or None if not found
    """
    try:
        conn = sqlite3.connect('memory.db')
        conn.row_factory = sqlite3.Row  # Get results as dictionaries
        c = conn.cursor()
        
        # Get the memory with all metadata
        c.execute("""
            SELECT rowid, value, category, importance, expires_at, timestamp 
            FROM memory 
            WHERE user_id = ? AND key = ? 
                AND (expires_at IS NULL OR datetime(expires_at) > datetime('now'))
            ORDER BY timestamp DESC 
            LIMIT 1
            """, 
            (user_id, key)
        )
        
        row = c.fetchone()
        
        if not row:
            logger.debug(f"No memory found for user {user_id} and key {key}")
            conn.close()
            return None
            
        # Get any tags for this memory
        memory_id = row['rowid']
        tags = []
        
        if memory_id:
            tag_cursor = conn.cursor()
            tag_cursor.execute("SELECT tag FROM memory_tags WHERE memory_id = ?", (memory_id,))
            tags = [tag[0] for tag in tag_cursor.fetchall()]
        
        # Log the access
        c.execute("""
            INSERT INTO memory_access_log (user_id, key, access_type)
            VALUES (?, ?, ?)
            """,
            (user_id, key, "read")
        )
        
        conn.commit()
        conn.close()
        
        if include_metadata:
            # Return the full metadata
            result = dict(row)
            result['tags'] = tags
            result['key'] = key
            result['user_id'] = user_id
            
            # Convert SQLite datetime strings to Python datetime objects
            if result.get('timestamp'):
                result['timestamp'] = datetime.strptime(result['timestamp'], '%Y-%m-%d %H:%M:%S')
            if result.get('expires_at'):
                result['expires_at'] = datetime.strptime(result['expires_at'], '%Y-%m-%dT%H:%M:%S.%f')
                
            logger.debug(f"Retrieved memory with metadata for user {user_id}: {key}")
            return result
        else:
            # Return just the value
            value = row['value']
            logger.debug(f"Retrieved memory for user {user_id}: {key}={value[:30]}..." if len(value) > 30 else f"Retrieved memory for user {user_id}: {key}={value}")
            return value
    except Exception as e:
        logger.error(f"Error getting memory: {str(e)}")
        return None

def get_all_user_memories(user_id: str, 
                     include_metadata: bool = False,
                     category: Optional[str] = None,
                     min_importance: int = 1,
                     include_expired: bool = False,
                     tags: Optional[List[str]] = None) -> Union[Dict[str, str], List[Dict[str, Any]]]:
    """
    Get all memories for a user with optional filtering (Phase 2)
    
    Args:
        user_id: The ID of the user
        include_metadata: Whether to return full objects with metadata
        category: Filter memories by category
        min_importance: Filter memories by minimum importance level
        include_expired: Whether to include expired memories
        tags: Filter memories that have all of these tags
        
    Returns:
        If include_metadata is False: Dictionary of key-value pairs
        If include_metadata is True: List of memory objects with full metadata
    """
    try:
        conn = sqlite3.connect('memory.db')
        
        if include_metadata:
            conn.row_factory = sqlite3.Row
            
        c = conn.cursor()
        
        # Start building the query
        query = """
            SELECT m.rowid, m.key, m.value, m.category, m.importance, m.expires_at, m.timestamp
            FROM memory m
            WHERE m.user_id = ? 
        """
        
        params = []
        params.append(user_id)  # First parameter is user_id
        
        # Add filters
        if category:
            query += " AND m.category = ? "
            params.append(category)
            
        if min_importance > 1:
            query += " AND m.importance >= ? "
            params.append(min_importance)
            
        if not include_expired:
            query += " AND (m.expires_at IS NULL OR datetime(m.expires_at) > datetime('now')) "
            
        # This ensures we only get the latest version of each memory
        query += """
            AND m.timestamp = (
                SELECT MAX(timestamp) 
                FROM memory 
                WHERE user_id = ? AND key = m.key
            )
        """
        params.append(user_id)
        
        # Add order by
        query += " ORDER BY m.key "
        
        # Execute the main query
        c.execute(query, params)
        rows = c.fetchall()
        
        # If tags filter is provided, post-process the results
        if tags and tags:
            # Get all memory_ids that match our initial query
            memory_ids = []
            if include_metadata:
                memory_ids = [row['rowid'] for row in rows]
            else:
                memory_ids = [row[0] for row in rows]
                
            if memory_ids:
                # For each tag, find the memories that have it
                filtered_ids = set(memory_ids)
                
                for tag in tags:
                    tag_query = "SELECT memory_id FROM memory_tags WHERE tag = ? AND memory_id IN ({})".format(
                        ','.join(['?'] * len(memory_ids))
                    )
                    
                    tag_cursor = conn.cursor()
                    tag_cursor.execute(tag_query, [tag] + memory_ids)
                    tag_matches = set(row[0] for row in tag_cursor.fetchall())
                    
                    # Intersect with our running set to keep only memories with all tags
                    filtered_ids &= tag_matches
                    
                # Filter our original results
                if include_metadata:
                    rows = [row for row in rows if row['rowid'] in filtered_ids]
                else:
                    rows = [row for row in rows if row[0] in filtered_ids]
        
        # Format the response
        if include_metadata:
            # Return full memory objects
            results = []
            
            for row in rows:
                memory = dict(row)
                
                # Get tags for this memory
                tag_cursor = conn.cursor()
                tag_cursor.execute("SELECT tag FROM memory_tags WHERE memory_id = ?", (memory['rowid'],))
                memory['tags'] = [tag[0] for tag in tag_cursor.fetchall()]
                
                # Convert timestamps
                if memory.get('timestamp'):
                    memory['timestamp'] = datetime.strptime(memory['timestamp'], '%Y-%m-%d %H:%M:%S')
                if memory.get('expires_at'):
                    memory['expires_at'] = datetime.strptime(memory['expires_at'], '%Y-%m-%dT%H:%M:%S.%f')
                
                results.append(memory)
                
            logger.debug(f"Retrieved {len(results)} detailed memories for user {user_id}")
        else:
            # Return simple key-value dictionary
            if include_metadata:
                results = {row['key']: row['value'] for row in rows}
            else:
                results = {row[1]: row[2] for row in rows}
                
            logger.debug(f"Retrieved {len(results)} memories for user {user_id}")
        
        # Log the access for analytics
        log_cursor = conn.cursor()
        for row in rows:
            key = row['key'] if include_metadata else row[1]
            log_cursor.execute(
                "INSERT INTO memory_access_log (user_id, key, access_type) VALUES (?, ?, ?)",
                (user_id, key, "read")
            )
            
        conn.commit()
        conn.close()
        
        return results
    except Exception as e:
        logger.error(f"Error getting all user memories: {str(e)}")
        return {} if not include_metadata else []

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

def add_memory_tags(memory_id: int, tags: List[str]) -> bool:
    """
    Add tags to a memory (Phase 2)
    
    Args:
        memory_id: The ID of the memory
        tags: List of tags to add
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect('memory.db')
        c = conn.cursor()
        
        for tag in tags:
            c.execute(
                "INSERT OR IGNORE INTO memory_tags (memory_id, tag) VALUES (?, ?)",
                (memory_id, tag)
            )
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Added {len(tags)} tags to memory {memory_id}")
        return True
    except Exception as e:
        logger.error(f"Error adding tags to memory: {str(e)}")
        return False

def remove_memory_tags(memory_id: int, tags: List[str]) -> bool:
    """
    Remove tags from a memory (Phase 2)
    
    Args:
        memory_id: The ID of the memory
        tags: List of tags to remove
        
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect('memory.db')
        c = conn.cursor()
        
        for tag in tags:
            c.execute(
                "DELETE FROM memory_tags WHERE memory_id = ? AND tag = ?",
                (memory_id, tag)
            )
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Removed {len(tags)} tags from memory {memory_id}")
        return True
    except Exception as e:
        logger.error(f"Error removing tags from memory: {str(e)}")
        return False

def get_memories_by_tag(user_id: str, tag: str, include_metadata: bool = False) -> Union[Dict[str, str], List[Dict[str, Any]]]:
    """
    Get all memories for a user that have a specific tag (Phase 2)
    
    Args:
        user_id: The ID of the user
        tag: The tag to filter by
        include_metadata: Whether to return full objects with metadata
        
    Returns:
        If include_metadata is False: Dictionary of key-value pairs
        If include_metadata is True: List of memory objects with full metadata
    """
    try:
        conn = sqlite3.connect('memory.db')
        
        if include_metadata:
            conn.row_factory = sqlite3.Row
            
        c = conn.cursor()
        
        query = """
            SELECT m.rowid, m.key, m.value, m.category, m.importance, m.expires_at, m.timestamp
            FROM memory m
            JOIN memory_tags mt ON m.rowid = mt.memory_id
            WHERE m.user_id = ? AND mt.tag = ?
            AND (m.expires_at IS NULL OR datetime(m.expires_at) > datetime('now'))
        """
        
        # Execute the query
        c.execute(query, (user_id, tag))
        rows = c.fetchall()
        
        # Format the response
        if include_metadata:
            # Return full memory objects
            results = []
            
            for row in rows:
                memory = dict(row)
                
                # Get all tags for this memory
                tag_cursor = conn.cursor()
                tag_cursor.execute("SELECT tag FROM memory_tags WHERE memory_id = ?", (memory['rowid'],))
                memory['tags'] = [tag[0] for tag in tag_cursor.fetchall()]
                
                # Convert timestamps
                if memory.get('timestamp'):
                    memory['timestamp'] = datetime.strptime(memory['timestamp'], '%Y-%m-%d %H:%M:%S')
                if memory.get('expires_at'):
                    memory['expires_at'] = datetime.strptime(memory['expires_at'], '%Y-%m-%dT%H:%M:%S.%f')
                
                results.append(memory)
                
            logger.debug(f"Retrieved {len(results)} memories with tag '{tag}' for user {user_id}")
        else:
            # Return simple key-value dictionary
            if include_metadata:
                results = {row['key']: row['value'] for row in rows}
            else:
                results = {row[1]: row[2] for row in rows}
                
            logger.debug(f"Retrieved {len(results)} memories with tag '{tag}' for user {user_id}")
        
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Error getting memories by tag: {str(e)}")
        return {} if not include_metadata else []

def get_memory_access_stats(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get statistics on memory access patterns (Phase 2)
    
    Args:
        user_id: Optional user ID to filter by
        
    Returns:
        Dictionary with access statistics
    """
    try:
        conn = sqlite3.connect('memory.db')
        c = conn.cursor()
        
        stats = {}
        
        # Base query parts
        base_select = "SELECT access_type, COUNT(*) as count"
        base_from = "FROM memory_access_log"
        base_group = "GROUP BY access_type"
        
        # Overall access by type
        if user_id:
            c.execute(f"{base_select} {base_from} WHERE user_id = ? {base_group}", (user_id,))
            where_clause = "WHERE user_id = ?"
            params = (user_id,)
        else:
            c.execute(f"{base_select} {base_from} {base_group}")
            where_clause = ""
            params = ()
            
        stats["access_by_type"] = {row[0]: row[1] for row in c.fetchall()}
        
        # Most accessed keys
        c.execute(f"""
            SELECT key, COUNT(*) as count 
            FROM memory_access_log
            {where_clause}
            GROUP BY key
            ORDER BY count DESC
            LIMIT 10
        """, params)
        
        stats["most_accessed_keys"] = {row[0]: row[1] for row in c.fetchall()}
        
        # Calculate average accesses per key
        c.execute(f"""
            SELECT COUNT(DISTINCT key) as key_count, COUNT(*) as access_count
            FROM memory_access_log
            {where_clause}
        """, params)
        
        row = c.fetchone()
        if row and row[0] > 0:
            stats["avg_accesses_per_key"] = row[1] / row[0]
        else:
            stats["avg_accesses_per_key"] = 0
            
        # Most recent accesses
        c.execute(f"""
            SELECT key, access_type, timestamp
            FROM memory_access_log
            {where_clause}
            ORDER BY timestamp DESC
            LIMIT 10
        """, params)
        
        stats["recent_accesses"] = [
            {"key": row[0], "access_type": row[1], "timestamp": row[2]} 
            for row in c.fetchall()
        ]
        
        conn.close()
        return stats
    except Exception as e:
        logger.error(f"Error getting memory access stats: {str(e)}")
        return {"error": str(e)}