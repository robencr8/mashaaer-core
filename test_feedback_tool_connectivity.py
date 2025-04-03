"""
Test script for verifying feedback tool connectivity

This script performs a series of tests against various endpoints to verify 
that they are accessible and properly configured for use with the web application feedback tool.
"""

import argparse
import json
import requests
import sys
import time

def format_headers(headers):
    """Format headers for display in a more readable way"""
    return '\n'.join([f"    {k}: {v}" for k, v in headers.items()])

def test_endpoint(session, url, origin=None, method="GET", data=None, description=None):
    """Test a specific endpoint with detailed logging"""
    headers = {}
    if origin:
        headers['Origin'] = origin
    
    if data and isinstance(data, dict):
        headers['Content-Type'] = 'application/json'
    
    print(f"\n{'=' * 50}")
    if description:
        print(f"{description}")
    print(f"Testing {method} {url}")
    if origin:
        print(f"With Origin: {origin}")
    
    start_time = time.time()
    
    try:
        if method.upper() == "GET":
            response = session.get(url, headers=headers, timeout=5)
        elif method.upper() == "POST":
            response = session.post(url, headers=headers, json=data, timeout=5)
        elif method.upper() == "OPTIONS":
            response = session.options(url, headers=headers, timeout=5)
        else:
            print(f"Unsupported method: {method}")
            return False
        
        elapsed = time.time() - start_time
        print(f"Response time: {elapsed:.2f}s")
        print(f"Status: {response.status_code} {response.reason}")
        
        print("\nResponse Headers:")
        print(format_headers(response.headers))
        
        # Check for CORS headers
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        print(f"\nCORS Check: Access-Control-Allow-Origin: {cors_origin}")
        
        if cors_origin == '*' or (origin and cors_origin == origin):
            print("✅ CORS Origin header is properly configured")
        elif cors_origin:
            print(f"⚠️ CORS Origin set but might be restrictive: {cors_origin}")
        else:
            print("❌ Missing CORS Origin header")
            
        # Check content 
        try:
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type.lower():
                print(f"\nJSON Response (first 500 chars):")
                json_response = response.json()
                formatted_json = json.dumps(json_response, indent=2)
                print(formatted_json[:500] + ('...' if len(formatted_json) > 500 else ''))
            elif 'text/plain' in content_type.lower() or 'text/html' in content_type.lower():
                print(f"\nResponse Content (first 500 chars):")
                content = response.text
                print(content[:500] + ('...' if len(content) > 500 else ''))
        except:
            print("\nFailed to parse response content")
            
        return response.status_code < 400
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to server")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout: Server did not respond within timeout period")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def run_tests(base_url):
    """Run a series of connectivity and CORS tests"""
    session = requests.Session()
    
    # Test basic health endpoint
    test_endpoint(
        session, 
        f"{base_url}/health", 
        description="1. Basic health check"
    )
    
    # Test minimal endpoint
    test_endpoint(
        session, 
        f"{base_url}/api/minimal", 
        description="2. Minimal API endpoint"
    )
    
    # Test ping endpoint
    test_endpoint(
        session, 
        f"{base_url}/api/ping", 
        description="3. API ping endpoint"
    )
    
    # Test with explicit origin
    test_endpoint(
        session, 
        f"{base_url}/api/ping", 
        origin="https://example.com",
        description="4. API ping with explicit origin"
    )
    
    # Test OPTIONS preflight
    test_endpoint(
        session, 
        f"{base_url}/api/ping", 
        method="OPTIONS",
        origin="https://example.com",
        description="5. OPTIONS preflight request"
    )
    
    # Test feedback tool specific endpoint
    test_endpoint(
        session, 
        f"{base_url}/feedback-tool-endpoint", 
        origin="https://example.com",
        description="6. Feedback tool specific endpoint"
    )
    
    # Test status endpoint
    test_endpoint(
        session, 
        f"{base_url}/api/status", 
        description="7. API status endpoint"
    )
    
    # Test debug-request endpoint
    test_endpoint(
        session, 
        f"{base_url}/api/debug-request", 
        description="8. API debug endpoint"
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test server connectivity and CORS configuration")
    parser.add_argument("base_url", nargs="?", default="http://localhost:5000", 
                        help="Base URL of the server to test (default: http://localhost:5000)")
    args = parser.parse_args()
    
    print(f"Testing connectivity to {args.base_url}")
    run_tests(args.base_url)
    print("\nConnectivity testing complete.")