#!/usr/bin/env python3
"""
Comprehensive diagnostic tool for the Mashaaer Feelings application

This script runs a series of diagnostic tests to verify server connectivity,
endpoint functionality, and CORS configuration. It helps isolate issues with
the web application feedback tool and other connectivity problems.

Usage:
    python run_diagnostics.py

The script will:
1. Test basic server connectivity
2. Verify CORS configuration
3. Check all diagnostic endpoints
4. Run connectivity test scripts
5. Generate a diagnostic report
"""

import os
import sys
import time
import json
import logging
import subprocess
from datetime import datetime
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("diagnostics")

def print_header(title):
    """Print a formatted header for sections"""
    width = 80
    padding = (width - len(title) - 4) // 2
    print("\n" + "=" * width)
    print(" " * padding + f"[ {title} ]")
    print("=" * width + "\n")

def run_server_check(base_url="http://localhost:5000"):
    """Run basic server connectivity check"""
    print_header("SERVER CONNECTIVITY CHECK")
    
    try:
        # Check root endpoint
        start_time = time.time()
        response = requests.get(f"{base_url}/", timeout=5)
        elapsed = time.time() - start_time
        
        print(f"Root endpoint: {response.status_code} ({elapsed:.2f}s)")
        print(f"Content type: {response.headers.get('Content-Type', 'Not specified')}")
        
        # Check health endpoint
        start_time = time.time()
        response = requests.get(f"{base_url}/health", timeout=5)
        elapsed = time.time() - start_time
        
        print(f"Health endpoint: {response.status_code} ({elapsed:.2f}s)")
        print(f"Response: {response.text}")
        
        # Check API status
        start_time = time.time()
        response = requests.get(f"{base_url}/api/status", timeout=5)
        elapsed = time.time() - start_time
        
        print(f"API status: {response.status_code} ({elapsed:.2f}s)")
        if response.headers.get('Content-Type', '').startswith('application/json'):
            print(f"API response: {json.dumps(response.json(), indent=2)}")
        
        return True
    except requests.RequestException as e:
        print(f"Error connecting to server: {e}")
        return False

def check_cors_configuration(base_url="http://localhost:5000"):
    """Check CORS configuration on various endpoints"""
    print_header("CORS CONFIGURATION CHECK")
    
    test_endpoints = [
        "/health",
        "/api/ping",
        "/api/status",
        "/api/minimal",
        "/feedback-tool-endpoint"
    ]
    
    test_origins = [
        "https://example.com",
        "https://replit.com",
        None  # No origin header
    ]
    
    for endpoint in test_endpoints:
        print(f"\nEndpoint: {endpoint}")
        print("-" * 40)
        
        for origin in test_origins:
            headers = {}
            origin_display = origin if origin else "No Origin header"
            
            if origin:
                headers['Origin'] = origin
                
            try:
                # Regular GET request
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                cors_header = response.headers.get('Access-Control-Allow-Origin', 'Not set')
                
                print(f"Origin: {origin_display}")
                print(f"  Status: {response.status_code}")
                print(f"  CORS Access-Control-Allow-Origin: {cors_header}")
                
                # OPTIONS preflight
                response = requests.options(f"{base_url}{endpoint}", headers=headers, timeout=5)
                preflight_cors = response.headers.get('Access-Control-Allow-Origin', 'Not set')
                preflight_methods = response.headers.get('Access-Control-Allow-Methods', 'Not set')
                
                print(f"  OPTIONS Status: {response.status_code}")
                print(f"  OPTIONS CORS Origin: {preflight_cors}")
                print(f"  OPTIONS CORS Methods: {preflight_methods}")
                print("")
                
            except requests.RequestException as e:
                print(f"  Error: {e}")

def run_diagnostic_tools(base_url="http://localhost:5000"):
    """Run external diagnostic tools and scripts"""
    print_header("RUNNING DIAGNOSTIC TOOLS")
    
    scripts = [
        "test_server_connectivity.py",
        "test_feedback_tool_connectivity.py"
    ]
    
    for script in scripts:
        if os.path.exists(script):
            print(f"\nRunning {script}...")
            try:
                result = subprocess.run([sys.executable, script, base_url], 
                               capture_output=True, text=True)
                
                print(f"Exit code: {result.returncode}")
                if result.stdout:
                    print("\nStandard output:")
                    print("-" * 40)
                    # Print only first 20 lines to avoid overwhelming output
                    output_lines = result.stdout.split('\n')
                    for i, line in enumerate(output_lines[:20]):
                        print(line)
                    if len(output_lines) > 20:
                        print(f"... (truncated, total lines: {len(output_lines)})")
                
                if result.returncode != 0 and result.stderr:
                    print("\nStandard error:")
                    print("-" * 40)
                    print(result.stderr)
            except Exception as e:
                print(f"Error running script: {e}")
        else:
            print(f"Script not found: {script}")

def generate_report(base_url="http://localhost:5000"):
    """Generate a comprehensive diagnostic report"""
    print_header("DETAILED SERVER INFORMATION")
    
    try:
        # Get detailed debug info
        response = requests.get(f"{base_url}/api/debug-request", timeout=5)
        if response.status_code == 200:
            try:
                debug_info = response.json()
                print(json.dumps(debug_info, indent=2))
            except json.JSONDecodeError:
                print(f"Received non-JSON response: {response.text[:200]}...")
        else:
            print(f"Failed to get debug info. Status: {response.status_code}")
            
        # Get server status
        print("\nServer Status:")
        print("-" * 40)
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            try:
                status_info = response.json()
                print(json.dumps(status_info, indent=2))
            except json.JSONDecodeError:
                print(f"Received non-JSON response: {response.text[:200]}...")
        else:
            print(f"Failed to get server status. Status: {response.status_code}")
    
    except requests.RequestException as e:
        print(f"Error generating report: {e}")

def main():
    """Main diagnostic function"""
    base_url = "http://localhost:5000"
    
    print_header("MASHAAER FEELINGS DIAGNOSTICS")
    print(f"Running diagnostics on {base_url}")
    print(f"Date and time: {datetime.now().isoformat()}")
    print(f"Python version: {sys.version}")
    
    # Run all diagnostic tests
    server_ok = run_server_check(base_url)
    
    if server_ok:
        check_cors_configuration(base_url)
        run_diagnostic_tools(base_url)
        generate_report(base_url)
    
    print_header("DIAGNOSTICS COMPLETE")
    
    if server_ok:
        print("Server is accessible and responding to requests.")
        print("If the web application feedback tool still reports connectivity issues,")
        print("please see KNOWN_ISSUES.md and FEEDBACK_TOOL_SUMMARY.md for more information.")
    else:
        print("Server connectivity check failed.")
        print("Please ensure the Flask application is running on port 5000.")
        print("Try restarting the server or checking server logs for errors.")

if __name__ == "__main__":
    main()