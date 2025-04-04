#!/usr/bin/env python3
"""
TTS Endpoint Testing Script
This script tests both the web API and mobile API TTS endpoints.
"""

import requests
import os
import json
import time

def test_tts_endpoint(endpoint, text="This is a test message for the text-to-speech system.", language="en"):
    """Test a TTS endpoint and report the results"""
    print(f"\n=== Testing {endpoint} ===")
    print(f"Sending request with text: '{text}' (language: {language})")
    
    # Start timer
    start_time = time.time()
    
    # Send request to TTS endpoint
    response = requests.post(
        f"http://localhost:5000{endpoint}",
        json={"text": text, "language": language}
    )
    
    # End timer
    elapsed_time = time.time() - start_time
    
    # Print response status
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response received in {elapsed_time:.2f} seconds")
            
            # Print success status
            if data.get('success'):
                print("✅ TTS generation successful")
                
                # Print audio details
                print(f"Audio path: {data.get('audio_path')}")
                print(f"Voice: {data.get('voice', 'Not specified')}")
                print(f"Language: {data.get('language', 'Not specified')}")
                
                # Print cache status if available
                if 'cache_status' in data:
                    print(f"Cache status: {data.get('cache_status')}")
                
                # Check if the audio file exists
                audio_path = data.get('audio_path', '').lstrip('/')
                if os.path.exists(audio_path):
                    audio_size = os.path.getsize(audio_path)
                    print(f"Audio file exists: {audio_path} (Size: {audio_size} bytes)")
                else:
                    print(f"❌ Audio file not found: {audio_path}")
                
                # Print processing time if available
                if 'processing_time_ms' in data:
                    print(f"Processing time: {data.get('processing_time_ms')} ms")
            else:
                print(f"❌ TTS generation failed: {data.get('error', 'Unknown error')}")
            
            # Print full response for debugging
            print(f"Full response: {json.dumps(data, indent=2)}")
        except Exception as e:
            print(f"❌ Error parsing response: {e}")
            print(f"Raw response: {response.text}")
    else:
        print(f"❌ Request failed with status code {response.status_code}")
        print(f"Error response: {response.text}")

if __name__ == "__main__":
    print("==== TTS Endpoint Testing ====")
    
    # Test web API endpoint
    test_tts_endpoint("/api/speak")
    
    # Test mobile API endpoint
    test_tts_endpoint("/mobile-api/speak")
    
    # Test with Arabic text
    print("\n==== Testing with Arabic text ====")
    arabic_text = "مرحبًا بك في مشاعر. اصنع المستقبل، أنا أسمعك."
    
    test_tts_endpoint("/api/speak", text=arabic_text, language="ar")
    test_tts_endpoint("/mobile-api/speak", text=arabic_text, language="ar")
    
    print("\n==== Testing Complete ====")
