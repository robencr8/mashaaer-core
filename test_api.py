"""
Test script for the Mashaaer API routes with RobinDecisionEngine integration
"""
import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API endpoint
API_URL = "http://localhost:5000/api/chat"

def test_sad_emotion():
    """Test the sad emotion with 'alone' keyword"""
    payload = {
        "message": "I feel alone today",
        "emotion": "sad",
        "user_id": "test_user",
        "lang": "en"
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Response for 'sad' emotion: {json.dumps(data, indent=2)}")
        
        # Verify the response structure
        assert "reply" in data, "Response should contain a 'reply' field"
        assert "action" in data, "Response should contain an 'action' field"
        assert "cosmic_soundscape" in data, "Response should contain a 'cosmic_soundscape' field"
        assert "detected_emotion" in data, "Response should contain a 'detected_emotion' field"
        
        # Verify the action is correct
        assert data["action"] == "offer_companionship", f"Expected action 'offer_companionship', got '{data['action']}'"
        
        # Verify the cosmic soundscape
        assert data["cosmic_soundscape"]["emotion"] == "sad", "Cosmic soundscape emotion should be 'sad'"
        assert data["cosmic_soundscape"]["track"] == "sad_cosmic.mp3", "Cosmic soundscape track should be 'sad_cosmic.mp3'"
        
        logger.info("✅ Test for 'sad' emotion passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test for 'sad' emotion failed: {str(e)}")
        return False

def test_happy_music():
    """Test the happy emotion with 'music' keyword"""
    payload = {
        "message": "I want to listen to some music",
        "emotion": "happy",
        "user_id": "test_user",
        "lang": "en"
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Response for 'happy music': {json.dumps(data, indent=2)}")
        
        # Verify the response structure
        assert "reply" in data, "Response should contain a 'reply' field"
        assert "action" in data, "Response should contain an 'action' field"
        assert "cosmic_soundscape" in data, "Response should contain a 'cosmic_soundscape' field"
        assert "detected_emotion" in data, "Response should contain a 'detected_emotion' field"
        assert "song" in data, "Response should contain a 'song' field for 'play_music' action"
        
        # Verify the action is correct
        assert data["action"] == "play_music", f"Expected action 'play_music', got '{data['action']}'"
        
        # Verify the cosmic soundscape
        assert data["cosmic_soundscape"]["emotion"] == "happy", "Cosmic soundscape emotion should be 'happy'"
        assert data["cosmic_soundscape"]["track"] == "happy_cosmic.mp3", "Cosmic soundscape track should be 'happy_cosmic.mp3'"
        
        logger.info("✅ Test for 'happy music' passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test for 'happy music' failed: {str(e)}")
        return False

def test_weather():
    """Test the neutral emotion with 'weather' keyword"""
    payload = {
        "message": "Could you check the weather today?",
        "emotion": "neutral",
        "user_id": "test_user",
        "lang": "en"
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Response for 'weather': {json.dumps(data, indent=2)}")
        
        # Verify the response structure
        assert "reply" in data, "Response should contain a 'reply' field"
        assert "action" in data, "Response should contain an 'action' field"
        assert "cosmic_soundscape" in data, "Response should contain a 'cosmic_soundscape' field"
        assert "detected_emotion" in data, "Response should contain a 'detected_emotion' field"
        
        # Verify the action is correct
        assert data["action"] == "fetch_weather", f"Expected action 'fetch_weather', got '{data['action']}'"
        
        # Verify the cosmic soundscape
        assert data["cosmic_soundscape"]["emotion"] == "neutral", "Cosmic soundscape emotion should be 'neutral'"
        assert data["cosmic_soundscape"]["track"] == "neutral_cosmic.mp3", "Cosmic soundscape track should be 'neutral_cosmic.mp3'"
        
        logger.info("✅ Test for 'weather' passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test for 'weather' failed: {str(e)}")
        return False

def test_arabic():
    """Test the Arabic language support"""
    payload = {
        "message": "أشعر بالوحدة",
        "emotion": "sad",
        "user_id": "test_user_arabic",
        "lang": "ar"
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Response for Arabic: {json.dumps(data, indent=2)}")
        
        # Verify the response structure
        assert "reply" in data, "Response should contain a 'reply' field"
        assert "action" in data, "Response should contain an 'action' field"
        assert "cosmic_soundscape" in data, "Response should contain a 'cosmic_soundscape' field"
        assert "detected_emotion" in data, "Response should contain a 'detected_emotion' field"
        
        logger.info("✅ Test for Arabic language passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test for Arabic language failed: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Testing Mashaaer API routes with RobinDecisionEngine integration...")
    
    # Run all tests
    tests = [
        ("Sad emotion test", test_sad_emotion),
        ("Happy music test", test_happy_music),
        ("Weather test", test_weather),
        ("Arabic language test", test_arabic)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\nRunning test: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    # Print summary
    logger.info("\n===== TEST SUMMARY =====")
    success_count = sum(1 for _, result in results if result)
    logger.info(f"Passed: {success_count}/{len(results)} tests")
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")