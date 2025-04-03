"""
Test script to verify CORS configuration with the new secret.
"""
import os
import requests
import json

def test_cors_config():
    """Test CORS configuration with the feedback tool origin."""
    print("Testing CORS configuration with FEEDBACK_TOOL_ORIGIN secret...")
    
    # Get the value of FEEDBACK_TOOL_ORIGIN
    feedback_tool_origin = os.environ.get('FEEDBACK_TOOL_ORIGIN')
    print(f"FEEDBACK_TOOL_ORIGIN = {feedback_tool_origin}")
    
    # Test a simple GET request to our API with the Origin header
    url = "http://localhost:5000/api/minimal"
    
    headers = {
        "Origin": feedback_tool_origin
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {json.dumps(dict(response.headers), indent=2)}")
        
        # Check for CORS headers
        if 'Access-Control-Allow-Origin' in response.headers:
            print(f"\nCORS Origin: {response.headers['Access-Control-Allow-Origin']}")
            if response.headers['Access-Control-Allow-Origin'] == feedback_tool_origin:
                print("✅ Success! The server is correctly using the FEEDBACK_TOOL_ORIGIN value")
            else:
                print("❌ The Access-Control-Allow-Origin header does not match FEEDBACK_TOOL_ORIGIN")
        else:
            print("❌ No Access-Control-Allow-Origin header in the response")
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to server: {e}")

if __name__ == "__main__":
    test_cors_config()
