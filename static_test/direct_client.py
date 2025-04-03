#!/usr/bin/env python3
"""
Direct HTTP client to test Mashaaer server connectivity
without browser CORS or security restrictions.

This tool helps diagnose connectivity issues by using
standard Python HTTP libraries to contact the server.
"""

import sys
import json
import argparse
import http.client
import urllib.parse
from datetime import datetime


def main():
    """Main function to run HTTP client tests."""
    parser = argparse.ArgumentParser(
        description="Test HTTP connectivity to Mashaaer server"
    )
    parser.add_argument(
        "--host", 
        default="localhost",
        help="Host to connect to (default: localhost)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=5000,
        help="Port to connect to (default: 5000)"
    )
    parser.add_argument(
        "--endpoint", 
        default="/api/status",
        help="Endpoint to test (default: /api/status)"
    )
    parser.add_argument(
        "--method", 
        default="GET",
        choices=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        help="HTTP method to use (default: GET)"
    )
    parser.add_argument(
        "--verbose", 
        "-v", 
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    print(f"📡 Testing connection to {args.host}:{args.port}{args.endpoint}")
    print(f"🔍 Using HTTP method: {args.method}")
    
    start_time = datetime.now()
    
    conn = None
    try:
        # Create connection
        conn = http.client.HTTPConnection(args.host, args.port, timeout=10)
        
        # Add headers
        headers = {
            "User-Agent": "Mashaaer-Direct-Test/1.0",
            "Accept": "application/json",
            "X-Test-Client": "Direct-Python-Client",
        }
        
        if args.verbose:
            print(f"🔌 Connecting to {args.host}:{args.port}...")
        
        # Send request
        conn.request(args.method, args.endpoint, headers=headers)
        
        # Get response
        response = conn.getresponse()
        status = response.status
        reason = response.reason
        
        # Read response data
        data = response.read().decode('utf-8')
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        print(f"⏱️  Response time: {duration:.2f}ms")
        print(f"📊 Status: {status} {reason}")
        
        # Print headers if verbose
        if args.verbose:
            print("\n📋 Response Headers:")
            for header, value in response.getheaders():
                print(f"    {header}: {value}")
        
        # Print data
        print("\n📄 Response Body:")
        
        # Try to parse and pretty-print JSON
        try:
            json_data = json.loads(data)
            print(json.dumps(json_data, indent=2))
        except json.JSONDecodeError:
            # If not JSON, print raw data
            print(data)
            
        # Check specifically for CORS headers
        print("\n🔒 CORS Headers Check:")
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Credentials",
            "Access-Control-Max-Age"
        ]
        
        found_cors = False
        for header in cors_headers:
            value = response.getheader(header)
            if value:
                found_cors = True
                print(f"    ✅ {header}: {value}")
            else:
                print(f"    ❌ {header}: <not present>")
                
        if not found_cors:
            print("    ⚠️  No CORS headers detected in response!")

        # Check for successful response
        if 200 <= status < 300:
            print("\n✅ Test SUCCESSFUL!")
        else:
            print(f"\n❌ Test FAILED with status code: {status}")
            
    except ConnectionRefusedError:
        print("\n❌ Connection REFUSED")
        print(f"   Could not connect to {args.host}:{args.port}")
        print("   Ensure the server is running and the port is correct.")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1
    finally:
        if conn:
            conn.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())