#!/usr/bin/env python3
"""
Simple script to check if the web server is accessible
"""
import requests
import sys
import time
import json

def check_endpoints():
    """Check multiple endpoints for accessibility"""
    base_url = "http://localhost:5000"
    endpoints = {
        "/": "Main page",
        "/health": "Health check endpoint",
        "/api/status": "API status endpoint",
        "/simple-test": "Test page"
    }
    
    results = {}
    all_successful = True
    
    print(f"Checking web server at {base_url}...")
    print("=" * 50)
    
    for endpoint, description in endpoints.items():
        url = f"{base_url}{endpoint}"
        try:
            print(f"Testing {description} ({url})...")
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            status = "SUCCESS"
            content = response.text[:100] + "..." if len(response.text) > 100 else response.text
            if response.headers.get('content-type', '').startswith('application/json'):
                content = json.dumps(response.json(), indent=2)
            
            results[endpoint] = {
                "status": status,
                "status_code": response.status_code,
                "content_type": response.headers.get('content-type'),
                "content_preview": content
            }
            print(f"  ✓ Status code: {response.status_code}")
            print(f"  ✓ Content type: {response.headers.get('content-type')}")
            print(f"  ✓ Content preview: {content[:100]}...")
        except requests.exceptions.RequestException as e:
            status = "FAILED"
            all_successful = False
            results[endpoint] = {
                "status": status,
                "error": str(e)
            }
            print(f"  ✗ Error: {e}")
        
        print("-" * 50)
    
    return all_successful, results

def main():
    """Main function"""
    # Wait a moment to ensure server is up
    time.sleep(1)
    
    # Check the endpoints
    success, results = check_endpoints()
    
    # Output summary
    print("\nSummary:")
    print("=" * 50)
    for endpoint, result in results.items():
        status_symbol = "✓" if result["status"] == "SUCCESS" else "✗"
        print(f"{status_symbol} {endpoint}: {result['status']}")
    
    # Exit with appropriate code
    if success:
        print("\nAll endpoints accessible!")
        return 0
    else:
        print("\nSome endpoints failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())