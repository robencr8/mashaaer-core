import logging
import os
import psycopg2
from datetime import datetime

def create_tables():
    """Create all required tables in the PostgreSQL database"""
    logger = logging.getLogger(__name__)
    logger.info("Creating database tables...")
    
    # Get database connection info from environment variables
    db_url = os.environ.get('DATABASE_URL')
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Create emotions table
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
        
        # Create emotion_data table (for visualizations)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emotion_data (
                id SERIAL PRIMARY KEY,
                timestamp TEXT NOT NULL,
                emotion TEXT NOT NULL,
                source TEXT DEFAULT 'text',
                intensity REAL DEFAULT 0.5,
                text TEXT,
                session_id TEXT
            )
        ''')
        
        # Create faces table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faces (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                encoding BYTEA,
                last_seen TEXT,
                metadata TEXT
            )
        ''')
        
        # Create recognition_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recognition_history (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                emotion TEXT DEFAULT 'neutral',
                session_id TEXT
            )
        ''')
        
        # Create user_preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id SERIAL PRIMARY KEY, 
                key TEXT UNIQUE NOT NULL,
                value TEXT
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start_time TEXT NOT NULL,
                end_time TEXT,
                user_name TEXT,
                device TEXT,
                language TEXT DEFAULT 'en'
            )
        ''')
        
        # Create user_profile table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id SERIAL PRIMARY KEY,
                full_name TEXT,
                preferred_name TEXT,
                age INTEGER,
                language TEXT DEFAULT 'en',
                voice_style TEXT,
                theme TEXT DEFAULT 'dark',
                preferred_tone TEXT,
                mood_type TEXT,
                dark_mode BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Create learning_metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_metrics (
                id SERIAL PRIMARY KEY,
                last_cycle TEXT,
                emotion_accuracy REAL DEFAULT 0.0,
                intent_accuracy REAL DEFAULT 0.0,
                face_recognition_rate REAL DEFAULT 0.0,
                voice_recognition_rate REAL DEFAULT 0.0,
                total_learning_cycles INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Database tables created successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    success = create_tables()
    print(f"Database setup {'successful' if success else 'failed'}")