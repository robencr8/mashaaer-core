import os
import logging
import sqlite3
import threading
import time

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_path="robin_memory.db"):
        self.logger = logging.getLogger(__name__)
        self.db_path = db_path
        
        # Connection pool (thread-local)
        self.local = threading.local()
        
        # Make sure the database directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def initialize_db(self):
        """Initialize the database and create tables"""
        self.logger.info(f"Initializing database at {self.db_path}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create core tables
        
        # 1. Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                type TEXT,
                updated_at TEXT
            )
        ''')
        
        # 2. Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                response TEXT,
                timestamp TEXT,
                emotion TEXT,
                intent TEXT
            )
        ''')
        
        # 3. User profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                face_id TEXT,
                preferences TEXT,
                last_interaction TEXT
            )
        ''')
        
        # 4. System logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                level TEXT,
                module TEXT,
                message TEXT
            )
        ''')
        
        conn.commit()
        self.logger.info("Database initialized successfully")
    
    def get_connection(self):
        """Get a database connection (thread-safe)"""
        # Create a new connection if one doesn't exist for this thread
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(self.db_path, timeout=30.0)
            # Enable foreign keys
            self.local.connection.execute("PRAGMA foreign_keys = ON")
        
        return self.local.connection
    
    def close_connections(self):
        """Close all database connections"""
        if hasattr(self.local, 'connection'):
            self.local.connection.close()
            delattr(self.local, 'connection')
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            
            return True
        
        except Exception as e:
            self.logger.error(f"Database query error: {str(e)}")
            self.logger.error(f"Query: {query}")
            if params:
                self.logger.error(f"Params: {params}")
            raise
    
    def get_setting(self, key, default=None):
        """Get a setting from the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT value, type FROM settings WHERE key = ?", (key,))
            result = cursor.fetchone()
            
            if not result:
                return default
            
            value, type_str = result
            
            # Convert based on type
            if type_str == "int":
                return int(value)
            elif type_str == "float":
                return float(value)
            elif type_str == "bool":
                return value.lower() in ("true", "1", "yes")
            else:
                return value
        
        except Exception as e:
            self.logger.error(f"Failed to get setting {key}: {str(e)}")
            return default
    
    def set_setting(self, key, value):
        """Set a setting in the database"""
        try:
            # Determine the type
            value_type = type(value).__name__
            
            # Convert to string for storage
            if value_type == "bool":
                value_str = "true" if value else "false"
            else:
                value_str = str(value)
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Use UPSERT
            cursor.execute(
                """
                INSERT INTO settings (key, value, type, updated_at)
                VALUES (?, ?, ?, datetime('now'))
                ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                type = excluded.type,
                updated_at = excluded.updated_at
                """,
                (key, value_str, value_type)
            )
            
            conn.commit()
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to set setting {key}: {str(e)}")
            return False
    
    def log_conversation(self, user_input, response, emotion="neutral", intent="unknown"):
        """Log a conversation to the database"""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO conversations 
                (user_input, response, timestamp, emotion, intent)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_input, response, timestamp, emotion, intent)
            )
            
            conn.commit()
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to log conversation: {str(e)}")
            return False
    
    def get_recent_conversations(self, limit=10):
        """Get recent conversations from the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT user_input, response, timestamp, emotion, intent
                FROM conversations
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,)
            )
            
            return cursor.fetchall()
        
        except Exception as e:
            self.logger.error(f"Failed to get recent conversations: {str(e)}")
            return []
    
    def get_db_size(self):
        """Get the database file size in MB"""
        try:
            size_bytes = os.path.getsize(self.db_path)
            size_mb = size_bytes / (1024 * 1024)
            return round(size_mb, 2)
        except Exception as e:
            self.logger.error(f"Failed to get DB size: {str(e)}")
            return 0
