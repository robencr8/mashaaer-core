import os
import logging
import threading
import time
import sqlite3
import psycopg2
from psycopg2 import pool
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from database.models import Base, Setting, EmotionData, Face, RecognitionHistory, VoiceLog

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
        self.engine = create_engine(f'sqlite:///{self.db_path}')  # Update for ORM
        self.Session = sessionmaker(bind=self.engine)

    def initialize_db(self):
        """Initialize the ORM database and create tables"""
        try:
            Base.metadata.create_all(self.engine)
            self.logger.info("✅ ORM Database schema created (or already exists).")
        except Exception as e:
            self.logger.error(f"❌ Error creating ORM tables: {str(e)}")

    def get_connection(self):
        """Get a database connection (thread-safe)"""
        # Create a new connection if one doesn't exist for this thread
        if not hasattr(self.local, 'connection'):
            if self.use_postgres:
                self.local.connection = self.pg_pool.getconn()
                # Create cursor with dict factory
                self.local.connection.autocommit = True  # Use autocommit to avoid transaction issues
            else:
                self.local.connection = sqlite3.connect(self.db_path, timeout=30.0)
                # Enable foreign keys in SQLite
                self.local.connection.execute("PRAGMA foreign_keys = ON")
        elif self.use_postgres:
            # If connection exists, check if it's in a failed transaction state
            # and create a new one if needed
            try:
                # Test connection with a simple query
                cursor = self.local.connection.cursor()
                cursor.execute("SELECT 1")
                cursor.close()
            except psycopg2.Error:
                # Connection is in a bad state, release it and get a new one
                self.logger.warning("Replacing failed PostgreSQL connection")
                try:
                    self.pg_pool.putconn(self.local.connection)
                except:
                    pass  # Connection might be closed already
                self.local.connection = self.pg_pool.getconn()
                self.local.connection.autocommit = True

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

    def get_emotions_by_session(self, session_id):
        """Get emotions by session ID using ORM"""
        try:
            with self.Session() as session:
                return session.query(EmotionData).filter_by(session_id=session_id).order_by(EmotionData.timestamp).all()
        except Exception as e:
            self.logger.error(f"Query error: {str(e)}")
            return []

    def get_or_create_setting(self, key, default=None):
        with self.Session() as session:
            setting = session.query(Setting).filter_by(key=key).first()
            if setting:
                return setting.value
            else:
                new_setting = Setting(key=key, value=default)
                session.add(new_setting)
                session.commit()
                return default
                
    def log_voice_recognition(self, session_id=None, language=None, error_type=None, 
                             raw_input=None, recognized_text=None, success=False, 
                             device_info=None, context=None):
        """
        Log voice recognition attempt to the database with detailed error tracking
        
        Args:
            session_id: Current user session ID
            language: Language code (e.g., 'en', 'ar')
            error_type: Type of error if recognition failed (e.g., 'no_audio', 'timeout', 'recognition_failed')
            raw_input: Raw audio data or metadata
            recognized_text: Text recognized (if successful)
            success: Whether recognition was successful
            device_info: Information about the user's device
            context: Context of the voice recognition (e.g., 'onboarding', 'main_interface')
            
        Returns:
            bool: Success status of the logging operation
        """
        try:
            # Generate timestamp in ISO format
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Use ORM approach
            with self.Session() as session:
                voice_log = VoiceLog(
                    timestamp=timestamp,
                    session_id=session_id or "unknown",
                    language=language or "unknown",
                    error_type=error_type,
                    raw_input=raw_input,
                    recognized_text=recognized_text,
                    success=success,
                    device_info=device_info,
                    context=context
                )
                session.add(voice_log)
                session.commit()
                
            self.logger.info(f"Voice recognition logged: language={language}, success={success}, error_type={error_type}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log voice recognition: {str(e)}")
            return False
            
    def get_voice_logs(self, limit=50, success_only=False, error_only=False, language=None):
        """
        Get voice recognition logs from the database with filtering options
        
        Args:
            limit: Maximum number of logs to retrieve
            success_only: If True, only successful recognitions are returned
            error_only: If True, only failed recognitions are returned
            language: Filter by specific language
            
        Returns:
            list: List of voice log entries
        """
        try:
            with self.Session() as session:
                query = session.query(VoiceLog)
                
                # Apply filters
                if success_only:
                    query = query.filter(VoiceLog.success == True)
                elif error_only:
                    query = query.filter(VoiceLog.success == False)
                    
                if language:
                    query = query.filter(VoiceLog.language == language)
                    
                # Get results
                return query.order_by(VoiceLog.timestamp.desc()).limit(limit).all()
                
        except Exception as e:
            self.logger.error(f"Failed to get voice logs: {str(e)}")
            return []