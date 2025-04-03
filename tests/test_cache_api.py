"""
Test for the API caching functionality, focusing on cache hit count tracking.
This version combines direct DB validation with API testing.
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

def test_api_cache_hit_count_tracking(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Test that hit counts are properly tracked when the API uses cached responses."""
    # Set up logging for debugging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # Log test start
    logger.info("======= STARTING API CACHE HIT COUNT TEST =======")
    
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
            
            # Step 3: Create a test text that will be consistent
            test_text = "APITestingCacheHitCount123"
            normalized_text = test_text.strip().lower()
            text_hash = hashlib.md5(normalized_text.encode()).hexdigest()
            expected_key = f"emotion_{text_hash}_en"
            logger.info(f"Test text: '{test_text}'")
            logger.info(f"Expected cache key: '{expected_key}'")
            
            # Pre-create cache entry directly (avoiding reliance on API for creation)
            from datetime import datetime, timedelta
            expires_at = datetime.now() + timedelta(seconds=300)
            
            test_data = {
                "primary_emotion": "happy",
                "confidence": 0.9,
                "emotions": {
                    "happy": 0.9,
                    "neutral": 0.1
                }
            }
            
            # Create cache entry directly
            cache_entry = Cache(
                key=expected_key,
                value=json.dumps(test_data),
                expires_at=expires_at,
                content_type='application/json',
                hit_count=0
            )
            
            # Add it to the session and commit
            logger.info("Creating cache entry directly...")
            db_session.add(cache_entry)
            db_session.commit()
            
            # Verify cache entry exists
            entry = db_session.query(Cache).filter(Cache.key == expected_key).first()
            assert entry is not None, f"Failed to create cache entry with key {expected_key}"
            initial_hit_count = entry.hit_count
            logger.info(f"Cache entry created with hit_count: {initial_hit_count}")
            
            # Step 4: Make an API call that should hit the cache
            with patch('emotion_tracker.EmotionTracker.analyze_text') as mock_analyze:
                # Configure mock for the unlikely case it gets called
                mock_analyze.return_value = test_data
                
                logger.info("Making API request (should hit cache)...")
                response = client.post(
                    "/mobile-api/analyze-emotion", 
                    json={"text": test_text, "language": "en", "include_details": True}
                )
                
                # Verify API response
                assert response.status_code == 200, f"Expected 200 response, got {response.status_code}"
                result = json.loads(response.data)
                logger.info(f"Response: {json.dumps(result, indent=2)}")
                
                # Verify cache was hit
                assert result.get("cache_status") == "hit", \
                    f"Expected cache_status='hit', got '{result.get('cache_status')}'"
                
                # Verify hit count was incremented in database
                db_session.refresh(entry)
                new_hit_count = entry.hit_count
                logger.info(f"Hit count after API call: {new_hit_count}")
                assert new_hit_count == initial_hit_count + 1, \
                    f"Expected hit count to increment from {initial_hit_count} to {initial_hit_count + 1}, got {new_hit_count}"
                
                # Verify mock was not called (since cache was hit)
                assert mock_analyze.call_count == 0, \
                    f"Expected analyze_text not to be called, but was called {mock_analyze.call_count} times"
                
                # Make a second API call to verify the hit count increments again
                logger.info("Making second API request...")
                response2 = client.post(
                    "/mobile-api/analyze-emotion", 
                    json={"text": test_text, "language": "en", "include_details": True}
                )
                
                # Verify second API response
                assert response2.status_code == 200, f"Expected 200 response, got {response2.status_code}"
                result2 = json.loads(response2.data)
                
                # Verify cache was hit again
                assert result2.get("cache_status") == "hit", \
                    f"Expected cache_status='hit', got '{result2.get('cache_status')}'"
                
                # Verify hit count was incremented again
                db_session.refresh(entry)
                final_hit_count = entry.hit_count
                logger.info(f"Hit count after second API call: {final_hit_count}")
                assert final_hit_count == new_hit_count + 1, \
                    f"Expected hit count to increment from {new_hit_count} to {new_hit_count + 1}, got {final_hit_count}"
                
                # Verify mock still was not called
                assert mock_analyze.call_count == 0, \
                    f"Expected analyze_text not to be called, but was called {mock_analyze.call_count} times"
                
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