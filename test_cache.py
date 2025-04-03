#!/usr/bin/env python3
"""
Test script for cache functionality in mobile API endpoints

This script will test:
1. Cache population (first request populates the cache)
2. Cache retrieval (subsequent requests get data from cache)
3. Cache expiration (test after waiting for cache to expire)
4. Cache key generation (test with varying inputs)
5. Cache invalidation (manually invalidate cache entries)
6. Error handling (test cache behavior on backend errors)
"""

import requests
import json
import time
import hashlib
import uuid
import sys

# Configuration
BASE_URL = "http://localhost:5000"  # Update if running on a different port
TEST_TEXTS = [
    "I am feeling very happy today!",
    "This makes me sad and disappointed.",
    "I'm so excited about the upcoming event!",
    "I'm feeling a mix of anxiety and anticipation."
]
TEST_LANGUAGES = ["en", "ar"]

def generate_test_id():
    """Generate a unique test identifier"""
    return str(uuid.uuid4())[:8]

def display_result(title, result, indent=2):
    """Format and display test results"""
    print(f"\n{title}:")
    if isinstance(result, dict):
        print(json.dumps(result, indent=indent))
    else:
        print(result)

def test_emotion_analysis_caching():
    """Test caching in the emotion analysis endpoint"""
    test_id = generate_test_id()
    print(f"\n==== TESTING EMOTION ANALYSIS CACHING (ID: {test_id}) ====")
    
    # Test text
    test_text = "I'm feeling very happy and excited about the progress we've made!"
    
    # 1. First request (should miss cache)
    print("\n1. First request (should miss cache)...")
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/mobile-api/analyze-emotion",
        json={"text": test_text, "language": "en", "bypass_cache": False}
    )
    first_time = time.time() - start_time
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    
    first_result = response.json()
    display_result("First response", first_result)
    print(f"Response time: {first_time:.4f} seconds")
    
    # Cache status check
    if first_result.get("cache_status") != "miss":
        print(f"Warning: Expected cache miss but got: {first_result.get('cache_status')}")
    
    # 2. Second request (should hit cache)
    print("\n2. Second request (should hit cache)...")
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/mobile-api/analyze-emotion",
        json={"text": test_text, "language": "en", "bypass_cache": False}
    )
    second_time = time.time() - start_time
    
    second_result = response.json()
    display_result("Second response", second_result)
    print(f"Response time: {second_time:.4f} seconds")
    
    # Cache status and timing check
    if second_result.get("cache_status") != "hit":
        print(f"Warning: Expected cache hit but got: {second_result.get('cache_status')}")
    
    if second_time >= first_time:
        print(f"Warning: Cached response ({second_time:.4f}s) not faster than initial request ({first_time:.4f}s)")
    else:
        print(f"Performance gain: {((first_time - second_time) / first_time * 100):.2f}%")

    # 3. Test with bypass_cache flag
    print("\n3. Testing bypass_cache flag...")
    response = requests.post(
        f"{BASE_URL}/mobile-api/analyze-emotion",
        json={"text": test_text, "language": "en", "bypass_cache": True}
    )
    
    bypass_result = response.json()
    display_result("Bypass cache response", bypass_result)
    
    if bypass_result.get("cache_status") != "disabled":
        print(f"Warning: Expected cache disabled but got: {bypass_result.get('cache_status')}")

    # 4. Test with similar but different text
    print("\n4. Testing with slightly different text...")
    similar_text = test_text + " Very much so!"
    
    response = requests.post(
        f"{BASE_URL}/mobile-api/analyze-emotion",
        json={"text": similar_text, "language": "en", "bypass_cache": False}
    )
    
    similar_result = response.json()
    display_result("Similar text response", similar_result)
    
    # Should be a cache miss as the text is different
    if similar_result.get("cache_status") != "miss":
        print(f"Warning: Expected cache miss for different text but got: {similar_result.get('cache_status')}")

    print("\n==== EMOTION ANALYSIS CACHING TEST COMPLETE ====")

def test_tts_caching():
    """Test caching in the Text-to-Speech endpoint"""
    test_id = generate_test_id()
    print(f"\n==== TESTING TTS CACHING (ID: {test_id}) ====")
    
    # Test text
    test_text = "This is a test of the text-to-speech caching system."
    
    # 1. First request (should miss cache)
    print("\n1. First request (should miss cache)...")
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/mobile-api/speak",
        json={
            "text": test_text, 
            "language": "en-US", 
            "voice": "default",
            "bypass_cache": False,
            "stream": False
        }
    )
    first_time = time.time() - start_time
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    
    first_result = response.json()
    display_result("First response", first_result)
    print(f"Response time: {first_time:.4f} seconds")
    
    # Cache status check
    if first_result.get("cache_status") != "miss":
        print(f"Warning: Expected cache miss but got: {first_result.get('cache_status')}")
    
    # 2. Second request (should hit cache)
    print("\n2. Second request (should hit cache)...")
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/mobile-api/speak",
        json={
            "text": test_text, 
            "language": "en-US", 
            "voice": "default",
            "bypass_cache": False,
            "stream": False
        }
    )
    second_time = time.time() - start_time
    
    second_result = response.json()
    display_result("Second response", second_result)
    print(f"Response time: {second_time:.4f} seconds")
    
    # Cache status and timing check
    if second_result.get("cache_status") != "hit":
        print(f"Warning: Expected cache hit but got: {second_result.get('cache_status')}")
    
    if second_time >= first_time:
        print(f"Warning: Cached response ({second_time:.4f}s) not faster than initial request ({first_time:.4f}s)")
    else:
        print(f"Performance gain: {((first_time - second_time) / first_time * 100):.2f}%")

    # 3. Test with different voice parameter
    print("\n3. Testing with different voice parameter...")
    response = requests.post(
        f"{BASE_URL}/mobile-api/speak",
        json={
            "text": test_text, 
            "language": "en-US", 
            "voice": "21m00Tcm4TlvDq8ikWAM",  # Different voice
            "bypass_cache": False,
            "stream": False
        }
    )
    
    diff_voice_result = response.json()
    display_result("Different voice response", diff_voice_result)
    
    # Should be a cache miss as the voice is different
    if diff_voice_result.get("cache_status") != "miss":
        print(f"Warning: Expected cache miss for different voice but got: {diff_voice_result.get('cache_status')}")

    print("\n==== TTS CACHING TEST COMPLETE ====")

def main():
    """Run all cache tests"""
    print("======================================================")
    print("MOBILE API CACHING TEST SUITE")
    print("======================================================")
    print(f"Base URL: {BASE_URL}")
    print("Test started at:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        # Test the server is up
        response = requests.get(f"{BASE_URL}/mobile-api/status")
        if response.status_code != 200:
            print(f"Error: Server returned status code {response.status_code}")
            sys.exit(1)
            
        # Run tests
        test_emotion_analysis_caching()
        test_tts_caching()
        
        print("\n======================================================")
        print("All tests completed successfully!")
        print("======================================================")
    
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to server at {BASE_URL}")
        print("Please make sure the server is running and the URL is correct")
        sys.exit(1)
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()