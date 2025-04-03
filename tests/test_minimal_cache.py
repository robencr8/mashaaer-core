"""
Minimal test to verify database-centric caching behavior.
This test focuses exclusively on cache hit count tracking functionality.
"""

import os
import json
import time
import logging
import hashlib
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

# Import models and session fixtures directly
from tests.conftest import app, client, db_session, clear_cache
from database.models import Cache
from database.db_manager import DatabaseManager
from config import Config

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_minimal_cache_hit_tracking(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Minimal test to verify cache hit count increments work correctly."""
    
    logger.info("======= STARTING MINIMAL CACHE TEST =======")
    
    with app.app_context():
        try:
            # Step 1: Verify table name in model
            logger.info(f"Cache model: {Cache.__name__}, table: {Cache.__tablename__}")
            
            # Step 2: Clear cache table
            clear_cache()
            
            # Verify cache is empty
            count = db_session.query(Cache).count()
            logger.info(f"Cache entries after clearing: {count}")
            assert count == 0, "Cache should be empty at start of test"
            
            # Step 3: Create a test entry with a known key
            test_key = f"test_cache_key_{int(time.time())}"
            test_value = {"data": "test value", "number": 123}
            expires_at = datetime.now() + timedelta(seconds=300)
            
            logger.info(f"Test key: '{test_key}'")
            logger.info(f"Test value: {json.dumps(test_value)}")
            
            # Create a test DatabaseManager with our test session
            config = Config()
            
            # Use a custom session factory for the DatabaseManager to use our test session
            def get_test_session():
                return db_session
            
            # Create DatabaseManager with a mocked session factory
            test_db_manager = DatabaseManager(config=config, db_path=":memory:")
            test_db_manager.Session = MagicMock(return_value=db_session)
            
            # Store test data directly using the overridden Session
            logger.info("Storing response in cache using test db_manager...")
            test_db_manager.store_cached_response(
                test_key, 
                test_value,
                expiry_seconds=300,
                content_type='application/json'
            )
            
            # Verify the cache entry was created
            cache_entry = db_session.query(Cache).filter(Cache.key == test_key).first()
            assert cache_entry is not None, f"Cache entry for key {test_key} should exist"
            initial_hit_count = cache_entry.hit_count
            logger.info(f"Cache entry created, hit_count: {initial_hit_count}")
            
            # Ensure initial hit count is 0
            assert initial_hit_count == 0, f"Expected initial hit_count=0, got {initial_hit_count}"
            
            # Step 4: Retrieve the cached data using the test db_manager
            logger.info("Retrieving cached response using test db_manager...")
            cached_data, metadata = test_db_manager.get_cached_response(test_key)
            
            # Verify the data is correct
            assert cached_data == test_value, "Retrieved data doesn't match original"
            
            # Refresh the database entry and verify hit count was incremented
            db_session.refresh(cache_entry)
            new_hit_count = cache_entry.hit_count
            logger.info(f"Hit count after retrieval: {new_hit_count}")
            assert new_hit_count == 1, f"Expected hit_count=1 after retrieval, got {new_hit_count}"
            
            # Verify metadata
            assert metadata.get("cache_hit") is True, "Metadata should show cache_hit=True"
            assert metadata.get("hit_count") == 1, f"Metadata hit_count should be 1, got {metadata.get('hit_count')}"
            
            # Step 5: Retrieve again and verify hit count increases again
            logger.info("Retrieving cached response a second time...")
            cached_data2, metadata2 = test_db_manager.get_cached_response(test_key)
            
            # Verify data is still correct
            assert cached_data2 == test_value, "Retrieved data doesn't match on second retrieval"
            
            # Verify hit count increased again
            db_session.refresh(cache_entry)
            final_hit_count = cache_entry.hit_count
            logger.info(f"Hit count after second retrieval: {final_hit_count}")
            assert final_hit_count == 2, f"Expected hit_count=2 after second retrieval, got {final_hit_count}"
            
            # Verify metadata updated
            assert metadata2.get("cache_hit") is True, "Metadata should show cache_hit=True"
            assert metadata2.get("hit_count") == 2, f"Metadata hit_count should be 2, got {metadata2.get('hit_count')}"
            
            logger.info("======= TEST PASSED =======")
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            # Print exception info for debugging
            import traceback
            logger.error(traceback.format_exc())
            raise
        finally:
            # Clean up
            logger.info("Cleaning up test resources")
            db_session.rollback()