"""
Add last_hit_at column to response_cache table

This script creates a migration to add the last_hit_at column to the response_cache table
to track when each cache entry was last accessed.
"""
import os
import sys
import logging
from sqlalchemy import create_engine, Column, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migration():
    """Run the migration to add the last_hit_at column."""
    logger.info("Starting migration to add last_hit_at column to response_cache table")
    
    try:
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return False
        
        logger.info(f"Using database URL: {database_url.split('@')[0].split(':')[0]}:***@{database_url.split('@')[1]}")
        
        # Create engine and session
        engine = create_engine(
            database_url,
            connect_args={
                'connect_timeout': 30  # 30 seconds timeout
            },
            pool_pre_ping=True,  # Test connection before using it
            pool_recycle=300     # Recycle connections after 5 minutes
        )
        
        # Check if the column already exists
        logger.info("Checking if last_hit_at column already exists...")
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'response_cache' AND column_name = 'last_hit_at'
            """))
            if result.rowcount > 0:
                logger.info("last_hit_at column already exists, migration not needed")
                return True
        
        # Add the column
        logger.info("Adding last_hit_at column to response_cache table...")
        try:
            with engine.connect() as connection:
                sql = """
                    ALTER TABLE response_cache
                    ADD COLUMN last_hit_at TIMESTAMP
                """
                logger.info(f"Executing SQL: {sql}")
                connection.execute(text(sql))
                
                # Verify column was added
                verify_sql = """
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'response_cache'
                """
                logger.info(f"Verifying with SQL: {verify_sql}")
                result = connection.execute(text(verify_sql))
                columns = [row[0] for row in result]
                logger.info(f"Columns after migration: {columns}")
                
                if 'last_hit_at' in columns:
                    logger.info("last_hit_at column successfully added")
                else:
                    logger.warning("last_hit_at column not found after migration")
        except Exception as e:
            logger.error(f"Error during SQL execution: {str(e)}")
            return False
            
        logger.info("Migration completed successfully")
        return True
            
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)