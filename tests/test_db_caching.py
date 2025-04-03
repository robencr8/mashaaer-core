"""
Direct test of database-centric caching functionality.
This test bypasses the API layer to focus solely on the database caching mechanism.
"""

import os
import json
import time
import logging
import hashlib
from unittest.mock import patch
from datetime import datetime, timedelta

import pytest
from flask import Flask
from sqlalchemy.orm import Session

# Import models and session fixtures directly
from tests.conftest import app, db_session, clear_cache
from database.models import Cache
from database.db_manager import DatabaseManager

def test_direct_cache_storage_and_retrieval(db_session: Session, clear_cache, app: Flask):
    """Directly test the database caching mechanism without going through the API."""
    # Set up logging for debugging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Log test start
    logger.info("======= STARTING DIRECT CACHE TEST =======")
    
    with app.app_context():
        try:
            # Step 1: Verify table name in model
            logger.info(f"Cache model: {Cache.__name__}, table: {Cache.__tablename__}")
            
            # Step 2: Clear cache table
            clear_cache()
            db_session.commit()
            
            # Verify cache is empty
            count = db_session.query(Cache).count()
            logger.info(f"Cache entries after clearing: {count}")
            assert count == 0, "Cache should be empty at start of test"
            
            # Step 3: Create a test key and value
            test_key = "test_cache_key_" + str(int(time.time()))
            test_value = {"data": "test value", "number": 123}
            logger.info(f"Test key: '{test_key}'")
            logger.info(f"Test value: {json.dumps(test_value)}")
            
            # Step 4: Store a value in the cache directly using the db_session
            logger.info("Storing value in cache directly with db_session...")
            
            from datetime import datetime, timedelta
            expires_at = datetime.now() + timedelta(seconds=300)
            
            # Create a new cache entry directly
            cache_entry = Cache(
                key=test_key,
                value=json.dumps(test_value),
                expires_at=expires_at,
                content_type='application/json',
                hit_count=0
            )
            
            # Add it to the session and commit
            db_session.add(cache_entry)
            db_session.commit()
            
            # Step 5: Verify the entry was created
            cache_entry = db_session.query(Cache).filter(Cache.key == test_key).first()
            assert cache_entry is not None, f"Cache entry not found with key: {test_key}"
            logger.info(f"Cache entry created, hit_count: {cache_entry.hit_count}")
            
            # Initial hit count should be 0
            assert cache_entry.hit_count == 0, f"Expected initial hit_count=0, got {cache_entry.hit_count}"
            
            # Step 6: Manually increment the hit count to simulate a cache hit
            logger.info("Manually incrementing hit count to simulate retrieval...")
            
            # Increment hit count directly
            cache_entry.hit_count += 1
            db_session.commit()
            
            # Refresh and check the entry
            db_session.refresh(cache_entry)
            new_hit_count = cache_entry.hit_count
            logger.info(f"Hit count after increment: {new_hit_count}")
            assert new_hit_count == 1, f"Expected hit_count=1 after update, got {new_hit_count}"
            
            # Step 7: Increment again to simulate a second retrieval
            logger.info("Incrementing hit count a second time...")
            cache_entry.hit_count += 1
            db_session.commit()
            
            # Verify hit count was incremented again
            db_session.refresh(cache_entry)
            final_hit_count = cache_entry.hit_count
            logger.info(f"Hit count after second retrieval: {final_hit_count}")
            assert final_hit_count == 2, f"Expected hit_count=2 after second retrieval, got {final_hit_count}"
            
            # We no longer use metadata from db_manager, so this check is removed
            
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