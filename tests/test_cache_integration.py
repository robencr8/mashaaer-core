"""
Integration test for the API cache with mocking of the database operations.
This test verifies that the mobile_api correctly manages the cache hit status.
"""

import os
import json
import time
import logging
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

import pytest
from flask import Flask
from flask.testing import FlaskClient

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_api_cache_with_mocked_db(client: FlaskClient, app: Flask):
    """Test the API caching functionality with mocked db_manager."""
    
    logger.info("======= STARTING API CACHE INTEGRATION TEST WITH MOCKING =======")
    
    # Define standard emotion analysis result to return from the mocked emotion tracker
    emotion_analysis_result = {
        "primary_emotion": "happy", 
        "emotions": {"happy": 0.9, "neutral": 0.1},
        "confidence": 0.9,
        "intensity": 0.9
    }
    
    with app.app_context():
        try:
            # Setup - Mock the DatabaseManager methods for cache operations
            test_text = "APITestCacheMock123"
            
            # Define a cache hit response with all required metadata
            mock_cache_hit_response = (
                emotion_analysis_result, 
                {
                    "cache_hit": True,
                    "hit_count": 1,
                    "content_type": "application/json",
                    "created_at": datetime.utcnow().isoformat(),
                    "expires_at": (datetime.utcnow() + timedelta(minutes=60)).isoformat()
                }
            )
            
            # Define a cache miss response
            mock_cache_miss_response = (None, {"cache_hit": False})
            
            # Set up mock for EmotionTracker.analyze_text
            with patch('emotion_tracker.EmotionTracker.analyze_text') as mock_analyze:
                # Return a standard result when the emotion tracker is called
                mock_analyze.return_value = emotion_analysis_result
                
                # Set up patch for the get_cached_response method
                with patch('database.db_manager.DatabaseManager.get_cached_response') as mock_get_cache:
                    # First API call should be a cache miss, then subsequently a hit
                    mock_get_cache.side_effect = [mock_cache_miss_response, mock_cache_hit_response]
                    
                    # Set up patch for store_cached_response - we'll just let it return success
                    with patch('database.db_manager.DatabaseManager.store_cached_response') as mock_store_cache:
                        mock_store_cache.return_value = True
                        
                        # First API call - should be a cache miss
                        logger.info("Making first API request (should be cache miss)...")
                        response1 = client.post(
                            "/mobile-api/analyze-emotion", 
                            json={"text": test_text, "language": "en"}
                        )
                        
                        # Verify API response
                        assert response1.status_code == 200, f"Expected 200 response, got {response1.status_code}"
                        result1 = json.loads(response1.data)
                        logger.info(f"First response: {json.dumps(result1, indent=2)}")
                        
                        # Verify cache miss status
                        assert result1.get("cache_status") == "miss", \
                            f"Expected cache_status='miss', got '{result1.get('cache_status')}'"
                        
                        # Verify the emotion tracker was called
                        mock_analyze.assert_called_once()
                        logger.info("Verified EmotionTracker.analyze_text was called")
                        
                        # Verify the store_cached_response method was called
                        mock_store_cache.assert_called_once()
                        logger.info("Verified DatabaseManager.store_cached_response was called")
                        
                        # Second API call - should be a cache hit
                        logger.info("Making second API request (should be cache hit)...")
                        response2 = client.post(
                            "/mobile-api/analyze-emotion", 
                            json={"text": test_text, "language": "en"}
                        )
                        
                        # Verify API response
                        assert response2.status_code == 200, f"Expected 200 response, got {response2.status_code}"
                        result2 = json.loads(response2.data)
                        logger.info(f"Second response: {json.dumps(result2, indent=2)}")
                        
                        # Verify cache hit status
                        assert result2.get("cache_status") == "hit", \
                            f"Expected cache_status='hit', got '{result2.get('cache_status')}'"
                        
                        # Verify primary emotion matches what we defined in our mock
                        assert result2["result"]["primary_emotion"] == "happy", \
                            f"Expected primary_emotion='happy', got '{result2['result']['primary_emotion']}'"
                        
                        # Verify the emotion tracker was not called a second time
                        assert mock_analyze.call_count == 1, \
                            f"Expected EmotionTracker.analyze_text to be called once, but was called {mock_analyze.call_count} times"
                        logger.info("Verified EmotionTracker.analyze_text was NOT called a second time (used cache)")
                
            logger.info("======= TEST PASSED =======")
            
        except Exception as e:
            logger.error(f"Test failed: {str(e)}")
            # Print exception info for debugging
            import traceback
            logger.error(traceback.format_exc())
            raise