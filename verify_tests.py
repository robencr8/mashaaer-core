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
import multiprocessing
import signal
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_database_connection():
    """Check if the database connection is working correctly and verify cache table."""
    logger.info("Checking database connection...")
    
    import traceback
    
    try:
        # Import necessary modules
        from sqlalchemy import create_engine, inspect
        from sqlalchemy.exc import SQLAlchemyError
        
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return False
        
        logger.info(f"Using database URL: {database_url.split('@')[0].split(':')[0]}:***@{database_url.split('@')[1]}")
        
        # Create engine and try to connect with a timeout
        engine = create_engine(
            database_url, 
            connect_args={
                'connect_timeout': 10  # 10 seconds timeout
            },
            pool_pre_ping=True,  # Test connection before using it
            pool_recycle=300     # Recycle connections after 5 minutes
        )
        
        logger.info("Attempting to connect to database...")
        connection = engine.connect()
        logger.info("Database connection established")
        
        # Check if the cache table exists
        logger.info("Inspecting database schema...")
        inspector = inspect(engine)
        available_tables = inspector.get_table_names()
        logger.info(f"Available tables: {available_tables}")
        
        cache_table_exists = 'response_cache' in available_tables
        
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
                logger.error(traceback.format_exc())
                if connection:
                    connection.close()
                return False
        else:
            logger.info("✅ Cache table 'response_cache' exists in the database")
            
            # Check the structure of the cache table
            columns = {c['name'] for c in inspector.get_columns('response_cache')}
            logger.info(f"Cache table columns: {columns}")
            
            required_columns = {'id', 'key', 'value', 'created_at', 'expires_at', 'hit_count'}
            
            if not required_columns.issubset(columns):
                missing = required_columns - columns
                logger.warning(f"⚠️ Cache table is missing columns: {missing}")
            else:
                logger.info("✅ Cache table structure is correct")
        
        if connection:
            connection.close()
        logger.info("✅ Database connection successful")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Could not import required modules: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    except SQLAlchemyError as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during database check: {str(e)}")
        logger.error(traceback.format_exc())
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

def verify_cache_entry(db_session, cache_key):
    """
    Verify if a specific cache entry exists and return its details.
    
    Args:
        db_session: SQLAlchemy database session
        cache_key: The cache key to look for
        
    Returns:
        Tuple of (entry_exists, value, metadata) where:
        - entry_exists: Boolean indicating if the entry exists
        - value: The cached value (deserialized if JSON) or None
        - metadata: Dictionary of metadata including hit_count, created_at, expires_at
    """
    try:
        from database.models import Cache
        import json
        
        # Debug info
        logger.info(f"Looking for cache entry with key: {cache_key}")
        
        # Get all keys from the cache table to help with debugging
        all_keys = [entry.key for entry in db_session.query(Cache.key).all()]
        logger.info(f"Available cache keys: {all_keys}")
        
        # Query the database for the cache entry
        logger.info("Executing database query...")
        cache_entry = db_session.query(Cache).filter(Cache.key == cache_key).first()
        
        if not cache_entry:
            logger.error(f"No cache entry found for key: {cache_key}")
            return False, None, {}
            
        # Attempt to deserialize the value if it's JSON
        value = cache_entry.value
        try:
            deserialized_value = json.loads(value)
            value = deserialized_value  # Use the deserialized value if successful
        except (json.JSONDecodeError, TypeError):
            # Not JSON or invalid JSON, use the raw value
            logger.debug(f"Cache value for key {cache_key} is not valid JSON, using raw value")
        
        # Extract metadata
        metadata = {
            'hit_count': cache_entry.hit_count,
            'created_at': cache_entry.created_at.isoformat() if cache_entry.created_at else None,
            'expires_at': cache_entry.expires_at.isoformat() if cache_entry.expires_at else None,
            'last_hit_at': cache_entry.last_hit_at.isoformat() if cache_entry.last_hit_at else None
        }
        
        logger.debug(f"Cache hit count: {metadata['hit_count']}")
        logger.debug(f"Last hit at: {metadata['last_hit_at']}")
        
        logger.info(f"Found cache entry for key: {cache_key}")
        logger.info(f"Hit count: {metadata['hit_count']}")
        logger.info(f"Created at: {metadata['created_at']}")
        logger.info(f"Expires at: {metadata['expires_at']}")
        
        return True, value, metadata
        
    except Exception as e:
        logger.error(f"Error verifying cache entry for key '{cache_key}': {e}")
        return False, None, {}

def verify_direct_cache_functionality():
    """Directly verify cache functionality using a real database connection."""
    logger.info("=== Starting Direct Cache Functionality Verification ===")
    
    import traceback
    
    try:
        # Import required modules
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.exc import SQLAlchemyError, OperationalError, TimeoutError
        from database.models import Cache
        from database.db_manager import DatabaseManager
        import json
        import hashlib
        
        # Get database URL from environment
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            logger.error("DATABASE_URL environment variable not set")
            return False
        
        logger.info(f"Using database URL: {database_url.split('@')[0].split(':')[0]}:***@{database_url.split('@')[1]}")
        
        # Create engine and session with timeout
        engine = create_engine(
            database_url,
            connect_args={
                'connect_timeout': 10  # 10 seconds timeout
            },
            pool_pre_ping=True,  # Test connection before using it
            pool_recycle=300     # Recycle connections after 5 minutes
        )
        Session = sessionmaker(bind=engine)
        
        logger.info("Creating DatabaseManager instance...")
        # Create a Config-like object for DatabaseManager
        class TestConfig:
            def __init__(self, database_url):
                self.USE_POSTGRES = True
                self.DATABASE_URL = database_url
                self.DB_PATH = None
        
        # Create a DatabaseManager instance with the proper config object
        test_config = TestConfig(database_url)
        db_manager = DatabaseManager(config=test_config)
        
        # Step 1: Clear any existing test cache entries
        logger.info("Clearing test cache entries...")
        try:
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
        except SQLAlchemyError as e:
            logger.warning(f"⚠️ Could not clear existing test cache entries: {str(e)}")
            # Continue with the test even if clearing fails
        
        # Step 2: Generate a test cache key
        test_text = "TestVerifyCacheDirectly"
        test_language = "en"
        cache_key = f"test_cache_verify_{hashlib.md5((test_text + test_language).encode()).hexdigest()}"
        logger.info(f"Generated test cache key: {cache_key}")
        
        # Step 3: Store a test value in cache
        logger.info(f"Storing test value in cache with key: {cache_key}")
        test_data = {
            "primary_emotion": "happy",
            "confidence": 0.9,
            "emotions": {"happy": 0.9, "neutral": 0.1},
            "language": test_language,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        try:
            store_success = db_manager.store_cached_response(
                cache_key, 
                json.dumps(test_data), 
                expiry_seconds=300  # 5 minutes
            )
            
            if not store_success:
                logger.error("❌ Failed to store test value in cache")
                return False
            
            logger.info("✅ Successfully stored test value in cache")
        except Exception as e:
            logger.error(f"❌ Error while storing cache entry: {str(e)}")
            logger.error(traceback.format_exc())
            return False
        
        # Step 4: Retrieve the cached value
        logger.info(f"Retrieving cached value for key: {cache_key}")
        try:
            cached_value, metadata = db_manager.get_cached_response(cache_key)
            
            if not cached_value:
                logger.error("❌ Failed to retrieve cached value")
                return False
            
            logger.info("✅ Successfully retrieved cached value")
            logger.debug(f"Retrieved value: {cached_value}")
            logger.debug(f"Retrieved metadata: {metadata}")
        except Exception as e:
            logger.error(f"❌ Error while retrieving cache entry: {str(e)}")
            logger.error(traceback.format_exc())
            return False
        
        # Step 5: Verify the retrieved value using the verify_cache_entry helper
        logger.info("Verifying cached value content using verify_cache_entry...")
        try:
            with Session() as session:
                entry_exists, entry_value, entry_metadata = verify_cache_entry(session, cache_key)
                
                if not entry_exists:
                    logger.error("❌ Cache entry not found in direct verification")
                    return False
                
                # Check that the cached data matches what we stored
                try:
                    assert entry_value.get("primary_emotion") == test_data["primary_emotion"], \
                        f"Cached primary_emotion {entry_value.get('primary_emotion')} doesn't match original {test_data['primary_emotion']}"
                    
                    assert entry_value.get("confidence") == test_data["confidence"], \
                        f"Cached confidence {entry_value.get('confidence')} doesn't match original {test_data['confidence']}"
                    
                    logger.info("✅ Cached value content is correct")
                except AssertionError as e:
                    logger.error(f"❌ Cache verification failed: {str(e)}")
                    logger.error(f"Expected: {test_data}")
                    logger.error(f"Got: {entry_value}")
                    return False
        except SQLAlchemyError as e:
            logger.error(f"❌ Database error during cache verification: {str(e)}")
            logger.error(traceback.format_exc())
            return False
        
        # Step 6: Verify hit count incrementing
        logger.info("Verifying hit count incrementing...")
        
        # Initial hit count from the entry_metadata
        initial_hit_count = entry_metadata.get("hit_count", 0)
        logger.info(f"Initial hit count: {initial_hit_count}")
        
        try:
            # Get the cached value again to increment hit count
            second_cached_value, second_metadata = db_manager.get_cached_response(cache_key)
            
            if not second_cached_value:
                logger.error("❌ Failed to retrieve cached value during hit count verification")
                return False
                
            second_hit_count = second_metadata.get("hit_count", 0)
            logger.info(f"Second hit count: {second_hit_count}")
            
            # The hit count should have incremented
            if second_hit_count != initial_hit_count + 1:
                logger.error(f"❌ Hit count didn't increment correctly. Expected {initial_hit_count + 1}, got {second_hit_count}")
                return False
                
            logger.info("✅ Hit count incremented correctly")
        except Exception as e:
            logger.error(f"❌ Error during hit count verification: {str(e)}")
            logger.error(traceback.format_exc())
            return False
        
        # Step 7: Verify updated database hit count using verify_cache_entry
        logger.info("Verifying database hit count...")
        try:
            with Session() as session:
                entry_exists, _, updated_metadata = verify_cache_entry(session, cache_key)
                
                if not entry_exists:
                    logger.error("❌ Cache entry not found in database during hit count verification")
                    return False
                    
                db_hit_count = updated_metadata.get("hit_count", 0)
                logger.info(f"Database hit count: {db_hit_count}")
                
                # The database hit count should match the metadata hit count
                if db_hit_count != second_hit_count:
                    logger.error(f"❌ Database hit count {db_hit_count} doesn't match metadata hit count {second_hit_count}")
                    return False
                    
                logger.info("✅ Database hit count matches metadata hit count")
        except SQLAlchemyError as e:
            logger.error(f"❌ Database error during hit count verification: {str(e)}")
            logger.error(traceback.format_exc())
            return False
        
        logger.info("=== Direct Cache Functionality Verification PASSED ===")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Could not import required modules: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    except OperationalError as e:
        logger.error(f"❌ Database operational error: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    except TimeoutError as e:
        logger.error(f"❌ Database connection timeout: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    except SQLAlchemyError as e:
        logger.error(f"❌ SQLAlchemy error: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during direct cache verification: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def run_verification():
    """Run the verification process for all tests."""
    logger.info("=== Starting Test Verification ===")
    start_time = time.time()
    
    try:
        # Step 1: Check database connection with timeout
        db_connection_check_timeout = 20  # seconds
        logger.info(f"Checking database connection (timeout: {db_connection_check_timeout}s)...")
        
        # Use a separate process for the database check to enforce timeout
        db_check_process = multiprocessing.Process(target=check_database_connection)
        db_check_process.start()
        db_check_process.join(timeout=db_connection_check_timeout)
        
        if db_check_process.is_alive():
            # Process is still running after timeout
            db_check_process.terminate()
            db_check_process.join()
            logger.error(f"❌ Database connection check timed out after {db_connection_check_timeout} seconds")
            logger.error("Check your database connection parameters and network connectivity")
            return False
        
        # Assume the process completed but we need to check if it was successful
        # Since we can't get a return value directly from the process, we'll check again
        db_connection_ok = check_database_connection()
        if not db_connection_ok:
            logger.error("❌ Database connection failed. Verification cannot continue.")
            logger.error("Check your DATABASE_URL environment variable and database server status")
            return False
        
        # Step 2: Verify direct cache functionality (if database is available)
        cache_functionality_timeout = 30  # seconds
        logger.info(f"Verifying cache functionality (timeout: {cache_functionality_timeout}s)...")
        
        # Use a separate process for the cache functionality check
        cache_check_process = multiprocessing.Process(target=verify_direct_cache_functionality)
        cache_check_process.start()
        cache_check_process.join(timeout=cache_functionality_timeout)
        
        if cache_check_process.is_alive():
            # Process is still running after timeout
            cache_check_process.terminate()
            cache_check_process.join()
            logger.error(f"❌ Cache functionality verification timed out after {cache_functionality_timeout} seconds")
            logger.warning("⚠️ Some database-dependent tests may fail")
            # Continue with tests despite timeout
        else:
            # Process completed, but check result
            cache_functionality_ok = verify_direct_cache_functionality()
            if not cache_functionality_ok:
                logger.warning("⚠️ Direct cache functionality verification failed.")
                logger.warning("⚠️ Some database-dependent tests may fail.")
            else:
                logger.info("✅ Direct cache functionality verified successfully")
        
        # Step 3: Verify each test file
        test_files = [
            "tests/test_cache_integration.py",  # Integration test with mocked DB
            "tests/test_db_caching.py",         # Direct DB cache test
            "tests/test_minimal_cache.py",      # Minimal cache test
            # "tests/test_cache_api.py",        # Complete API integration test (may be more complex)
        ]
        
        test_results = {}
        all_tests_passed = True
        
        for test_file in test_files:
            logger.info(f"Running test file: {test_file}")
            test_passed = verify_single_test(test_file)
            test_results[test_file] = "✅ PASSED" if test_passed else "❌ FAILED"
            
            if not test_passed:
                all_tests_passed = False
        
        # Step 4: Report results
        execution_time = round(time.time() - start_time, 2)
        logger.info("=== Test Verification Results ===")
        
        # Print individual test results
        for test_file, result in test_results.items():
            logger.info(f"{result}: {test_file}")
        
        logger.info("=== Test Verification Complete ===")
        logger.info(f"Execution Time: {execution_time} seconds")
        logger.info(f"Overall Result: {'✅ SUCCESS' if all_tests_passed else '❌ FAILURE'}")
        
        return all_tests_passed
        
    except Exception as e:
        import traceback
        logger.error(f"❌ Unexpected error during verification: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    try:
        success = run_verification()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Verification script failed with error: {e}", exc_info=True)
        sys.exit(1)