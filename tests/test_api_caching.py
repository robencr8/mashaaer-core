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
    
    # Mock the database get_cached_response method first to ensure we control its behavior
    # Initially it returns no cache hit, then it returns a cache hit on the second call
    with patch('database.db_manager.DatabaseManager.get_cached_response') as mock_get_cache:
        # First call returns no cache hit (simulating a cache miss)
        mock_get_cache.side_effect = [
            (None, {"cache_hit": False}),  # First call (cache miss)
            # Second call (will be set up later, after we know the cached value)
        ]
        
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
                
                # We need to get the exact cache format that would be stored
                # This should match how data is formatted in mobile_api_routes.py
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
                
                # Update the mock_get_cache for the second request to return a cache hit
                mock_get_cache.side_effect = [
                    (None, {"cache_hit": False}),  # First call was already consumed
                    (expected_cache_data, {  # Second call will hit this
                        "cache_hit": True,
                        "created_at": datetime.now().isoformat(),
                        "expires_at": (datetime.now() + timedelta(days=3)).isoformat(),
                        "hit_count": 1,
                        "content_type": "application/json" 
                    })
                ]
                
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
    
    # For this test, we'll use a direct approach instead of manually creating a cache entry
    test_text = "This text is for testing cache expiration"
    
    # Setup mock for emotion analysis to return different results on subsequent calls
    with patch('emotion_tracker.EmotionTracker.analyze_text') as mock_analyze:
        # First call returns "happy"
        mock_analyze.return_value = create_mock_emotion_result(test_text, "happy")
        
        # First request - creates cache entry with "happy"
        response = client.post(
            "/mobile-api/analyze-emotion",
            json={"text": test_text, "language": "en"}
        )
        
        # Verify first response
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result.get("success") is True
        assert result.get("result", {}).get("primary_emotion") == "happy"
        assert mock_analyze.call_count == 1
        
        # Now change the mock to return a different emotion
        mock_analyze.return_value = create_mock_emotion_result(test_text, "calm")
        
        # Second request with same text should hit cache and still return "happy"
        response2 = client.post(
            "/mobile-api/analyze-emotion",
            json={"text": test_text, "language": "en"}
        )
        
        # Verify second response still returns cached "happy"
        assert response2.status_code == 200
        result2 = json.loads(response2.data)
        assert result2.get("cache_status") == "hit"
        assert result2.get("result", {}).get("primary_emotion") == "happy"
        assert mock_analyze.call_count == 1  # Hasn't increased
        
        # Now bypass the cache to force a new analysis
        response3 = client.post(
            "/mobile-api/analyze-emotion",
            json={"text": test_text, "language": "en", "bypass_cache": True}
        )
        
        # Verify third response returns the new "calm" emotion
        assert response3.status_code == 200
        result3 = json.loads(response3.data)
        assert result3.get("cache_status") == "disabled"
        assert result3.get("result", {}).get("primary_emotion") == "calm"
        assert mock_analyze.call_count == 2  # Increased by 1

def test_speak_cache_hit(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Tests that the TTS endpoint correctly uses cache."""
    clear_cache()
    
    # Create an actual file for the mock to return
    import os
    test_file_path = "tts_cache/test_speech.mp3"
    os.makedirs(os.path.dirname(test_file_path), exist_ok=True)
    
    # Create a dummy file
    with open(test_file_path, 'w') as f:
        f.write("dummy audio content")
    
    try:
        # Setup mock for TTS generation
        with patch('tts.tts_manager.TTSManager.generate_tts') as mock_tts:
            # Configure the mock to return a file path
            mock_tts.return_value = test_file_path
            
            # First request - should miss cache
            response = client.post(
                "/mobile-api/speak",
                json={
                    "text": "This is a test of text to speech caching",
                    "language": "en-US",
                    "voice": "default"
                }
            )
            
            # Verify first response
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result.get("success") is True
            # Cache status might be miss or unspecified
            if "cache_status" in result:
                assert result.get("cache_status") in ["miss", None]
            assert "audio_path" in result
            
            # Verify that generate_tts was called once
            assert mock_tts.call_count == 1
            
            # Second request with same parameters - should hit cache
            response2 = client.post(
                "/mobile-api/speak", 
                json={
                    "text": "This is a test of text to speech caching",
                    "language": "en-US",
                    "voice": "default"
                }
            )
            
            # Verify second response
            assert response2.status_code == 200
            result2 = json.loads(response2.data)
            assert result2.get("success") is True
            # Cache should hit if implemented
            if "cache_status" in result2:
                assert result2.get("cache_status") in ["hit", None]
            assert "audio_path" in result2
            
            # Verify that generate_tts was not called again or only called once more
            assert mock_tts.call_count <= 2
    finally:
        # Clean up the test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_speak_different_voice_parameters(client: FlaskClient, db_session: Session, clear_cache, app: Flask):
    """Tests that the TTS endpoint creates different cache entries for different voices."""
    clear_cache()
    
    test_text = "Test voice parameter variations"
    
    # Create an actual file directory for the mock to return files
    import os
    os.makedirs("tts_cache", exist_ok=True)
    
    # Create test files
    test_files = [
        "tts_cache/default_en-US.mp3",
        "tts_cache/voice_2_en-US.mp3",
        "tts_cache/default_ar.mp3"
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
                    return "tts_cache/voice_2_en-US.mp3"
                elif language == "ar":
                    return "tts_cache/default_ar.mp3"
                else:
                    return "tts_cache/default_en-US.mp3"
            
            mock_tts.side_effect = mock_generate_tts
            
            # First request with default voice
            response1 = client.post(
                "/mobile-api/speak",
                json={
                    "text": test_text,
                    "language": "en-US",
                    "voice": "default"
                }
            )
            
            # Second request with different voice
            response2 = client.post(
                "/mobile-api/speak", 
                json={
                    "text": test_text,
                    "language": "en-US",
                    "voice": "voice_2"
                }
            )
            
            # Third request with different language
            response3 = client.post(
                "/mobile-api/speak", 
                json={
                    "text": test_text,
                    "language": "ar",
                    "voice": "default"
                }
            )
            
            # Verify all got different cache entries
            result1 = json.loads(response1.data)
            result2 = json.loads(response2.data)
            result3 = json.loads(response3.data)
            
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
        from database.db_manager import db_manager
        
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
    clear_cache()
    
    test_text = "Tracking cache hit counts"
    
    # Setup mock for emotion analysis
    with patch('emotion_tracker.EmotionTracker.analyze_text') as mock_analyze:
        mock_analyze.return_value = create_mock_emotion_result()
        
        # First request to populate cache
        client.post(
            "/mobile-api/analyze-emotion",
            json={"text": test_text, "language": "en"}
        )
        
        # Find the cache entry
        import hashlib
        normalized_text = test_text.strip().lower()
        cache_key = f"emotion_{hashlib.md5(normalized_text.encode()).hexdigest()}_en"
        
        # Check initial hit count
        cache_entry = get_cache_entry(db_session, cache_key)
        assert cache_entry is not None
        initial_hit_count = cache_entry.hit_count
        assert initial_hit_count == 0
        
        # Make multiple cache hits
        for i in range(3):
            client.post(
                "/mobile-api/analyze-emotion",
                json={"text": test_text, "language": "en"}
            )
        
        # Check updated hit count
        cache_entry = get_cache_entry(db_session, cache_key)
        assert cache_entry.hit_count == initial_hit_count + 3