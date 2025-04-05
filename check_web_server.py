"""
Simple utility to check if the web server is running.
"""
import requests
import time
import sys

def check_server(url="http://localhost:5000", max_attempts=3, delay=2):
    """
    Check if the server is running by making a request to the specified URL.
    
    Args:
        url: The URL to check
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
        
    Returns:
        True if server is running, False otherwise
    """
    print(f"Checking if web server is running at {url}...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"Success! Server is running (status code: {response.status_code})")
                return True
            else:
                print(f"Attempt {attempt}/{max_attempts}: Server responded with status code {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"Attempt {attempt}/{max_attempts}: Connection error - server may not be running")
        except requests.exceptions.Timeout:
            print(f"Attempt {attempt}/{max_attempts}: Request timed out")
        except Exception as e:
            print(f"Attempt {attempt}/{max_attempts}: Unexpected error: {str(e)}")
        
        if attempt < max_attempts:
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    
    print("Failed to connect to the server after multiple attempts.")
    return False

def check_endpoint(url="http://localhost:5000/micro-test", max_attempts=3, delay=2):
    """
    Check if a specific endpoint is accessible.
    
    Args:
        url: The endpoint URL to check
        max_attempts: Maximum number of attempts
        delay: Delay between attempts in seconds
        
    Returns:
        True if endpoint is accessible, False otherwise
    """
    print(f"Checking if endpoint is accessible at {url}...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"Success! Endpoint is accessible (status code: {response.status_code})")
                content_preview = response.text[:100] + "..." if len(response.text) > 100 else response.text
                print(f"Content preview: {content_preview}")
                return True
            else:
                print(f"Attempt {attempt}/{max_attempts}: Endpoint responded with status code {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"Attempt {attempt}/{max_attempts}: Connection error - server may not be running")
        except requests.exceptions.Timeout:
            print(f"Attempt {attempt}/{max_attempts}: Request timed out")
        except Exception as e:
            print(f"Attempt {attempt}/{max_attempts}: Unexpected error: {str(e)}")
        
        if attempt < max_attempts:
            print(f"Retrying in {delay} seconds...")
            time.sleep(delay)
    
    print("Failed to access the endpoint after multiple attempts.")
    return False

if __name__ == "__main__":
    # Check server and specific endpoint
    server_url = "http://localhost:5000"
    endpoint_url = "http://localhost:5000/micro-test"
    
    # Override URLs if provided as command line arguments
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    if len(sys.argv) > 2:
        endpoint_url = sys.argv[2]
    
    server_running = check_server(server_url)
    if server_running:
        endpoint_accessible = check_endpoint(endpoint_url)
        if endpoint_accessible:
            print("All checks passed. The server and endpoint are working correctly.")
            sys.exit(0)
        else:
            print("Server is running but the specific endpoint is not accessible.")
            sys.exit(1)
    else:
        print("Server check failed. Please ensure the server is running.")
        sys.exit(1)