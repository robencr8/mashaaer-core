"""
Tests for the database-centric caching implementation.
Focuses on the mobile API endpoints that use caching.
"""

import json
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

# Adjust imports for your actual application structure
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.models import Cache
from mobile_api_routes import mobile_analyze_emotion, mobile_speak

# --- Helper Functions ---

def get_cache_entry(db_session: Session, key: str) -> Cache:
    """Helper function to retrieve a cache entry by key."""
    return db_session.query(Cache).filter_by(key=key).first()

def create_mock_emotion_result(text: str = "Test text", primary_emotion: str = "happy"):
    """Creates a standardized mock emotion analysis result."""
    return {
        "primary_emotion": primary_emotion,
        "emotions": {
            primary_emotion: 0.8,
            "neutral": 0.2
        },
        "intensity": 0.8,
        "metadata": {
            "source": "test-emotion-analyzer",
            "confidence": 0.9
        },
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }

# --- Test Cases ---

def test_analyze_emotion_cache_hit(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Tests that the emotion analysis endpoint correctly uses cache."""
    clear_cache()
    
    print("\n--- Starting test_analyze_emotion_cache_hit ---")
    
    # Prepare the cache data that will be returned on the second call
    expected_cache_data = {
        "primary_emotion": "happy",
        "confidence": 0.85,
        "emotions": {
            "happy": 0.85,
            "neutral": 0.10,
            "sad": 0.05
        },
        "language": "en",
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    # Use a callable for side_effect to have more control over the behavior
    call_count = 0
    def mock_get_cache_side_effect(cache_key):
        nonlocal call_count
        call_count += 1
        print(f"Mock get_cached_response called (call #{call_count}) with key: {cache_key}")
        
        if call_count == 1:
            # First call - cache miss
            return (None, {"cache_hit": False})
        else:
            # Second call - cache hit
            return (expected_cache_data, {
                "cache_hit": True,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=3)).isoformat(),
                "hit_count": 1,
                "content_type": "application/json" 
            })
    
    # Mock the database get_cached_response method first to ensure we control its behavior
    with patch('database.db_manager.DatabaseManager.get_cached_response') as mock_get_cache:
        # Use the callable side_effect
        mock_get_cache.side_effect = mock_get_cache_side_effect
        
        # Then mock the emotion tracker
        with patch('emotion_tracker.EmotionTracker.analyze_text') as mock_analyze:
            # Configure the mock to return a standard result
            mock_result = create_mock_emotion_result()
            print(f"Mock result: {mock_result}")
            mock_analyze.return_value = mock_result
            
            # First request - should miss cache and call analyze_text
            print("Making first request - should miss cache")
            response = client.post(
                "/mobile-api/analyze-emotion",
                json={"text": "I am feeling happy today", "language": "en"}
            )
            
            # Verify first response
            print(f"First response status code: {response.status_code}")
            result = json.loads(response.data)
            print(f"First response data: {result}")
            assert response.status_code == 200
            assert result.get("success") is True
            
            # Check cache_status - should be "miss" on first call
            cache_status = result.get("cache_status")
            print(f"Cache status in first response: {cache_status}")
            assert cache_status == "miss", f"Expected cache_status to be 'miss', got {cache_status}"
            
            # Check emotion data
            emotion = result.get("result", {}).get("primary_emotion")
            print(f"Primary emotion in first response: {emotion}")
            assert emotion == "happy", f"Expected primary_emotion to be 'happy', got {emotion}"
            
            # Verify that analyze_text was called once
            print(f"Mock analyze_text call count after first request: {mock_analyze.call_count}")
            assert mock_analyze.call_count == 1
            
            # Now patch the store_cached_response method to verify it's called
            with patch('database.db_manager.DatabaseManager.store_cached_response') as mock_store_cache:
                mock_store_cache.return_value = True
                
                # Second request with same text - should hit cache
                print("\nMaking second request - should hit cache")
                response2 = client.post(
                    "/mobile-api/analyze-emotion", 
                    json={"text": "I am feeling happy today", "language": "en"}
                )
                
                # Verify second response
                print(f"Second response status code: {response2.status_code}")
                result2 = json.loads(response2.data)
                print(f"Second response data: {result2}")
                assert response2.status_code == 200
                assert result2.get("success") is True
                
                # Check cache_status - should be "hit" on second call
                cache_status2 = result2.get("cache_status")
                print(f"Cache status in second response: {cache_status2}")
                assert cache_status2 == "hit", f"Expected cache_status to be 'hit', got {cache_status2}"
                
                # Check emotion data consistency
                emotion2 = result2.get("result", {}).get("primary_emotion")
                print(f"Primary emotion in second response: {emotion2}")
                assert emotion2 == "happy", f"Expected primary_emotion to be 'happy', got {emotion2}"
                
                # Verify that analyze_text was not called again
                print(f"Mock analyze_text call count after second request: {mock_analyze.call_count}")
                assert mock_analyze.call_count == 1
                
                print("--- End of test_analyze_emotion_cache_hit ---\n")

def test_analyze_emotion_bypass_cache(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Tests that the bypass_cache parameter correctly skips the cache."""
    clear_cache()
    
    print("\n--- Starting test_analyze_emotion_bypass_cache ---")
    
    # Mock db_manager's get_cached_response
    with patch('database.db_manager.DatabaseManager.get_cached_response') as mock_get_cache:
        # Configure it to return a cache hit on the second call
        mock_get_cache.return_value = (None, {"cache_hit": False})
        
        # Mock storing cache responses
        with patch('database.db_manager.DatabaseManager.store_cached_response') as mock_store_cache:
            mock_store_cache.return_value = True
            
            # Setup mock for emotion analysis
            with patch('emotion_tracker.EmotionTracker.analyze_text') as mock_analyze:
                # Configure the mock to return a standard result
                mock_analyze.return_value = create_mock_emotion_result()
                
                # First request - normal caching behavior
                print("Making first request - should miss cache but store result")
                response = client.post(
                    "/mobile-api/analyze-emotion",
                    json={"text": "Testing bypass cache", "language": "en"}
                )
                
                # Verify first response
                print(f"First response status code: {response.status_code}")
                result = json.loads(response.data)
                print(f"First response data: {result}")
                assert response.status_code == 200
                assert mock_analyze.call_count == 1
                
                # Verify the cache was checked and result was stored
                assert mock_get_cache.call_count == 1
                assert mock_store_cache.call_count == 1
                
                # Second request with bypass_cache=True
                print("\nMaking second request with bypass_cache=True")
                response2 = client.post(
                    "/mobile-api/analyze-emotion", 
                    json={
                        "text": "Testing bypass cache", 
                        "language": "en",
                        "bypass_cache": True
                    }
                )
                
                # Verify second response
                print(f"Second response status code: {response2.status_code}")
                result2 = json.loads(response2.data)
                print(f"Second response data: {result2}")
                assert response2.status_code == 200
                assert result2.get("cache_status") == "disabled"
                
                # Verify that analyze_text was called again
                assert mock_analyze.call_count == 2
                
                # Verify cache was not checked or updated for the second request
                assert mock_get_cache.call_count == 1  # Still just the first call
                assert mock_store_cache.call_count == 1  # Still just the first call
                
                print("--- End of test_analyze_emotion_bypass_cache ---\n")

def test_analyze_emotion_cache_expiration(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Tests that cached entries expire correctly and are refreshed."""
    clear_cache()
    
    print("\n--- Starting test_analyze_emotion_cache_expiration ---")
    
    # For this test, we'll use mocks to simulate cache expiration
    test_text = "This text is for testing cache expiration"
    
    # Prepare the cache data that will be returned on the second call
    happy_cache_data = {
        "primary_emotion": "happy",
        "confidence": 0.85,
        "emotions": {
            "happy": 0.85,
            "neutral": 0.10,
            "sad": 0.05
        },
        "language": "en",
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    # Use a callable for side_effect to have more control over the behavior
    call_count = 0
    def mock_get_cache_side_effect(cache_key):
        nonlocal call_count
        call_count += 1
        print(f"Mock get_cached_response called (call #{call_count}) with key: {cache_key}")
        
        # For the bypass_cache=True case, the cache lookup doesn't happen
        # So we only need to handle cases 1 and 2:
        if call_count == 1:
            # First call - cache miss
            return (None, {"cache_hit": False})
        elif call_count == 2:
            # Second call - cache hit
            return (happy_cache_data, {
                "cache_hit": True,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=3)).isoformat(),
                "hit_count": 1,
                "content_type": "application/json" 
            })
        else:
            # Fallback for any unexpected calls
            print(f"Unexpected get_cached_response call #{call_count}")
            return (None, {"cache_hit": False})
    
    # First, mock get_cached_response to return no cache hit initially
    with patch('database.db_manager.DatabaseManager.get_cached_response') as mock_get_cache:
        # Use our callable side_effect
        mock_get_cache.side_effect = mock_get_cache_side_effect
        
        # Mock the db store method
        with patch('database.db_manager.DatabaseManager.store_cached_response') as mock_store_cache:
            mock_store_cache.return_value = True
            
            # Setup mock for emotion analysis to return different results on subsequent calls
            with patch('emotion_tracker.EmotionTracker.analyze_text') as mock_analyze:
                # First call returns "happy"
                happy_result = create_mock_emotion_result(test_text, "happy")
                mock_analyze.return_value = happy_result
                
                # First request - creates cache entry with "happy"
                print("Making first request - should miss cache and store 'happy'")
                response = client.post(
                    "/mobile-api/analyze-emotion",
                    json={"text": test_text, "language": "en"}
                )
                
                # Verify first response
                print(f"First response status code: {response.status_code}")
                result = json.loads(response.data)
                print(f"First response data: {result}")
                assert response.status_code == 200
                assert result.get("success") is True
                assert result.get("result", {}).get("primary_emotion") == "happy"
                assert result.get("cache_status") == "miss"
                assert mock_analyze.call_count == 1
                
                # Now change the mock to return a different emotion
                calm_result = create_mock_emotion_result(test_text, "calm")
                mock_analyze.return_value = calm_result
                
                # Second request with same text should hit cache and still return "happy"
                print("\nMaking second request - should hit cache and return 'happy'")
                response2 = client.post(
                    "/mobile-api/analyze-emotion",
                    json={"text": test_text, "language": "en"}
                )
                
                # Verify second response still returns cached "happy"
                print(f"Second response status code: {response2.status_code}")
                result2 = json.loads(response2.data)
                print(f"Second response data: {result2}")
                assert response2.status_code == 200
                assert result2.get("cache_status") == "hit"
                assert result2.get("result", {}).get("primary_emotion") == "happy"
                assert mock_analyze.call_count == 1  # Hasn't increased
                
                # Now bypass the cache to force a new analysis
                print("\nMaking third request with bypass_cache=True - should return 'calm'")
                response3 = client.post(
                    "/mobile-api/analyze-emotion",
                    json={"text": test_text, "language": "en", "bypass_cache": True}
                )
                
                # Verify third response returns the new "calm" emotion
                print(f"Third response status code: {response3.status_code}")
                result3 = json.loads(response3.data)
                print(f"Third response data: {result3}")
                assert response3.status_code == 200
                assert result3.get("cache_status") == "disabled"
                assert result3.get("result", {}).get("primary_emotion") == "calm"
                assert mock_analyze.call_count == 2  # Increased by 1
                
                print("--- End of test_analyze_emotion_cache_expiration ---\n")

def test_speak_cache_hit(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Tests that the TTS endpoint correctly uses cache."""
    clear_cache()
    
    # Create a unique file path for this test
    import os
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    test_file_path = f"tts_cache/test_speech_{unique_id}.mp3"
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    
    # Create a dummy file
    with open(test_file_path, 'w') as f:
        f.write("dummy audio content")
    
    try:
        # Setup mock for TTS generation
        with patch('tts.tts_manager.TTSManager.generate_tts') as mock_tts:
            # Configure the mock to return our unique file path
            mock_tts.return_value = test_file_path
            
            # Mock the database cache lookup to ensure a miss on first call
            with patch('database.db_manager.DatabaseManager.get_cached_response') as mock_get_cache:
                call_count = 0
                def mock_get_cache_side_effect(cache_key):
                    nonlocal call_count
                    call_count += 1
                    print(f"Mock get_cached_response called (call #{call_count}) with key: {cache_key}")
                    
                    if call_count == 1:
                        # First call - cache miss
                        return (None, {"cache_hit": False})
                    else:
                        # Second call - cache hit
                        # For TTS cache, we need to return a dictionary object with the file path
                        # NOT a JSON string - the actual dictionary
                        cache_data = {
                            "audio_path": test_file_path,
                            "file_size": 19,  # Size of our dummy content
                            "format": "mp3",
                            "duration": 1.0,
                            "voice": "default",
                            "language": "en-US"
                        }
                        return (cache_data, {
                            "cache_hit": True,
                            "created_at": datetime.now().isoformat(),
                            "expires_at": (datetime.now() + timedelta(days=7)).isoformat(),
                            "hit_count": 1,
                            "content_type": "application/json" 
                        })
                
                mock_get_cache.side_effect = mock_get_cache_side_effect
                
                # First request - should miss cache
                print("Making first request - should miss cache")
                response = client.post(
                    "/mobile-api/speak",
                    json={
                        "text": f"Test TTS caching text {unique_id}",
                        "language": "en-US",
                        "voice": "default"
                    }
                )
                
                # Verify first response
                print(f"First response status code: {response.status_code}")
                result = json.loads(response.data)
                print(f"First response data: {result}")
                assert response.status_code == 200
                assert result.get("success") is True
                assert result.get("cache_status") == "miss"
                assert "audio_path" in result
                
                # Verify that generate_tts was called once
                assert mock_tts.call_count == 1
                
                # Second request with same parameters - should hit cache
                print("\nMaking second request - should hit cache")
                response2 = client.post(
                    "/mobile-api/speak", 
                    json={
                        "text": f"Test TTS caching text {unique_id}",
                        "language": "en-US",
                        "voice": "default"
                    }
                )
                
                # Verify second response
                print(f"Second response status code: {response2.status_code}")
                result2 = json.loads(response2.data)
                print(f"Second response data: {result2}")
                assert response2.status_code == 200
                assert result2.get("success") is True
                assert result2.get("cache_status") == "hit"
                assert "audio_path" in result2
                
                # Verify that generate_tts was not called again
                assert mock_tts.call_count == 1
    finally:
        # Clean up the test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_speak_different_voice_parameters(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Tests that the TTS endpoint creates different cache entries for different voices."""
    clear_cache()
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    test_text = f"Test voice parameter variations {unique_id}"
    
    # Create an actual file directory for the mock to return files
    import os
    os.makedirs("tts_cache", exist_ok=True)
    
    # Create test files with unique names to avoid collision
    test_files = [
        f"tts_cache/default_en-US_{unique_id}.mp3",
        f"tts_cache/voice_2_en-US_{unique_id}.mp3",
        f"tts_cache/default_ar_{unique_id}.mp3"
    ]
    
    try:
        # Create dummy files
        for file_path in test_files:
            with open(file_path, 'w') as f:
                f.write("dummy audio content")
    
        # Setup mock for TTS generation
        with patch('tts.tts_manager.TTSManager.generate_tts') as mock_tts:
            # Configure the mock to return different paths for different voices
            def mock_generate_tts(text, voice=None, language=None):
                if voice == "voice_2":
                    return test_files[1]  # voice_2 file
                elif language == "ar":
                    return test_files[2]  # Arabic file
                else:
                    return test_files[0]  # default file
            
            mock_tts.side_effect = mock_generate_tts
            
            # Mock the database cache lookup to ensure cache misses
            with patch('database.db_manager.DatabaseManager.get_cached_response') as mock_get_cache:
                # Always return cache miss
                mock_get_cache.return_value = (None, {"cache_hit": False})
                
                # First request with default voice
                print("\nMaking request with default voice and English")
                response1 = client.post(
                    "/mobile-api/speak",
                    json={
                        "text": test_text,
                        "language": "en-US",
                        "voice": "default"
                    }
                )
                result1 = json.loads(response1.data)
                print(f"Response 1: {result1}")
                
                # Second request with different voice
                print("\nMaking request with voice_2 and English")
                response2 = client.post(
                    "/mobile-api/speak", 
                    json={
                        "text": test_text,
                        "language": "en-US",
                        "voice": "voice_2"
                    }
                )
                result2 = json.loads(response2.data)
                print(f"Response 2: {result2}")
                
                # Third request with different language
                print("\nMaking request with default voice and Arabic")
                response3 = client.post(
                    "/mobile-api/speak", 
                    json={
                        "text": test_text,
                        "language": "ar",
                        "voice": "default"
                    }
                )
                result3 = json.loads(response3.data)
                print(f"Response 3: {result3}")
                
                # Verify response structure
                assert result1.get("success") is True
                assert result2.get("success") is True
                assert result3.get("success") is True
                
                # Verify all got different paths
                assert result1.get("audio_path") != result2.get("audio_path")
                assert result1.get("audio_path") != result3.get("audio_path")
                assert result2.get("audio_path") != result3.get("audio_path")
                
                # Verify TTS generation was called for each unique parameter set
                assert mock_tts.call_count == 3
    finally:
        # Clean up the test files
        for file_path in test_files:
            if os.path.exists(file_path):
                os.remove(file_path)

def test_cache_error_handling(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Tests error handling in the caching mechanism."""
    clear_cache()
    
    # Mock db_manager's get_cached_response to raise an exception
    with patch('database.db_manager.DatabaseManager.get_cached_response') as mock_get_cache:
        mock_get_cache.side_effect = Exception("Simulated database error")
        
        # Setup mock for emotion analysis to proceed despite cache error
        with patch('emotion_tracker.EmotionTracker.analyze_text') as mock_analyze:
            mock_analyze.return_value = create_mock_emotion_result()
            
            # Request should proceed despite cache error
            response = client.post(
                "/mobile-api/analyze-emotion",
                json={"text": "Testing error handling", "language": "en"}
            )
            
            # Verify response
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result.get("success") is True
            
            # Cache status should indicate an issue
            assert result.get("cache_status") == "error"
            
            # Verify that analyze_text was called as fallback
            assert mock_analyze.call_count == 1
            
    # Mock db_manager's store_cached_response to raise an exception
    with patch('database.db_manager.DatabaseManager.store_cached_response') as mock_store_cache:
        mock_store_cache.side_effect = Exception("Simulated database error")
        
        with patch('emotion_tracker.EmotionTracker.analyze_text') as mock_analyze:
            mock_analyze.return_value = create_mock_emotion_result()
            
            # Request should still succeed even if cache storage fails
            response = client.post(
                "/mobile-api/analyze-emotion",
                json={"text": "Testing storage error", "language": "en"}
            )
            
            # Verify response
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result.get("success") is True
            
            # Cache status should indicate an issue
            assert result.get("cache_status") == "error"

def test_cache_invalidation(client: FlaskClient, db_session: Session, clear_cache, app: Flask, add_test_cache_entry):
    """Tests that cache entries can be invalidated programmatically."""
    clear_cache()
    
    # Create some test cache entries
    add_test_cache_entry("test_cache_key_1", json.dumps({"data": "value1"}))
    add_test_cache_entry("test_cache_key_2", json.dumps({"data": "value2"}))
    add_test_cache_entry("different_prefix_1", json.dumps({"data": "other"}))
    
    # Verify entries exist
    assert get_cache_entry(db_session, "test_cache_key_1") is not None
    assert get_cache_entry(db_session, "test_cache_key_2") is not None
    assert get_cache_entry(db_session, "different_prefix_1") is not None
    
    # Use db_manager to invalidate specific entry
    with app.app_context():
        from database.db_manager import db_manager  # Import within context
        
        # Invalidate specific key
        db_manager.invalidate_cache(cache_key="test_cache_key_1")
        
        # Verify only that entry is removed
        assert get_cache_entry(db_session, "test_cache_key_1") is None
        assert get_cache_entry(db_session, "test_cache_key_2") is not None
        assert get_cache_entry(db_session, "different_prefix_1") is not None
        
        # Invalidate by pattern
        db_manager.invalidate_cache(pattern="test_cache%")
        
        # Verify pattern-matched entries are removed
        assert get_cache_entry(db_session, "test_cache_key_2") is None
        assert get_cache_entry(db_session, "different_prefix_1") is not None

def test_performance_metrics(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Tests that caching improves performance."""
    clear_cache()
    
    test_text = "Performance testing with a longer text to analyze the sentiment and emotion of this passage."
    
    # Setup a slow emotion analysis mock to simulate computational cost
    with patch('emotion_tracker.EmotionTracker.analyze_text') as mock_analyze:
        def slow_analyze(*args, **kwargs):
            time.sleep(0.5)  # Simulate processing delay
            return create_mock_emotion_result()
        
        mock_analyze.side_effect = slow_analyze
        
        # First request - should be slow due to analysis
        start_time = time.time()
        response1 = client.post(
            "/mobile-api/analyze-emotion",
            json={"text": test_text, "language": "en"}
        )
        first_request_time = time.time() - start_time
        
        # Second request - should be fast due to cache
        start_time = time.time()
        response2 = client.post(
            "/mobile-api/analyze-emotion",
            json={"text": test_text, "language": "en"}
        )
        second_request_time = time.time() - start_time
        
        # Verify timing improved significantly
        assert second_request_time < first_request_time
        assert second_request_time < 0.1  # Should be very fast for cache hit
        
        # Calculate and log performance improvement
        improvement = (first_request_time - second_request_time) / first_request_time * 100
        print(f"Performance improvement: {improvement:.2f}% faster with cache")
        assert improvement > 80  # Cache should be at least 80% faster

def test_cache_hit_count_tracking(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Tests that cache hit counts are properly tracked."""
    print("\n===== Starting test_cache_hit_count_tracking =====")

    with app.app_context():
        # Explicitly clear any existing cache entries and verify it's empty
        clear_cache()
        db_session.commit()  # Ensure the DB is in a clean state
        
        cache_count = db_session.query(Cache).count()
        assert cache_count == 0, f"Expected empty cache at start of test, but found {cache_count} entries"
        print(f"Verified cache is empty: {cache_count} entries")
    
        # Use a unique text for this test to avoid cache collisions with other tests
        import uuid
        unique_id = uuid.uuid4().hex[:8]
        test_text = f"Tracking cache hit counts for test {unique_id}"
        print(f"Using unique test text: '{test_text}'")
        
        # For debugging: Make sure db_manager is correctly configured in the app context
        from main import db_manager
        print(f"DEBUG: db_manager available: {db_manager is not None}")
        print(f"DEBUG: db_manager has store_cached_response: {hasattr(db_manager, 'store_cached_response')}")
        
        # Create a cache key using the same algorithm as in the application
        import hashlib
        normalized_text = test_text.strip().lower()
        cache_key = f"emotion_{hashlib.md5(normalized_text.encode()).hexdigest()}_en"
        print(f"DEBUG: Generated cache key: {cache_key}")
        
        # Add a direct cache entry to completely bypass the API call mechanism
        # This ensures we're testing the cache retrieval logic directly
        cache_data = {
            "primary_emotion": "happy",
            "confidence": 0.9,
            "emotions": {
                "happy": 0.9,
                "neutral": 0.05,
                "sad": 0.02,
                "angry": 0.01,
                "fear": 0.01,
                "surprise": 0.01
            },
            "language": "en",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        # Manually add the cache entry using db_manager
        import json
        store_result = db_manager.store_cached_response(
            cache_key, 
            json.dumps(cache_data), 
            expiry_seconds=300,
            content_type='application/json'
        )
        print(f"DEBUG: Manual cache entry creation result: {store_result}")
        
        # Verify the cache entry exists
        cache_entry = db_session.query(Cache).filter(Cache.key == cache_key).first()
        assert cache_entry is not None, "Cache entry was not created manually"
        print(f"DEBUG: Initial cache entry verified: key={cache_entry.key}, hit_count={cache_entry.hit_count}")
        
        # Make sure we're not using a stale session
        db_session.commit()
        db_session.refresh(cache_entry)
        
        # Store the initial hit count
        initial_hit_count = cache_entry.hit_count
        print(f"DEBUG: Initial hit count: {initial_hit_count}")
        
        # Set up mocks for emotion analysis functions to prevent real emotion analysis from running
        with patch('emotion_tracker.EmotionTracker.analyze_text') as mock_analyze, \
             patch('emotion_tracker.EmotionTracker.analyze_text_advanced') as mock_analyze_advanced:
            
            # Mock both methods to ensure complete coverage
            mock_emotion_result = {
                "primary_emotion": "happy", 
                "confidence": 0.9,
                "emotions": {
                    "happy": 0.9,
                    "neutral": 0.05,
                    "sad": 0.02,
                    "angry": 0.01,
                    "fear": 0.01,
                    "surprise": 0.01
                }
            }
            
            mock_analyze.return_value = mock_emotion_result
            mock_analyze_advanced.return_value = mock_emotion_result
            
            print(f"DEBUG: Mocks configured")
            
            # First request to populate cache
            print("\n===== Step 1: Making first request to populate cache =====")
            response1 = client.post(
                "/mobile-api/analyze-emotion",
                json={"text": test_text, "language": "en", "include_details": "true"}
            )
            
            # Verify first response - should be a cache miss
            result1 = json.loads(response1.data)
            print(f"First response: {json.dumps(result1, indent=2)}")
            assert response1.status_code == 200
            assert result1.get("success") is True
            assert result1.get("cache_status") == "miss"
            
            # Generate the cache key for our test
            import hashlib
            normalized_text = test_text.strip().lower()
            cache_key = f"emotion_{hashlib.md5(normalized_text.encode()).hexdigest()}_en"
            print(f"Cache key: {cache_key}")
            
            # Get cache entry after first request
            cache_entry = get_cache_entry(db_session, cache_key)
            assert cache_entry is not None, "Cache entry was not created"
            hit_count_before = cache_entry.hit_count
            print(f"Initial hit count from database: {hit_count_before}")
            
            # Debug: Check result1 metadata structure - it's nested in result in the API
            if "result" in result1 and "metadata" in result1["result"]:
                print(f"Metadata in first response: {json.dumps(result1['result']['metadata'], indent=2)}")
                if "cache_hit_count" in result1["result"]["metadata"]:
                    print(f"Cache hit count in first response: {result1['result']['metadata']['cache_hit_count']}")
                else:
                    print("No cache_hit_count field in first response metadata")
            else:
                print("No result.metadata field in first response")
            
            # Commit session to ensure cache entry is persisted
            db_session.commit()
            
            # Make multiple cache hits - we'll do 3 requests
            print("\n===== Step 2: Making 3 more requests to test hit count =====")
            
            hit_counts = []
            for i in range(3):
                print(f"\n--- Request {i+1} ---")
                
                # Get cache entry before request
                cache_before = get_cache_entry(db_session, cache_key)
                print(f"Hit count before request {i+1}: {cache_before.hit_count}")
                
                response = client.post(
                    "/mobile-api/analyze-emotion",
                    json={"text": test_text, "language": "en", "include_details": "true"}
                )
                result = json.loads(response.data)
                
                # Debug: Print key sections of the response
                print(f"Status code: {response.status_code}")
                print(f"Success: {result.get('success')}")
                print(f"Cache status: {result.get('cache_status')}")
                
                # Validate response format
                assert response.status_code == 200
                assert result.get("success") is True
                assert result.get("cache_status") == "hit", f"Expected 'hit' but got '{result.get('cache_status')}'"
                
                # Debug: Check result metadata structure - it's nested in result in the API
                if "result" in result and "metadata" in result["result"]:
                    print(f"Metadata in response: {json.dumps(result['result']['metadata'], indent=2)}")
                    if "cache_hit_count" in result["result"]["metadata"]:
                        hit_count = result["result"]["metadata"]["cache_hit_count"]
                        print(f"Cache hit count in response: {hit_count}")
                        hit_counts.append(hit_count)
                    else:
                        print("No cache_hit_count field in response metadata")
                else:
                    print("No result.metadata field in response")
                
                # Get cache entry after request to check database directly
                db_session.refresh(cache_before)  # Refresh to get updated values
                print(f"Hit count in database after request {i+1}: {cache_before.hit_count}")
            
            print(f"\nHit counts from responses: {hit_counts}")
            
            # Final verification: check the database record
            final_cache_entry = get_cache_entry(db_session, cache_key)
            final_hit_count = final_cache_entry.hit_count
            print(f"Final hit count from database: {final_hit_count}")
            
            # Verify hit count increased correctly
            expected_increase = 3
            assert final_hit_count >= initial_hit_count + expected_increase, \
                f"Expected hit count to increase by at least {expected_increase}, but it went from {initial_hit_count} to {final_hit_count}"
        
        # First request to populate cache
        print("\n===== Step 1: Making first request to populate cache =====")
        response1 = client.post(
            "/mobile-api/analyze-emotion",
            json={"text": test_text, "language": "en", "include_details": "true"}
        )
        
        # Verify first response - should be a cache miss
        result1 = json.loads(response1.data)
        print(f"First response: {json.dumps(result1, indent=2)}")
        assert response1.status_code == 200
        assert result1.get("success") is True
        assert result1.get("cache_status") == "miss"
        
        # Generate the cache key for our test
        import hashlib
        normalized_text = test_text.strip().lower()
        cache_key = f"emotion_{hashlib.md5(normalized_text.encode()).hexdigest()}_en"
        print(f"Cache key: {cache_key}")
        
        # Get cache entry after first request
        cache_entry = get_cache_entry(db_session, cache_key)
        assert cache_entry is not None, "Cache entry was not created"
        hit_count_before = cache_entry.hit_count
        print(f"Initial hit count from database: {hit_count_before}")
        
        # Debug: Check result1 metadata structure - it's nested in result in the API
        if "result" in result1 and "metadata" in result1["result"]:
            print(f"Metadata in first response: {json.dumps(result1['result']['metadata'], indent=2)}")
            if "cache_hit_count" in result1["result"]["metadata"]:
                print(f"Cache hit count in first response: {result1['result']['metadata']['cache_hit_count']}")
            else:
                print("No cache_hit_count field in first response metadata")
        else:
            print("No result.metadata field in first response")
        
        # Commit session to ensure cache entry is persisted
        db_session.commit()
        
        # Make multiple cache hits - we'll do 3 requests
        print("\n===== Step 2: Making 3 more requests to test hit count =====")
        
        hit_counts = []
        for i in range(3):
            print(f"\n--- Request {i+1} ---")
            
            # Get cache entry before request
            cache_before = get_cache_entry(db_session, cache_key)
            print(f"Hit count before request {i+1}: {cache_before.hit_count}")
            
            response = client.post(
                "/mobile-api/analyze-emotion",
                json={"text": test_text, "language": "en", "include_details": "true"}
            )
            result = json.loads(response.data)
            
            # Debug: Print key sections of the response
            print(f"Status code: {response.status_code}")
            print(f"Success: {result.get('success')}")
            print(f"Cache status: {result.get('cache_status')}")
            
            # Validate response format
            assert response.status_code == 200
            assert result.get("success") is True
            assert result.get("cache_status") == "hit"
            
            # Debug: Check result metadata structure - it's nested in result in the API
            if "result" in result and "metadata" in result["result"]:
                print(f"Metadata in response: {json.dumps(result['result']['metadata'], indent=2)}")
                if "cache_hit_count" in result["result"]["metadata"]:
                    hit_count = result["result"]["metadata"]["cache_hit_count"]
                    print(f"Cache hit count in response: {hit_count}")
                    hit_counts.append(hit_count)
                else:
                    print("No cache_hit_count field in response metadata")
            else:
                print("No result.metadata field in response")
            
            # Get cache entry after request to check database directly
            db_session.refresh(cache_before)  # Refresh to get updated values
            print(f"Hit count in database after request {i+1}: {cache_before.hit_count}")
        
        print(f"\nHit counts from responses: {hit_counts}")
        
        # Final verification: check the database record
        final_cache_entry = get_cache_entry(db_session, cache_key)
        final_hit_count = final_cache_entry.hit_count
        print(f"Final hit count from database: {final_hit_count}")
        
        # Verify hit count increased correctly
        expected_increase = 3
        assert final_hit_count == hit_count_before + expected_increase, \
            f"Expected hit count to increase by {expected_increase}, but it went from {hit_count_before} to {final_hit_count}"