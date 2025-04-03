#!/usr/bin/env python3
"""
Test script for validating server connectivity and CORS configuration

This script performs a series of tests against various endpoints to verify 
that the server is accessible and properly configured for CORS.

Usage:
    python test_server_connectivity.py [base_url]
    - If base_url is not provided, defaults to http://localhost:5000
"""

import sys
import json
import time
import requests
from datetime import datetime

def format_headers(headers):
    """Format headers for display in a more readable way"""
    return "\n".join([f"  {k}: {v}" for k, v in headers.items()])

def test_endpoint(session, url, origin=None, method="GET", data=None, description=None):
    """Test a specific endpoint with detailed logging"""
    print(f"\n{'=' * 50}")
    print(f"Testing: {url}")
    if description:
        print(f"Description: {description}")
    print(f"Method: {method}")
    print(f"Origin: {origin or 'Not specified'}")
    print(f"Time: {datetime.now().isoformat()}")
    
    # Set request headers
    headers = {}
    if origin:
        headers["Origin"] = origin
    
    # Record start time
    start_time = time.time()
    
    try:
        # Make the request
        if method.upper() == "GET":
            response = session.get(url, headers=headers, timeout=5)
        elif method.upper() == "POST":
            response = session.post(url, headers=headers, json=data, timeout=5)
        elif method.upper() == "OPTIONS":
            response = session.options(url, headers=headers, timeout=5)
        else:
            print(f"Error: Unsupported method {method}")
            return
        
        # Calculate duration
        duration = (time.time() - start_time) * 1000
        
        # Print results
        print(f"\nResponse Status: {response.status_code} {response.reason}")
        print(f"Response Time: {duration:.2f}ms")
        print("\nResponse Headers:")
        print(format_headers(response.headers))
        
        # Print CORS-specific headers if present
        cors_headers = [h for h in response.headers.keys() if h.lower().startswith("access-control")]
        if cors_headers:
            print("\nCORS Headers:")
            for header in cors_headers:
                print(f"  {header}: {response.headers[header]}")
        
        # Print response content
        content_type = response.headers.get("Content-Type", "")
        print("\nResponse Content:")
        if "application/json" in content_type:
            try:
                json_content = response.json()
                print(json.dumps(json_content, indent=2))
            except:
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        else:
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        
        # Evaluate CORS compliance
        if origin:
            acao = response.headers.get("Access-Control-Allow-Origin")
            if acao:
                if acao == "*" or acao == origin:
                    print("\n✅ CORS: Access-Control-Allow-Origin is properly set.")
                else:
                    print(f"\n❌ CORS: Access-Control-Allow-Origin is '{acao}' but expected '{origin}' or '*'.")
            else:
                print("\n❌ CORS: Access-Control-Allow-Origin header is missing.")
        
        return response
    
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        return None

def run_tests(base_url):
    """Run a series of connectivity and CORS tests"""
    print(f"Testing server at {base_url}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    # Create a session for connection reuse
    session = requests.Session()
    
    # Test regular endpoints
    test_endpoint(session, f"{base_url}/api/status", description="Regular API status endpoint")
    test_endpoint(session, f"{base_url}/api/ping", description="Simple ping endpoint")
    
    # Test minimal endpoints
    test_endpoint(session, f"{base_url}/api/minimal", description="Minimal endpoint with plain text response")
    test_endpoint(session, f"{base_url}/feedback-tool-endpoint", description="Special endpoint for feedback tool")
    
    # Test CORS with specific origins
    feedback_tool_origin = "https://b846eda6-3902-424b-86a3-00b49b2e7d19-00-m9cxfx7bc3dj.worf.replit.dev"
    test_endpoint(session, f"{base_url}/api/feedback-tool-status", origin=feedback_tool_origin, 
                 description="Feedback tool status endpoint with specific origin")
    
    # Test with OPTIONS method (preflight)
    test_endpoint(session, f"{base_url}/api/feedback-tool-status", origin=feedback_tool_origin, 
                 method="OPTIONS", description="Preflight request to feedback tool status endpoint")
    
    print("\nTests completed!")

if __name__ == "__main__":
    # Use command line argument as base URL if provided, otherwise use default
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    run_tests(base_url)