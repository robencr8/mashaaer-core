"""
Minimal test to verify database-centric caching behavior.
This test focuses exclusively on cache hit count tracking functionality.
"""

import os
import json
import time
import logging
import hashlib
from unittest.mock import patch
from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

# Import models and session fixtures directly
from tests.conftest import app, client, db_session, clear_cache
from database.models import Cache

def test_minimal_cache_hit_tracking(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Minimal test to verify cache hit count increments work correctly."""
    # Set up logging for debugging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Log test start
    logger.info("======= STARTING MINIMAL CACHE HIT COUNT TEST =======")
    
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
            
            # Step 3: Create a simple test request with predictable cache key
            test_text = "TestingCacheHitCount123"
            normalized_text = test_text.strip().lower()
            cache_key = f"emotion_{hashlib.md5(normalized_text.encode()).hexdigest()}_en"
            logger.info(f"Test text: '{test_text}'")
            logger.info(f"Cache key: '{cache_key}'")
            
            # Step 4: Mock the emotion analysis to return consistent results
            with patch('emotion_tracker.EmotionTracker.analyze_text') as mock_analyze:
                mock_analyze.return_value = {
                    "primary_emotion": "happy",
                    "confidence": 0.9,
                    "emotions": {
                        "happy": 0.9,
                        "neutral": 0.1
                    }
                }
                
                # Step 5: First request - this should create a cache entry
                logger.info("Making first API request (should create cache entry)")
                response1 = client.post(
                    "/mobile-api/analyze-emotion",
                    json={"text": test_text, "language": "en", "include_details": True}
                )
                
                # Verify response
                assert response1.status_code == 200, f"Expected 200 response, got {response1.status_code}"
                result1 = json.loads(response1.data)
                logger.info(f"First response: {json.dumps(result1, indent=2)}")
                
                # Step 6: Verify cache entry was created
                db_session.commit()  # Ensure transaction is committed
                
                # First, dump all cache entries for debugging
                all_cache_entries = db_session.query(Cache).all()
                logger.info(f"Total cache entries: {len(all_cache_entries)}")
                for entry in all_cache_entries:
                    logger.info(f"Entry: key={entry.key}, hit_count={entry.hit_count}")
                
                # Now look for our specific entry
                cache_entry = db_session.query(Cache).filter(Cache.key == cache_key).first()
                assert cache_entry is not None, f"Cache entry not found with key: {cache_key}"
                
                # Record initial hit count
                initial_hit_count = cache_entry.hit_count
                logger.info(f"Initial hit count: {initial_hit_count}")
                
                # Step 7: Second request - this should hit the cache
                logger.info("Making second API request (should hit cache)")
                response2 = client.post(
                    "/mobile-api/analyze-emotion",
                    json={"text": test_text, "language": "en", "include_details": True}
                )
                
                # Verify response
                assert response2.status_code == 200, f"Expected 200 response, got {response2.status_code}"
                result2 = json.loads(response2.data)
                logger.info(f"Second response: {json.dumps(result2, indent=2)}")
                
                # Step 8: Verify hit count was incremented
                db_session.refresh(cache_entry)
                new_hit_count = cache_entry.hit_count
                logger.info(f"New hit count: {new_hit_count}")
                
                # Core assertion: hit count should increase by 1
                assert new_hit_count == initial_hit_count + 1, \
                    f"Hit count should increment from {initial_hit_count} to {initial_hit_count + 1}, got {new_hit_count}"
                
                # Verify cache_status indicates a hit
                assert result2.get("cache_status") == "hit", \
                    f"Expected cache_status='hit', got '{result2.get('cache_status')}'"
                
                # Verify mock was only called once (for the first request)
                assert mock_analyze.call_count == 1, \
                    f"Expected analyze_text to be called once, got {mock_analyze.call_count}"
                
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