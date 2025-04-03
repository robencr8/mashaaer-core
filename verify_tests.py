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

def run_verification():
    """Run the verification process for all tests."""
    logger.info("=== Starting Test Verification ===")
    start_time = time.time()
    
    # Step 1: Check database connection
    db_connection_ok = check_database_connection()
    if not db_connection_ok:
        logger.error("Database connection failed. Verification cannot continue.")
        return False
    
    # Step 2: Verify each test file
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
    
    # Step 3: Report results
    execution_time = round(time.time() - start_time, 2)
    logger.info("=== Test Verification Complete ===")
    logger.info(f"Execution Time: {execution_time} seconds")
    logger.info(f"Overall Result: {'SUCCESS' if all_tests_passed else 'FAILURE'}")
    
    return all_tests_passed

if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)