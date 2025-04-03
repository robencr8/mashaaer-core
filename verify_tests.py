#!/usr/bin/env python3
"""
Test Verification Script for Mashaaer Feelings

This script verifies that the database connection is working correctly and
that tests can be run successfully. It's designed to be run in environments
where PostgreSQL is available and properly configured.

Usage:
    python verify_tests.py

Environment variables required:
    - DATABASE_URL: PostgreSQL connection string
"""

import os
import sys
import time
import logging
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_connection():
    """Check if the database connection is working correctly and verify cache table."""
    logger.info("Checking database connection...")
    
    try:
        # Import necessary modules
        from sqlalchemy import create_engine, inspect
        from sqlalchemy.exc import SQLAlchemyError
        
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return False
        
        # Create engine and try to connect
        engine = create_engine(database_url)
        connection = engine.connect()
        
        # Check if the cache table exists
        inspector = inspect(engine)
        cache_table_exists = 'response_cache' in inspector.get_table_names()
        
        if not cache_table_exists:
            logger.warning("⚠️ Cache table 'response_cache' does not exist in the database")
            logger.info("Attempting to create database tables...")
            
            # Try to create tables by importing the models and creating them
            try:
                from database.models import Base
                Base.metadata.create_all(engine)
                logger.info("✅ Database tables created successfully")
            except Exception as e:
                logger.error(f"❌ Failed to create database tables: {str(e)}")
                connection.close()
                return False
        else:
            logger.info("✅ Cache table 'response_cache' exists in the database")
            
            # Check the structure of the cache table
            columns = {c['name'] for c in inspector.get_columns('response_cache')}
            required_columns = {'id', 'key', 'value', 'created_at', 'expires_at', 'hit_count'}
            
            if not required_columns.issubset(columns):
                missing = required_columns - columns
                logger.warning(f"⚠️ Cache table is missing columns: {missing}")
            else:
                logger.info("✅ Cache table structure is correct")
        
        connection.close()
        logger.info("✅ Database connection successful")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Could not import required modules: {str(e)}")
        return False
    except SQLAlchemyError as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during database check: {str(e)}")
        return False

def verify_single_test(test_file):
    """Run a single test file and verify it passes."""
    logger.info(f"Verifying test: {test_file}")
    
    try:
        # Run pytest with verbose flag
        result = subprocess.run(
            ["python", "-m", "pytest", test_file, "-v"],
            capture_output=True,
            text=True,
            timeout=30  # Set a timeout of 30 seconds
        )
        
        # Check if test succeeded
        success = result.returncode == 0
        
        if success:
            logger.info(f"✅ Test {test_file} PASSED")
        else:
            logger.error(f"❌ Test {test_file} FAILED (return code {result.returncode})")
            logger.error(f"Output: {result.stdout}")
            logger.error(f"Errors: {result.stderr}")
            
        return success
        
    except subprocess.TimeoutExpired:
        logger.error(f"⏱️ Test {test_file} TIMED OUT (exceeded 30 seconds)")
        return False
    except Exception as e:
        logger.error(f"💥 Error running test {test_file}: {str(e)}")
        return False

def verify_direct_cache_functionality():
    """Directly verify cache functionality using a real database connection."""
    logger.info("=== Starting Direct Cache Functionality Verification ===")
    
    try:
        # Import required modules
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from database.models import Cache
        from database.db_manager import DatabaseManager
        import json
        import hashlib
        
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return False
        
        # Create engine and session
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        
        # Create a DatabaseManager instance
        db_manager = DatabaseManager(config={'SQLALCHEMY_DATABASE_URI': database_url})
        
        # Step 1: Clear any existing test cache entries
        logger.info("Clearing test cache entries...")
        with Session() as session:
            test_entries = session.query(Cache).filter(
                Cache.key.like('test_cache_verify_%')
            ).all()
            
            if test_entries:
                for entry in test_entries:
                    session.delete(entry)
                session.commit()
                logger.info(f"Cleared {len(test_entries)} existing test cache entries")
            else:
                logger.info("No existing test cache entries to clear")
        
        # Step 2: Generate a test cache key
        test_text = "TestVerifyCacheDirectly"
        test_language = "en"
        cache_key = f"test_cache_verify_{hashlib.md5((test_text + test_language).encode()).hexdigest()}"
        
        # Step 3: Store a test value in cache
        logger.info(f"Storing test value in cache with key: {cache_key}")
        test_data = {
            "primary_emotion": "happy",
            "confidence": 0.9,
            "emotions": {"happy": 0.9, "neutral": 0.1},
            "language": test_language,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        store_success = db_manager.store_cached_response(
            cache_key, 
            json.dumps(test_data), 
            expiry_seconds=300  # 5 minutes
        )
        
        if not store_success:
            logger.error("❌ Failed to store test value in cache")
            return False
        
        logger.info("✅ Successfully stored test value in cache")
        
        # Step 4: Retrieve the cached value
        logger.info(f"Retrieving cached value for key: {cache_key}")
        cached_value, metadata = db_manager.get_cached_response(cache_key)
        
        if not cached_value:
            logger.error("❌ Failed to retrieve cached value")
            return False
        
        logger.info("✅ Successfully retrieved cached value")
        
        # Step 5: Verify the retrieved value
        logger.info("Verifying cached value content...")
        try:
            cached_data = json.loads(cached_value) if isinstance(cached_value, str) else cached_value
            
            # Check that the cached data matches what we stored
            assert cached_data.get("primary_emotion") == test_data["primary_emotion"], \
                f"Cached primary_emotion {cached_data.get('primary_emotion')} doesn't match original {test_data['primary_emotion']}"
            
            assert cached_data.get("confidence") == test_data["confidence"], \
                f"Cached confidence {cached_data.get('confidence')} doesn't match original {test_data['confidence']}"
            
            logger.info("✅ Cached value content is correct")
        except Exception as e:
            logger.error(f"❌ Cache verification failed: {str(e)}")
            return False
        
        # Step 6: Verify hit count incrementing
        logger.info("Verifying hit count incrementing...")
        
        # Initial hit count should be 1 after the first get
        initial_hit_count = metadata.get("hit_count", 0)
        logger.info(f"Initial hit count: {initial_hit_count}")
        
        # Get the cached value again to increment hit count
        second_cached_value, second_metadata = db_manager.get_cached_response(cache_key)
        second_hit_count = second_metadata.get("hit_count", 0)
        logger.info(f"Second hit count: {second_hit_count}")
        
        # The hit count should have incremented
        if second_hit_count != initial_hit_count + 1:
            logger.error(f"❌ Hit count didn't increment correctly. Expected {initial_hit_count + 1}, got {second_hit_count}")
            return False
            
        logger.info("✅ Hit count incremented correctly")
        
        # Step 7: Verify direct database hit count
        logger.info("Verifying database hit count...")
        with Session() as session:
            db_entry = session.query(Cache).filter(Cache.key == cache_key).first()
            
            if not db_entry:
                logger.error("❌ Cache entry not found in database")
                return False
                
            logger.info(f"Database hit count: {db_entry.hit_count}")
            
            # The database hit count should match the metadata hit count
            if db_entry.hit_count != second_hit_count:
                logger.error(f"❌ Database hit count {db_entry.hit_count} doesn't match metadata hit count {second_hit_count}")
                return False
                
            logger.info("✅ Database hit count matches metadata hit count")
        
        logger.info("=== Direct Cache Functionality Verification PASSED ===")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Could not import required modules: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during direct cache verification: {str(e)}")
        logger.error("Stack trace:", exc_info=True)
        return False

def run_verification():
    """Run the verification process for all tests."""
    logger.info("=== Starting Test Verification ===")
    start_time = time.time()
    
    # Step 1: Check database connection
    db_connection_ok = check_database_connection()
    if not db_connection_ok:
        logger.error("Database connection failed. Verification cannot continue.")
        return False
    
    # Step 2: Verify direct cache functionality (if database is available)
    cache_functionality_ok = verify_direct_cache_functionality()
    if not cache_functionality_ok:
        logger.warning("⚠️ Direct cache functionality verification failed.")
        logger.warning("Some database-dependent tests may fail.")
    else:
        logger.info("✅ Direct cache functionality verified successfully")
    
    # Step 3: Verify each test file
    test_files = [
        "tests/test_cache_integration.py",  # Integration test with mocked DB
        "tests/test_db_caching.py",         # Direct DB cache test
        "tests/test_minimal_cache.py",      # Minimal cache test
        # "tests/test_cache_api.py",        # Complete API integration test (may be more complex)
    ]
    
    all_tests_passed = True
    for test_file in test_files:
        test_passed = verify_single_test(test_file)
        if not test_passed:
            all_tests_passed = False
    
    # Step 4: Report results
    execution_time = round(time.time() - start_time, 2)
    logger.info("=== Test Verification Complete ===")
    logger.info(f"Execution Time: {execution_time} seconds")
    logger.info(f"Overall Result: {'SUCCESS' if all_tests_passed else 'FAILURE'}")
    
    return all_tests_passed

if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)