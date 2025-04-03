"""
Server Connectivity Test Script for Mashaaer API

This script provides a simple way to verify server connectivity
by testing multiple endpoints and displaying detailed results.
"""

import requests
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"  # Local development server
TIMEOUT = 5  # seconds
TEST_ENDPOINTS = [
    "/",
    "/test",
    "/api/minimal",
    "/api/status",
    "/api/ping",
    "/api/test-cors"
]

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)

def get_timestamp():
    """Get current timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def test_endpoint(url, method="GET", data=None, headers=None):
    """Test a specific endpoint and return results."""
    if headers is None:
        headers = {"Origin": "http://localhost"}
    
    start_time = time.time()
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
        else:
            return {
                "success": False,
                "status_code": None,
                "message": f"Unsupported method: {method}",
                "response_time": 0,
                "headers": None,
                "content": None
            }
        
        response_time = time.time() - start_time
        
        # Try to parse JSON, but don't fail if it's not JSON
        try:
            content = response.json()
            content_type = "json"
        except json.JSONDecodeError:
            content = response.text
            content_type = "text"
            
        return {
            "success": 200 <= response.status_code < 300,
            "status_code": response.status_code,
            "message": "OK" if 200 <= response.status_code < 300 else f"HTTP {response.status_code}",
            "response_time": response_time,
            "headers": dict(response.headers),
            "content": content,
            "content_type": content_type
        }
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        return {
            "success": False,
            "status_code": None,
            "message": "Request timed out",
            "response_time": response_time,
            "headers": None,
            "content": None,
            "content_type": None
        }
    except requests.exceptions.ConnectionError:
        response_time = time.time() - start_time
        return {
            "success": False,
            "status_code": None,
            "message": "Connection error",
            "response_time": response_time,
            "headers": None,
            "content": None,
            "content_type": None
        }
    except Exception as e:
        response_time = time.time() - start_time
        return {
            "success": False,
            "status_code": None,
            "message": f"Error: {str(e)}",
            "response_time": response_time,
            "headers": None,
            "content": None,
            "content_type": None
        }

def run_server_tests():
    """Run all server connectivity tests."""
    print_header(f"MASHAAER SERVER CONNECTIVITY TEST - {get_timestamp()}")
    print(f"Base URL: {BASE_URL}")
    print(f"Timeout: {TIMEOUT} seconds")
    
    # Test results summary
    results = {
        "total": len(TEST_ENDPOINTS),
        "success": 0,
        "failed": 0,
        "total_time": 0
    }
    
    for endpoint in TEST_ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"
        
        print(f"\n> Testing endpoint: {endpoint}")
        print(f"  URL: {url}")
        
        # Test GET request
        print("  Method: GET")
        result = test_endpoint(url)
        results["total_time"] += result["response_time"]
        
        if result["success"]:
            results["success"] += 1
            print(f"  ✅ Success: HTTP {result['status_code']} ({result['response_time']:.2f}s)")
        else:
            results["failed"] += 1
            print(f"  ❌ Failed: {result['message']} ({result['response_time']:.2f}s)")
        
        # Show response headers related to CORS
        if result["headers"]:
            cors_headers = {k: v for k, v in result["headers"].items() if "access-control" in k.lower()}
            if cors_headers:
                print("\n  CORS Headers:")
                for name, value in cors_headers.items():
                    print(f"  - {name}: {value}")
        
        # Show response content (truncated if too long)
        if result["content"]:
            print("\n  Response Content:")
            if result["content_type"] == "json":
                content_str = json.dumps(result["content"], indent=2)
                if len(content_str) > 500:
                    content_str = content_str[:500] + "... [truncated]"
                print(f"  {content_str}")
            else:
                content_str = str(result["content"])
                if len(content_str) > 500:
                    content_str = content_str[:500] + "... [truncated]"
                print(f"  {content_str}")
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"Total endpoints tested: {results['total']}")
    print(f"Successful tests: {results['success']}")
    print(f"Failed tests: {results['failed']}")
    print(f"Success rate: {results['success'] / results['total'] * 100:.1f}%")
    print(f"Total response time: {results['total_time']:.2f} seconds")
    
    return results["failed"] == 0

if __name__ == "__main__":
    success = run_server_tests()
    sys.exit(0 if success else 1)