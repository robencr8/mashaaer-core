import os
import logging
import sqlite3
import threading
import time
import psycopg2
from psycopg2 import pool

class DatabaseManager:
    """Manages database connections and operations with support for SQLite and PostgreSQL"""
    
    def __init__(self, config=None, db_path="robin_memory.db"):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.db_path = db_path
        self.use_postgres = False
        
        if config and config.USE_POSTGRES and config.DATABASE_URL:
            self.use_postgres = True
            self.logger.info("Using PostgreSQL database")
            # Initialize PostgreSQL connection pool
            self.pg_pool = pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=config.DATABASE_URL
            )
        else:
            self.logger.info(f"Using SQLite database at {db_path}")
            # Make sure the database directory exists for SQLite
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        
        # Connection pool (thread-local)
        self.local = threading.local()
    
    def initialize_db(self):
        """Initialize the database and create tables"""
        self.logger.info(f"Initializing database at {self.db_path}")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Create core tables based on database type
            if self.use_postgres:
                # 1. Settings table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        type TEXT,
                        updated_at TIMESTAMP
                    )
                ''')
                
                # 2. Conversations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id SERIAL PRIMARY KEY,
                        user_input TEXT,
                        response TEXT,
                        timestamp TIMESTAMP,
                        emotion TEXT,
                        intent TEXT
                    )
                ''')
                
                # 3. User profiles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_profiles (
                        id SERIAL PRIMARY KEY,
                        name TEXT,
                        face_id TEXT,
                        preferences TEXT,
                        last_interaction TIMESTAMP
                    )
                ''')
                
                # 4. System logs table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_logs (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP,
                        level TEXT,
                        module TEXT,
                        message TEXT
                    )
                ''')
                
                # 5. Emotion data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS emotion_data (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP,
                        emotion TEXT,
                        source TEXT,
                        intensity REAL,
                        text TEXT
                    )
                ''')
                
                # 6. Face profiles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS face_profiles (
                        id SERIAL PRIMARY KEY,
                        name TEXT,
                        encoding BYTEA,
                        last_seen TIMESTAMP,
                        metadata JSONB
                    )
                ''')
                
            else:
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
                
                # 5. Emotion data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS emotion_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        emotion TEXT,
                        source TEXT,
                        intensity REAL,
                        text TEXT
                    )
                ''')
                
                # 6. Face profiles table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS face_profiles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        encoding BLOB,
                        last_seen TEXT,
                        metadata TEXT
                    )
                ''')
            
            conn.commit()
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def get_connection(self):
        """Get a database connection (thread-safe)"""
        # Create a new connection if one doesn't exist for this thread
        if not hasattr(self.local, 'connection'):
            if self.use_postgres:
                self.local.connection = self.pg_pool.getconn()
                # Create cursor with dict factory
                self.local.connection.autocommit = False
            else:
                self.local.connection = sqlite3.connect(self.db_path, timeout=30.0)
                # Enable foreign keys in SQLite
                self.local.connection.execute("PRAGMA foreign_keys = ON")
        
        return self.local.connection
    
    def close_connections(self):
        """Close all database connections"""
        if hasattr(self.local, 'connection'):
            if self.use_postgres:
                # Return connection to the pool
                self.pg_pool.putconn(self.local.connection)
            else:
                self.local.connection.close()
            delattr(self.local, 'connection')
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            conn = self.get_connection()
            
            # Create cursor with the appropriate type
            if self.use_postgres:
                cursor = conn.cursor()
                # Convert SQLite placeholders (?) to PostgreSQL placeholders ($1, $2, etc.)
                if params and "?" in query:
                    param_count = query.count("?")
                    for i in range(1, param_count + 1):
                        query = query.replace("?", f"%s", 1)
            else:
                cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            
            # Check if it's a SELECT query
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                # Convert dict rows to tuples for SQLite compatibility if needed
                if self.use_postgres:
                    # This depends on your needs - sometimes you want dicts, sometimes tuples
                    pass
                return result
            
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
            
            if self.use_postgres:
                cursor.execute("SELECT value, type FROM settings WHERE key = %s", (key,))
            else:
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
            
            # Use UPSERT - syntax differs between SQLite and PostgreSQL
            if self.use_postgres:
                cursor.execute(
                    """
                    INSERT INTO settings (key, value, type, updated_at)
                    VALUES (%s, %s, %s, NOW())
                    ON CONFLICT(key) DO UPDATE SET
                    value = EXCLUDED.value,
                    type = EXCLUDED.type,
                    updated_at = NOW()
                    """,
                    (key, value_str, value_type)
                )
            else:
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
            
            if self.use_postgres:
                cursor.execute(
                    """
                    INSERT INTO conversations 
                    (user_input, response, timestamp, emotion, intent)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (user_input, response, timestamp, emotion, intent)
                )
            else:
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
            
            if self.use_postgres:
                cursor.execute(
                    """
                    SELECT user_input, response, timestamp, emotion, intent
                    FROM conversations
                    ORDER BY timestamp DESC
                    LIMIT %s
                    """,
                    (limit,)
                )
            else:
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
            if self.use_postgres:
                # For PostgreSQL, retrieve size from pg_database
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT pg_database_size(current_database()) / (1024*1024) as size_mb
                """)
                result = cursor.fetchone()
                return round(float(result[0]), 2) if result else 0
            else:
                # For SQLite, get the file size
                size_bytes = os.path.getsize(self.db_path)
                size_mb = size_bytes / (1024 * 1024)
                return round(size_mb, 2)
        except Exception as e:
            self.logger.error(f"Failed to get DB size: {str(e)}")
            return 0
